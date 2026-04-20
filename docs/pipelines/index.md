---
title: 数据管线
description: 入湖、ETL、多模预处理、编排 —— 湖仓的"血管"
---

# 数据管线

!!! tip "它是什么"
    湖仓的"数据从哪来"和"数据怎么处理"统一集中在这一节。包括入湖协议、多模内容预处理（图/视/音/文档）、编排与调度。

## 入湖与同步

- [Kafka 到湖：从日志到事实表](kafka-ingestion.md) —— Kafka / Debezium / Flink CDC 的组合拳
- [Bulk Loading（批量装载）](bulk-loading.md) —— 初始化 / 历史数据迁移 / 从 Hive 过来
- [流式入湖](../scenarios/streaming-ingestion.md) _（场景页，端到端视图）_

## 多模内容管线（"数据湖" 里 "多模" 那部分的真功夫）

- [图像管线](image-pipeline.md) —— 归一化 → caption → embedding
- [视频管线](video-pipeline.md) —— 抽帧 → 代表帧 → 时序聚合
- [音频管线](audio-pipeline.md) —— ASR → diarization → embedding
- [文档管线](document-pipeline.md) —— 解析 + OCR + chunking

## Embedding 与特征

- [Embedding 流水线](../ml-infra/embedding-pipelines.md) _（概念页，批+流）_
- [离线训练数据流水线](../scenarios/offline-training-pipeline.md) _（场景页）_
- [Feature Serving](../scenarios/feature-serving.md) _（场景页）_

## 编排

- [编排系统概览](orchestration.md) —— Airflow / Dagster / Prefect / Flyte 怎么选

## 相关

- [Streaming Upsert / CDC](../lakehouse/streaming-upsert-cdc.md)
- [Compaction](../lakehouse/compaction.md)
- [可观测性](../ops/observability.md)
