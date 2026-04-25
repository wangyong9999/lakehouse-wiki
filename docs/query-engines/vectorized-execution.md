---
title: 向量化执行（Vectorized Execution）
type: concept
level: B
depth: 进阶
tags: [foundations, execution]
aliases: [Vectorized Query Processing, 向量化查询]
related: [columnar-vs-row, parquet, compression-encoding]
systems: [duckdb, clickhouse, starrocks, spark, velox]
applies_to: DuckDB · ClickHouse · StarRocks · Velox · Photon · Spark Tungsten · Polars
last_reviewed: 2026-04-18
status: stable
---

# 向量化执行

!!! tip "一句话理解"
    一次处理**一批行**（几百到几千）而不是一行行处理。每个算子对列式 batch 做循环，编译器能用 SIMD / 缓存预取，是"同样硬件跑出 10 倍吞吐"的核心技术。

## 为什么它出现

火山模型（Volcano / Iterator）是经典查询执行范式——算子之间通过 `next()` 调用，每次返回一行。每调一次 `next()` 就是一次虚函数 + 一次行处理。问题：

- 虚函数调用的分支预测失败频繁
- 每行数据重新进 cache，命中率低
- SIMD 指令没机会发挥
- CPU 流水线吃不饱

这些问题在 OLAP 大扫描场景放大到"CPU 明明没满，查询就是慢"。

## 向量化怎么解

1. **批量**：算子之间传递一个 `Batch`（一批列向量），而不是一行
2. **内循环是列循环**：`for (i=0; i<N; ++i) out[i] = a[i] + b[i]`
3. **数据连续**：列式 batch 在内存里就是连续数组，cache 友好
4. **编译器能自动 SIMD 化** 这种循环

```
Volcano:                          Vectorized:
filter.next()   ← 一行              filter.next()   ← 一批 1024 行
  scan.next()                         scan.next()
    project.eval(row)                   project.eval(batch)
```

在典型 TPCH / SSB 场景下，向量化执行器相对 Volcano 往往 **5–20 倍**吞吐提升，硬件一致。

## 不同算子的向量化

"向量化" 不只是过滤 —— 每种算子都有对应的批处理实现：

| 算子 | 向量化做法 | 关键技巧 |
|---|---|---|
| **Filter** | `for i in batch: mask[i] = pred(data[i])` | SIMD 比较 + selection vector |
| **Project / Expression** | 批内逐列算，算完再拼 | Const folding · 短路求值 |
| **Hash Aggregation** | 分批插入 hash table，冲突链 SIMD 探测 | 预 hash 整批 · 线性探测缓存友好 |
| **Hash Join** | Build 端批量建 hash table；Probe 端批量探测 | Bloom prefilter · radix 分桶 |
| **Sort** | 批内 radix sort / pdqsort | 基于列切片而非行 |
| **Top-N** | 维护 N 大小的堆，批量比较 | 可以结合 Bloom 早停 |

**关键**：hash aggregation 和 hash join 是 OLAP 最重的算子，它们的向量化实现（分桶 + SIMD 探测）是现代引擎打败老系统的关键。

## 延迟解码 · 在压缩数据上直接 SIMD

**现代向量化的杀手锏**：尽量"不解码"地处理数据。

经 [Dictionary 编码](../foundations/compression-encoding.md) 后，`country` 列从字符串变成 int index（如 `0=CN, 1=US, 2=JP`）。执行 `WHERE country = 'CN'` 时：

```
1. 查字典：'CN' → 0  （一次）
2. 对整列 int index 做 SIMD 比较 ==0  （每 CPU cycle 16 元素）
3. 延迟解码：只对命中的行去解字典（或压根不解）
```

这比"先全表解成字符串再比较"**快几十倍**。DuckDB · Velox · ClickHouse · Polars 都大量使用这条路径。[压缩与编码](../foundations/compression-encoding.md) 有更完整的讨论（见"和向量化执行的协同"段）。

## 延展：Compile-time 代码生成（Codegen）

有些引擎把"循环内的表达式"JIT 成机器码：

- **Spark Tungsten**：Whole-stage code generation
- **ClickHouse**：内联 + LLVM codegen 一些表达式
- **DuckDB**：采用向量化但不做 JIT，靠优质 C++ 加模板

两条路各有优缺：JIT 开销大但内循环极快，纯向量化无 JIT 延迟但 cross-operator 优化弱一点。

## 和列式存储的关系

**列式 + 向量化是同一个故事的两面**：

- 存储侧（Parquet/Arrow/Lance）就是"列连续的一批"
- 执行侧（Vectorized）直接消费这批，零转换
- 端到端的"零拷贝 + SIMD"链路

湖仓所有现代引擎都吃这条增益：Trino、Spark（Tungsten/Columnar）、DuckDB、StarRocks、ClickHouse。

## 相关概念

- [列式 vs 行式](../foundations/columnar-vs-row.md) —— 存储侧的前提
- [压缩与编码](../foundations/compression-encoding.md) —— "在压缩数据上 SIMD" 的另一半
- [Parquet](../foundations/parquet.md) / [Lance Format](../foundations/lance-format.md) —— 典型列式源
- [谓词下推](predicate-pushdown.md) —— 减少进入向量化引擎的数据量

## 延伸阅读

- **[*MonetDB/X100 · Hyper-Pipelining Query Execution*](https://www.cidrdb.org/cidr2005/papers/P19.pdf)** (Boncz et al., CIDR 2005) —— 向量化的原始论文
- **[*Everything You Always Wanted to Know About Compiled and Vectorized Queries*](https://www.vldb.org/pvldb/vol11/p2209-kersten.pdf)** (Kersten et al., VLDB 2018) —— 向量化 vs JIT 对比
- **[*Velox · Meta's Unified Execution Engine*](https://research.facebook.com/publications/velox-metas-unified-execution-engine/)** (VLDB 2022) —— 工业级向量化引擎的抽象
- **[DuckDB · Execution Format](https://duckdb.org/why_duckdb#fast)** · **[ClickHouse · Columnar Engine](https://clickhouse.com/docs/en/development/architecture)**
