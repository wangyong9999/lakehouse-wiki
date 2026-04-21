---
title: 工业案例 · 数据平台参考
description: Netflix · LinkedIn · Uber · Databricks · Snowflake · Pinterest 等工业数据平台深度参考
last_reviewed: 2026-04-21
---

# 工业案例 · 数据平台参考

!!! tip "一句话定位"
    **世界级数据平台公开资料的拆解归档**。Netflix / LinkedIn / Uber / Databricks / Snowflake / Pinterest / Airbnb 等工业团队的数据平台架构 · 按统一坐标系（存储 / 表格式 / Catalog / 检索 / 计算 / 消费）整理 · 供团队做架构决策和方案评审时参考。

!!! warning "本章定位 · reference 性质 · 非机制 canonical"
    - **本章**：**工业案例参考**（reference）· 讲"别人怎么做 · 规模多大 · 有什么经验"· **不深挖机制原理**
    - **机制原理**：去对应技术栈章（[lakehouse/](../lakehouse/index.md) · [retrieval/](../retrieval/index.md) · [catalog/](../catalog/index.md) · [query-engines/](../query-engines/index.md) · [ai-workloads/](../ai-workloads/index.md) · [ml-infra/](../ml-infra/index.md)）
    - **架构模式**：去 [unified/](../unified/index.md) · 讲跨章组合视角
    - **业务端到端**：去 [scenarios/](../scenarios/index.md) · 讲具体业务场景的编排
    
    **用法**：做架构设计 / 选型评审时翻一翻 · 知道"业界是怎么做的"。

## 深度案例（每案 200+ 行）

- [**Netflix 数据平台**](netflix.md) ⭐ —— Apache Iceberg 创始地 · 10 万+ Iceberg 表 · Metacat / Genie / Maestro / Metaflow 全开源
- [**LinkedIn 数据平台**](linkedin.md) ⭐ —— Kafka 原生地 · Pinot / Samza / Venice / Feathr / DataHub 全家桶
- [**Uber 数据平台**](uber.md) ⭐ —— Apache Hudi 诞生地 · Michelangelo MLOps 鼻祖 · 实时 + ML 驱动

## 综述 · 多家横比

- [**六家综述**](studies.md) —— Databricks · Snowflake · Netflix · LinkedIn · Uber · Pinterest 按统一坐标系对比

## 评估坐标系 · 怎么读案例

每个案例按这 8 个维度描述：

| 维度 | 关注点 |
|---|---|
| **主场景** | BI / AI / 搜索 / 推荐 / 多模 |
| **表格式** | Iceberg / Delta / Paimon / Hudi / 自研 |
| **Catalog** | HMS / UC / Polaris / 自研 |
| **存储** | 对象存储 / 自建分布式文件系统 |
| **向量层** | 独立向量库 / 湖原生 / Puffin |
| **检索** | Dense / Hybrid / Rerank |
| **主要引擎** | Spark / Trino / Flink / 内部 |
| **独特做法** | 最值得学的那件事 |

## 从这些案例能抽出的共同规律

1. **Catalog 在升级成治理平面** —— Unity / Polaris / DataHub 都在往"多模资产 + 血缘 + 权限"走
2. **SQL 是长期入口** —— 底层都在把 embedding / LLM / rerank 做成 SQL 算子（详见 [query-engines/compute-pushdown](../query-engines/compute-pushdown.md)）
3. **向量层的位置在变** —— 从"独立系统"正在逐步被"湖上就地检索"蚕食
4. **表格式与协议中立化** —— Iceberg REST 作为事实标准被越来越多家采纳
5. **Embedding 是工程主语料** —— 不是"给 RAG 用" · 是"给检索、推荐、训练、缓存、去重通用"

## 对团队的启示

- **Catalog 治理平面** —— 先有 Unity / Polaris · 再谈其他一体化（详见 [catalog/strategy](../catalog/strategy.md)）
- **表格式 + Puffin** —— 投资 Iceberg 上的向量索引下沉能力（详见 [lakehouse/puffin](../lakehouse/puffin.md)）
- **Embedding 流水线** —— 作为事实上的基础设施而非"某 AI 项目的附属"（详见 [ml-infra/embedding-pipelines](../ml-infra/embedding-pipelines.md)）
- **SQL 层的 Vector / LLM UDF 标准** —— 关注社区进展（详见 [query-engines/compute-pushdown](../query-engines/compute-pushdown.md)）

## 相关

- [一体化架构](../unified/index.md) —— 跨章组合视角
- [Lake + Vector 融合架构](../unified/lake-plus-vector.md) —— 三种融合范式
- [Catalog 策略](../catalog/strategy.md) —— 选型决策 canonical
- [Iceberg vs Paimon vs Hudi vs Delta](../compare/iceberg-vs-paimon-vs-hudi-vs-delta.md) —— 表格式横比
- [Vendor Landscape](../frontier/vendor-landscape.md) —— 厂商生态全景

## 来源与更新

!!! note "信息来源"
    以下案例信息**来源于各家公开博客、技术分享、官方文档**。具体实现细节以对应公司最新公开材料为准。技术栈演进快 · 建议交叉验证最新博客。
