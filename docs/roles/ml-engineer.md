---
title: ML / AI 工程师
description: 向量检索、Embedding、RAG、Feature Store、Model Serving
hide:
  - toc
---

# ML / AI 工程师 · 优先阅读清单

**你的主战场**：在湖上做检索、训练、RAG、Agent、多模。

## 入门 · 先理解"湖 + 向量"

- [湖表](../lakehouse/lake-table.md)
- [向量数据库](../retrieval/vector-database.md)
- [Embedding](../retrieval/embedding.md)
- [多模 Embedding](../retrieval/multimodal-embedding.md)
- [多模数据建模](../unified/multimodal-data-modeling.md)
- [Lake + Vector 融合架构](../unified/lake-plus-vector.md)

## 检索核心

- [HNSW](../retrieval/hnsw.md) / [IVF-PQ](../retrieval/ivf-pq.md) / [DiskANN](../retrieval/diskann.md)
- [Hybrid Search](../retrieval/hybrid-search.md)
- [Rerank](../retrieval/rerank.md)
- [检索评估](../retrieval/evaluation.md)
- [跨模态查询](../unified/cross-modal-queries.md)

## AI 负载

- [RAG](../ai-workloads/rag.md)
- [RAG 评估](../ai-workloads/rag-evaluation.md)
- [Prompt 管理](../ai-workloads/prompt-management.md)
- [Agents on Lakehouse](../ai-workloads/agents-on-lakehouse.md)
- [Semantic Cache](../ai-workloads/semantic-cache.md)
- [Feature Store](../ai-workloads/feature-store.md)
- [Embedding 流水线](../ai-workloads/embedding-pipelines.md)
- [微调数据准备](../ai-workloads/fine-tuning-data.md)

## ML 基础设施

- [Model Registry](../ml-infra/model-registry.md)
- [Model Serving](../ml-infra/model-serving.md)
- [训练编排](../ml-infra/training-orchestration.md)
- [GPU 调度](../ml-infra/gpu-scheduling.md)

## 多模管线（团队主线）

- [图像管线](../pipelines/image-pipeline.md)
- [视频管线](../pipelines/video-pipeline.md)
- [音频管线](../pipelines/audio-pipeline.md)
- [文档管线](../pipelines/document-pipeline.md)

## 场景

- [RAG on Lake](../scenarios/rag-on-lake.md)
- [多模检索流水线](../scenarios/multimodal-search-pipeline.md)
- [离线训练数据流水线](../scenarios/offline-training-pipeline.md)
- [Feature Serving](../scenarios/feature-serving.md)

## 建议学习路径

走 [一周新人路径](../learning-paths/week-1-newcomer.md) →
[一月 AI 方向](../learning-paths/month-1-ai-track.md) →
之后按 "多模管线 → ML 基础设施 → Agent" 推进。

## 常用速查

- [ANN 参数速查](../cheatsheets/ann-params.md)
- [向量 SQL 语法对照](../cheatsheets/sql-vector.md)
- [Embedding 模型速查](../cheatsheets/embedding-quickpick.md)

## 横向对比

- [向量数据库对比](../compare/vector-db-comparison.md)
- [ANN 索引对比](../compare/ann-index-comparison.md)
- [Embedding 模型横比](../compare/embedding-models.md)
