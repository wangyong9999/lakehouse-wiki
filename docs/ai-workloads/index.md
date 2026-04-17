---
title: AI 负载
description: 在湖仓 / 多模检索之上跑的 AI 应用与基础设施
---

# AI 负载

"湖仓 + 检索" 本身是基础设施，这一节回答 **AI 应用怎么用它**。

## 已有

- [RAG](rag.md) —— 检索增强生成
- [RAG 评估](rag-evaluation.md) —— Groundedness / Context Relevance / Answer Relevance
- [Prompt 管理](prompt-management.md) —— Prompt 作为代码资产
- [Agents on Lakehouse](agents-on-lakehouse.md) —— LLM + 工具 + 湖
- [Semantic Cache](semantic-cache.md) —— 降低 LLM 调用成本的语义缓存
- [Feature Store](feature-store.md) —— ML 特征的一等公民
- [Embedding 流水线](embedding-pipelines.md) —— 持续把语料转成向量并回落到湖
- [微调数据准备](fine-tuning-data.md) —— SFT / DPO 数据工程

## 底层依赖

- [ML 基础设施](../ml-infra/index.md) —— Model Registry / Serving / Training / GPU 调度
- [多模检索](../retrieval/index.md) —— 向量 + Hybrid + Rerank

## 场景

- [RAG on Lake](../scenarios/rag-on-lake.md)
- [多模检索流水线](../scenarios/multimodal-search-pipeline.md)
- [离线训练数据流水线](../scenarios/offline-training-pipeline.md)
- [Feature Serving](../scenarios/feature-serving.md)

## 架构参考

- [Lake + Vector 融合架构](../unified/lake-plus-vector.md)
- [Compute Pushdown](../unified/compute-pushdown.md)

## 待补

- Online / Offline 特征一致性细节
- LLM Gateway（OpenAI proxy / LiteLLM / LangSmith）
- 安全对齐（guardrails / moderation）
