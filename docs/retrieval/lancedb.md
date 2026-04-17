---
title: LanceDB
type: system
tags: [retrieval, vector, lakehouse, embedded]
category: vector-db
repo: https://github.com/lancedb/lancedb
license: Apache-2.0
status: stable
---

# LanceDB

!!! tip "一句话定位"
    **湖上原生的向量数据库**：数据和索引都以 Lance 格式存在对象存储里，嵌入式库形态运行。没有中心服务端、没有独立数据平面——这让它在"多模数据湖"场景下比传统向量库更顺理成章。

## 它解决什么

传统向量库（Milvus、Qdrant）是**独立系统**：数据从湖里 ETL 过去，查询也走它自己的 RPC。痛点：

- **双写**：原始数据在湖、embedding 又在向量库，一致性维护成本高
- **存储分裂**：两套存储预算
- **元数据分裂**：湖里用 Catalog 管，向量库里另外一套 collection / schema

LanceDB 反过来：**直接把湖当底座**。数据以 [Lance Format](../foundations/lance-format.md) 落对象存储，向量索引作为 Lance 文件的一部分；LanceDB 本身是一个嵌入式库，像 DuckDB 一样打开一个 URI 即开用。

## 架构与使用形态

```python
import lancedb
db = lancedb.connect("s3://bucket/warehouse/")     # 直连对象存储
tbl = db.create_table("docs", data=df, mode="overwrite")
tbl.create_index("vector", metric="cosine")
tbl.search([0.1, 0.2, ...]).where("kind = 'image'").limit(10).to_pandas()
```

- 无服务端（OSS 版）；云版 LanceDB Cloud 提供托管
- 支持 Python / JS / Rust / Java SDK
- 索引支持 IVF-PQ / HNSW / 全文 / 稀疏
- 原生 Hybrid Search（向量 + BM25）

## 关键能力

- **零服务端**：任何能读对象存储的进程都能查
- **事务**：Lance 格式自带版本与 manifest
- **增量索引**：新写入的 Fragment 可增量构建索引
- **过滤前提下的检索**：filter-aware，非 post-filter
- **和 Iceberg / Delta 互操作**：开发中，方向是"一张 Iceberg 表能被 LanceDB 以向量表视角读"

## 在"多模数据湖"场景的价值

这是我们团队主线相关最直接的系统。它实现了以下闭环：

- 原始图 / 文 / 音 / 视 入湖（Lance 表 或 Iceberg + Lance 混用）
- 同一张表里直接存 CLIP / BGE 向量
- 查询时一条 API 完成 "向量检索 + 结构化过滤"
- 无独立向量库 → 数据零拷贝、无同步漂移

## 和 Milvus / Qdrant / pgvector 对比

- **Milvus** —— 分布式、大规模、集群；LanceDB 嵌入式、"湖上就地"
- **Qdrant** —— 独立服务，强过滤语义；LanceDB 更偏"湖的原住民"
- **pgvector** —— 关系 DB 插件，适合"向量量小 + 结构化主导"；LanceDB 适合"向量量大 + 多模原生"

横向见 [向量数据库对比](../compare/vector-db-comparison.md)。

## 陷阱与坑

- **大集群场景**：嵌入式形态下的并发写入依赖上层协调
- **索引大小**：亿级向量以 HNSW 会占大量内存；用 IVF-PQ 更现实
- **生态较新**：工具 / Connector 成熟度不如 Iceberg / Parquet 生态老牌

## 延伸阅读

- LanceDB docs: <https://lancedb.github.io/lancedb/>
- *Lance: Fast Columnar Format for ML*（官方博客）
