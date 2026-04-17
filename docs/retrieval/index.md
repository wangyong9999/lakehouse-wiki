---
title: 多模检索
description: 向量数据库、ANN 索引、Hybrid Search、多模 Embedding
---

# 多模检索

"检索"是 AI 负载接触湖仓的第一界面。本节覆盖向量存储、索引结构、混合检索与评估。

## 核心概念

- [向量数据库](vector-database.md) —— 把相似度检索作为一等公民的系统
- [HNSW](hnsw.md) —— 最常见的 ANN 索引
- [Hybrid Search](hybrid-search.md) —— 稠密 + 稀疏融合

## 待补

- IVF-PQ / DiskANN / ScaNN
- Embedding 生成与刷新
- 多模 Embedding（CLIP / BLIP / 图文音视频）
- Rerank 模型
- 评估指标（Recall@K、MRR、nDCG）
- 向量索引下沉到湖表（Lance、Iceberg + Puffin）

## 相关

- 上游：[AI 负载](../ai-workloads/index.md) · [一体化架构](../unified/index.md)
