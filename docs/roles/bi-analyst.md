---
title: BI / 数据分析师
description: 湖上 SQL、建模、物化视图、仪表盘 —— BI 视角的优先阅读
hide:
  - toc
---

# BI / 数据分析师 · 优先阅读清单

**你的主战场**：写 SQL 出数、做报表、搭仪表盘、解释业务指标。理解湖的底层够用，**不必深到操作内核**。

!!! tip "高频任务速跳"
    - **报表跑得慢** → [谓词下推](../query-engines/predicate-pushdown.md) · [性能调优](../ops/performance-tuning.md) · [查询加速](../bi-workloads/query-acceleration.md)
    - **建语义层 / 指标中台** → [Semantic Layer](../bi-workloads/semantic-layer.md)（dbt / Cube / LookML）
    - **选加速副本** → [OLAP 加速副本对比](../compare/olap-accelerator-comparison.md) · [物化视图](../bi-workloads/materialized-view.md)
    - **建模（星型 / 宽表 / Data Vault）** → [OLAP 建模](../bi-workloads/olap-modeling.md)
    - **端到端 BI on Lake** → [BI on Lake 场景](../scenarios/bi-on-lake.md)

## 必读：知道数据在哪里、怎么来

- [湖表](../lakehouse/lake-table.md)（粗读即可）
- [Snapshot](../lakehouse/snapshot.md) —— 知道"时间旅行"就够
- [OLTP vs OLAP](../foundations/oltp-vs-olap.md)
- [列式 vs 行式](../foundations/columnar-vs-row.md)

## BI 核心

- [OLAP 建模](../bi-workloads/olap-modeling.md) —— 星型 / 雪花 / 宽表 / Data Vault / Galaxy / VARIANT
- [**语义层 · Semantic Layer**](../bi-workloads/semantic-layer.md) ⭐ —— dbt / Cube / LookML 指标中台 · LLM × SL
- [物化视图](../bi-workloads/materialized-view.md) —— IVM · Query Rewrite · Iceberg MV
- [查询加速](../bi-workloads/query-acceleration.md) —— Zone Maps / Sort / Z-order / Puffin / 加速副本
- [**仪表盘 SLO**](../bi-workloads/dashboard-slo.md) ⭐ —— 并发/延迟/新鲜度工程
- [**BI × LLM**](../bi-workloads/bi-plus-llm.md) ⭐ —— 2026 变革 · Genie/Cortex Analyst/Tableau Pulse
- [BI on Lake 场景](../scenarios/bi-on-lake.md)

!!! tip "你要不要当 Analytics Engineer"
    如果你的工作越来越偏"**定义指标、写 dbt models、管语义层**"，而不只是写 SQL 取数，那你其实在做 Analytics Engineering。除了上面 BI 核心，额外读 [Semantic Layer](../bi-workloads/semantic-layer.md) 的 dbt / Cube 章节 + [数据治理](../ops/data-governance.md) + [OLAP 建模](../bi-workloads/olap-modeling.md) 里的 Data Vault 2.0 段。

## 查询引擎（按遇到的）

- [Trino](../query-engines/trino.md) —— 交互式最常用
- [DuckDB](../query-engines/duckdb.md) —— 本地探索
- [StarRocks](../query-engines/starrocks.md) —— 加速层常见
- [ClickHouse](../query-engines/clickhouse.md)
- [Apache Spark](../query-engines/spark.md) —— 看懂 DWD 作业

## 性能感
- [谓词下推](../query-engines/predicate-pushdown.md) —— **这个一定读**，让你知道为什么"看起来一样的 SQL"会差几百倍
- [性能调优](../ops/performance-tuning.md)（分析师视角读"诊断"部分即可）

## 建议学习路径

先走 [一周新人路径](../learning-paths/week-1-newcomer.md)（湖 + 检索心智模型），再走 [一月 BI 方向](../learning-paths/month-1-bi-track.md)。

> **一月 BI 方向** 覆盖：OLAP 建模（星型 / 宽表 / Data Vault）· 物化视图与查询加速 · 语义层 / dbt · OLAP 加速副本（StarRocks / ClickHouse）· BI on Lake 场景端到端 · SLA / SLO 打法。

## 常用参考

- [Apache Iceberg §5 代码示例 + §6 维护](../lakehouse/iceberg.md) —— 常用 SQL 和时间旅行
- [物化视图](../bi-workloads/materialized-view.md) · [查询加速](../bi-workloads/query-acceleration.md)

## 场景

- [BI on Lake](../scenarios/bi-on-lake.md)

## 随时回头看

- [FAQ](../faq.md)
- [术语表](../glossary.md)

## 你会写的 ADR 类型

- "为什么我们选择按宽表而不是星型建模 XX 事实表"
- "Dashboard X 的 SLA 与优化路径"
- "加速副本 vs 物化视图 的成本 / 效果对比"
