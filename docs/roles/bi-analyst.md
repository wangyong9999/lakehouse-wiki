---
title: BI / 数据分析师
description: 湖上 SQL、建模、物化视图、仪表盘 —— BI 视角的优先阅读
hide:
  - toc
---

# BI / 数据分析师 · 优先阅读清单

**你的主战场**：写 SQL 出数、做报表、搭仪表盘、解释业务指标。理解湖的底层够用，**不必深到操作内核**。

## 必读：知道数据在哪里、怎么来

- [湖表](../lakehouse/lake-table.md)（粗读即可）
- [Snapshot](../lakehouse/snapshot.md) —— 知道"时间旅行"就够
- [OLTP vs OLAP](../foundations/oltp-vs-olap.md)
- [列式 vs 行式](../foundations/columnar-vs-row.md)

## BI 核心

- [OLAP 建模](../bi-workloads/olap-modeling.md)
- [物化视图](../bi-workloads/materialized-view.md)
- [查询加速](../bi-workloads/query-acceleration.md)
- [BI on Lake 场景](../scenarios/bi-on-lake.md)

## 查询引擎（按遇到的）

- [Trino](../query-engines/trino.md) —— 交互式最常用
- [DuckDB](../query-engines/duckdb.md) —— 本地探索
- [StarRocks](../query-engines/starrocks.md) —— 加速层常见
- [ClickHouse](../query-engines/clickhouse.md)
- [Apache Spark](../query-engines/spark.md) —— 看懂 DWD 作业

## 性能感
- [谓词下推](../foundations/predicate-pushdown.md) —— **这个一定读**，让你知道为什么"看起来一样的 SQL"会差几百倍
- [性能调优](../ops/performance-tuning.md)（分析师视角读"诊断"部分即可）

## 建议学习路径

走 [一周新人路径](../learning-paths/week-1-newcomer.md) →
[一月 BI 方向](../learning-paths/month-1-bi-track.md)。

## 常用速查

- [Iceberg 速查](../cheatsheets/iceberg.md) —— 常用 SQL 和时间旅行

## 场景

- [BI on Lake](../scenarios/bi-on-lake.md)

## 随时回头看

- [FAQ](../faq.md)
- [术语表](../glossary.md)

## 你会写的 ADR 类型

- "为什么我们选择按宽表而不是星型建模 XX 事实表"
- "Dashboard X 的 SLA 与优化路径"
- "加速副本 vs 物化视图 的成本 / 效果对比"
