---
title: 参考资料 · BI 负载
type: reference
status: stable
tags: [reference, references, bi]
description: OLAP 建模 / 物化视图 / 语义层 / dbt 经典
last_reviewed: 2026-04-25
---

# 参考资料 · BI 负载

## OLAP / 维度建模

- **[The Data Warehouse Toolkit](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/data-warehouse-dw-toolkit/)** _(2013, book - Kimball)_ —— 维度建模经典圣经。
- **[Building the Data Warehouse](https://www.wiley.com/en-us/Building+the+Data+Warehouse%2C+4th+Edition-p-9780764599446)** _(2005, book - Inmon)_ —— Inmon vs Kimball 争论的另一方。

## 物化视图 / IVM

- **[Materialized Views](https://users.cs.duke.edu/~ashwin/teaching/CPS296_2008/papers/gupta_kdd97.pdf)** _(1997, survey)_ —— MV 经典综述。
- **[Differential Dataflow](https://github.com/TimelyDataflow/differential-dataflow)** _(official-doc)_ —— 增量计算理论 + Materialize 引擎。
- **[Materialize Documentation](https://materialize.com/docs/)** _(official-doc)_ —— 流式 MV 引擎。

## 语义层 / Metrics Layer

- **[dbt Semantic Layer Documentation](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)** _(official-doc)_ —— dbt 语义层。
- **[Cube.dev Documentation](https://cube.dev/docs)** _(official-doc)_ —— Cube 语义层。
- **[Airbnb - Minerva](https://medium.com/airbnb-engineering/how-airbnb-achieved-metric-consistency-at-scale-f23cc53dea70)** _(2021, blog)_ —— 语义层鼻祖博客。
- **[The Rise of the Metrics Layer](https://benn.substack.com/p/metrics-layer)** _(2021, blog - Benn Stancil)_ —— Metrics Layer 行业演进。

## 查询加速

- **[Z-order Curves](https://en.wikipedia.org/wiki/Z-order_curve)** _(reference)_ —— Z-order 数据布局。
- **[Liquid Clustering (Databricks)](https://docs.databricks.com/en/delta/clustering.html)** _(official-doc)_ —— Delta Lake 后续 clustering。

## BI × LLM

- **[Snowflake Cortex Analyst Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)** _(official-doc)_ —— Text-to-SQL 工业先驱。
- **[Databricks Genie Documentation](https://docs.databricks.com/en/genie/index.html)** _(official-doc)_ —— Genie 自然语言 BI。

---

**待补**：Cube.dev 与 dbt SL 对比的工业实践博客；Materialize / RisingWave 对比
