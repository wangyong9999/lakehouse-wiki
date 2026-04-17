---
title: 场景指南
description: 端到端的典型场景 —— 输入、流水线、关键选型
---

# 场景指南

每一页都是一条**端到端叙事**：从数据源到最终消费，把各层的选择串起来。

## 已有

- [RAG on Lake](rag-on-lake.md) —— 把湖作为 RAG 的单一事实源
- [BI on Lake](bi-on-lake.md) —— 把传统 BI 负载搬到湖仓之上
- [多模检索流水线](multimodal-search-pipeline.md) —— 图 / 文 / 音 / 视混合检索

## 待补

- Streaming Ingestion（Kafka → Paimon / Iceberg 流式入湖）
- Offline Training Pipeline（基于湖上数据做模型训练）
- Feature Serving（在线推理的特征供给）
