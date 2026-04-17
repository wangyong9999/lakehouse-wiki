---
title: 一体化架构
description: 湖 + 向量 + Catalog + 计算的统一范式 —— 团队长期关注的主线
---

# 一体化架构

团队最核心的主线。**BI 和 AI 的负载，为什么应该跑在同一个湖仓上**，这节给答案和案例。

## 已有

- [Lake + Vector 融合架构](lake-plus-vector.md) —— 把向量检索做成"湖的原住民"的三种范式
- [多模数据建模](multimodal-data-modeling.md) —— 一张湖表承载图 / 文 / 音 / 视 + 多种向量
- [统一 Catalog 策略](unified-catalog-strategy.md) —— 从"表注册中心"升级到"治理平面"

## 待补

- 业内案例拆解（Databricks Mosaic、Snowflake Cortex、OpenAI 私有湖仓）
- 计算统一（同一引擎读关系表 + 向量表）
- Compute Pushdown 下沉到湖（湖上跑 UDF / 模型推理）

## 相关

- 底座：[湖表](../lakehouse/lake-table.md) · [向量数据库](../retrieval/vector-database.md)
- 场景：[RAG on Lake](../scenarios/rag-on-lake.md) · [多模检索流水线](../scenarios/multimodal-search-pipeline.md)
