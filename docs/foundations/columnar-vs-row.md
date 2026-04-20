---
title: 列式 vs 行式存储
type: concept
tags: [foundations, storage]
aliases: [Columnar vs Row]
related: [parquet, lance-format, vectorized-execution]
systems: [parquet, orc, lance, innodb]
status: stable
---

# 列式 vs 行式存储

!!! tip "一句话理解"
    **行式**把一行所有字段连着存 —— 适合"读整行"的 OLTP；**列式**把一列所有值连着存 —— 适合"扫很多行但只取少数列"的 OLAP 与 AI 数据准备。湖仓 99% 选列式。

## 结构差异

给一张表 `(id, name, age, city)`，三行数据：

**行式**存储：

```
[1|Alice|30|NYC] [2|Bob|25|SF] [3|Cat|35|LA]
```

**列式**存储：

```
id   : [1, 2, 3]
name : [Alice, Bob, Cat]
age  : [30, 25, 35]
city : [NYC, SF, LA]
```

一个是"行粒度连续"，一个是"列粒度连续"。

## 为什么列式适合分析

1. **列剪裁（column pruning）** —— 查询 `SELECT avg(age)` 只读 `age` 这一列，完全不碰其他
2. **压缩比高** —— 同列值类型一致、重复多，字典 / RLE / bit-packing 效果极好；行式做不到
3. **向量化执行友好** —— 一列连续存放 = SIMD 批处理的天然输入
4. **谓词下推 + 统计** —— 每个 Row Group / Block 存 min/max/bloom，查询可以**跳过**大片数据

典型 10 倍以上的分析吞吐差距，都来自这四件事。

## 为什么行式适合事务

1. **写一行 = 一次 IO** —— 列式要写 N 次（每列一次）
2. **点查读整行方便** —— 列式要拼回 N 列
3. **行锁 / MVCC 简单** —— 行是最小管理单位

所以 OLTP（MySQL InnoDB、dstore）全用行式，OLAP / 湖仓 / AI 训练数据全用列式。

## 混合派：PAX / Row Group

两个世界中间有一条路叫 **PAX / Row Group**：把一批行（例如 128MB）作为一个"块"，块内按列存。这是 Parquet / ORC / Lance 共用的思路：

- 块内列式 → 批量分析快
- 块仍以"批行"为单位 → IO 粒度可控

这基本等于"列式的 99%，但对大块批写更友好"。

## 湖仓里的含义

湖表层面你看到的 Parquet / ORC / Lance 都是**列式**的（更准确说是 PAX 列式）。
这决定了你**在湖上最好的两件事**：

- **OLAP 分析** —— 列式天然加成
- **AI 数据准备 / 训练集** —— 批扫 + 列剪裁是典型访问模式

**最坏的事**：高频行级点查。这种负载要么离开湖（走 DB），要么在湖上加一层加速（ClickHouse / StarRocks 作为物化层）。

## 相关概念

- [Parquet](parquet.md)、[Lance Format](lance-format.md) —— 主流列式实现
- [向量化执行](../query-engines/vectorized-execution.md) —— 列式的直接受益者

## 延伸阅读

- *Column-Stores vs. Row-Stores: How Different Are They Really?* (Abadi et al., SIGMOD 2008)
- *Weaving Relations for Cache Performance* (PAX paper, VLDB 2001)
