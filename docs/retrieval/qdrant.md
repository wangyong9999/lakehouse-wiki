---
title: Qdrant
type: system
tags: [retrieval, vector, filter-aware]
category: vector-db
repo: https://github.com/qdrant/qdrant
license: Apache-2.0
status: stable
---

# Qdrant

!!! tip "一句话定位"
    Rust 实现的向量数据库。**最强的元数据过滤语义**——filter-aware 图搜索让"向量相似 + 复杂条件"组合查询又快又准。中等规模 + 强过滤场景首选。

## 它解决什么

大多数向量库的过滤是 **post-filter**：先 ANN 召回 Top-K，再按元数据条件过滤剩下多少是多少。问题：

- 严格条件（如 `WHERE tenant = X AND ts > Y`）可能过滤后只剩几个
- 要么扩大召回 K（慢），要么接受 recall 丢失

Qdrant 把**过滤条件编织进 HNSW 搜索本身**——图节点上带 metadata indicator，搜索时跳过不符合条件的邻居，直接从符合条件的图部分走。

## 架构

```mermaid
flowchart LR
  client[REST / gRPC / SDK] --> api[API Layer]
  api --> storage[Storage Engine<br/>RocksDB]
  api --> index[HNSW Index<br/>per collection]
  api --> payload[Payload Index<br/>(metadata 过滤)]
```

- 单机或集群（sharded collection）
- 本地持久化（RocksDB）或云对象存储（Qdrant Cloud）
- Payload：每个 vector 带任意 JSON 元数据

## 关键能力

- **Filter-aware HNSW** —— 上述的核心卖点
- **Scalar quantization / Binary quantization** —— 压缩向量节省内存 / 磁盘
- **Hybrid Search** —— 稠密 + 稀疏（`sparse vector` 字段）+ text 过滤
- **Multi-tenancy** via payload partitioning
- **Snapshots + 快速恢复**
- **Distributed mode**：一致性哈希分片

## 什么时候选它

- 有**复杂结构化过滤** + 向量检索混合查询
- 中等规模（千万–亿级）
- 想要 Rust 栈 + 单二进制部署
- 多租户 SaaS 场景

## 什么时候不选

- 超大规模（百亿级） → Milvus
- 湖原生 + 多模资产 → LanceDB
- 已有 PG → pgvector

## 陷阱

- **集群模式**相对较新，生产案例不如 Milvus 多
- **payload 索引**要显式创建，忘了创建过滤会回退到全扫
- **Quantization 精度**损失要评估，不是所有场景都能直接开

## 相关

- [向量数据库](vector-database.md)
- [HNSW](hnsw.md)
- [向量数据库对比](../compare/vector-db-comparison.md)

## 延伸阅读

- Qdrant docs: <https://qdrant.tech/documentation/>
- *Filterable HNSW*（Qdrant 博客）
