---
title: 查询引擎
description: 直接读湖仓表的主流 SQL / 分析引擎
---

# 查询引擎

在湖仓之上执行 SQL / 分析 / 流处理的引擎。每个引擎都在"向量化 × 分布式 × 湖表读写能力"三个轴上有取舍。

## 已有

- [Trino](trino.md) —— 交互式查询，BI 前台
- [Apache Spark](spark.md) —— 批 ETL + Structured Streaming + ML
- [DuckDB](duckdb.md) —— 嵌入式 OLAP，开发态 / 单机分析利器

## 待补

- Apache Flink —— 流优先
- StarRocks / Apache Doris —— MPP + 物化视图
- ClickHouse —— 明细事实表的极致

## 相关

- 底座：[湖仓表格式](../lakehouse/index.md) · [Catalog](../catalog/index.md)
