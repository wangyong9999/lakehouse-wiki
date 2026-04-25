---
title: 横向对比
type: reference
status: stable
tags: [index, compare]
description: 同层对象之间的硬比，每一页都直接回答一个选型问题
last_reviewed: 2026-04-18
---

# 横向对比

新人最常用的入口之一。**每页解决一个"我到底该选 A 还是 B"的问题**。

## 底座层

- [DB 存储引擎 vs 湖表](db-engine-vs-lake-table.md) —— 底层差异与何时选谁
- [Iceberg vs Paimon vs Hudi vs Delta](iceberg-vs-paimon-vs-hudi-vs-delta.md) —— 四大湖表格式
- [Catalog 全景对比](catalog-landscape.md) —— HMS / REST / Nessie / Unity / Polaris / Gravitino
- [Parquet vs ORC vs Lance](parquet-vs-orc-vs-lance.md) —— 三种列式文件格式
- [Puffin vs Lance](puffin-vs-lance.md) —— 向量下沉到湖的两条路

## 计算引擎

- [计算引擎对比](compute-engines.md) —— Trino / Spark / Flink / DuckDB
- [**OLAP 加速副本横比**](olap-accelerator-comparison.md) ⭐ —— StarRocks / ClickHouse / Doris / Druid / Pinot
- [**流处理引擎横比**](streaming-engines.md) ⭐ —— Flink / Spark Streaming / Kafka Streams / RisingWave

## 检索 / 向量

- [ANN 索引对比](ann-index-comparison.md) —— HNSW / IVF-PQ / DiskANN / Flat
- [向量数据库对比](vector-db-comparison.md) —— Milvus / LanceDB / Qdrant / Weaviate / pgvector
- [Embedding 模型横比](embedding-models.md) —— BGE / E5 / Jina / OpenAI / Cohere
- [**Rerank 模型横比**](rerank-models.md) ⭐ —— bge-reranker / Cohere Rerank / Jina Reranker
- [**稀疏检索对比**](sparse-retrieval.md) ⭐ —— BM25 / SPLADE / ColBERT / Elser

## 平台 / MLOps

- [**Feature Store 横比**](feature-store-comparison.md) ⭐ —— Feast / Tecton / Hopsworks / Databricks FS / 自建
- [**调度系统横比**](orchestrators.md) ⭐ —— Airflow / Dagster / Prefect / DolphinScheduler

