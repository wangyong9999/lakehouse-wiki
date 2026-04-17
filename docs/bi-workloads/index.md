---
title: BI 负载
description: 在湖仓上支撑 OLAP / 报表 / 仪表盘的工程实践
---

# BI 负载

传统 BI 的主要诉求是 **"大数据量 + 低交互延迟 + 业务人员能自助"**。本节聚焦湖仓能力如何支撑这些诉求。

## 已有

- [OLAP 建模](olap-modeling.md) —— 星型 / 雪花 / 宽表，湖仓为什么偏爱宽表
- [物化视图](materialized-view.md) —— 预聚合加速的主力手段
- [查询加速](query-acceleration.md) —— Zone Maps / Sort / Z-order / Liquid Clustering

## 待补

- 缓存层（Alluxio / 查询结果缓存）
- Dashboard 模式与反模式
- Semantic Layer / Metrics Layer

## 相关

- 场景：[BI on Lake](../scenarios/bi-on-lake.md)
- 引擎：[Trino](../query-engines/trino.md) · [Spark](../query-engines/spark.md) · [StarRocks](../query-engines/starrocks.md) · [DuckDB](../query-engines/duckdb.md)
- 学习路径：[一月 BI 方向](../learning-paths/month-1-bi-track.md)
