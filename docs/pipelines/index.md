---
title: 数据管线
type: reference
status: stable
tags: [index, pipelines]
description: 入湖、CDC、多模预处理、编排 —— 湖仓的"血管"
last_reviewed: 2026-04-20
---

# 数据管线

湖仓的"**数据从哪来**"和"**数据怎么处理**"集中在这一节：入湖协议、CDC 技术、托管 EL(T) 工具、多模内容预处理、编排调度，以及生产必修的管线韧性横切主题。

!!! info "和其他章节的边界"
    - [lakehouse/Streaming Upsert · CDC](../lakehouse/streaming-upsert-cdc.md) · 讲**湖表侧**如何接 CDC（MoR · changelog producer · 主键表语义）
    - [query-engines/Apache Flink](../query-engines/flink.md) · 讲 Flink **作为引擎**的架构
    - [scenarios/流式入湖](../scenarios/streaming-ingestion.md) · 讲**端到端场景**（业务视角）
    - [ops/灾难恢复 DR](../ops/disaster-recovery.md) · 讲**湖表层**灾备（本章 pipeline-resilience 讲**管线层**韧性）

## 5 种入湖路径 · 先决策再看产品

| 场景 | 推荐路径 |
|---|---|
| OLTP DB（MySQL / PG / Mongo）持续同步到湖 | **CDC** · [Flink CDC 3.x Pipeline](cdc-internals.md) / [Paimon CDC](cdc-internals.md) / [Debezium+Kafka](kafka-ingestion.md) |
| 历史 / 冷启动 / 迁库 | **[Bulk Loading](bulk-loading.md)** |
| 小团队 / 不想自建栈 | **[托管 EL(T)](managed-ingestion.md)** · Airbyte / Fivetran / SeaTunnel / AWS DMS / Databricks Auto Loader |
| 多模内容（图 / 视 / 音 / 文档）预处理入湖 | **[模态管线](image-pipeline.md)** |
| 持续消费 Kafka 流入湖 | **[Kafka 到湖](kafka-ingestion.md)** |

**端到端架构总览** · 看 **[架构模式总览](pipeline-patterns.md)**——**6 种端到端模式**（含 1 种 **非湖仓对照路径** Kafka→OLAP DB 避免读者形成"湖仓至上"偏见）· 每种的拓扑 / 工具栈 / 延迟 / 陷阱 / 选型决策树。

## 入湖与 CDC

- [CDC 内核](cdc-internals.md) —— 三种范式 · Debezium · Flink CDC 3.x · Paimon CDC · Iceberg Sink 跨引擎
- [Kafka 到湖](kafka-ingestion.md) —— Kafka 作为中转的工程决策
- [托管数据入湖](managed-ingestion.md) —— Airbyte / Fivetran / SeaTunnel / Auto Loader / AWS DMS
- [Bulk Loading（批量装载）](bulk-loading.md) —— 初始化 / 历史数据迁移
- [事件时间 · Watermark](event-time-watermark.md) —— 流式时间语义前置
- [流式入湖](../scenarios/streaming-ingestion.md) _（场景页 · 端到端视图）_

## 多模内容管线（"数据湖"里"多模"那部分的真功夫）

- [图像管线](image-pipeline.md) —— 归一化 → caption → embedding
- [视频管线](video-pipeline.md) —— 抽帧 → 代表帧 → 时序聚合
- [音频管线](audio-pipeline.md) —— ASR → diarization → embedding
- [文档管线](document-pipeline.md) —— 解析 + OCR + chunking

## 编排

- [编排系统概览](orchestration.md) —— Airflow / Dagster / Prefect / Flyte 怎么选
- [调度系统横比](../compare/orchestrators.md) _（对比页）_

## 生产韧性 · 横切主题

- [管线韧性](pipeline-resilience.md) —— 端到端 Exactly-once · Schema Evolution 传播 · DLQ · 回填 · Backpressure

## Embedding 与特征 · 相邻章节

- [Embedding 流水线](../ml-infra/embedding-pipelines.md) _（ml-infra 页 · 批+流）_
- [离线训练数据流水线](../scenarios/offline-training-pipeline.md) _（场景页）_
- [Feature Serving](../scenarios/feature-serving.md) _（场景页）_

## 相关

- [Streaming Upsert / CDC](../lakehouse/streaming-upsert-cdc.md) _（湖表侧语义）_
- [Compaction · 维护生命周期](../lakehouse/compaction.md)
- [可观测性](../ops/observability.md)
