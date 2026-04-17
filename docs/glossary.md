---
title: 术语表
description: 字母序的概念兜底索引
---

# 术语表

字母序的概念索引。若你不确定该去哪个目录查，先来这里。

## A – C

- **ACID on Object Store** —— 对象存储上怎么做 ACID，见 [湖表](lakehouse/lake-table.md)
- **ANN（Approximate Nearest Neighbor）** —— 近似最近邻搜索，见 [HNSW](retrieval/hnsw.md) / [IVF-PQ](retrieval/ivf-pq.md) / [DiskANN](retrieval/diskann.md)
- **Catalog** —— 湖仓的表注册中心与治理平面，见 [Catalog 章节](catalog/index.md)
- **CDC（Change Data Capture）** —— 见 [Streaming Upsert / CDC](lakehouse/streaming-upsert-cdc.md)
- **CLIP / SigLIP** —— 多模 Embedding 模型，见 [多模 Embedding](retrieval/multimodal-embedding.md)
- **ClickHouse** —— 明细事实表引擎（待补）
- **Columnar Storage（列式存储）** —— 见 [列式 vs 行式](foundations/columnar-vs-row.md)
- **Compaction** —— 小文件合并，见 [Compaction](lakehouse/compaction.md)
- **CoW / MoR** —— Copy-on-Write / Merge-on-Read，见 [Hudi](lakehouse/hudi.md) / [Delete Files](lakehouse/delete-files.md)
- **Cost Optimization** —— 见 [成本优化](ops/cost-optimization.md)

## D – F

- **Delete Files** —— 行级删除背后的机制，见 [Delete Files](lakehouse/delete-files.md)
- **Delta Lake** —— Databricks 主推的湖表格式，见 [Delta Lake](lakehouse/delta-lake.md)
- **DiskANN** —— 磁盘友好 ANN 图索引，见 [DiskANN](retrieval/diskann.md)
- **DuckDB** —— 嵌入式 OLAP 引擎，见 [DuckDB](query-engines/duckdb.md)
- **Embedding** —— 语义向量化，见 [Embedding](retrieval/embedding.md)
- **Embedding Pipeline** —— 见 [Embedding 流水线](ai-workloads/embedding-pipelines.md)
- **Feature Store（特征存储）** —— ML 特征管理，见 [Feature Store](ai-workloads/feature-store.md)
- **Flink** —— 流优先计算引擎，见 [Apache Flink](query-engines/flink.md)

## G – I

- **Hive Metastore** —— Hadoop 时代 Catalog 事实标准，见 [Hive Metastore](catalog/hive-metastore.md)
- **HNSW** —— 分层图 ANN 索引，见 [HNSW](retrieval/hnsw.md)
- **Hybrid Search** —— 稠密 + 稀疏混合检索，见 [Hybrid Search](retrieval/hybrid-search.md)
- **Iceberg** —— 最"协议化"的湖表格式，见 [Apache Iceberg](lakehouse/iceberg.md)
- **Iceberg REST Catalog** —— 下一代 Catalog 协议，见 [Iceberg REST Catalog](catalog/iceberg-rest-catalog.md)
- **IVF-PQ** —— 倒排桶 + 乘积量化的 ANN 索引，见 [IVF-PQ](retrieval/ivf-pq.md)

## J – M

- **Lake Table（湖表）** —— 见 [湖表](lakehouse/lake-table.md)
- **Lake + Vector** —— 一体化湖仓架构主线，见 [Lake + Vector 融合架构](unified/lake-plus-vector.md)
- **Lance Format** —— 多模原生列式格式，见 [Lance Format](foundations/lance-format.md)
- **LanceDB** —— 湖原生向量库，见 [LanceDB](retrieval/lancedb.md)
- **Manifest** —— 湖表的二层元数据索引，见 [Manifest](lakehouse/manifest.md)
- **Materialized View（物化视图）** —— 见 [物化视图](bi-workloads/materialized-view.md)
- **Milvus** —— 分布式向量数据库，见 [Milvus](retrieval/milvus.md)
- **MRR / nDCG** —— 检索评估指标，见 [检索评估](retrieval/evaluation.md)
- **Multimodal Embedding（多模 Embedding）** —— 见 [多模 Embedding](retrieval/multimodal-embedding.md)
- **Multimodal Data Modeling（多模建模）** —— 见 [多模数据建模](unified/multimodal-data-modeling.md)
- **MVCC** —— 多版本并发控制，见 [MVCC](foundations/mvcc.md)

## N – R

- **Nessie** —— Git-like 事务 Catalog，见 [Nessie](catalog/nessie.md)
- **Object Storage（对象存储）** —— 见 [对象存储](foundations/object-storage.md)
- **Observability（可观测性）** —— 见 [可观测性](ops/observability.md)
- **OLAP Modeling** —— 见 [OLAP 建模](bi-workloads/olap-modeling.md)
- **ORC** —— 列式文件格式，见 [ORC](foundations/orc.md)
- **Paimon** —— 流式原生湖表格式，见 [Apache Paimon](lakehouse/paimon.md)
- **Parquet** —— 最主流的列式存储格式，见 [Parquet](foundations/parquet.md)
- **Performance Tuning** —— 见 [性能调优](ops/performance-tuning.md)
- **pgvector** —— PostgreSQL 向量扩展，见 [pgvector](retrieval/pgvector.md)
- **Polaris** —— Snowflake 开源 Catalog，见 [Apache Polaris](catalog/polaris.md)
- **Puffin** —— Iceberg 辅助索引文件格式，见 [Puffin](lakehouse/puffin.md)
- **Qdrant** —— Rust 向量数据库，见 [Qdrant](retrieval/qdrant.md)
- **Query Acceleration** —— 见 [查询加速](bi-workloads/query-acceleration.md)
- **RAG（Retrieval-Augmented Generation）** —— 见 [RAG](ai-workloads/rag.md)
- **Recall@K** —— 召回评估指标，见 [检索评估](retrieval/evaluation.md)
- **Rerank（重排）** —— 两阶段检索的第二阶段，见 [Rerank](retrieval/rerank.md)

## S – Z

- **Schema Evolution** —— 不重写历史改表结构，见 [Schema Evolution](lakehouse/schema-evolution.md)
- **Semantic Cache** —— LLM 语义缓存，见 [Semantic Cache](ai-workloads/semantic-cache.md)
- **Snapshot** —— 湖表的时间切片，见 [Snapshot](lakehouse/snapshot.md)
- **Spark** —— 湖仓的重型瑞士军刀，见 [Apache Spark](query-engines/spark.md)
- **StarRocks** —— MPP OLAP 引擎，见 [StarRocks](query-engines/starrocks.md)
- **Streaming Upsert / CDC** —— 见 [Streaming Upsert / CDC](lakehouse/streaming-upsert-cdc.md)
- **Time Travel（时间旅行）** —— 见 [Time Travel](lakehouse/time-travel.md)
- **Trino** —— 交互式分析引擎，见 [Trino](query-engines/trino.md)
- **Unity Catalog** —— 多模资产统一目录，见 [Unity Catalog](catalog/unity-catalog.md)
- **Vectorized Execution（向量化执行）** —— 见 [向量化执行](foundations/vectorized-execution.md)
- **Vector Database（向量数据库）** —— 见 [向量数据库](retrieval/vector-database.md)
- **Z-order / Liquid Clustering** —— 见 [查询加速](bi-workloads/query-acceleration.md)

---

!!! note "维护约定"
    本页手工维护。新增概念页时顺手加一行。未来条目数 > 100 时改脚本自动生成。
