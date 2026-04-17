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
- [流式入湖](streaming-ingestion.md) —— CDC + 事件流持续入湖
- [Real-time Lakehouse](real-time-lakehouse.md) —— 端到端分钟级一体化（BI + AI + DS 都读准实时）
- [离线训练数据流水线](offline-training-pipeline.md) —— 可复现 + PIT 的训练集生成
- [Feature Serving](feature-serving.md) —— 在线推理的毫秒级特征拉取

## 待补

- Cross-cloud / 多区域
- 数据迁移手册（Hive → Iceberg 等）
