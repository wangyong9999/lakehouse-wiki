---
title: 术语表
description: 字母序的概念兜底索引
---

# 术语表

字母序的概念索引。不确定该去哪个目录查，先来这里；具体问题去 [FAQ](faq.md)；角色路径去 [按角色入门](roles/index.md)。

## A – C

- **ACID on Object Store** —— 见 [湖表](lakehouse/lake-table.md)
- **Agents on Lakehouse** —— 见 [Agents](ai-workloads/agents-on-lakehouse.md)
- **ANN（Approximate Nearest Neighbor）** —— 见 [HNSW](retrieval/hnsw.md) / [IVF-PQ](retrieval/ivf-pq.md) / [DiskANN](retrieval/diskann.md)
- **ASR（Automatic Speech Recognition）** —— 见 [音频管线](pipelines/audio-pipeline.md)
- **Benchmark** —— 见 [Benchmark 参考](frontier/benchmarks.md)
- **Branching & Tagging** —— Iceberg 原生分支标签，见 [Branching & Tagging](lakehouse/branching-tagging.md)
- **Bulk Loading** —— 见 [Bulk Loading](pipelines/bulk-loading.md)
- **Case Studies（案例拆解）** —— 见 [案例拆解](unified/case-studies.md)
- **Catalog** —— 见 [Catalog 章节](catalog/index.md)
- **CDC（Change Data Capture）** —— 见 [Streaming Upsert / CDC](lakehouse/streaming-upsert-cdc.md)
- **Cheatsheet** —— 见 [速查单](cheatsheets/index.md)
- **CLIP / SigLIP** —— 多模 Embedding 模型，见 [多模 Embedding](retrieval/multimodal-embedding.md)
- **ClickHouse** —— 见 [ClickHouse](query-engines/clickhouse.md)
- **Columnar Storage** —— 见 [列式 vs 行式](foundations/columnar-vs-row.md)
- **Compaction** —— 见 [Compaction](lakehouse/compaction.md)
- **Compute Pushdown** —— 见 [Compute Pushdown](unified/compute-pushdown.md)
- **Compute-Storage Separation（存算分离）** —— 见 [存算分离](foundations/compute-storage-separation.md)
- **Consistency（一致性模型）** —— 见 [一致性模型](foundations/consistency-models.md)
- **CoW / MoR** —— 见 [Hudi](lakehouse/hudi.md) / [Delete Files](lakehouse/delete-files.md)
- **Cost Optimization** —— 见 [成本优化](ops/cost-optimization.md)
- **Cross-modal Query** —— 见 [跨模态查询](unified/cross-modal-queries.md)

## D – F

- **Data Governance** —— 见 [数据治理](ops/data-governance.md)
- **Debezium** —— 见 [Kafka 到湖](pipelines/kafka-ingestion.md)
- **Delete Files** —— 见 [Delete Files](lakehouse/delete-files.md)
- **Delta Lake** —— 见 [Delta Lake](lakehouse/delta-lake.md)
- **DiskANN** —— 见 [DiskANN](retrieval/diskann.md) / [论文笔记](frontier/diskann-paper.md)
- **Document Pipeline** —— 见 [文档管线](pipelines/document-pipeline.md)
- **Doris** —— 见 [Apache Doris](query-engines/doris.md)
- **DuckDB** —— 见 [DuckDB](query-engines/duckdb.md)
- **Embedding** —— 见 [Embedding](retrieval/embedding.md)
- **Embedding Pipeline** —— 见 [Embedding 流水线](ai-workloads/embedding-pipelines.md)
- **Feature Store** —— 见 [Feature Store](ai-workloads/feature-store.md)
- **Feature Serving** —— 见 [Feature Serving](scenarios/feature-serving.md)
- **Fine-tuning Data** —— 见 [微调数据准备](ai-workloads/fine-tuning-data.md)
- **Flink** —— 见 [Apache Flink](query-engines/flink.md)

## G – I

- **GPU 调度** —— 见 [GPU 调度](ml-infra/gpu-scheduling.md)
- **Gravitino** —— 见 [Apache Gravitino](catalog/gravitino.md)
- **Hive Metastore** —— 见 [Hive Metastore](catalog/hive-metastore.md)
- **HNSW** —— 见 [HNSW](retrieval/hnsw.md)
- **Hybrid Search** —— 见 [Hybrid Search](retrieval/hybrid-search.md)
- **Iceberg** —— 见 [Apache Iceberg](lakehouse/iceberg.md) / [速查](cheatsheets/iceberg.md)
- **Iceberg REST Catalog** —— 见 [Iceberg REST Catalog](catalog/iceberg-rest-catalog.md)
- **Image Pipeline** —— 见 [图像管线](pipelines/image-pipeline.md)
- **IVF-PQ** —— 见 [IVF-PQ](retrieval/ivf-pq.md)

## J – M

- **Kafka → 湖** —— 见 [Kafka 到湖](pipelines/kafka-ingestion.md)
- **Lake Table（湖表）** —— 见 [湖表](lakehouse/lake-table.md)
- **Lake + Vector** —— 见 [Lake + Vector 融合架构](unified/lake-plus-vector.md)
- **Lance Format** —— 见 [Lance Format](foundations/lance-format.md)
- **LanceDB** —— 见 [LanceDB](retrieval/lancedb.md)
- **LLM Serving** —— 见 [Model Serving](ml-infra/model-serving.md)
- **Manifest** —— 见 [Manifest](lakehouse/manifest.md)
- **Materialized View** —— 见 [物化视图](bi-workloads/materialized-view.md)
- **Migration Playbook** —— 见 [迁移手册](ops/migration-playbook.md)
- **Milvus** —— 见 [Milvus](retrieval/milvus.md)
- **Model Registry** —— 见 [Model Registry](ml-infra/model-registry.md)
- **Model Serving** —— 见 [Model Serving](ml-infra/model-serving.md)
- **MRR / nDCG** —— 见 [检索评估](retrieval/evaluation.md)
- **Multimodal Data Modeling** —— 见 [多模数据建模](unified/multimodal-data-modeling.md)
- **Multimodal Embedding** —— 见 [多模 Embedding](retrieval/multimodal-embedding.md)
- **MVCC** —— 见 [MVCC](foundations/mvcc.md)

## N – R

- **Nessie** —— 见 [Nessie](catalog/nessie.md)
- **Object Storage** —— 见 [对象存储](foundations/object-storage.md)
- **Observability** —— 见 [可观测性](ops/observability.md)
- **Offline Training Pipeline** —— 见 [离线训练数据流水线](scenarios/offline-training-pipeline.md)
- **OLAP Modeling** —— 见 [OLAP 建模](bi-workloads/olap-modeling.md)
- **OLTP vs OLAP** —— 见 [OLTP vs OLAP](foundations/oltp-vs-olap.md)
- **ORC** —— 见 [ORC](foundations/orc.md)
- **Orchestration（编排）** —— 见 [编排系统概览](pipelines/orchestration.md)
- **Paimon** —— 见 [Apache Paimon](lakehouse/paimon.md)
- **Parquet** —— 见 [Parquet](foundations/parquet.md)
- **Partition Evolution** —— 见 [Partition Evolution](lakehouse/partition-evolution.md)
- **Performance Tuning** —— 见 [性能调优](ops/performance-tuning.md)
- **pgvector** —— 见 [pgvector](retrieval/pgvector.md)
- **Polaris** —— 见 [Apache Polaris](catalog/polaris.md)
- **Predicate Pushdown（谓词下推）** —— 见 [谓词下推](foundations/predicate-pushdown.md)
- **Prompt Management** —— 见 [Prompt 管理](ai-workloads/prompt-management.md)
- **Puffin** —— 见 [Puffin](lakehouse/puffin.md)
- **Qdrant** —— 见 [Qdrant](retrieval/qdrant.md)
- **Query Acceleration** —— 见 [查询加速](bi-workloads/query-acceleration.md)
- **RAG** —— 见 [RAG](ai-workloads/rag.md)
- **RAG Evaluation** —— 见 [RAG 评估](ai-workloads/rag-evaluation.md)
- **Recall@K** —— 见 [检索评估](retrieval/evaluation.md)
- **Rerank** —— 见 [Rerank](retrieval/rerank.md)

## S – Z

- **Schema Evolution** —— 见 [Schema Evolution](lakehouse/schema-evolution.md)
- **Security** —— 见 [安全与权限](ops/security-permissions.md)
- **Semantic Cache** —— 见 [Semantic Cache](ai-workloads/semantic-cache.md)
- **Snapshot** —— 见 [Snapshot](lakehouse/snapshot.md)
- **Spark** —— 见 [Apache Spark](query-engines/spark.md)
- **StarRocks** —— 见 [StarRocks](query-engines/starrocks.md)
- **Streaming Upsert / CDC** —— 见 [Streaming Upsert / CDC](lakehouse/streaming-upsert-cdc.md)
- **Time Travel** —— 见 [Time Travel](lakehouse/time-travel.md)
- **Training Orchestration** —— 见 [训练编排](ml-infra/training-orchestration.md)
- **Trino** —— 见 [Trino](query-engines/trino.md)
- **Troubleshooting** —— 见 [故障排查手册](ops/troubleshooting.md)
- **Unity Catalog** —— 见 [Unity Catalog](catalog/unity-catalog.md)
- **Vectorized Execution** —— 见 [向量化执行](foundations/vectorized-execution.md)
- **Vector Database** —— 见 [向量数据库](retrieval/vector-database.md)
- **Video Pipeline** —— 见 [视频管线](pipelines/video-pipeline.md)
- **vLLM** —— 见 [Model Serving](ml-infra/model-serving.md)
- **Weaviate** —— 见 [Weaviate](retrieval/weaviate.md)
- **Whisper** —— 见 [音频管线](pipelines/audio-pipeline.md)
- **Z-order / Liquid Clustering** —— 见 [查询加速](bi-workloads/query-acceleration.md)

---

!!! note "维护约定"
    本页手工维护。新增概念页时顺手加一行。未来条目数 > 200 时改脚本自动生成。
