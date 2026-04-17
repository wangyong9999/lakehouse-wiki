---
title: 向量化执行（Vectorized Execution）
type: concept
tags: [foundations, execution]
aliases: [Vectorized Query Processing, 向量化查询]
related: [columnar-vs-row, parquet]
systems: [duckdb, clickhouse, starrocks, spark]
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

- [列式 vs 行式](columnar-vs-row.md) —— 存储侧的前提
- [Parquet](parquet.md) / [Lance Format](lance-format.md) —— 典型列式源

## 延伸阅读

- *MonetDB/X100: Hyper-Pipelining Query Execution* (Boncz et al., CIDR 2005) —— 向量化的原始论文
- *Everything You Always Wanted to Know About Compiled and Vectorized Queries But Were Afraid to Ask* (Kersten et al., VLDB 2018)
