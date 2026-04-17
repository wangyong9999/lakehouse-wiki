---
title: 多模检索
description: 向量数据库、ANN 索引、Hybrid Search、多模 Embedding
---

# 多模检索

"检索"是 AI 负载接触湖仓的第一界面。本节覆盖向量存储、索引结构、多模 embedding、混合检索与重排。

## 核心概念

- [向量数据库](vector-database.md) —— 把相似度检索作为一等公民的系统
- [Embedding](embedding.md) —— AI 检索的通用货币
- [多模 Embedding](multimodal-embedding.md) —— 把图 / 文 / 音 / 视对齐到同一空间
- [HNSW](hnsw.md) —— 最常见的 ANN 索引
- [IVF-PQ](ivf-pq.md) —— 亿级规模 + 内存预算紧的首选
- [Hybrid Search](hybrid-search.md) —— 稠密 + 稀疏融合
- [Rerank](rerank.md) —— 两阶段检索的第二阶段，决定最终质量

## 主流系统

- [Milvus](milvus.md) —— 分布式，亿级到百亿级
- [LanceDB](lancedb.md) —— 嵌入式 + 湖原生，多模检索的天然选项

## 横向对比

- [ANN 索引对比](../compare/ann-index-comparison.md)
- [向量数据库对比](../compare/vector-db-comparison.md)

## 待补

- DiskANN / ScaNN 独立页
- Qdrant / Weaviate / pgvector 系统页
- 检索评估（Recall@K / MRR / nDCG）
- Embedding 流水线（批生成 + 增量刷新）
