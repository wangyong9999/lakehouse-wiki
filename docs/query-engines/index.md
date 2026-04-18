---
title: 查询引擎
description: 直接读湖仓表的主流 SQL / 分析引擎
---

# 查询引擎

在湖仓之上执行 SQL / 分析 / 流处理的引擎。每个引擎都在"向量化 × 分布式 × 湖表读写能力"三个轴上有取舍。

## 引擎

- [Trino](trino.md) —— 交互式查询，BI 前台
- [Apache Spark](spark.md) —— 批 ETL + Structured Streaming + ML
- [Apache Flink](flink.md) —— 流优先，CDC 入湖主力
- [DuckDB](duckdb.md) —— 嵌入式 OLAP，开发态 / 单机分析利器
- [StarRocks](starrocks.md) —— MPP + 物化视图，BI 加速层首选
- [ClickHouse](clickhouse.md) —— 单表大扫描 + 高并发聚合的极致
- [Apache Doris](doris.md) —— MPP + 湖仓融合，StarRocks 的同源兄弟

## 相关

- 底座：[湖仓表格式](../lakehouse/index.md) · [Catalog](../catalog/index.md)
- 场景：[BI on Lake](../scenarios/bi-on-lake.md) · [流式入湖](../scenarios/streaming-ingestion.md)
