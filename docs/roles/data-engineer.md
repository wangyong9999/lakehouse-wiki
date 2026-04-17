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

走 [一周新人路径](../learning-paths/week-1-newcomer.md) → 之后按"入湖 → 运维 → 深入某个引擎"推进。

## 常用速查

- [Iceberg 速查](../cheatsheets/iceberg.md)

## 随时回头看

- [FAQ](../faq.md)
- [术语表](../glossary.md)
