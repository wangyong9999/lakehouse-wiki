---
title: 数据工程师
description: 入湖、建表、ETL、Compaction、性能 —— 数据工程师的优先阅读
hide:
  - toc
---

# 数据工程师 · 优先阅读清单

**你的主战场**：湖表怎么建、数据怎么进、作业怎么稳、性能怎么调。

## 入门 · 先把心智模型搭起来

- [湖表](../lakehouse/lake-table.md)
- [Snapshot](../lakehouse/snapshot.md)
- [Manifest](../lakehouse/manifest.md)
- [对象存储](../foundations/object-storage.md)
- [DB 引擎 vs 湖表](../compare/db-engine-vs-lake-table.md)

## 进阶 · 表格式 + 演化

- [Schema Evolution](../lakehouse/schema-evolution.md)
- [Partition Evolution](../lakehouse/partition-evolution.md)
- [Time Travel](../lakehouse/time-travel.md)
- [Branching & Tagging](../lakehouse/branching-tagging.md)
- [Apache Iceberg](../lakehouse/iceberg.md)
- [Apache Paimon](../lakehouse/paimon.md)

## 入湖与管线

- [Streaming Upsert / CDC](../lakehouse/streaming-upsert-cdc.md)
- [Kafka 到湖](../pipelines/kafka-ingestion.md)
- [Bulk Loading](../pipelines/bulk-loading.md)
- [编排系统概览](../pipelines/orchestration.md)
- 场景：[流式入湖](../scenarios/streaming-ingestion.md)

## 运维必修

- [Compaction](../lakehouse/compaction.md)
- [Delete Files](../lakehouse/delete-files.md)
- [可观测性](../ops/observability.md)
- [性能调优](../ops/performance-tuning.md)
- [故障排查手册](../ops/troubleshooting.md)

## 建议学习路径

先走 [一周新人路径](../learning-paths/week-1-newcomer.md)（湖 + 检索心智模型）。之后按下面 4-6 周节奏推进：

| 周 | 主题 | 重点页 |
|---|---|---|
| **Week 2** | 入湖链路：CDC / Kafka / Bulk | [Streaming Upsert · CDC](../lakehouse/streaming-upsert-cdc.md) · [Kafka 到湖](../pipelines/kafka-ingestion.md) · [Bulk Loading](../pipelines/bulk-loading.md) · [流式入湖场景](../scenarios/streaming-ingestion.md) |
| **Week 3** | 运维日常：Compaction / 小文件 / 删除 | [Compaction](../lakehouse/compaction.md) · [Delete Files](../lakehouse/delete-files.md) · [20 反模式](../ops/anti-patterns.md) |
| **Week 4** | 性能与可观测 | [性能调优](../ops/performance-tuning.md) · [可观测性](../ops/observability.md) · [故障排查](../ops/troubleshooting.md) |
| **Week 5-6** | 深入一个引擎（按负载选） | [Spark](../query-engines/spark.md) · [Flink](../query-engines/flink.md) · [Trino](../query-engines/trino.md) · [DuckDB](../query-engines/duckdb.md) |
| **后续** | 资深路径 | [一季度资深路径](../learning-paths/quarter-advanced.md) |

> AI / BI 方向的同事有独立 month-1 路径；数据工程角色跨度大，按"实际在处理什么"选一两周深入即可，不必线性读完。

## 常用速查

- [Iceberg 速查](../cheatsheets/iceberg.md)

## 随时回头看

- [FAQ](../faq.md)
- [术语表](../glossary.md)
