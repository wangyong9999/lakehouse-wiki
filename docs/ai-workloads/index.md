---
title: AI 负载
description: 在湖仓 / 多模检索之上跑的 AI 应用与基础设施
---

# AI 负载

"湖仓 + 检索" 本身是基础设施，这一节回答 **AI 应用怎么用它**。

## 已有

- [RAG](rag.md) —— 检索增强生成
- [Feature Store](feature-store.md) —— ML 特征的一等公民

## 待补

- Online / Offline 特征一致性
- Embedding 流水线（批生成 + 增量刷新）
- Semantic Cache
- LLM on Lakehouse（训练数据准备、评估集管理）

## 相关

- 上游：[多模检索](../retrieval/index.md)
- 场景：[RAG on Lake](../scenarios/rag-on-lake.md) · [多模检索流水线](../scenarios/multimodal-search-pipeline.md)
- 架构：[Lake + Vector 融合架构](../unified/lake-plus-vector.md)
