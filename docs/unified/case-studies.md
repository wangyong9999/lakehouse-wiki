---
title: 案例拆解
type: concept
tags: [unified, case-study]
aliases: [Case Studies, 业内案例]
related: [lake-plus-vector, multimodal-data-modeling, unified-catalog-strategy]
systems: [databricks, snowflake]
status: stable
---

# 案例拆解

!!! tip "一句话理解"
    把**业内公开的"BI + AI 一体化湖仓"**参考架构拆成相同坐标系：存储、表格式、Catalog、检索、计算、消费。看清楚别人怎么做、为什么做，避免重复造轮子。

> **注意**：以下信息来源于各家公开博客、技术分享、官方文档。具体实现细节以对应公司最新公开材料为准。

## 评估坐标系

每个案例按这 8 个维度统一描述：

| 维度 | 我们关注什么 |
| --- | --- |
| 主场景 | BI / AI / 搜索 / 推荐 / 多模 |
| 表格式 | Iceberg / Delta / Paimon / 自研 |
| Catalog | HMS / UC / Polaris / 自研 |
| 存储 | 对象存储 / 自建分布式文件系统 |
| 向量层 | 独立向量库 / 湖原生 / Puffin |
| 检索 | Dense / Hybrid / Rerank |
| 主要引擎 | Spark / Trino / Flink / 内部 |
| 独特做法 | 最值得学的那件事 |

---

## 案例 1：Databricks Mosaic + Unity Catalog

- **主场景**：通用数据 + AI 平台
- **表格式**：Delta Lake（推 UniForm 做多协议兼容）
- **Catalog**：Unity Catalog —— **多模资产统一管理**（Table / Model / Volume / Function / Vector Index）
- **存储**：云对象存储
- **向量层**：Vector Search（Databricks 托管）+ Mosaic Vector DB
- **检索**：Dense + Hybrid + Rerank 全家桶，接入 Model Serving
- **主引擎**：Spark（Photon 向量化）+ DBSQL
- **最值得学**：**"Catalog 作为治理平面"** —— 从表权限到向量权限到模型权限一张模型，行列级 + Tag 策略 + 血缘。这是我们 [统一 Catalog 策略](unified-catalog-strategy.md) 的直接参考

---

## 案例 2：Snowflake Cortex + Open Catalog (Polaris)

- **主场景**：云数仓 + AI 内嵌
- **表格式**：内部原生 + Iceberg（Open Catalog = Polaris 开源实现）
- **Catalog**：Polaris（Iceberg REST Catalog + RBAC）
- **存储**：对象存储
- **向量层**：表内原生向量列 + Cortex Search
- **检索**：Cortex Search（Dense + Hybrid + Reranker）
- **主引擎**：Snowflake SQL 引擎 + Cortex LLM UDF
- **最值得学**：**"SQL 里直接调 LLM / embedding 函数"** —— `CORTEX.EMBED_TEXT()` / `CORTEX.COMPLETE()` 作为一等表达式。这是 [Compute Pushdown](compute-pushdown.md) 的极致形态

---

## 案例 3：Netflix（历史 Iceberg 诞生地）

- **主场景**：大规模批分析 + 流
- **表格式**：Iceberg（发源地）
- **Catalog**：自研（早期 HMS 起源 → 现代 REST）
- **存储**：S3
- **向量层**：独立专用系统
- **检索**：业务场景内
- **主引擎**：Spark、Trino、Flink
- **最值得学**：**"表格式即协议"**——Iceberg 从第一天就是把"表 = 一堆文件 + 元数据协议"抽象出来，让任何引擎都能互操作。多引擎中立的长远受益非常大

---

## 案例 4：LinkedIn（多模检索 + 推荐）

- **主场景**：岗位 / 人 / 内容多模检索
- **表格式**：Iceberg（迁移自 Hive）
- **Catalog**：内部（DataHub 做血缘 / 治理）
- **存储**：HDFS + 对象存储
- **向量层**：独立（LinkedIn 开源 ScANN-like 系统）
- **检索**：Dense + 结构化特征 + Learning-to-rank
- **主引擎**：Spark + 自研 Serving
- **最值得学**：**"搜索 / 推荐 = 向量 + 结构化 + 行为数据"** —— 不是纯向量、不是纯 BM25，而是工程上把三者稳定拼起来

---

## 案例 5：Uber（流式数据湖先驱，Hudi 诞生地）

- **主场景**：订单、行程、定价、风控
- **表格式**：Hudi（发源地）
- **Catalog**：HMS → 现代 Catalog
- **存储**：HDFS + S3
- **向量层**：ML 平台独立
- **检索**：特征存储（Palette → Michelangelo）
- **主引擎**：Spark、Flink、Presto
- **最值得学**：**"流式 upsert 到湖"的工程化**——Hudi 的 CoW/MoR、Incremental Query、Timeline，全是被实际流量压出来的设计

---

## 案例 6：Pinterest（多模推荐）

- **主场景**：Pin 内容推荐（图 + 文 + 行为）
- **表格式**：Iceberg
- **Catalog**：自研 + Iceberg REST
- **存储**：S3
- **向量层**：PinSage / GraphJet 风格，多模 embedding
- **检索**：向量召回 + LTR 精排
- **主引擎**：Spark + 自研 serving
- **最值得学**：**"embedding 是主语料"** —— 用户行为 → embedding → 召回。行为数据的向量化是第一公民

---

## 从这些案例能抽出的共同规律

1. **Catalog 在升级成治理平面** —— Unity / Polaris / DataHub 都在往"多模资产+血缘+权限"走
2. **SQL 是长期入口** —— 无论前端多花哨，底层都在把 embedding / LLM / rerank 做成 SQL 算子
3. **向量层的位置在变** —— 从"独立系统"正在逐步被"湖上就地检索"蚕食
4. **表格式与协议中立化** —— Iceberg REST 作为事实标准被越来越多家采纳
5. **Embedding 是工程主语料** —— 不是"给 RAG 用"，是"给检索、推荐、训练、缓存、去重通用"

## 对我们的启示

团队方向和业内主流一致。优先级参考：

1. **Catalog 治理平面** —— 先有 Unity / Polaris，再谈其他一体化
2. **表格式 + Puffin** —— 投资 Iceberg 上的向量索引下沉能力
3. **Embedding 流水线** —— 作为事实上的基础设施而非"某 AI 项目的附属"
4. **SQL 层的 Vector / LLM UDF 标准** —— 关注社区进展

## 相关

- [Lake + Vector 融合架构](lake-plus-vector.md)
- [统一 Catalog 策略](unified-catalog-strategy.md)
- [Compute Pushdown](compute-pushdown.md)
- 学习路径：[一月 AI 方向](../learning-paths/month-1-ai-track.md)

## 延伸阅读

- Databricks / Snowflake 官方技术博客（持续更新）
- Netflix Data Platform Blog
- Uber Engineering Blog
- LinkedIn Engineering Blog
- *The Composable Data Stack*（a16z）
