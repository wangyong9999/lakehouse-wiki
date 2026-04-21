---
title: Data Quality for ML · Data Contract · Quality Gates · Label Quality
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: Great Expectations 0.18+ · Soda 3.x · Monte Carlo · Anomalo · Elementary · dbt tests · Data Contracts OSS · 2024-2026 实践
prerequisites: [mlops-lifecycle, feature-store]
tags: [ml-infra, data-quality, data-contract, label-quality, observability]
aliases: [数据质量, Data Contract, Label Quality, 数据契约]
related: [mlops-lifecycle, feature-store, model-monitoring, ml-evaluation, data-governance, lake-table, schema-evolution]
systems: [great-expectations, soda, monte-carlo, anomalo, elementary, dbt, data-contracts]
status: stable
---

# Data Quality for ML

!!! tip "一句话定位"
    **ML 事故的头部来源是数据问题**——训练集不干净 · label 不可信 · 上游 schema 悄悄变 · 评估集泄漏 · 标注口径不一致。本页把**数据契约 · 数据质量闸门 · Label 质量 · 泄漏防御**统一成一个一等主题 · 不再散落在 lifecycle / feature-store / fine-tuning 各处。

!!! warning "边界声明"
    - **本页**：**面向 ML 场景的数据和 label 质量**（训练集 / 评估集 / 特征 / label）
    - **[data-governance](../ops/data-governance.md)**：通用数据治理（合规 · 目录 · 分类 · 血缘 · GDPR 管辖）—— 组织制度层
    - **[feature-store §Drift](feature-store.md)**：特征**在线 vs 离线**对账（分布对齐）· 本页提到但不深讲
    - **[model-monitoring](model-monitoring.md) §Label Quality**：**上线后**的 label 质量监控 —— 本页讲**上线前 + 训练期**
    - 三者合起来 = ML 数据质量全景

!!! abstract "TL;DR"
    - **Data Contract** 是上下游契约：schema + 完整性 + 时延 + owner · 违约是**阻断性事件**
    - **Data Quality Gates** 是自动化闸门：训练/推理前置 GE/Soda/dbt test · 不通过不上车
    - **Label Quality** 独立话题：delayed label · implicit label drift · 标注员一致性 · bot 污染
    - **评估集泄漏防御**：time split · source split · near-dedup hard check
    - **Schema Evolution 和 ML** 专门视角：加列 / 改类型 / 弃用列对训练作业的冲击
    - 工具栈 2026：**Great Expectations** · **Soda** · **Monte Carlo** · **Anomalo** · **Elementary** · **dbt tests**

## 1. 为什么独立一页

典型 ML 团队的真实事故分布（粗估）：
- 上游数据源 schema 变 → 训练 pipe 静默失败 / 特征计算错
- Label 来源的 proxy 语义悄悄变（"停留时长"被 clickbait 优化绑架）
- 训练集和评估集 near-dedup 没做 → 离线 AUC 乐观
- 标注员口径飘（外包团队换人）· Kappa 值骤降
- Bot / 作弊流量污染 label
- **以上问题大多在"数据进入训练作业之前"就发生** · 但没有统一守门

把这一主题**独立**能让它成为：
- **CI 的强守门**（和单测等价）
- **Platform 团队的工程资产**（共享 test suite）
- **合规审计的证据链**（EU AI Act 训练数据描述）

## 2. Data Contract · 上下游契约

**Data Contract = 数据生产者对消费者的 SLO**。

### 2.1 最小契约 schema

```yaml
# contracts/events.user_click.yaml
contract:
  name: events.user_click
  version: v3
  owner: data-platform@corp
  
  schema:
    user_id:        {type: BIGINT, nullable: false}
    item_id:        {type: BIGINT, nullable: false}
    event_ts:       {type: TIMESTAMP, nullable: false, timezone: UTC}
    dwell_ms:      {type: INT, nullable: true, min: 0, max: 3600000}
    is_bot:        {type: BOOLEAN, nullable: false, default: false}
  
  quality:
    freshness:     {sla: 15min, alert_after: 30min}
    completeness:  {null_rate_max: 0.01}
    uniqueness:    {primary_key: [user_id, item_id, event_ts]}
    volume:        {expected_daily_rows: "1M ± 30%"}
  
  semantic:
    dwell_ms: "用户在 item 详情页停留时长 · 不含 prerender · 跨 session 不累计"
    is_bot:   "Anti-cheat 团队实时打标 · 每日一次回填历史修正"
  
  breaking_change_policy:
    - major: 删列 / 改 type / 改语义 · 需提前 30 天通知
    - minor: 加列 · 不 block 下游
    - 通知渠道: #data-contracts Slack channel
  
  downstream_consumers:
    - recsys_feature_store
    - fraud_model_training
    - ctr_model_training
```

### 2.2 工具与落地

| 工具 | 定位 |
|---|---|
| **Data Contracts OSS**（如 `datacontract-cli`）| YAML schema + 自动化检测 |
| **dbt contracts**（dbt 1.6+）| 模型层契约 · CI 集成 |
| **Apache Iceberg Schema + Required fields** | 湖表原生约束 |
| **Protobuf / Avro schema registry** | 流式数据契约 |

### 2.3 为什么要专门强调

- ML 训练作业**依赖上游稳定性**的程度远高于 BI 报表
- BI 报表错一天影响小 · 训练集错一天**污染模型权重 · 要重训才能救**
- Data Contract 把"口头约定"变成"自动化检测 + 违约机制"

## 3. Data Quality Gates · 自动化闸门

### 3.1 三层闸门

```
上游源 → [闸门 A · Contract 校验] → 湖表 → [闸门 B · ML 专属 Quality] → 训练集/特征 → [闸门 C · 训练前置] → 训练
```

### 闸门 A · Contract 校验

- Schema 匹配 · 类型 · nullable · required
- 完整性（null_rate / 唯一性）
- Freshness（到达时间 SLA）
- 工具：dbt tests · 入湖作业里

### 闸门 B · ML 专属 Quality

ML 关心的东西**不止 schema 对**：
- **分布稳定性**：每个特征 PSI / KS vs baseline（历史均值）
- **取值范围**：超出训练 min/max 告警（超出可能是数据 bug）
- **特征间关系**：例如 `purchase_amount > 0` 时 `is_paid must be true`（业务规则）
- **时间覆盖**：事件时间戳分布是否有断层（某天数据丢失）
- **PII 扫描**：有无不该出现的敏感字段

工具：**Great Expectations** · **Soda** · **Anomalo**（自动异常检测）

```python
# Great Expectations 典型 expectation suite for ML
import great_expectations as ge

df = ge.from_pandas(training_df)

df.expect_column_values_to_not_be_null("user_id")
df.expect_column_values_to_be_between("dwell_ms", min_value=0, max_value=3_600_000)
df.expect_column_values_to_match_regex("email", r"^[^@]+@[^@]+\.[^@]+$", mostly=0.99)
df.expect_column_pair_values_A_to_be_greater_than_B("purchase_amount", "discount_amount")
df.expect_column_kl_divergence_to_be_less_than(
    "avg_7d_gmv",
    partition_object=baseline_partition,
    threshold=0.1,
)

result = df.validate()
if not result.success:
    raise DataQualityError(result)
```

### 闸门 C · 训练前置

- **评估集泄漏 hard check**（§5）
- **类别平衡** · 类别分布未突变
- **label 分布** · positive rate 未突变
- **特征完整性** · 高缺失率的新特征告警

## 4. Label Quality · 独立关键话题

### 4.1 Label 的 4 种来源 · 各有坑

| 来源 | 例子 | 典型问题 |
|---|---|---|
| **Implicit label**（用户行为隐含）| 点击 = 正样本 · 停留长 = 正样本 | Bot 污染 · proxy 语义漂移 · **Clickbait 优化风险** |
| **Explicit feedback** | 用户评分 · 赞 / 踩 | 样本稀疏 · 选择性偏差 · 五星集中 |
| **Delayed label**（结果滞后）| 转化 · 贷款违约 · 医疗预后 | **时间跨度长**（天-年）· 训练时 label 未知 |
| **Annotated label**（人工标注）| 图像分类 · NLP 标注 · 客服回答评级 | **标注员一致性**（Kappa）· 外包换人导致飘 · 口径漂移 |

### 4.2 Bot / 作弊污染

- CTR 模型训练集有 bot 流量 → 学到 "bot 喜欢什么" 而非 "真实用户"
- 解法：
  - Anti-cheat 团队打 `is_bot` 标签 · 训练时过滤
  - 异常检测清洗（点击速率 / 时序模式）
  - 白名单用户池（高质量 label 源）

### 4.3 Delayed Label 的工程挑战

- **训练 label 的"可用窗口"**：CTR 分钟级 · 转化小时级 · 留存周级 · 违约月-年级
- **训练节奏**适配 label 延迟：越慢的 label · 越长的 label horizon · 更少的重训频率
- **中间 proxy label**：用早期可观察的信号替代（点击 → 加购 → 下单）
- **right-censored data**：未到期的样本不能简单当 "negative"

### 4.4 Annotated Label 质量指标

| 指标 | 意义 | 工程动作 |
|---|---|---|
| **Cohen's Kappa**（两标注员）| 一致性 · > 0.7 可接受 | 双标 + 审核 |
| **Fleiss' Kappa**（多标注员）| 扩展 Kappa | 多数投票 |
| **Krippendorff's alpha** | 允许缺失 · 更灵活 | 大规模抽样 |
| **争议率** | 两人不一致的比例 | 送 senior 裁决 |
| **Guideline drift** | 时间维度一致性 | 定期复标历史样本 |

### 4.5 Weak Supervision / Active Learning

- **Weak supervision**（Snorkel）：多个启发式规则 + 合并为概率 label
- **Programmatic labeling**：LLM / 规则预标 · 人工抽检
- **Active learning**：模型不确定的样本优先送标注
- **Self-training / Pseudo-labeling**：模型高置信预测回作 label · 注意放大偏差

（详细方法见 [fine-tuning-data §5.5 合成数据](fine-tuning-data.md)）

## 5. 评估集泄漏防御 · 三道防线

**离线 AUC 乐观 · 上线崩溃**的典型根因是评估集泄漏。

### 5.1 防线 1 · Time Split

```
2024-Q1 ~ 2025-Q4 → 训练集
2026-Q1           → 评估集
```

**注意**：
- 事件时间（event_ts）切 · 不是 ingest 时间
- **窗口特征**（7d GMV）算的时候不能跨 split · PIT Join 严格
- 季节性必须覆盖（春节 / 双 11 / 黑五）

### 5.2 防线 2 · Source Split

```
某类对话（客服 tier-2 转接）→ 只进评估集
客服 tier-1 对话             → 训练集
```

好处：模型在新来源上 generalization 能真正被测到。

### 5.3 防线 3 · Near-dedup Hard Check

评估集每一条 · 在训练集里**无语义相似匹配**：

```python
from datasketch import MinHashLSH

lsh = MinHashLSH(threshold=0.85, num_perm=128)
for i, doc in enumerate(train_docs):
    lsh.insert(f"train_{i}", minhash(doc))

leaked = []
for i, doc in enumerate(eval_docs):
    matches = lsh.query(minhash(doc))
    if matches:
        leaked.append((i, matches))

assert len(leaked) == 0, f"评估集 {len(leaked)} 条泄漏到训练集"
```

**三道防线缺一不可**。只做 time split 还会有"同一用户的数据跨到两边"的泄漏（leaking by identity）。

## 6. Schema Evolution 对 ML 的影响

湖表 Schema Evolution 是常态（见 [schema-evolution](../lakehouse/schema-evolution.md)）· 但对 ML 比 BI 更敏感：

| 变更 | BI 影响 | ML 影响 |
|---|---|---|
| **加列** | 新列数据开始产生 · 历史 null | 训练时长期 null 是常态 · 但 serving 时若列缺失 → 特征工程失败 |
| **改列类型**（INT → BIGINT）| 多数兼容 | dtype 检查严格的模型（Feast）会炸 |
| **改列语义**（`amount` 从分变成元）| 报表数字变 · 易发现 | 特征值突变 · 模型静默退化 · 最难发现 |
| **弃用列** | 改 SQL | 所有用该列的特征定义 / 模型需重训 |
| **加非空约束** | 旧数据可能违约 | 训练管道崩 |

**防御**：
- Data Contract 里列 **breaking change policy**（§2.1）
- 上游改语义必须**加新列**（`amount_cents`）· 不改旧列
- Schema registry 自动扫描影响的 ML artifact（Feature Store 定义 / 训练 pipeline）
- 兼容性测试：新 schema 下重跑训练 CI

## 7. 工具栈对比 · 2026

| 工具 | 类型 | 定位 | 适合 |
|---|---|---|---|
| **Great Expectations** | OSS · Python | Expectation suite · 灵活 | 通用 · 团队大 |
| **Soda**（Core + Cloud）| OSS + 商业 | SodaCL DSL · 简洁 | dbt-like team |
| **Monte Carlo**（"Data Observability" 代表）| 商业 · 全托管 | 异常检测 · 血缘冲击分析 | 企业客户 |
| **Anomalo** | 商业 | 自动异常检测 · 少配置 | 大规模表 |
| **Elementary**（dbt 生态）| OSS | dbt-native observability | dbt 重用户 |
| **dbt tests / contracts** | OSS | 模型层 unit tests + schema 契约 | dbt 核心团队 |
| **Databricks Lakehouse Monitoring** | 平台托管 | UC 集成 · drift + data quality | Databricks 用户 |
| **Datafold** | 商业 | Data diff / regression · CI 集成 | PR diff ML 数据 |

**默认推荐**：
- 开源 / 技术团队：**Great Expectations** 或 **Soda Core**
- dbt 重用户：**dbt tests + Elementary**
- 大规模企业：**Monte Carlo** / **Anomalo** / **Datafold**

## 8. 和其他章节的协同

```
Data Contract（本页 §2）
    ↓
闸门 A 入湖校验（本页 §3）
    ↓
Iceberg / Paimon 表（lakehouse 章 · Schema Evolution）
    ↓
Feature Store 定义（feature-store.md）
    ↓
闸门 B ML 专属 Quality（本页 §3）
    ↓
训练作业启动（training-orchestration）
    ↓
闸门 C 训练前置 + 评估集泄漏（本页 §5）
    ↓
Experiment Tracking 记录 dataset snapshot（experiment-tracking.md）
    ↓
ML Evaluation 离线评估（ml-evaluation.md）
    ↓
上线 → Model Monitoring 持续监测 label / drift（model-monitoring.md）
```

**Data Quality 是整条管线的守门员**。

## 9. 实务建议 · 成熟度路径

### Level 0 · 事后救火
- 业务投诉 · 排查发现数据问题 · 手工修 · 重训
- **90% 团队起点**（说法粗估 `[来源未验证]`）

### Level 1 · 人工守门
- 数据工程师每周 review 关键表
- dbt tests 跑 · 出错看邮件

### Level 2 · 自动化闸门
- GE / Soda 集成 pipeline · 失败自动停
- Data Contract 版本化 · breaking change 走审批
- 评估集泄漏 hard check 进 CI

### Level 3 · 平台化 + observability
- Monte Carlo / Anomalo 自动异常检测
- 血缘分析 · 哪些模型受冲击
- Label quality 持续监控（model-monitoring 对接）
- 业务 KPI 失败自动回溯到数据源

**务实**：大多数团队 L1 → L2 过渡 · 直接 L3 代价高。

## 10. 陷阱 · 反模式

- **没有 Data Contract**：上游说变就变 · 下游全崩
- **Quality Gates 只在 pipeline 末端**：训练完才发现 · 浪费算力
- **只测 schema 不测 value 分布**：shape 对 · 语义漂移看不见
- **评估集泄漏没 hard check**：AUC 乐观 · 上线崩
- **Label 延迟不明确**：训练节奏错位
- **外包标注不监控 Kappa**：换人后质量悄悄降
- **Bot / 作弊流量进训练集**：模型学错目标
- **Schema Evolution 不联动 ML 端**：特征定义静默失效
- **PII 扫描漏过**：训练集带 PII · GDPR 事故
- **数据契约只口头**：出问题无违约责任
- **把 `data-quality` 当 "DQA" 工具**：实际是全流程工程纪律 · 不是一个脚本
- **`Level 3 全自动化` 当 day 1 目标**：投入 >> ROI · 先 L1-L2

## 11. 相关

- [MLOps 生命周期](mlops-lifecycle.md) §1 数据 —— 本页是深化
- [Feature Store](feature-store.md) —— 特征契约 + drift 监控
- [ML Evaluation](ml-evaluation.md) §评估集泄漏 —— 和本页 §5 互相引用
- [Model Monitoring](model-monitoring.md) §Label Quality —— 上线后监测
- [Schema Evolution](../lakehouse/schema-evolution.md) —— 湖表层机制
- [Time Travel](../lakehouse/time-travel.md) —— 数据 snapshot 基础
- [LLM Fine-tuning](fine-tuning-data.md) §5 数据流水线 —— LLM 场景
- [数据治理](../ops/data-governance.md) —— 制度 / 合规层

## 12. 延伸阅读

- Great Expectations: <https://greatexpectations.io/>
- Soda: <https://docs.soda.io/>
- Monte Carlo: <https://www.montecarlodata.com/>
- Data Contracts OSS: <https://datacontract.com/>
- *Data Quality Fundamentals*（Moses et al., O'Reilly）
- *Designing Data-Intensive Applications*（Kleppmann）—— Schema Evolution 深度
- *Snorkel: Rapid Training Data Creation with Weak Supervision*（Ratner et al., VLDB 2017）
- *Foundations of Reliable Data Engineering* · dbt Contracts docs
