---
title: Lakehouse 厂商与开源生态格局（2025-2026）
type: reference
depth: 资深
level: A
last_reviewed: 2026-04-18
applies_to: 2025-2026 市场 · 定价有效期请以官方为准
tags: [frontier, market, vendor, ecosystem]
aliases: [Vendor Landscape]
related: [tco-model, data-systems-evolution, modern-data-stack]
status: stable
---

# Lakehouse 厂商与开源生态格局

!!! tip "一句话定位"
    **客观描述 2025-2026 Lakehouse 及 AI Infra 市场主要玩家、他们的卖点与边界、商业与技术博弈**。**注意时效**：此页是市场观察，非广告；厂商立场快速变化，重大决策前请以官方最新信息为准。

!!! abstract "TL;DR"
    - **商业巨头三极**：Databricks（Lakehouse 平台）· Snowflake（云数仓）· Google BigQuery（Google 系）
    - **开源 + 商业中立**：Tabular（被 Databricks 收购）· Onehouse · Starburst
    - **Lakehouse 整合中**：2024 Databricks 收购 Tabular → **Delta + Iceberg 融合成趋势**
    - **国内**：阿里 / 字节 / 华为 / PingCap 都在做 Lakehouse 产品
    - **关键变化**：**Iceberg 在多引擎场景被广泛采纳**（Snowflake / Databricks / AWS / GCP 均在兼容）
    - **对团队决策**：**别信厂商一面之词**，看开放协议 + 数据可移植

## 1. 市场格局概览

### 2024-2025 三极格局

```
                  商业数仓路线
                Snowflake / BigQuery
                       ↑
                       |
     Lakehouse ← 融合 → 云数仓
                       |
                       ↓
              Databricks / 自建
                Lakehouse 路线
```

**Databricks + Snowflake 作为两大商业主力**正在互相融合：
- Snowflake 2023 支持 Iceberg Tables
- Databricks 2024 收购 Tabular，承诺 Iceberg 与 Delta 协议融合
- BigQuery 2024 推 BigLake + Iceberg 兼容

**长期趋势**：**数据格式开放（Iceberg）、计算引擎多样、商业服务差异化**。

### 几类玩家

| 类别 | 代表 |
|---|---|
| **云数仓 / Lakehouse 平台** | Databricks · Snowflake · BigQuery · Redshift · Fabric |
| **开源 Lakehouse 商业化** | Tabular（被收购）· Onehouse（Hudi）· Starburst（Trino） |
| **专业向量库** | Pinecone · Weaviate · Qdrant · Zilliz（Milvus） |
| **ML / MLOps 平台** | Dataiku · DataRobot · Hopsworks · Tecton · Feast（OSS） |
| **数据治理 / Catalog** | Collibra · Alation · Atlan · Unity / Polaris（OSS）· DataHub |
| **数据接入 / ETL** | Fivetran · Airbyte · Rivery |
| **BI / 可视化** | Looker · Tableau · Power BI · ThoughtSpot · Sigma |
| **流处理** | Confluent · Decodable · Ververica（Flink） |

### 国内格局

| 类别 | 代表 |
|---|---|
| 云 Lakehouse | 阿里 MaxCompute · 字节 ByteHouse / ByteLake · 华为 DLI / MRS · 腾讯 TCHouse |
| 湖表贡献 | 阿里 **Paimon** · 字节 **Apache Lance** 贡献 · 蚂蚁 Nebula |
| OLAP | StarRocks · Apache Doris · ByteHouse（ClickHouse 变种） |
| 向量 | Zilliz Milvus · DingoDB · 各家云向量服务 |
| 数据栈 | 神策 / GrowingIO / 火山引擎 / PingCAP TiDB（HTAP） |

## 2. 主要玩家 · 客观描述

### Databricks

**定位**：**Lakehouse Platform** 的代表。

**核心卖点**：
- 一体化（湖仓 + ML + SQL + Notebook）
- Photon 引擎高性能
- Unity Catalog 治理完整
- MLflow 生态
- **2024 收购 Tabular** → Iceberg 也加入生态

**边界 / 争议**：
- **锁定度中等偏高**（Photon 闭源、商业能力多只在商业版）
- 成本**非线性增长**，规模大时昂贵
- 开源 Delta 和 Databricks Delta 有功能差距
- Iceberg 协议融合**尚未完成**（路线图中）

**典型用户**：北美大中型企业、金融、医疗、零售头部。

### Snowflake

**定位**：**云数仓标杆**，计算存储分离开创者。

**核心卖点**：
- 零运维体验最好
- 跨云（AWS / Azure / GCP）
- **Snowpark + Cortex**（AI 原生）
- 2023+ 支持 Iceberg Tables

**边界 / 争议**：
- **按 credit 计费**可能炸（warehouse 不 auto-suspend 成本爆）
- 传统上**对 ML 支持弱**，Cortex 正在补但还年轻
- **数据出来贵**（egress cost）
- 生态较封闭（主要自家产品组合）

**典型用户**：中型分析团队、SaaS 公司、快速起步场景。

### Google BigQuery

**定位**：GCP 原生数据仓库 + Lakehouse。

**核心卖点**：
- Serverless
- 按扫描字节计费（或 slot 包月）
- BigLake 兼容 Iceberg
- Vertex AI 集成好

**边界**：
- **绑定 GCP**
- On-demand 定价对大扫描成本难控
- 跨云弱

### AWS 系（Redshift + Glue + S3 + Athena + Lake Formation）

**定位**：AWS 全家桶组合，非单一产品。

**核心卖点**：
- 和 AWS 生态深度集成
- Iceberg 完整支持（Glue Catalog / Athena / EMR）
- 成本相对灵活

**边界**：
- 组件多，集成复杂度高
- 没有"统一"产品（和 Databricks / Snowflake 不同）

### Tabular（被 Databricks 收购）

**历史**：Ryan Blue（Iceberg 创始人）+ Daniel Weeks + Jason Reid 2021 创立。**2024.06 被 Databricks 收购**。

**后续**：
- Tabular 产品合并入 Databricks
- Ryan Blue 继续主导 Iceberg 社区
- 这是**Delta + Iceberg 融合的关键信号**

**对团队影响**：
- 独立 Iceberg 托管产品生态缺一块
- 但 Iceberg 开源协议**加速推进**
- Databricks 承诺继续支持 Iceberg

### Onehouse

**定位**：Hudi 创始团队（Uber 系）成立的商业公司。**Apache Hudi 的主要推动方**。

**核心卖点**：
- 托管 Hudi
- Lakehouse 多表格兼容（支持 Hudi + Delta + Iceberg）
- 实时 Ingestion

**边界**：
- 市场份额相对 Databricks / Snowflake 小
- Hudi vs Iceberg 竞争中处于守势

### Starburst

**定位**：**Trino 商业化**公司。

**核心卖点**：
- Trino 企业版（Starburst Enterprise / Galaxy）
- 多源联邦查询
- 数据治理集成

**边界**：
- **竞争对手多**：Databricks / Snowflake 都能做类似事
- Trino 本身开源，商业化差异化压力大

### Confluent

**定位**：**Kafka 商业化**+ Flink 托管。

**核心卖点**：
- Kafka / Flink 全托管
- **Tableflow**（2024）：直接把 Kafka topic 物化成 Iceberg 表

**边界**：
- Kafka 成本高
- 实时分析方向 vs RisingWave / Confluent Flink 竞争

### Pinecone / Weaviate / Qdrant

**定位**：专业向量数据库。

**对比**：

| | Pinecone | Weaviate | Qdrant | Zilliz (Milvus) |
|---|---|---|---|---|
| 主导 | 商业 Serverless | 开源 + 商业 | 开源 + 商业 | 开源 + 商业 |
| 规模 | 中-大 | 中 | 中 | 亿-百亿 |
| Hybrid 开箱 | 近期加 | 是 | 是 | 是 |
| 自主可控 | 低 | 中 | 高 | 高 |

**2024-2025 趋势**：专业向量库**被云原生厂商挤压**（AWS OpenSearch / GCP Vertex / Azure AI Search 都内置向量），中小客户转向更轻的 pgvector + LanceDB。

### 国内头部

**阿里云**：
- MaxCompute（老牌数仓）
- **Paimon 主导**（2023 Apache 毕业）→ 在流批一体上领先
- Hologres（OLAP）

**字节**：
- ByteHouse（内部 ClickHouse）
- ByteLake（内部 Lakehouse）
- 对 Lance 有投入

**华为云**：
- MRS（大数据全家桶）
- DLI（Serverless 分析）
- 企业级客户多

**腾讯云**：
- TCHouse（StarRocks 系 / ClickHouse 系）
- EMR

## 3. 关键竞争与博弈

### 开源协议战争（已基本收官）

- **Iceberg** 事实上胜出，**Delta / Hudi / Paimon** 都在"兼容 Iceberg"
- Delta Uniform 让 Delta 被 Iceberg 引擎读
- Hudi 支持 Iceberg 兼容
- **Paimon** 独立走流一体路线，不直接竞争 Iceberg

**启示**：选**Iceberg + Paimon 组合**最安全。

### Catalog 竞争（进行中）

- Iceberg REST Catalog 标准化
- 实现方：**Polaris**（Snowflake）· **Unity Catalog**（Databricks）· **Tabular**（被收购）· **Nessie** · **Gravitino**
- **两大阵营**：Databricks Unity 和 Snowflake Polaris 都要做"行业 Catalog"
- 独立选项：Nessie / Gravitino 生态小但中立

### 向量库在湖上（演进中）

- **Lance format** 走"湖原生向量"路线
- Iceberg **Puffin** 未来放向量索引
- 专业向量库 vs 湖上方案：**中小规模看融合**，超大规模仍用 Milvus / Pinecone

### ML Platform 收敛

- MLflow 开源但**被 Databricks 强管理**
- Kubeflow 开源但运维复杂
- Tecton / Hopsworks 聚焦 Feature Store
- **云原生方案**（SageMaker / Vertex AI / Azure ML）占大头

## 4. 选型实务

### 决策轴

1. **云绑定容忍度**（多云？单云？）
2. **商业 vs 开源**（预算 vs 人力）
3. **规模**（GB / TB / PB）
4. **AI + BI 比重**（哪个是主场景）
5. **合规 / 数据主权**（数据可否出境 / 跨云）

### 典型组合

| 规模 / 偏好 | 推荐 |
|---|---|
| 中型团队 + 零运维 + 成本不敏感 | **Snowflake + dbt + Looker** |
| 大型团队 + ML 重 + 已在 Azure | **Databricks Lakehouse Platform** |
| 大型团队 + 中立开源 | **Iceberg + Trino + Flink + Spark** 自建 |
| 小团队 + 快启动 | **BigQuery + dbt + Metabase** |
| AWS 深度用户 | **S3 + Glue + Athena + Redshift Spectrum** |
| 国内合规 + 国产化 | 阿里 MaxCompute + Paimon 或自建 |
| 实时 + ML | **Paimon + Flink + Feast + StarRocks** |

### 避免的做法

- **盲目相信厂商"比另一家快 N ×"**：看 benchmark 条件 + 自家 POC
- **一次迁到新平台**：渐进迁移、并行跑一段时间
- **只看 license 省**：开源不是免费，人力 + 运维才是大头
- **以为"开放协议"就没锁定**：看数据出站能力 + 元数据导出

## 5. 2026 前瞻

### 可能的演进

- **Iceberg 协议成熟 + 跨厂商统一** → 数据真 portable
- **Databricks / Snowflake 收敛**：功能越来越像
- **AI Infra（向量 + LLM）** 继续融入 Lakehouse
- **国产化替代**：字节 / 阿里 / 华为继续推开源

### 对中国团队的启示

- **关注开源协议的演进**（Iceberg / Paimon / Lance）
- **别迷信某厂商的"全家桶"**
- **Iceberg + Paimon 混合** 是 2024-2025 最稳妥的湖仓选型
- **向量库选开源为主**（Milvus / LanceDB），避免 Pinecone 这类绑定

## 6. 现实检视 · 这一页的局限

- **厂商信息快速过期**：每季度都有重大变化
- **中立性挑战**：**本页不构成投资 / 采购建议**
- **量化数据缺**：市场份额 / 收入数据散落各处，不准确
- **重要决策**：以官方文档 + 自家 POC 为准，不以此页为最终依据

## 7. 延伸阅读 · 跟踪资源

- **[a16z Data Infrastructure Landscape](https://future.com/emerging-architectures-for-modern-data-infrastructure/)**
- **[*The Modern Data Stack Handbook*](https://www.moderndatastack.xyz/)**
- **[Gartner Magic Quadrant for Data Management](https://www.gartner.com/)**（付费但有公开摘要）
- **[Forrester Wave Reports](https://go.forrester.com/)**
- **[CB Insights 数据栈追踪](https://www.cbinsights.com/)**
- 主要厂商官方博客：Databricks · Snowflake · BigQuery · Pinecone · Starburst · Confluent

## 相关

- [TCO 模型](../ops/tco-model.md) —— 具体成本分析
- [三代数据系统演进史](../foundations/data-systems-evolution.md) · [Modern Data Stack](../foundations/modern-data-stack.md)
- [业务场景全景](../scenarios/business-scenarios.md) · [横向对比](../compare/index.md)
