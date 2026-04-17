---
title: 向量数据库 (Vector Database)
type: concept
tags: [retrieval, vector, ann]
aliases: [Vector DB, 向量库]
related: [hnsw, hybrid-search]
systems: [milvus, lancedb, qdrant, weaviate, pgvector]
status: stable
---

# 向量数据库 (Vector Database)

!!! tip "一句话理解"
    把**向量相似度检索**作为一等公民的存储系统；核心围绕"ANN 索引 + 元数据过滤 + 批量 upsert"三件事。

## 它是什么

向量数据库是**为高维稠密浮点数组的近邻检索而优化的数据系统**。相对于传统 DB，它有三件"非经典"的事：

1. **ANN 索引** —— 在亿级向量下，精确最近邻在毫秒级无法做到，必须近似；核心是 [HNSW](hnsw.md) / IVF-PQ / DiskANN / ScaNN 等结构
2. **Top-K 查询语义** —— 查询不是"等值 / 范围"，而是"给我离 q 最近的 K 个"，并常需配合元数据过滤（`WHERE category = 'image' AND ts > ...`）
3. **批写 + 索引刷新** —— Embedding 通常离线批量产出，系统要能吞吐批写并异步重建索引，而不是行级事务

## 关键设计维度

| 维度 | 选择谱系 |
| --- | --- |
| 索引结构 | [HNSW](hnsw.md)（图）/ IVF-PQ（倒排量化）/ DiskANN（磁盘友好图）/ ScaNN（Google） |
| 存储介质 | 内存 / 本地 SSD / 对象存储 |
| 过滤语义 | pre-filter / post-filter / filter-aware 图搜索 |
| 部署形态 | 独立服务 / 嵌入式库 / DB 扩展（pgvector） |
| 一致性模型 | 最终一致为主；少数提供读写一致可配 |
| 多租户 | collection / partition / namespace 三种粒度 |

## 在典型 OSS 里的形态

- **Milvus** —— 分布式，segment + 异步索引构建，Pulsar/Kafka 作为 WAL；集群形态最完整
- **LanceDB** —— 嵌入式 + 对象存储原生，Lance 列格式自带向量索引；"湖上向量库"路线
- **Qdrant** —— Rust 实现，单机/集群兼顾，强过滤语义
- **Weaviate** —— 自带 schema、内置向量化器与 reranker module
- **pgvector** —— PostgreSQL 扩展；和关系数据共存的最小路径，成本最低

## 和湖仓的关系

向量数据常常源自湖上的原始数据（文本、图片、日志），又被 AI 负载反复消费。当下两条融合路径：

1. **向量索引下沉到湖表** —— Lance format 自带、Iceberg 通过 Puffin 索引文件
2. **Catalog 统一** —— Unity / Polaris / Gravitino 同时管关系表和向量表

这是 [一体化架构](../unified/index.md) 里"Lake + Vector"的核心命题，也是我们团队的主线。

## 什么时候不需要专门的向量库

- 向量规模 < 1M 且 QPS 低：pgvector / Faiss 直用即可
- 严格"向量 + 大量结构化过滤"的场景：考虑 PG + pgvector 以避开二次查询
- 离线批任务为主：直接 Faiss + Parquet 落盘最省事

## 相关概念

- [HNSW](hnsw.md) —— 最常见的 ANN 索引
- [Hybrid Search](hybrid-search.md) —— 向量 + 关键字混合
- [RAG](../ai-workloads/rag.md) —— 向量库的头号下游消费者

## 延伸阅读

- *ANN-Benchmarks*: <https://ann-benchmarks.com/>
- *Milvus: A Purpose-Built Vector Data Management System* (SIGMOD 2021)
- *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node* (NeurIPS 2019)
