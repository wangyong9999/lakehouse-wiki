---
title: 多模检索
description: 向量数据库 · ANN 索引 · 检索流水线 · 多模 Embedding · 产品实现
last_reviewed: 2026-04-20
---

# 多模检索

本章聚焦 **"向量检索（ANN）+ 稀疏检索 + 多模 embedding"** 这条数据检索主线——**把 embedding 变成可查询的一等资产**，让 AI 应用（RAG / 推荐 / 搜索 / 多模）能够高效召回相关内容。

!!! info "和其他章节的边界"
    检索领域在湖仓手册里跨多个章节 · 本章职责明确：

    | 章节 | 职责 | 和 retrieval 的关系 |
    |---|---|---|
    | **本章 retrieval/** | **检索本身**——embedding 如何存储 + ANN 索引如何建 + 相似度查询如何执行 | 核心 |
    | [query-engines/](../query-engines/index.md) | SQL 引擎做**数据处理** · 包含"向量化执行"（SIMD 列批）和附属的"向量检索函数"（ClickHouse/StarRocks/DuckDB 2024+ 加的） | 附属能力 · retrieval 更深做相似度查询主路径 |
    | [lakehouse/multi-modal-lake](../lakehouse/multi-modal-lake.md) | **湖表如何承载多模数据** · 向量作为湖表的一个列类型的存储层 | 补本章 "检索" 侧 · 关注"存储侧承载" |
    | [pipelines/image-pipeline](../pipelines/image-pipeline.md) 等 4 页 | **生成 embedding** 的管线 · 图/视/音/文档解析+向量化 | 生产侧 · retrieval 消费这些 embedding |
    | [ai-workloads/rag](../ai-workloads/rag.md) | **用** 检索做 RAG 应用 | 应用层 · retrieval 是基础设施 |

    **一句话**：pipelines 生产 embedding → lakehouse / retrieval 存储 → retrieval 查询 → ai-workloads 消费。

## 学习路径 · 4 步

!!! tip "从"第一次做向量检索"到"能做生产选型"的 4 步路径"
    1. **[向量数据库](vector-database.md)** —— 先理解"把相似度检索作为一等公民的系统"是什么
    2. **[Embedding](embedding.md)** + **[多模 Embedding](multimodal-embedding.md)** —— AI 检索的"通用货币" · 选对模型决定上限
    3. **ANN 索引三家** —— [HNSW](hnsw.md)（最常见）/ [IVF-PQ](ivf-pq.md)（规模/内存紧）/ [DiskANN](diskann.md)（十亿级 + SSD）+ [Quantization](quantization.md)（压缩策略）
    4. **生产主路径** —— [Hybrid Search](hybrid-search.md)（稠+稀融合）→ [Rerank](rerank.md)（二阶段质量）→ [检索评估](evaluation.md)（监控指标）· 进阶看 [Filter-aware ANN](filter-aware-search.md) / [Sparse Retrieval](sparse-retrieval.md)

## 核心概念

### 基础
- [向量数据库](vector-database.md) —— 把相似度检索作为一等公民的系统
- [Embedding](embedding.md) —— AI 检索的通用货币 · 2026 模型矩阵 + Matryoshka + 选型
- [多模 Embedding](multimodal-embedding.md) —— 把图 / 文 / 音 / 视对齐到同一空间

### ANN 索引
- [HNSW](hnsw.md) —— 最常见的图索引
- [IVF-PQ](ivf-pq.md) —— 倒排 + 量化 · 亿级 + 内存预算紧
- [DiskANN](diskann.md) —— 图索引落盘 · 十亿级 + SSD 友好
- [Quantization](quantization.md) —— PQ / SQ / BQ / Matryoshka · 压缩策略横切

### 检索流水线
- [Hybrid Search](hybrid-search.md) —— 稠密 + 稀疏融合（RRF / convex combination）
- [Sparse Retrieval](sparse-retrieval.md) —— BM25 / SPLADE / BM42 独立
- [Filter-aware ANN](filter-aware-search.md) —— 结构化谓词 + 向量 组合查询
- [Rerank](rerank.md) —— 两阶段的第二阶段 · 决定最终质量
- [检索评估](evaluation.md) —— Recall@K / MRR / nDCG / BEIR / MTEB

## 产品实现

- [Milvus](milvus.md) —— 分布式 · 亿级到百亿级
- [LanceDB](lancedb.md) —— 嵌入式 + 湖原生 · 多模天然选项
- [Qdrant](qdrant.md) —— Rust 实现 · filter-aware 图搜索
- [Weaviate](weaviate.md) —— 自带向量化 + Reranker module
- [pgvector](pgvector.md) —— PostgreSQL 扩展 · 结构化主导场景最小路径

## 横向对比

- [ANN 索引对比](../compare/ann-index-comparison.md)
- [向量数据库对比](../compare/vector-db-comparison.md)
- [Embedding 模型横比](../compare/embedding-models.md)
- [Rerank 模型横比](../compare/rerank-models.md)
- [稀疏检索对比](../compare/sparse-retrieval.md)

## 团队决策

- [ADR-0003 多模向量存储选 LanceDB](../adr/0003-lancedb-for-multimodal-vectors.md)
