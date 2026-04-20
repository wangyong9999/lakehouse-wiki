---
title: AI 负载
description: 在湖仓 / 多模检索之上跑的 AI 应用与基础设施
---

# AI 负载

"湖仓 + 检索" 本身是基础设施，这一节回答 **AI 应用怎么用它**。

## 核心概念

- [**RAG · 检索增强生成**](rag.md) ⭐ —— 原理 + 管线 + 2025 高级范式
- [**Feature Store**](../ml-infra/feature-store.md) ⭐ —— ML 特征的一等公民
- [**MLOps 生命周期**](../ml-infra/mlops-lifecycle.md) ⭐ —— 数据 → 训练 → 评估 → 上线 → 监控闭环
- [**MCP · Model Context Protocol**](mcp.md) ⭐ —— Anthropic 2024 开放协议

## 应用能力

- [RAG 评估](rag-evaluation.md) —— Groundedness / Context Relevance / Answer Relevance
- [Prompt 管理](prompt-management.md) —— Prompt 作为代码资产
- [Agents on Lakehouse](agents-on-lakehouse.md) —— LLM + 工具 + 湖
- [Semantic Cache](semantic-cache.md) —— 降低 LLM 调用成本
- [Embedding 流水线](../ml-infra/embedding-pipelines.md) —— 持续把语料转成向量并回落到湖
- [微调数据准备](../ml-infra/fine-tuning-data.md) —— SFT / DPO 数据工程

## 前沿专题（跳转 frontier）

- [RAG 前沿](../frontier/rag-advances-2025.md) —— CRAG / Self-RAG / Agentic RAG / Contextual Retrieval
- [LLM 推理优化](../frontier/llm-inference-opt.md) —— vLLM / Flash Attention / Speculative / MoE
- [向量检索前沿](../frontier/vector-trends.md) —— Matryoshka / Binary / SPLADE v3
- [AI 治理](../frontier/ai-governance.md) —— EU AI Act / Guardrails / Red Teaming

## 横向对比（跳转 compare）

- [Feature Store 横比](../compare/feature-store-comparison.md)
- [Embedding 模型横比](../compare/embedding-models.md) · [Rerank 模型横比](../compare/rerank-models.md)

## 底层依赖

- [ML 基础设施](../ml-infra/index.md) —— Model Registry / Serving / Training / GPU
- [多模检索](../retrieval/index.md) —— 向量 + Hybrid + Rerank

## 场景

- [RAG on Lake](../scenarios/rag-on-lake.md) · [多模检索流水线](../scenarios/multimodal-search-pipeline.md)
- [推荐系统](../scenarios/recommender-systems.md) · [欺诈检测](../scenarios/fraud-detection.md) · [CDP](../scenarios/cdp-segmentation.md)
- [Agentic 工作流](../scenarios/agentic-workflows.md)
- [离线训练数据流水线](../scenarios/offline-training-pipeline.md) · [Feature Serving](../scenarios/feature-serving.md)

## 架构参考

- [Lake + Vector 融合架构](../unified/lake-plus-vector.md) · [Compute Pushdown](../unified/compute-pushdown.md)

