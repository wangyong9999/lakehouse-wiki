---
title: 一体化架构
description: 湖 + 向量 + Catalog + 计算的统一范式 —— 团队长期关注的主线
---

# 一体化架构

团队最核心的主线。**BI 和 AI 的负载，为什么应该跑在同一个湖仓上**，这节给答案和案例。

## 架构与范式

- [Lake + Vector 融合架构](lake-plus-vector.md) —— 把向量检索做成"湖的原住民"的三种范式
- [多模数据建模](multimodal-data-modeling.md) —— 一张湖表承载图 / 文 / 音 / 视 + 多种向量
- [统一 Catalog 策略](unified-catalog-strategy.md) —— 从"表注册中心"升级到"治理平面"
- [跨模态查询](cross-modal-queries.md) —— 一条 SQL 同时做结构化过滤 + 向量相似度
- [Compute Pushdown](compute-pushdown.md) —— 把计算、UDF、模型推理下沉到湖

## 业内深度案例

- [**案例 · Netflix 数据平台**](case-netflix.md) ⭐ —— Iceberg 创始地 · 全开源生态
- [**案例 · LinkedIn 数据平台**](case-linkedin.md) ⭐ —— Kafka / Pinot / DataHub / Feathr 全家桶
- [**案例 · Uber 数据平台**](case-uber.md) ⭐ —— Hudi + Michelangelo，实时 + ML 驱动
- [案例拆解（多家综述）](case-studies.md) —— Databricks / Snowflake / Airbnb / Pinterest 等

## 团队决策

- [ADR-0002 选择 Iceberg 作为主表格式](../adr/0002-iceberg-as-primary-table-format.md)
- [ADR-0003 多模向量存储选 LanceDB](../adr/0003-lancedb-for-multimodal-vectors.md)

## 相关

- 底座：[湖表](../lakehouse/lake-table.md) · [向量数据库](../retrieval/vector-database.md)
- 场景：[RAG on Lake](../scenarios/rag-on-lake.md) · [多模检索流水线](../scenarios/multimodal-search-pipeline.md)

## 待补（下一轮）

- 案例 · 字节 / 阿里 / Shopify 等
- 多模一体化的内部案例脚本
