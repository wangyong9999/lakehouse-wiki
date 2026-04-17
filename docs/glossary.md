---
title: 术语表
description: 字母序的概念兜底索引
---

# 术语表

字母序的概念索引。若你不确定该去哪个目录查，先来这里。

## A – C

- **ACID on Object Store** —— 对象存储上怎么做 ACID，见 [湖表](lakehouse/lake-table.md)
- **ANN（Approximate Nearest Neighbor）** —— 近似最近邻搜索，见 [HNSW](retrieval/hnsw.md) / [IVF-PQ](retrieval/ivf-pq.md)
- **Catalog** —— 湖仓的表注册中心与治理平面，见 [Catalog 章节](catalog/index.md)
- **CDC（Change Data Capture）** —— 业务库变更同步到湖，见 [Paimon](lakehouse/paimon.md)
- **CLIP / SigLIP** —— 多模 Embedding 模型，见 [多模 Embedding](retrieval/multimodal-embedding.md)
- **Columnar Storage（列式存储）** —— 见 [列式 vs 行式](foundations/columnar-vs-row.md)
- **Compaction** —— 小文件合并，湖仓运维必修
- **CoW / MoR** —— Copy-on-Write / Merge-on-Read，见 [Hudi](lakehouse/hudi.md)

## D – F

- **Delta Lake** —— Databricks 主推的湖表格式，见 [Delta Lake](lakehouse/delta-lake.md)
- **DiskANN** —— 磁盘友好的图索引，见 [ANN 索引对比](compare/ann-index-comparison.md)
- **DuckDB** —— 嵌入式 OLAP 引擎，见 [DuckDB](query-engines/duckdb.md)
- **Embedding** —— 语义向量化，见 [Embedding](retrieval/embedding.md)
- **Feature Store（特征存储）** —— ML 特征管理，见 [Feature Store](ai-workloads/feature-store.md)
- **Flink** —— 流计算引擎（待补系统页）

## G – I

- **Hive Metastore** —— Hadoop 时代的事实标准 Catalog，见 [Hive Metastore](catalog/hive-metastore.md)
- **HNSW** —— 分层图 ANN 索引，见 [HNSW](retrieval/hnsw.md)
- **Hybrid Search** —— 稠密 + 稀疏混合检索，见 [Hybrid Search](retrieval/hybrid-search.md)
- **Iceberg** —— 最"协议化"的湖表格式，见 [Apache Iceberg](lakehouse/iceberg.md)
- **Iceberg REST Catalog** —— 下一代 Catalog 协议，见 [Iceberg REST Catalog](catalog/iceberg-rest-catalog.md)
- **IVF-PQ** —— 倒排桶 + 乘积量化的 ANN 索引，见 [IVF-PQ](retrieval/ivf-pq.md)

## J – M

- **Lake Table（湖表）** —— 见 [湖表](lakehouse/lake-table.md)
- **Lake + Vector** —— 一体化湖仓的架构主线，见 [Lake + Vector 融合架构](unified/lake-plus-vector.md)
- **Lance Format** —— 多模原生列式格式，见 [Lance Format](foundations/lance-format.md)
- **LanceDB** —— 湖原生向量库，见 [LanceDB](retrieval/lancedb.md)
- **Manifest** —— 湖表的二层元数据索引，见 [Manifest](lakehouse/manifest.md)
- **Materialized View** —— 物化视图（待补）
- **Milvus** —— 分布式向量数据库，见 [Milvus](retrieval/milvus.md)
- **Multimodal Embedding（多模 Embedding）** —— 见 [多模 Embedding](retrieval/multimodal-embedding.md)
- **MVCC** —— 多版本并发控制（待补）

## N – R

- **Nessie** —— Git-like 事务 Catalog，见 [Nessie](catalog/nessie.md)
- **Object Storage（对象存储）** —— 见 [对象存储](foundations/object-storage.md)
- **ORC** —— 列式文件格式（待补）
- **Paimon** —— 流式原生湖表格式，见 [Apache Paimon](lakehouse/paimon.md)
- **Parquet** —— 最主流的列式存储格式，见 [Parquet](foundations/parquet.md)
- **Puffin** —— Iceberg 辅助索引文件格式，见 [Puffin](lakehouse/puffin.md)
- **RAG（Retrieval-Augmented Generation）** —— 见 [RAG](ai-workloads/rag.md)
- **Rerank（重排）** —— 两阶段检索的第二阶段，见 [Rerank](retrieval/rerank.md)

## S – Z

- **Schema Evolution** —— 不重写历史改表结构，见 [Schema Evolution](lakehouse/schema-evolution.md)
- **Snapshot** —— 湖表的时间切片，见 [Snapshot](lakehouse/snapshot.md)
- **Spark** —— 湖仓的重型瑞士军刀，见 [Apache Spark](query-engines/spark.md)
- **Time Travel（时间旅行）** —— 见 [Time Travel](lakehouse/time-travel.md)
- **Trino** —— 交互式分析引擎，见 [Trino](query-engines/trino.md)
- **Unity Catalog** —— 多模资产统一目录，见 [Unity Catalog](catalog/unity-catalog.md)
- **Vector Database（向量数据库）** —— 见 [向量数据库](retrieval/vector-database.md)

---

!!! note "维护约定"
    本页手工维护。新增概念页时顺手加一行。未来条目数 > 100 时改脚本自动生成。
