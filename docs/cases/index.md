---
title: 工业案例 · 数据平台参考
description: 7 家工业数据平台深度案例 · Databricks / Snowflake / Netflix / LinkedIn / Uber / Pinterest / 阿里巴巴 · 统一 12 节坐标系深度拆解
applies_to: 2024-2026 各家公开资料 · 具体技术栈版本见各深度页 applies_to
last_reviewed: 2026-04-21
---

# 工业案例 · 数据平台参考

!!! tip "一句话定位"
    **世界级数据平台公开资料的深度拆解归档**。**7 家深度案例**按统一 12 节坐标系（历史 · 架构 · 组件 · 演进 · 规模 · 取舍 · 失败 · 启示）整理 · 供资深工程师做**架构决策 / 方案评审 / 技术选型**时参考。

!!! warning "本章定位 · reference 性质"
    - **本章**：**工业案例参考**（reference）· 讲"**别人怎么做 · 规模多大 · 取舍为何 · 失败在哪**"
    - **不讲机制原理**：机制去对应技术栈章（[lakehouse/](../lakehouse/index.md) / [retrieval/](../retrieval/index.md) / [catalog/](../catalog/index.md) / [query-engines/](../query-engines/index.md) / [ai-workloads/](../ai-workloads/index.md) / [ml-infra/](../ml-infra/index.md)）
    - **架构模式 / 战略主张**：去 [unified/](../unified/index.md) · 本章**不做战略判断**
    - **业务场景端到端**：去 [scenarios/](../scenarios/index.md) · 讲具体业务
    - **厂商选型商业视角**：去 [Vendor Landscape](../vendor-landscape.md)
    
    **用法**：做架构设计 / 选型评审 / 方案论证时翻一翻 · 知道"业界是怎么做的 · 为什么这么做 · 哪里踩过坑"。

!!! danger "读前必读 · 样本类型分层（S32 重要修复）"
    **cases/ 的 7 家案例不是同一层级对象** · 读横比结论前必须理解：
    
    | 类型 | 案例 | 公开资料性质 | 横比适用度 |
    |---|---|---|---|
    | **商业产品平台** | Databricks · Snowflake | 产品文档 + marketing + keynote | 作**产品能力对比**合适 · 作"内部规模"不可比 |
    | **大厂内部数据平台** | Netflix · LinkedIn · Uber · 阿里巴巴 | 工程技术博客 + 论文 + 开源项目 | 作**工程经验对比**合适 · 作"客户规模"不可比 |
    | **业务系统案例** | Pinterest（PinSage / Pixie 推荐系统）| 论文 + Engineering Blog | **不是数据平台全景** · 是特定业务系统（推荐）的工业代表 |
    
    **跨类型横比有天然失真风险**（如"Databricks 客户 10000+" vs "Netflix 内部 Iceberg 表 10 万+"不是同一维度）。本章 [studies.md](studies.md) 的横比矩阵**按类型分组** · 请配合类型声明阅读。

!!! note "事实 / 推断 / 推测三层分层（S32 新规范）"
    reference 章严格区分：
    
    - **客观事实**（来自公开博客 / 论文 / 发布公告）· 正文默认性质
    - **作者合理推断**（基于事实的架构判断）· 用 `!!! info` 标注
    - **未来推测**（未经官方确认的趋势判断）· 集中在 §6 关键演进的独立子节 · 不混入事实节
    
    各深度页已按此规范修订（S32）。

!!! info "本章**有时效性** · 按 ADR 0007 SOP 定期复检"
    工业案例的技术栈变化快（一年一个新动向）。**本章所有深度页 `last_reviewed: 2026-04-21`** · 下次计划在 2026-Q3 复检。读者使用时应**交叉验证各公司最新博客 / 发布**（见 §9 延伸阅读）。

## 1. 7 家深度案例 · 按样本类型分组（和 §S32 admonition 一致）

!!! info "分类轴 · 样本类型分层"
    案例按**样本类型**分三类（和本页上方"样本类型分层"admonition · studies.md §1-2 矩阵对齐）。**不按业务领域 / 开源性质 / 地域混分类** —— 保证 MECE · 避免读者误导。

### 1.1 商业产品平台

**公开资料 = 产品文档 + marketing + keynote · 作产品能力对比合适 · 作'内部规模'不可比**。

- [**Databricks**](databricks.md) ⭐ —— Delta + **Unity Catalog**（多模资产最全）+ MosaicML 整合 + Vector Search + AI Functions · **2026 工业一体化平台代表**
- [**Snowflake**](snowflake.md) ⭐ —— **Cortex**（SQL LLM UDF 工业先驱 · 2024 GA）+ Polaris（2026-02 Apache TLP）+ Iceberg 原生支持 · 云数仓 AI 内嵌代表

### 1.2 大厂内部数据平台

**公开资料 = 工程技术博客 + 论文 + 开源项目 · 作工程经验对比合适 · 作'客户规模'不可比**。

- [**Netflix**](netflix.md) ⭐ —— **Iceberg 诞生地**（2017 Ryan Blue）· Metacat / Genie / Maestro / Metaflow 全开源 · 工程方法论最深远
- [**LinkedIn**](linkedin.md) ⭐ —— **Kafka / Pinot / Venice / DataHub 全家桶** · **2024 OpenHouse 开源** + **Feathr 捐 Apache** · 单品开源 + 商业化培育典范
- [**Uber**](uber.md) ⭐ —— **Hudi 诞生地** + **Michelangelo MLOps 鼻祖**（2017 博客）· 实时 + ML 驱动巨无霸
- [**阿里巴巴**](alibaba.md) ⭐ —— **Apache Paimon 诞生地**（2022）+ **Celeborn** + **Fluss** · Flink 最大贡献方 · Hologres HSAP · 中国工业实践直接借鉴

### 1.3 业务系统案例

**公开资料 = 论文 + Engineering Blog · 不是数据平台全景 · 是特定业务系统（推荐）的工业代表**。

- [**Pinterest**](pinterest.md) —— **PinSage GNN**（SIGKDD 2018）+ **Pixie random walk**（SIGMOD 2018）+ Homefeed · 多模推荐最成熟案例

### 1.4 综述横比

- [**7 家横比矩阵**](studies.md) —— 8 维坐标系统一对比（表格式 · Catalog · 向量 · ML · SQL LLM UDF 等维度）+ 按场景找案例反向索引

## 2. 统一 12 节案例模板

每家深度案例按以下 12 节组织（这是 S31 系统重构的成果）：

| 节 | 内容 | 资深读者价值点 |
|---|---|---|
| 1 | 性质声明 + TL;DR | 快速判断是否继续读 |
| 2 | 为什么这个案例值得学 | 明确阅读收益 |
| 3 | 历史背景 · 关键转折 | 理解选型动机 |
| 4 | 核心架构（Mermaid）| 全景视图 |
| 5 | 8 维坐标系表 | 跨案例可比 |
| 6 | 关键技术组件深度（3-5 个）| 选关键不罗列 |
| 7 | 2024-2026 关键演进 | 时效性 |
| 8 | 规模数字（带来源标签）| 量级感 |
| 9 | **★ 深度技术取舍**（为什么选 X 不选 Y）| **资深读者核心价值** |
| 10 | **真实失败 / 踩坑 / 教训** | **工业案例最稀缺信号** |
| 11 | 对团队的启示（标观点 warning）| 主张分层 |
| 12 | 技术博客 / 论文 + 相关章节 | 延伸入口 |

## 3. cases/ 和 scenarios/ 的配对关系（S33 重要）

!!! success "本章 = 全栈企业视角 · scenarios/ = 业务场景切面视角 · 两者配对阅读"
    2026-Q2 S33 建立 **场景-案例强配对**：
    
    | 视角 | 章 | 定位 |
    |---|---|---|
    | **全栈企业视角** | 本章 cases/ | "这家公司做数据平台的全栈 · 历史 · 取舍 · 失败 · 启示" |
    | **业务场景切面** | [scenarios/](../scenarios/index.md) | "在 X 业务场景下 · 这家公司怎么做的 · 关键数字 · 踩坑 · 和本 wiki 推荐路径对比" |
    
    **每家案例在哪些 scenarios 有切面分析**：
    - [Netflix](netflix.md) → [bi-on-lake](../scenarios/bi-on-lake.md) · [offline-training-pipeline](../scenarios/offline-training-pipeline.md)
    - [LinkedIn](linkedin.md) → [recommender-systems](../scenarios/recommender-systems.md) · [feature-serving](../scenarios/feature-serving.md) · [fraud-detection](../scenarios/fraud-detection.md) · [cdp-segmentation](../scenarios/cdp-segmentation.md)
    - [Uber](uber.md) → [fraud-detection](../scenarios/fraud-detection.md) · [offline-training-pipeline](../scenarios/offline-training-pipeline.md) · [feature-serving](../scenarios/feature-serving.md) · [real-time-lakehouse](../scenarios/real-time-lakehouse.md)
    - [Pinterest](pinterest.md) → [recommender-systems](../scenarios/recommender-systems.md) · [multimodal-search-pipeline](../scenarios/multimodal-search-pipeline.md)
    - [阿里巴巴](alibaba.md) → [cdp-segmentation](../scenarios/cdp-segmentation.md) · [real-time-lakehouse](../scenarios/real-time-lakehouse.md) · [recommender-systems](../scenarios/recommender-systems.md) · [multimodal-search-pipeline](../scenarios/multimodal-search-pipeline.md)
    - [Databricks](databricks.md) → [bi-on-lake](../scenarios/bi-on-lake.md) · [rag-on-lake](../scenarios/rag-on-lake.md) · [agentic-workflows](../scenarios/agentic-workflows.md) · [text-to-sql-platform](../scenarios/text-to-sql-platform.md) · [multimodal-search-pipeline](../scenarios/multimodal-search-pipeline.md)
    - [Snowflake](snowflake.md) → [bi-on-lake](../scenarios/bi-on-lake.md) · [rag-on-lake](../scenarios/rag-on-lake.md) · [agentic-workflows](../scenarios/agentic-workflows.md) · [text-to-sql-platform](../scenarios/text-to-sql-platform.md)
    
    **反向索引**（从场景找哪家案例）· 见 [studies.md §6](studies.md)。

## 4. 按问题找案例 · 反向索引

**"做 X 该学谁"**（详见 [studies.md §5](studies.md)）：

| 问题 | 首选案例 | 备选 |
|---|---|---|
| 做 **ML 平台** | [Uber · Michelangelo](uber.md)（鼻祖 · 7 年演进）| [Databricks](databricks.md) · [Netflix · Metaflow](netflix.md) |
| 做 **多模推荐** | [Pinterest](pinterest.md)（PinSage 论文级）| [LinkedIn](linkedin.md) · [阿里](alibaba.md) |
| 做 **Catalog / 治理平面** | [Databricks · UC](databricks.md)（最全）| [Snowflake · Polaris](snowflake.md) · [Netflix · Metacat](netflix.md) |
| 做 **流式湖仓** | [阿里巴巴 · Paimon](alibaba.md)（最现代）| [Uber · Hudi](uber.md)（第一代） |
| 做 **实时 OLAP** | [LinkedIn · Pinot](linkedin.md)（工业标杆）| [Uber](uber.md) · [阿里 · Hologres](alibaba.md) |
| 做 **SQL LLM UDF** | [Snowflake · Cortex](snowflake.md)（工业先驱 · 2024 GA）| [Databricks · AI Functions](databricks.md) |
| 做 **Feature Store** | [Uber · Palette/Genoa](uber.md)（鼻祖）| [LinkedIn · Feathr ASF](linkedin.md) |
| 学 **BI + AI 一体化商业化** | [Databricks](databricks.md) | [Snowflake](snowflake.md) |
| 学 **开源策略** | [LinkedIn](linkedin.md)（单品专精 + 商业化）| [Netflix](netflix.md) · [阿里巴巴](alibaba.md) |
| 学 **大规模 Iceberg 运维** | [Netflix](netflix.md)（10 万+ 表）| [LinkedIn · OpenHouse](linkedin.md) |
| 学 **中国工业实践** | [阿里巴巴](alibaba.md) | （后续加字节 / 腾讯 / 美团）|

## 5. 和 vendor-landscape 的分工

| | **本章 cases/** | **[Vendor Landscape](../vendor-landscape.md)** |
|---|---|---|
| **视角** | **案例事实**（历史 · 规模 · 取舍 · 教训）| **厂商选型**（商业产品横比 · 定价 · 生态） |
| **性质** | reference 拆解 | compare + 前沿观察 |
| **对象** | 具体公司的数据平台 | 商业产品和开源项目 |
| **时间** | 历史 + 当前 | 当前 + 未来展望 |

**两章可互为补充** · 不重叠。

## 6. 不同读者的阅读建议

### 6.1 架构师 / CTO（30-60 分钟快读）

1. 读本 index §1-3 了解 7 家 · 找最相关的 2-3 家
2. 对每家深度页 · 重点读：
   - §1 TL;DR + §5 8 维坐标系（量级感）
   - §9 深度技术取舍（资深价值）
   - §10 失败 / 教训（实战信号）
3. 读 [studies.md §3 关键维度对比](studies.md) 做跨案例综合判断

### 6.2 做技术选型的资深工程师（2-3 小时深度）

按"反向索引"（§4）找 2-3 家相关 · 每家完整读 12 节。重点对照：
- §6 关键组件（具体实现选择）
- §9 深度取舍（替代方案对比）
- §11 启示（主张分层 · 判断可借鉴性）

### 6.3 新接触 wiki 的工程师（1 小时全景）

先读 [studies.md](studies.md)（7 家横比矩阵）· 然后按兴趣挑 1 家深度页完整读。

### 6.4 研究生 / 论文读者（学术视角）

关注：
- **Netflix · Iceberg** 论文（CIDR 2020）
- **Databricks · Lakehouse** 论文（CIDR 2021）
- **Pinterest · PinSage** 论文（SIGKDD 2018 · GNN 推荐）· **Pixie** 论文（SIGMOD 2018 · 实时 random walk）
- **Uber · Michelangelo** 博客
- **Snowflake · Elastic DW** 论文（SIGMOD 2016）

## 7. 从 7 家案例抽出的共同规律（客观观察）

详见 [studies.md §4](studies.md)：

1. **Catalog 升级成治理平面** —— UC / Polaris / DataHub / OpenHouse 都往"多模资产 + 血缘 + 权限"走
2. **SQL 是长期 AI 入口** —— Cortex / AI Functions / BigQuery ML 先驱 SQL LLM UDF
3. **向量层从"独立"转"湖仓原生"** —— Databricks Vector Search / Snowflake Cortex / Hologres 向量
4. **表格式协议中立化** —— Iceberg REST 成事实标准 · 商业厂商"绑 primary + 开放 secondary"
5. **Embedding 是工程主语料** —— 不只"给 RAG 用"· 是检索 + 推荐 + 训练 + 缓存 + 去重通用基础设施
6. **闭源走向有限开放** —— 所有商业厂商"开放部分 + 锁定部分"
7. **单品开源 + 商业化**（LinkedIn 模式）成为主流路径

## 8. 观察要点 · 战略指向 unified/

!!! warning "以下观点简明 · 战略判断 canonical 在 [unified/index §5 团队路线主张](../unified/index.md)"
    本章 = reference · **不做战略主张**（S32 后规范）。以下仅列**从 7 家案例可以观察到的高价值信号** · 深度战略决策指向 [unified/](../unified/index.md) · [catalog/strategy](../catalog/strategy.md) · [compare/](../compare/index.md)。

- **Catalog 治理平面先行** · 具体选型见 [catalog/strategy](../catalog/strategy.md)
- **Iceberg + Puffin 组合**是 2024-2026 OSS 主线之一
- **Embedding 流水线**作基础设施（[ml-infra/embedding-pipelines](../ml-infra/embedding-pipelines.md) canonical）
- **SQL LLM UDF** 是新范式（[query-engines/compute-pushdown](../query-engines/compute-pushdown.md) canonical）
- **国内团队关注阿里 Paimon + Flink CDC** 组合（详见 [cases/alibaba](alibaba.md)）
- **规模打折** —— 不照搬 Netflix / Uber 全栈 · 按自己规模取舍
- **自研 ≠ 永恒** —— 定期评估 vs 社区方案 · 敢替换（LinkedIn Samza → Flink 教训）

## 9. 后续待补案例（下一轮）

!!! note "本章未完成度声明"
    本轮（S31）重构完成 7 家深度案例。**下一轮计划新增**：
    
    - **Meta**（Presto 诞生地 · FBLearner · PyTorch 原生 · RocksDB）
    - **Airbnb**（Minerva 语义层鼻祖 · dbt-like experimentation）
    - **Stripe** / **Shopify**（中型团队规模参考）
    - **字节跳动**（ByConity · Doris 背后 · 数据栈多元）
    - **Booking**（欧洲成熟 ML + BI 团队）
    
    读者有具体建议可反馈。

## 10. 延伸阅读 · 权威来源

### 各家官方技术博客（持续更新）

- [Databricks Engineering Blog](https://www.databricks.com/blog/engineering)
- [Snowflake Engineering Blog](https://www.snowflake.com/engineering-blog/)
- [Netflix Tech Blog](https://netflixtechblog.com/)
- [LinkedIn Engineering Blog](https://engineering.linkedin.com/)
- [Uber Engineering Blog](https://www.uber.com/blog/engineering/)
- [Pinterest Engineering Medium](https://medium.com/pinterest-engineering)
- [阿里云开发者博客](https://developer.aliyun.com/)

### 综述 / 分析

- *Designing Data-Intensive Applications*（Kleppmann · 数据系统设计必读）
- *The Composable Data Stack*（a16z · 数据栈演进视角）
- *Modern Data Stack* 分析（本 wiki [Modern Data Stack](../modern-data-stack.md)）
- 各家开源项目官方文档（Iceberg / Paimon / Hudi / Delta · Kafka / Pinot / Flink 等）

## 11. 章节相关

- [unified/](../unified/index.md) —— 跨章组合视角
- [Vendor Landscape](../vendor-landscape.md) —— 厂商选型商业视角
- [Modern Data Stack](../modern-data-stack.md) —— 现代数据栈全景
- [数据系统演进史](../data-systems-evolution.md) —— 三代数据系统演进史（Netflix / LinkedIn / Uber 在第三代）
- [compare/iceberg-vs-paimon-vs-hudi-vs-delta](../compare/iceberg-vs-paimon-vs-hudi-vs-delta.md) —— 表格式横比
- [catalog/strategy](../catalog/strategy.md) —— Catalog 选型决策（综合 7 家案例经验）
- [lakehouse/](../lakehouse/index.md) · [retrieval/](../retrieval/index.md) · [catalog/](../catalog/index.md) · [ml-infra/](../ml-infra/index.md) · [ai-workloads/](../ai-workloads/index.md) —— 机制 canonical
