---
title: AI 负载
description: 在湖仓 / 多模检索之上跑的 AI 应用与基础设施
---

# AI 负载

"湖仓 + 检索" 本身是基础设施，这一节回答 **AI 应用怎么用它**。

## 已有

- [RAG](rag.md) —— 检索增强生成
- [Embedding 流水线](embedding-pipelines.md) —— 持续把语料转成向量并回落到湖
- [Feature Store](feature-store.md) —— ML 特征的一等公民
- [Semantic Cache](semantic-cache.md) —— 降低 LLM 调用成本的语义缓存

## 待补

- Online / Offline 特征一致性
- LLM on Lakehouse（训练数据准备、评估集管理）
- Agent + 湖上工具调用

## 相关

- 上游：[多模检索](../retrieval/index.md)
- 场景：[RAG on Lake](../scenarios/rag-on-lake.md) · [多模检索流水线](../scenarios/multimodal-search-pipeline.md)
- 架构：[Lake + Vector 融合架构](../unified/lake-plus-vector.md)
