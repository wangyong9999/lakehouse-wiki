---
title: 按技术栈索引 · Technology Index
description: 你团队的技术栈 → 对应相关的手册内容
hide:
  - toc
---

# 按技术栈索引

**"我们用 AWS + Iceberg + Trino + Feast，我要看哪些页？"** 这是手册的第四轴导航（按章节 / 按角色 / 按 tag / **按技术栈**）。

---

## AWS 生态

- **底座**：[S3 + Iceberg](lakehouse/iceberg.md) · [Glue Catalog](catalog/hive-metastore.md)
- **计算**：[EMR / Athena / Redshift Spectrum](query-engines/trino.md)（都可以读 Iceberg）
- **ML**：SageMaker + [Feast](compare/feature-store-comparison.md) + MLflow
- **流处理**：Kinesis + [Flink on EMR](query-engines/flink.md)
- **向量**：[pgvector on RDS](retrieval/pgvector.md) 或 OpenSearch
- **Catalog**：Glue（绑定）或自建 [Iceberg REST Catalog](catalog/iceberg-rest-catalog.md)
- **合规**：[AWS Lake Formation](ops/compliance.md)

---

## GCP 生态

- **底座**：GCS + BigQuery（BigLake + Iceberg）
- **计算**：Dataflow + BigQuery + Dataproc（Spark/Flink）
- **ML**：[Vertex AI Feature Store](compare/feature-store-comparison.md) + Vertex AI Model Registry
- **向量**：Vertex AI Vector Search
- **Catalog**：Dataplex / 自建
- **合规**：按 [合规](ops/compliance.md) 章节

---

## Azure 生态

- **底座**：ADLS + Databricks + Unity Catalog
- **计算**：Databricks Runtime + Synapse
- **ML**：Azure ML + [Feast](compare/feature-store-comparison.md)
- **向量**：Azure AI Search (vector) · Cosmos DB
- **Catalog**：[Unity Catalog](catalog/unity-catalog.md)

---

## Databricks 全栈

- **底座**：[Delta Lake](lakehouse/delta-lake.md) · [Unity Catalog](catalog/unity-catalog.md)
- **计算**：Databricks Runtime (Spark + Photon) · [SQL Warehouse](query-engines/spark.md)
- **ML**：[MLflow](ai-workloads/mlops-lifecycle.md) · [Databricks Feature Store](compare/feature-store-comparison.md) · Vector Search
- **协作**：Notebook / Workflows / DLT
- **优势**：一站式；**劣势**：锁定
- 对比：[湖仓演进史](foundations/data-systems-evolution.md)

---

## Snowflake 全栈

- **底座**：原生 + [Snowflake Open Catalog (Polaris)](catalog/polaris.md) · [Iceberg Tables](lakehouse/iceberg.md)
- **计算**：Snowpark + SQL
- **ML**：Snowpark ML · [Cortex](ai-workloads/rag.md) · Snowpipe
- **Streaming**：Snowpipe Streaming
- **对比**：[TCO 模型](ops/tco-model.md)

---

## 开源自建 Lakehouse

- **底座**：[Iceberg](lakehouse/iceberg.md) + [Paimon](lakehouse/paimon.md)
- **Catalog**：[Iceberg REST Catalog](catalog/iceberg-rest-catalog.md) / [Nessie](catalog/nessie.md) / [Polaris](catalog/polaris.md)
- **计算**：[Trino](query-engines/trino.md) + [Spark](query-engines/spark.md) + [Flink](query-engines/flink.md) + [DuckDB](query-engines/duckdb.md)
- **加速**：[StarRocks](query-engines/starrocks.md) / [ClickHouse](query-engines/clickhouse.md) / [Doris](query-engines/doris.md) → [对比](compare/olap-accelerator-comparison.md)
- **向量**：[Milvus](retrieval/milvus.md) / [LanceDB](retrieval/lancedb.md) / [Qdrant](retrieval/qdrant.md)
- **调度**：[Airflow / Dagster / Prefect](compare/orchestrators.md)
- **ML**：MLflow / Kubeflow / Ray + [Feast](compare/feature-store-comparison.md)

---

## 实时 / 流处理栈

- **核心**：[Flink](query-engines/flink.md) + [Paimon](lakehouse/paimon.md)
- **入口**：Kafka / Pulsar + [Flink CDC](scenarios/streaming-ingestion.md)
- **加速**：StarRocks 增量物化视图
- **下游**：BI / 实时特征 Feature Store
- **对比**：[流处理引擎横比](compare/streaming-engines.md)
- **场景**：[Real-time Lakehouse](scenarios/real-time-lakehouse.md) · [欺诈检测](scenarios/fraud-detection.md)

---

## RAG 技术栈（企业 AI）

- **语料存储**：[Iceberg raw_docs + doc_chunks](scenarios/rag-on-lake.md)
- **向量**：[LanceDB](retrieval/lancedb.md) · [Milvus](retrieval/milvus.md) · [pgvector](retrieval/pgvector.md)
- **Embedding**：BGE / E5 / Cohere（[对比](compare/embedding-models.md)）
- **Rerank**：bge-reranker / Cohere Rerank（[对比](compare/rerank-models.md)）
- **LLM**：[vLLM / SGLang / TGI](frontier/llm-inference-opt.md)
- **前沿**：[Contextual Retrieval / CRAG / Self-RAG](frontier/rag-advances-2025.md)
- **管线**：LangChain / LlamaIndex / Haystack
- **评估**：RAGAS / TruLens
- **协议**：[MCP](ai-workloads/mcp.md)

---

## 推荐系统栈

- **明细**：[Paimon 行为表](lakehouse/paimon.md)
- **特征**：[Feature Store (Feast / Tecton / Hopsworks)](compare/feature-store-comparison.md)
- **召回**：LanceDB / Milvus（向量）+ 多路召回
- **精排**：XGBoost / DNN ([Classical ML](scenarios/classical-ml.md))
- **在线**：Redis / Aerospike + 模型 serving (Triton / vLLM)
- **近实时**：[Flink](query-engines/flink.md) 实时特征
- **场景**：[推荐系统场景](scenarios/recommender-systems.md)

---

## BI 技术栈

- **数据**：[Iceberg + Spark ETL](scenarios/bi-on-lake.md)
- **建模**：dbt（Medallion: ODS/DWD/DWS/ADS）
- **交互查询**：[Trino](query-engines/trino.md) / [DuckDB](query-engines/duckdb.md)
- **加速**：[StarRocks / ClickHouse](compare/olap-accelerator-comparison.md)
- **BI 工具**：Superset / Tableau / Metabase
- **语义层**：dbt Semantic Layer / Cube

---

## MLOps 栈

- **训练**：Spark MLlib / Ray Train / PyTorch
- **跟踪**：MLflow / Weights & Biases
- **Registry**：MLflow / [Unity Catalog](catalog/unity-catalog.md)
- **Serving**：[vLLM / TGI](frontier/llm-inference-opt.md) / Triton / Ray Serve
- **监控**：Prometheus + 自建 drift
- **闭环**：[MLOps Lifecycle](ai-workloads/mlops-lifecycle.md)

---

## Agent 技术栈（2025+）

- **LLM**：Claude / GPT / 开源（[推理优化](frontier/llm-inference-opt.md)）
- **协议**：[MCP](ai-workloads/mcp.md)
- **框架**：LangGraph / AutoGen / CrewAI
- **工具**：Tool-based（SQL / API / 代码执行）
- **评估**：SWE-bench / τ-bench / GAIA
- **场景**：[Agentic Workflows](scenarios/agentic-workflows.md)

---

## Feature Store 栈

- **开源**：[Feast](compare/feature-store-comparison.md) + Redis / DynamoDB
- **商业**：Tecton / Hopsworks
- **云厂商**：SageMaker FS / Vertex AI FS / Databricks FS
- **自建**：Iceberg + Redis + dbt
- **概念**：[Feature Store](ai-workloads/feature-store.md)

---

## 安全 / 合规栈

- **治理 Catalog**：[Unity](catalog/unity-catalog.md) / [DataHub / OpenMetadata](foundations/modern-data-stack.md)
- **血缘**：DataHub / OpenLineage
- **质量**：Great Expectations / Soda / dbt tests
- **合规**：[GDPR / HIPAA / PDPA / 个保法](ops/compliance.md)
- **AI 治理**：[EU AI Act / Guardrails / Red Teaming](frontier/ai-governance.md)

---

## 国产化技术栈

- **底座**：[Paimon](lakehouse/paimon.md)（阿里）· [Iceberg](lakehouse/iceberg.md)
- **OLAP**：[StarRocks](query-engines/starrocks.md) / [Doris](query-engines/doris.md) / [ByteHouse (ClickHouse)](query-engines/clickhouse.md)
- **图**：Nebula Graph / TigerGraph
- **调度**：[DolphinScheduler](compare/orchestrators.md)
- **向量**：[Milvus](retrieval/milvus.md)（Zilliz）· DingoDB
- **云**：阿里云 MaxCompute · 腾讯云 COS · 华为 DLI

---

## 相关

- [按角色入门](roles/index.md) —— 另一维度索引
- [业务场景全景](scenarios/business-scenarios.md) —— 业务→技术映射
- [术语表](glossary.md) —— 字母序兜底
