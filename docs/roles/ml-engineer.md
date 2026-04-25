---
title: ML / AI 工程师
type: reference
status: stable
tags: [role, ml-engineer]
description: 向量检索、Embedding、RAG、Feature Store、Model Serving
hide:
  - toc
last_reviewed: 2026-04-22
---

# ML / AI 工程师 · 优先阅读清单

**你的主战场**：在湖上做检索、训练、RAG、Agent、多模。

!!! note "不必深入（交给其他角色）"
    - **Compaction / Delete Files / 入湖 CDC 运维** → [数据工程师](data-engineer.md)
    - **Catalog 权限 / 多租户 / FinOps / K8s** → [平台工程师](platform-engineer.md)
    - **OLAP 建模 / 物化视图 / 语义层** → [BI 分析师](bi-analyst.md)
    - **引擎内部算法**（Spark Catalyst · Trino Planner · StarRocks 向量化细节）→ 了解定位即可，不需要深入

!!! tip "你是哪种 ML / AI 工程师"
    本页覆盖两类工作，入口不同：

    - **A · LLM / 检索 / Agent 方向**（以下称 **AI 工程**）：做 RAG、向量检索、Agent、多模搜索。主线：向量库 + Embedding + RAG + Agent。
    - **B · Classical ML 方向**（以下称 **数据科学 / ML 建模**）：做 GBDT / 深度学习 / 推荐召排 / 欺诈检测。主线：Feature Store + 离线训练 + 在线服务。

    两类有大量共享基础（湖表 / Feature Store / Model Serving），但**检索 / LLM 相关的内容** A 重 B 轻，**特征工程 / 训练编排 / 评估**则 B 重 A 轻。下面按 A 的主线排，B 方向的重点用"📊 Classical ML 重点"标签。

!!! tip "高频任务速跳"
    - **搭 RAG MVP** → [RAG](../ai-workloads/rag.md) · [60 分钟 RAG on Iceberg tutorial](../tutorials/rag-on-iceberg.md) · [RAG on Lake 场景](../scenarios/rag-on-lake.md)
    - **选向量库** → [向量数据库对比](../compare/vector-db-comparison.md) · [ADR-0003 选 LanceDB](../adr/0003-lancedb-for-multimodal-vectors.md)
    - **检索质量评估** → [检索评估](../retrieval/evaluation.md) · [RAG 评估](../ai-workloads/rag-evaluation.md)
    - **多模流水线** → [多模检索流水线](../scenarios/multimodal-search-pipeline.md) · [文档管线](../pipelines/document-pipeline.md) · [图像管线](../pipelines/image-pipeline.md)
    - **Feature Store / 离线训练** 📊 → [Feature Store](../ml-infra/feature-store.md) · [Feature Store 横比](../compare/feature-store-comparison.md) · [离线训练数据流水线](../scenarios/offline-training-pipeline.md)

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
- [跨模态查询](../retrieval/cross-modal-queries.md)

## AI 负载

- [RAG](../ai-workloads/rag.md)
- [RAG 评估](../ai-workloads/rag-evaluation.md)
- [Prompt 管理](../ai-workloads/prompt-management.md)
- [Agents on Lakehouse](../ai-workloads/agents-on-lakehouse.md)
- [Semantic Cache](../ai-workloads/semantic-cache.md)
- [**Feature Store**](../ml-infra/feature-store.md) 📊 **Classical ML 重点** —— 离线 / 在线一致的特征中台
- [Embedding 流水线](../ml-infra/embedding-pipelines.md)
- [微调数据准备](../ml-infra/fine-tuning-data.md) 📊 Classical ML 也可借鉴（数据质量）

### Classical ML · 数据科学方向补充 📊

如果你做 GBDT / 深度学习 / 推荐 / 风控，下面这条线更关键：

- [**Feature Store**](../ml-infra/feature-store.md) —— PIT Join · Train-Serve Skew · Online-Offline 一致
- [**离线训练数据流水线**](../scenarios/offline-training-pipeline.md) —— 可复现 · 点时间正确的训练集生成
- [**Feature Serving**](../scenarios/feature-serving.md) —— 毫秒级特征在线拉取
- [**推荐系统 · 搜索 · 发现**](../scenarios/recommender-systems.md) —— 四阶段流水线（召回 → 粗排 → 精排 → 重排）
- [**欺诈检测**](../scenarios/fraud-detection.md) —— 四层拦截 · 样本不平衡 · 标签延迟
- [**Classical ML 场景**](../scenarios/classical-ml.md) —— 综述
- [MLOps 生命周期](../ml-infra/mlops-lifecycle.md) —— 数据 → 训练 → 评估 → 上线 → 监控

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

先走 [一周新人路径](../learning-paths/week-1-newcomer.md)（湖 + 检索心智模型），再走 [一月 AI 方向](../learning-paths/month-1-ai-track.md)，之后按 "多模管线 → ML 基础设施 → Agent" 推进。

> **一月 AI 方向** 覆盖：Embedding 与多模 · 向量检索三大索引（HNSW / IVF-PQ / DiskANN） · Hybrid Search + Rerank · RAG 原理与评估 · Feature Store · MLOps 生命周期 · Agent 基础。

## 常用参考

- [ANN 索引对比 §决策速查](../compare/ann-index-comparison.md) · 规模 + 预算 → 索引选择
- [向量数据库 §7 多引擎 SQL](../retrieval/vector-database.md) · pgvector / Milvus / Qdrant 等语法
- [Embedding §3 一分钟速选](../retrieval/embedding.md) · 按场景快速选型
- [HNSW §场景典型配方](../retrieval/hnsw.md) · M / ef 参数

## 横向对比

- [向量数据库对比](../compare/vector-db-comparison.md)
- [ANN 索引对比](../compare/ann-index-comparison.md)
- [Embedding 模型横比](../compare/embedding-models.md)
