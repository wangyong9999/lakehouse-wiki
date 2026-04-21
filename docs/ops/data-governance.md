---
title: 数据治理 · 血缘 · 契约 · 合规
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-21
applies_to: OpenLineage 1.x · DataHub 0.14+ · Unity Catalog · Data Contracts 规范 · 2024-2026 实践
tags: [ops, governance, lineage, contract]
aliases: [Data Governance, 血缘, 数据契约]
related: [security-permissions, observability, catalog-strategy, data-quality-for-ml]
systems: [datahub, openlineage, unity-catalog]
status: stable
---

!!! warning "章节分工声明（S34 重要）"
    - **本页**：湖仓通用治理——**血缘 · Data Contract · 合规标签 · Catalog 治理平面集成**
    - **ML 数据质量**（PIT · Label Quality · Evaluation 集泄漏 · GE/Soda ML 用法 · Data Quality Gates）→ [ml-infra/data-quality-for-ml](../ml-infra/data-quality-for-ml.md) **canonical**
    - **Catalog 治理平面机制**（UC / Polaris / Gravitino）→ [catalog/strategy](../catalog/strategy.md) canonical
    - **合规法规**（GDPR / EU AI Act 等）→ [compliance](compliance.md)
    - **观测集成** → [observability](observability.md) §专用面 Data Quality Observability
    - 本页瘦身后关注**治理工程视角**（血缘 / 契约 / 合规标签）· 不讲 ML 数据质量工程细节

# 数据治理

!!! tip "一句话理解"
    数据治理不是"合规部门的事"。在湖仓一体化时代，它是**工程基础能力**：**血缘（谁生出了谁）+ 质量（能信多少）+ 契约（跨团队承诺）+ 合规（能不能留）**。

## 四件主线

### 1. 血缘（Lineage）

"这个字段从哪来？"是每个 BI 分析师每周问的问题。血缘就是答案。

- **表级血缘**：`table_a → transform → table_b`
- **列级血缘**：`table_a.col_x → transform → table_b.col_y` （更精细，AI 场景尤其重要）
- **跨引擎血缘**：Spark / Flink / Trino / dbt 作业都要能吐血缘事件

工具链：

- **OpenLineage** —— 标准事件协议（引擎 → 治理系统）
- **DataHub** —— 收集与可视化，社区最活跃
- **Marquez** —— OpenLineage 的参考实现
- **Unity Catalog** —— 自带血缘

血缘的价值从"出事后溯源"放大到"**变更影响分析**"—— 改一张上游表，自动知道下游谁会爆。

### 2. 质量（Data Quality）

"这张表能信吗？" 数据质量体系三要素：

- **期望（Expectation）** —— `order_amount >= 0`、`not null customer_id`
- **校验（Validation）** —— 定期或事件触发跑校验
- **可见（Visibility）** —— 结果写回 Catalog，BI 用户查表能看到"质量评分"

!!! info "数据质量工程深度在 [ml-infra/data-quality-for-ml](../ml-infra/data-quality-for-ml.md)"
    S27 建立了 data-quality-for-ml 作 ML 数据质量 canonical（三层 Quality Gates · Label Quality · 评估集泄漏 · Schema Evolution 对 ML 的影响 · 工具矩阵 GE / Soda / Monte Carlo / Anomalo / Elementary · 成熟度 L0-L3）· **本页不重复机制细节**。

工具链（精简 · 指向 canonical 深度）：
- **Great Expectations / Soda / dbt tests** · OSS 数据质量框架
- **Elementary**（dbt-native · 2024 活跃）· **Monte Carlo / Anomalo**（企业自动异常检测）
- **Iceberg / Paimon Stats Plugin** · 自带列直方图

质量门禁是治理第一道防线。具体的 Data Contract + Quality Gates 工程实施 · 去 data-quality-for-ml canonical。

### 3. 契约（Data Contract）

跨团队协作时，数据提供方和消费方的**"正式承诺"**：

```yaml
contract:
  table: orders_dwd
  owner: data-platform-team
  sla:
    freshness: "< 1h"
    availability: "99.5%"
  schema:
    - name: order_id
      type: bigint
      nullable: false
    - name: amount
      type: decimal(18,2)
      pii: false
  quality:
    - expect: "amount >= 0"
    - expect: "order_id is unique"
```

破坏契约 = 通知消费方，不是"悄悄加列删列"。dbt / Sodas / Great Expectations 都有 contract 能力。

### 4. 合规 / 数据保护

- **PII 识别与分级**：sensitivity tag → 权限策略自动生效
- **保留策略**：哪些数据保留多久、过期自动删除
- **跨境合规**：数据驻留区
- **删除权（GDPR）**：跨所有系统删干净

## 和一体化湖仓的耦合

一体化时代治理的**三个新维度**：

1. **向量 / 模型也要血缘** —— `doc_chunks → embed() → doc_vectors → model_v3`
2. **RAG 输出要可溯源** —— LLM 回答引用到具体 chunk，chunk 归属到具体源表
3. **模型版本与数据版本绑定** —— 模型训练的时候用了哪个 snapshot

没有治理平面，这些都说不清。**Catalog = 治理平面**这句话就是这个意思。

## 落地顺序

不要一上来搞"完美治理"。按价值顺序：

1. **Week 1**：owner + 基本 tag（pii 标注）
2. **Month 1**：质量门禁（关键表 5–10 条期望）
3. **Month 3**：血缘（OpenLineage 事件打通）
4. **Quarter 1**：契约化最关键 3–5 张表
5. **Year 1**：跨系统治理平面（DataHub / Unity）

## 陷阱

- **把治理等同于审计** —— 审计是合规视角；治理是工程视角
- **工具选太多** —— DataHub + Ranger + Marquez + 自研…互相对不上
- **治理平面没有用户** —— BI 用户不用 = 没价值；要把它嵌到 BI 工具里
- **契约流于形式** —— 没有 CI 卡 schema 变更 = 契约白写

## 最小有用治理平面

对中等规模团队：

- [ ] Catalog 里每张表有 owner + business description
- [ ] PII 列打 tag，对应 Mask 策略
- [ ] 关键表（Top 20）有 3–5 条质量规则
- [ ] OpenLineage 事件从 Spark / Flink / Airflow 出来
- [ ] 每季度 stale / orphan review
- [ ] 敏感数据删除流程 SOP

## 相关

- [可观测性](observability.md) —— 治理的邻居
- [安全与权限](security-permissions.md)
- [统一 Catalog 策略](../catalog/strategy.md)
- [Unity Catalog](../catalog/unity-catalog.md)

## 延伸阅读

- *OpenLineage Specification*: <https://openlineage.io/>
- DataHub docs: <https://datahubproject.io/docs/>
- *Data Contracts* —— Andrew Jones 的书与博客系列
- *Great Expectations* docs
