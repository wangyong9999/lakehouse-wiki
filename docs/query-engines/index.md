---
title: 查询引擎
description: 直接读湖仓表的主流 SQL / 分析引擎
---

# 查询引擎

在湖仓之上执行 SQL / 分析 / 流处理的引擎。每个引擎都在"向量化 × 分布式 × 湖表读写能力"三个轴上有取舍。

## 待补

- Trino / Presto —— 交互式查询
- Apache Spark —— 批处理 + 流 + 机器学习
- Apache Flink —— 流优先
- DuckDB —— 嵌入式 OLAP
- StarRocks / Apache Doris —— MPP + 物化视图
- ClickHouse —— 明细事实表的极致

## 相关

- 基础：向量化执行、MPP、列式存储
- 上游：[湖仓表格式](../lakehouse/index.md) · [Catalog](../catalog/index.md)
