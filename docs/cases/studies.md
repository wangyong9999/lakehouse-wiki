---
title: 工业案例综述 · 7 家横比矩阵
type: reference
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: Databricks · Snowflake · Netflix · LinkedIn · Uber · Pinterest · 阿里巴巴 · 2024-2026 公开资料
tags: [case-study, comparison, databricks, snowflake, netflix, linkedin, uber, pinterest, alibaba]
aliases: [Case Studies, 工业案例综述]
related: [databricks, snowflake, netflix, linkedin, uber, pinterest, alibaba]
systems: [databricks, snowflake, iceberg, delta, paimon, hudi, unity-catalog, polaris]
status: stable
---

# 工业案例综述 · 7 家横比矩阵

!!! info "本页性质 · 纯事实横比 · 不做战略判断"
    本页**仅做客观事实横比**（表格式 · Catalog · 引擎 · 向量层等维度）· **不做**"什么更好 / 团队应该选什么 / 工业共同规律"**等战略判断** —— 这些判断在 [unified/](../unified/index.md) · [catalog/strategy](../catalog/strategy.md) · [compare/](../compare/index.md) 做 canonical。
    
    读本页的正确方式：**看事实、找差异 · 回上层（unified/strategy/compare）做决策**。

!!! danger "样本类型分层 · 跨类型横比有失真风险"
    **7 家案例不是同一层级对象**：
    
    - **商业产品平台**：[Databricks](databricks.md) · [Snowflake](snowflake.md)
    - **大厂内部数据平台**：[Netflix](netflix.md) · [LinkedIn](linkedin.md) · [Uber](uber.md) · [阿里巴巴](alibaba.md)
    - **业务系统案例**（非通用数据平台）：[Pinterest](pinterest.md)（推荐系统专题 · PinSage/Pixie）
    
    矩阵的"规模"/"向量层"/"检索"等维度**在商业 vs 内部 vs 业务系统之间不完全可比**。本页按类型分组呈现。

!!! abstract "7 家覆盖的光谱"
    - **商业一体化平台**：[Databricks](databricks.md)（Lakehouse AI）· [Snowflake](snowflake.md)（Data Cloud + Cortex）
    - **OSS 基础设施代表**：[Netflix](netflix.md)（Iceberg 诞生地）· [LinkedIn](linkedin.md)（Kafka 全家桶）· [Uber](uber.md)（Hudi + Michelangelo）
    - **多模推荐工业代表**：[Pinterest](pinterest.md)（PinSage + Homefeed）
    - **中国工业代表**：[阿里巴巴](alibaba.md)（Paimon 诞生地 + Flink 深度使用）
    - **配合 [Vendor Landscape](../frontier/vendor-landscape.md)**（厂商选型视角）使用

## 1. 评估坐标系 · 8 维

每家按以下 8 个维度描述（和各深度页 §4 对齐）：

| 维度 | 关注点 |
|---|---|
| **主场景** | BI / AI / 搜索 / 推荐 / 多模 / 数仓 / 交易 |
| **表格式** | Iceberg / Delta / Paimon / Hudi / 自研 |
| **Catalog** | HMS / UC / Polaris / Nessie / DataHub / 自研 |
| **存储** | 对象存储 / HDFS / 云存储 / 跨云 |
| **向量层** | 独立向量库 / 湖原生 / 托管 / 自研 |
| **检索** | Dense / Hybrid / Rerank / GNN / LTR |
| **主引擎** | Spark / Trino / Flink / 自研 / 云托管 SQL |
| **独特做法** | 最值得学的那件事 |

## 2. 7 家横比矩阵（核心）

| 维度 | **Databricks** | **Snowflake** | **Netflix** | **LinkedIn** | **Uber** | **Pinterest** | **阿里巴巴** |
|---|---|---|---|---|---|---|---|
| **主场景** | BI+AI 一体化平台 | 云数仓+AI 内嵌 | 批+流+ML | 推荐+检索+实时 OLAP | 实时 ML 决策 | 多模推荐 | 电商超大规模 |
| **表格式** | Delta + **UniForm** | 内部 FDN + Iceberg 外部 | **Iceberg**（诞生地）| **Iceberg**（迁移中） | **Hudi**（诞生地） | Iceberg | **Paimon**（诞生地）|
| **Catalog** | **UC** 商业+OSS | **Polaris**（2024 捐 ASF · 2026 TLP）+ Horizon | **Metacat**（联邦） | 内部（DataHub 做发现） | HMS → 现代 | 自研 + Iceberg REST | 阿里云 DMS |
| **Table Lifecycle 层**（Catalog 之上）| Delta Lake 运维内建 | Snowflake 内部托管 | Iceberg 内建 + 自建脚本 | **OpenHouse**（2024 开源 · LinkedIn 独家贡献） | 自建 | 自建 | 自建 |
| **存储** | 云对象（跨云） | 云对象（跨云） | S3 | HDFS + 对象 | HDFS + S3 | S3 | OSS + HDFS |
| **向量层** | **Vector Search** 托管 | **Cortex Search**（向量原生）| 独立 · 业务内嵌 | 自研 · 紧耦合推荐 | ML 平台内嵌 | **自研 ANN**（PinSage）| Hologres 2024+ / ProxiMA 自研 |
| **检索** | Dense + Hybrid + Reranker | Cortex Search（三段式）| 业务场景内 | **Dense + 结构化 + LTR** | Feature Store 驱动 | **多路召回+LTR+重排** | 多路召回+LTR |
| **主引擎** | **Spark+Photon** + DBSQL | **Snowflake SQL** + Snowpark | **Trino** + Spark | Spark + Trino + Flink | Spark+Flink+Presto | 自研 serving + Spark | **Flink** + MaxCompute |
| **独特做法** | **Catalog 作治理平面** | **SQL 里直接调 LLM**（Cortex 先驱）| **表格式即开放协议** | **单品开源 + 商业化培育** | **流式湖表工程化 + MLOps 平台化** | **Embedding 是主语料** | **流式湖仓 Paimon + Flink CDC** |

## 3. 关键维度深度对比

### 3.1 表格式之争（2024-2026 视角）

**三条技术路线 · 四家主要玩家**：

| 表格式 | 代表案例 | 核心场景 |
|---|---|---|
| **Iceberg** | [Netflix](netflix.md)（诞生）· [LinkedIn](linkedin.md)（迁移中）· [Snowflake](snowflake.md)（外部支持） | 多引擎开放 · 批为主 |
| **Delta** | [Databricks](databricks.md)（主推 + UniForm 兼容）| Databricks 生态 · 追开放 |
| **Hudi** | [Uber](uber.md)（诞生）| 流式 upsert · Spark 生态 |
| **Paimon** | [阿里巴巴](alibaba.md)（诞生）| Flink 流式 + LSM-tree |

**关键观察**：
- 2024-2026 **Iceberg 生态明显领先**（贡献方多元 · 多引擎支持深）
- Delta 通过 **UniForm**（2024）与 Iceberg 互操作 · 保 primary 地位
- Hudi 在 **流式场景**仍有技术优势 · 但生态窄
- **Paimon 是最活跃的新项目**（2024 TLP）· 流式场景正在追上 Iceberg

详见 [Iceberg vs Paimon vs Hudi vs Delta](../compare/iceberg-vs-paimon-vs-hudi-vs-delta.md) 横比。

### 3.2 Catalog 之争（2024-2026）

| Catalog | 主推方 | 定位 |
|---|---|---|
| **Unity Catalog**（商业+OSS）| [Databricks](databricks.md) · 2024 捐 LF AI | **多模资产最全** · 治理能力最深 |
| **Polaris**（Apache TLP 2026-02）| [Snowflake](snowflake.md)（开源+托管） | **纯 Iceberg REST + RBAC** · 协议最"纯净" |
| **Gravitino**（Apache TLP）| 字节系 + 社区 | **联邦多源** |
| **Nessie** | Dremio | **Git-like 分支** |
| **Metacat** | [Netflix](netflix.md) | 联邦 · 特色但未全面开源 |
| **OpenHouse** | [LinkedIn](linkedin.md)（2024 开源）| Iceberg 之上的**运维控制平面** |

**2026 格局**：
- **UC vs Polaris** 是最激烈的商业竞争（分别代表 Databricks 和 Snowflake 战略）
- **Gravitino** 在"**联邦多源**"场景填补空白
- **OpenHouse** 是新层次（不是 Catalog 替代 · 是**Catalog 之上的 table lifecycle**）

详见 [catalog/strategy](../catalog/strategy.md)。

### 3.3 ML / AI 平台成熟度

| 公司 | ML 平台状态 | 代表产品 |
|---|---|---|
| [Databricks](databricks.md) | **最成熟**（2019+ 领先）| MLflow + Mosaic AI Training + Vector Search + AI Functions |
| [Uber](uber.md) | **鼻祖**（Michelangelo 2017）| Michelangelo + Palette/Genoa |
| [Snowflake](snowflake.md) | **追赶期**（2023+）| Snowpark ML + Cortex |
| [Netflix](netflix.md) | 深度使用但无强产品 | Metaflow（Workflow）+ MLflow（Registry） |
| [LinkedIn](linkedin.md) | Feature Store 突出 | Feathr（Apache Incubator 2024）|
| [Pinterest](pinterest.md) | 推荐场景特化 | PinSage + 自研 ML |
| [阿里巴巴](alibaba.md) | 覆盖完整 | PAI 平台 + 定制化 |

### 3.4 向量检索策略

| 公司 | 策略 | 实现 |
|---|---|---|
| [Databricks](databricks.md) | **湖原生 + 托管** | Vector Search（Delta 一等索引） |
| [Snowflake](snowflake.md) | **向量原生 SQL** | Cortex Search |
| [Pinterest](pinterest.md) | **自研 ANN**（规模优先）| ScaNN-like 自研 |
| [阿里巴巴](alibaba.md) | **HSAP 集成**（Hologres）+ 自研（ProxiMA）| Hologres + OpenSearch + 自研 |
| [Netflix](netflix.md) | 独立专用系统 | 内嵌业务 |
| [LinkedIn](linkedin.md) | 推荐深度耦合 | 自研 |
| [Uber](uber.md) | ML 平台内嵌 | Feature Store 驱动 |

**关键观察**（事实 · 非主张）：
- "湖仓一体化向量"（Databricks + Snowflake + Hologres）是 2024-2026 可观察趋势
- 头部推荐公司普遍自研 ANN（Pinterest · 阿里 · Netflix · LinkedIn）
- 中小规模团队用通用向量库（Milvus / Qdrant / LanceDB）是常见选择

## 4. 事实观察 · 非战略判断

!!! note "本节仅做事实观察 · 战略判断在别章"
    以下是跨案例可观察的**事实模式** · 不是"团队应该怎么做"的推荐。**战略建议在 [unified/index §5 团队路线主张](../unified/index.md) · [catalog/strategy](../catalog/strategy.md) · [compare/](../compare/index.md)** · 本页不替它们做结论。

### 4.1 Catalog 层分化 · 不是一条"规律"

各家 Catalog 选型差异反映不同战略 · **不是一条统一规律**：

- Databricks · UC 多模全包（商业 + OSS）· 争行业标准
- Snowflake · Polaris 纯 Iceberg + RBAC（2024 捐 ASF · 2026 TLP）
- Netflix · Metacat 联邦（多 metastore 联邦）
- LinkedIn · 内部 + **OpenHouse**（**table lifecycle 层 · 不是 Catalog 替代**）
- 阿里 · DMS 自研

**不同战略的取舍** · [catalog/strategy](../catalog/strategy.md) canonical 做深度分析 · 本页不重复。

### 4.2 商业厂商普遍"开放部分 + 锁定部分"

- Snowflake：支持 Iceberg 外部表 + 开源 Polaris · 但内部 FDN 仍主推
- Databricks：UniForm 读 Iceberg · 但 Delta 仍 primary
- 阿里 MaxCompute：2023+ 支持 Paimon / Iceberg 外部表 · 但内部格式仍主力

**是事实观察** · 不代表读者应选什么。

### 4.3 商业案例 vs 内部平台的"失败"口径不同

**读者注意** · 跨类型比较失败有天然失真：

- **商业产品失败**（Databricks · Snowflake）= 生态战 / 增长节奏 / 产品线混乱
  - 如 Snowflake Unistore 接受度低 · Databricks MosaicML 整合期产品线混乱
- **内部平台失败**（Netflix · LinkedIn · Uber · 阿里）= 工程弯路 / 自研输给社区 / 迁移低估
  - 如 Uber AresDB 降级 · Netflix 自研 OLAP 失败 · LinkedIn Azkaban 老化

**跨类型的"失败"横比请谨慎** · 各家深度页 §9 保留各自口径的详细说明。

## 5. 组织 / 迁移 / adoption 横比 · 工业案例最稀缺信号

工业案例最有价值的**不是技术组件清单** · 是**组织和工程推进方式**。这一节从 7 家公开资料提炼相关信号。

### 5.1 团队分工模式

| 案例 | 平台团队定位 | 业务团队自由度 |
|---|---|---|
| Netflix | **Platform + Self-Service 模板**（Genie / Maestro / Metaflow · "给工具不给规定"） | 极高 · 业务选用或不用 |
| LinkedIn | **独立平台组** · 多单品深度 | 中 · 标准栈 + 可不用（Samza → Flink 自然迁移） |
| Uber | **强平台推动**（早期 Michelangelo adoption 强制）| 中低 · 2022+ 简化后改善 |
| 阿里 | **多云多平台并存**（闭源 + 开源栈）| 中 · 业务选择云 / 开源组合 |
| Databricks / Snowflake | 商业产品 · 客户视角 | 客户决定 |
| Pinterest | **业务推荐团队独立** · 平台支撑 | 推荐团队自研多 |

**观察**：大厂内部平台走向"**工具 + golden path · 不强制**"（Netflix / LinkedIn 2020+ 风格）· 比"**强平台 adoption**"（早期 Uber 风格）更可持续。

### 5.2 adoption 推动策略

| 案例 | 推动方式 |
|---|---|
| Netflix · Iceberg | 一张小表试点 · 业务自发扩展 · 5+ 年渐进 |
| LinkedIn · Kafka | 公司统一"事件总线" · 强标准但接受度自然 |
| LinkedIn · Iceberg 迁移 | 2023 启动 · 2-3 年窗口（大规模 Hive → Iceberg 进行时）|
| Uber · Michelangelo | 早期 adoption 强推 · 2022+ 简化才稳定 |
| 阿里 · Paimon | **通过开源社区扩展 · 内外部并行**（先开源生态再内部 adoption）|
| Databricks / Snowflake | 商业营销 + 客户成功 + 社区（商业产品路径）|

### 5.3 大规模迁移共同模式

**Hive → Iceberg 大规模迁移都给出 2-3+ 年窗口**：

- Netflix 2017-2020+（已完成大部分）
- LinkedIn 2023-2026（进行中）
- Pinterest 2020+（进行中）
- Databricks / Snowflake 客户迁移（双方支持）

**共同教训（事实观察）**：**表格式迁移是组织工程 · 不是技术工程** · 时间估算 × 2 起步 · 业务团队教育 + 下游工具链适配成本常被低估。

### 5.4 build vs buy 取舍

| 能力 | 代表 build 案例 | 代表 buy / 用 OSS 案例 | 工业观察 |
|---|---|---|---|
| **表格式** | Netflix Iceberg / Uber Hudi / 阿里 Paimon（build 后开源）| LinkedIn / Pinterest（用 OSS Iceberg） | **build 后开源 + 社区贡献**成主流 |
| **Catalog** | Netflix Metacat · LinkedIn OpenHouse（build）· Databricks UC / Snowflake Polaris（build 后开源）| 中小团队（用 OSS UC/Polaris） | **商业产品主导 · 开源版可选** |
| **ML 平台** | Uber Michelangelo · Netflix Metaflow（build 周期 7 年+）| MLflow + Databricks / 阿里 PAI | **build 周期 7 年起 · 非差异化需求优先用开源** |
| **实时 OLAP** | LinkedIn Pinot（build 后开源）· Uber AresDB（build 后降级）| Pinot / Druid / ClickHouse（OSS）| **OSS 主导 · 自研逐步让位**（AresDB 典型） |
| **调度** | Netflix Maestro · LinkedIn Azkaban · Uber Peloton（全 build · 多数降级）| Airflow / Dagster / Prefect（OSS）| **OSS 追上 · 自研维护困难是常态** |

**资深观察**（事实 · 非推荐）：**2010-2020 是大厂自研黄金期** · **2020+ 社区 OSS 普遍追上** · 自研的长期维护成本高于起步预期。

### 5.5 中央 vs self-service 边界

**公开资料呈现的常见模式**（跨案例观察 · 非推荐）：
- **工具 + 标准** 倾向中央提供（Registry · Catalog · Feature Store 后端 · 调度）
- **业务逻辑 + 实验** 倾向 self-service（Notebook · 训练代码 · 模型超参搜索）
- **边界在不同案例间不同** · 但"中央定规矩 · 不做业务代码"在 Netflix / LinkedIn 等成熟阶段是共识

具体案例看各深度页 §5 关键组件和 §8 取舍。

## 6. 按 scenarios 场景找案例 · 配对反向索引

**读者典型路径**：读 scenarios/X 业务页 · 想看工业案例 · 查这张表找哪家在 X 场景有值得学的做法。

| scenarios 页 | 主推案例 + 哪家看哪部分 | 次要参考 |
|---|---|---|
| [scenarios/recommender-systems](../scenarios/recommender-systems.md) | [**Pinterest**](pinterest.md) §5.1 PinSage · §5.2 Pixie · [**阿里**](alibaba.md) §5.2 Flink + Paimon 推荐数据栈 · [**LinkedIn**](linkedin.md) §5.3 Venice | — |
| [scenarios/rag-on-lake](../scenarios/rag-on-lake.md) | [**Databricks**](databricks.md) §5.3 UC + §5.6 AI Functions · [**Snowflake**](snowflake.md) §5.2 Cortex · §5.3 Cortex Search | [Netflix](netflix.md) · 内部 RAG 推断 |
| [scenarios/bi-on-lake](../scenarios/bi-on-lake.md) | [**Databricks**](databricks.md) §5.4 Photon · §5.9 DBSQL · [**Snowflake**](snowflake.md) §5.1 VW · [**Netflix**](netflix.md) §5.1 Metacat + Trino/Iceberg | — |
| [scenarios/fraud-detection](../scenarios/fraud-detection.md) | [**Uber**](uber.md) §5.2 Michelangelo · §5.3 Palette/Genoa | [LinkedIn](linkedin.md) 内容安全推断 |
| [scenarios/cdp-segmentation](../scenarios/cdp-segmentation.md) | [**阿里**](alibaba.md) §5.3 Hologres HSAP | [LinkedIn](linkedin.md) 用户分群推断 |
| [scenarios/agentic-workflows](../scenarios/agentic-workflows.md) | [**Databricks**](databricks.md) §5.10 Genie · [**Snowflake**](snowflake.md) §5.3 Cortex Agents 2025+ | — |
| [scenarios/text-to-sql-platform](../scenarios/text-to-sql-platform.md) | [**Databricks**](databricks.md) §5.10 Genie · [**Snowflake**](snowflake.md) Cortex Analyst | [阿里](alibaba.md) 内部 Text-to-SQL 推断 |
| [scenarios/multimodal-search-pipeline](../scenarios/multimodal-search-pipeline.md) | [**Pinterest**](pinterest.md) §5.5 多模 embedding 产线 · [**阿里**](alibaba.md) OpenSearch 向量 · [**Databricks**](databricks.md) §5.5 Vector Search | — |
| [scenarios/offline-training-pipeline](../scenarios/offline-training-pipeline.md) | [**Uber**](uber.md) §5.2 Michelangelo · [**Netflix**](netflix.md) §5.4 Metaflow | — |
| [scenarios/feature-serving](../scenarios/feature-serving.md) | [**LinkedIn**](linkedin.md) §5.3 Venice · [**Uber**](uber.md) §5.3 Palette/Genoa | — |
| [scenarios/real-time-lakehouse](../scenarios/real-time-lakehouse.md) | [**阿里**](alibaba.md) §5.1 Paimon · §5.2 Flink CDC · [**Uber**](uber.md) §5.1 Hudi | — |
| [scenarios/streaming-ingestion](../scenarios/streaming-ingestion.md) | [**LinkedIn**](linkedin.md) §5.1 Kafka · [**阿里**](alibaba.md) Flink CDC | — |

**用法**：
- 你想做 **X 场景** · 看 scenarios/X 是"怎么做"的 · 回来查这张表看"哪家怎么做的" · 点深度案例页看全栈上下文

## 7. 按问题找案例 · 能力反向索引

**"做 X 该学谁"**：

| 问题 | 首选案例 | 备选 |
|---|---|---|
| **做 ML 平台** | [Uber · Michelangelo](uber.md) | [Databricks](databricks.md) · [Netflix · Metaflow](netflix.md) |
| **做多模推荐** | [Pinterest](pinterest.md) | [LinkedIn](linkedin.md) · [阿里巴巴](alibaba.md) |
| **做 Catalog / 治理平面** | [Databricks · UC](databricks.md) | [Snowflake · Polaris](snowflake.md) · [Netflix · Metacat](netflix.md) |
| **做流式湖仓** | [阿里巴巴 · Paimon](alibaba.md) | [Uber · Hudi](uber.md) |
| **做实时 OLAP** | [LinkedIn · Pinot](linkedin.md) | [Uber](uber.md) · [阿里 · Hologres](alibaba.md) |
| **做 SQL LLM UDF** | [Snowflake · Cortex](snowflake.md) | [Databricks · AI Functions](databricks.md) |
| **做 Feature Store** | [Uber · Palette](uber.md) | [LinkedIn · Feathr](linkedin.md) |
| **学 BI + AI 一体化商业化** | [Databricks](databricks.md) | [Snowflake](snowflake.md) |
| **学开源策略** | [LinkedIn](linkedin.md) | [Netflix](netflix.md) · [阿里巴巴](alibaba.md) |
| **学大规模 Iceberg 运维** | [Netflix](netflix.md) | [LinkedIn · OpenHouse](linkedin.md) |
| **学中国工业实践** | [阿里巴巴](alibaba.md) | （后续案例页可加字节 / 腾讯） |


## 8. 不同读者的阅读路径建议

!!! info "本节是导航 · 不是推荐"
    以下路径是**按主题的读者导航** · 不是"这家最好"的主张。表述为**案例定位** · 不是评价。


### 架构师 / CTO

按"独特做法"列读起（每家一段）· 然后挑最相关的 2-3 家深度读（§5 关键技术 + §8 深度取舍 + §9 失败教训）。

### 做流式湖仓的工程师

先 [阿里](alibaba.md)（Paimon 诞生地）· 再 [Uber](uber.md)（Hudi 原始设计）· 横比决定路线。

### 做多模推荐的工程师

先 [Pinterest](pinterest.md)（最完整 · PinSage 论文级细节）· 再 [LinkedIn](linkedin.md)（推荐 + 检索组合）· [阿里巴巴](alibaba.md)（电商规模）。

### 做 Catalog 选型的平台工程师

先 [Databricks · UC](databricks.md)（最全）· 再 [Snowflake · Polaris](snowflake.md)（最开放）· [Netflix · Metacat](netflix.md)（联邦模式参考）。

### 做 ML 平台的平台工程师

先 [Uber · Michelangelo](uber.md)（鼻祖 · 7 年演进）· 再 [Databricks](databricks.md)（最成熟商业平台）· [Netflix · Metaflow](netflix.md)（Workflow 哲学）。

## 9. 本章定位声明

!!! note "本章 = reference · 非机制 canonical"
    - **机制原理**：去对应技术栈章（[lakehouse/](../lakehouse/index.md) / [catalog/](../catalog/index.md) / [retrieval/](../retrieval/index.md) / [ml-infra/](../ml-infra/index.md) / [ai-workloads/](../ai-workloads/index.md)）
    - **架构组合决策**：[unified/](../unified/index.md)
    - **业务场景端到端**：[scenarios/](../scenarios/index.md)
    - **厂商选型（商业视角）**：[frontier/vendor-landscape](../frontier/vendor-landscape.md)
    - **前沿未来**：[frontier/](../frontier/index.md)

## 10. 相关 · 延伸阅读

- 各家深度案例：[Databricks](databricks.md) · [Snowflake](snowflake.md) · [Netflix](netflix.md) · [LinkedIn](linkedin.md) · [Uber](uber.md) · [Pinterest](pinterest.md) · [阿里巴巴](alibaba.md)
- [Modern Data Stack](../frontier/modern-data-stack.md) —— 现代数据栈全景
- [Vendor Landscape](../frontier/vendor-landscape.md) —— 厂商选型（商业视角）
- [Iceberg vs Paimon vs Hudi vs Delta](../compare/iceberg-vs-paimon-vs-hudi-vs-delta.md) —— 表格式横比
- [Catalog 策略](../catalog/strategy.md) —— Catalog 选型决策
- [Lake + Vector 融合架构](../unified/lake-plus-vector.md) —— 架构组合视角

### 外部延伸

- Databricks / Snowflake 官方技术博客（持续更新）
- Netflix Tech Blog / Uber Engineering Blog / LinkedIn Engineering Blog
- Pinterest Engineering Medium · 阿里云开发者博客
- *Designing Data-Intensive Applications*（Kleppmann · LinkedIn 前员工）
- *The Composable Data Stack*（a16z）
