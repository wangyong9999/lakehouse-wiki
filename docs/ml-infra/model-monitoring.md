---
title: Model Monitoring · Drift / Performance / Fairness / Auto-retrain
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: Evidently AI 0.4+ · Arize AX · Fiddler · WhyLabs · Grafana 自建 · NannyML · DeepChecks · 2024-2026 实践
prerequisites: [mlops-lifecycle, feature-store, model-serving]
tags: [ml-infra, monitoring, drift, fairness, auto-retrain]
aliases: [ML 监控, 模型监控, ML Observability]
related: [feature-store, model-serving, mlops-lifecycle, model-registry, llm-observability]
systems: [evidently, arize, fiddler, whylabs, nannyml, deepchecks, grafana]
status: stable
---

# Model Monitoring

!!! tip "一句话定位"
    **模型上线之后的眼睛**。三个问题必须持续回答：**输入分布变了吗（data drift）· 输入输出关系变了吗（concept drift）· 业务 KPI 是否在掉（performance drift）**。再加一道合规闸门：**不同人群之间表现是否公平（fairness drift）**。

!!! warning "和 LLM Observability 的分工"
    - **本页**：传统 ML 模型监控 —— 分类 / 回归 / 排序 / 推荐 / 风控 · 核心是**特征分布 + 预测分布 + 业务 KPI + fairness**
    - **[ai-workloads/llm-observability.md](../ai-workloads/llm-observability.md)**：LLM 应用 observability —— Trace / Cost / Latency / Prompt Version / Tool Trace · 核心是 OTel GenAI 规范 + Langfuse / LangSmith / Phoenix 等
    - 两者都存在 drift · 但观测对象（tabular feature vs prompt/token）和工具链（Evidently/Arize vs Langfuse）不同 · 大型平台通常两套并存

!!! abstract "TL;DR"
    - **三类 drift** 必须区分：Data drift（X 变）· Concept drift（P(y|X) 变）· Prediction drift（ŷ 分布变）· Fairness drift（subgroup 性能差距变）
    - **三层指标栈**：技术（latency · 错误率）· 模型（AUC / MAE / NDCG · PSI / KS · calibration）· 业务（CTR · GMV · 转化 · 风险接受率）
    - **Label 延迟**决定了监控节奏 · 有的场景只能靠 **proxy label** 或 **pairwise 对比**
    - **Auto-retrain 契约**不是"漂移就重训"——需要守门规则防止坏模型替换好模型
    - **Shadow / Canary / Rollback** 和 [Model Serving](model-serving.md) §Shadow/Canary/Rollback 合并理解
    - 2026 工具栈：**Evidently / Arize / Fiddler / WhyLabs / NannyML / Grafana 自建**

## 1. 业务痛点 · 没有监控会怎样

### 典型静默事故

| 症状 | 根因 | 发现滞后 |
|---|---|---|
| 推荐 CTR 季度环比降 20% | 用户偏好分布迁移 · 未重训 | 季度汇报才发现 |
| 风控模型某族群拒绝率异常 | 数据分布对小群体偏移 / fairness drift | 投诉 / 监管问询 |
| 欺诈检测漏报翻倍 | 新攻击 pattern 出现 · 模型没见过 | 损失做大才查 |
| CTR 预测低于实际 | calibration 失准 · 缺乏校准层 | A/B 才显现 |

**根本问题**：模型上线后**沉默**——不会像服务宕机那样报警。

### 监控覆盖哪些面

```
生产模型
├─ 技术指标（和通用服务一样）
│  └─ latency · 错误率 · 吞吐 · GPU 利用率     → Prometheus / Grafana
├─ 特征侧（输入）
│  └─ 每 feature 分布 · 缺失率 · 取值范围       → PSI / KS / missing rate
├─ 预测侧（输出）
│  └─ 预测分布 · 置信度分布 · 类别比例           → prediction drift
├─ 业务侧（效果）
│  └─ CTR / GMV / 转化 / 风险接受率             → 业务 KPI 看板
└─ 公平性（合规）
   └─ subgroup metric diff                   → fairness report
```

## 2. Drift 三类型 · 严格区分

**这三类是监控第一原则** —— 混为一谈会错判。

### Data Drift · P(X) 变

**定义**：输入特征分布变化 · 和 label 无关。
**例子**：新用户群体涌入 · 上游数据源 schema 悄悄变 · 季节性周期。
**检测**：PSI · KS · Wasserstein · chi-square。

### Concept Drift · P(y|X) 变

**定义**：输入到 label 的映射变化 · **即使** X 分布不变。
**例子**：欺诈攻击者换手法（同样的交易特征下 · 欺诈比例升高）· 用户偏好变迁。
**检测**：难——需要 label · 通常用滚动窗口 AUC / MAE 下降判断。

### Prediction Drift · P(ŷ) 变

**定义**：模型输出分布变化。
**例子**：预测 positive 比例从 10% → 25% · 模型"信心"突降。
**检测**：ŷ 直方图 PSI · mean prediction shift。
**用途**：**label 延迟场景**的 proxy（不能等 label 就先看 ŷ）。

### Fairness Drift · subgroup 性能差距变

**定义**：不同人群之间 metric gap 变化（demographic parity / equalized odds / disparate impact 等）。
**例子**：风控模型对某族群拒绝率上升 · 而整体 AUC 没变。
**检测**：按敏感属性切片算 metric · 追踪 gap 时序。
**合规**：EU AI Act 高风险系统 · 美国 EEOC · GDPR 自动化决策条款。

!!! tip "为什么三类必须分开"
    **Data drift 不一定导致模型变差**（模型可能泛化良好）。Concept drift **一定**影响模型但难检测。Prediction drift 是**前哨**但不能作为唯一依据。三者组合判断才对。

## 3. 三层指标栈

### 层 1 · 技术指标（通用服务）

- latency p50 / p90 / p99 · 错误率 · 吞吐 QPS · GPU 利用率
- **工具**：Prometheus + Grafana（和普通服务一样）

### 层 2 · 模型指标

#### 特征分布

| 指标 | 意义 | 阈值经验 `[来源未验证 · 示意性]` |
|---|---|---|
| **PSI**（Population Stability Index） | 分布偏移量 | < 0.1 稳定 · 0.1-0.25 关注 · > 0.25 告警 |
| **KS** | 两分布最大差异 | < 0.1 稳 · > 0.2 告警 |
| **Missing rate** | 缺失率变化 | 绝对变化 > 5% 告警 |
| **Value range** | 边界突破 | 超出训练集 min/max 告警 |
| **Cardinality**（类别特征） | 新增 / 消失类别 | 新类别比例 > 1% 告警 |

#### 预测分布

- ŷ 直方图 PSI
- Mean prediction shift（均值 / 方差）
- 置信度分布（low-confidence 比例抬升）
- 类别比例（分类模型 positive rate）

#### 性能指标（需要 label）

- 分类：AUC · precision · recall · F1 · log-loss · Brier score
- 回归：MAE · RMSE · MAPE
- 排序：NDCG · MAP · MRR · Recall@K · HitRate
- 推荐专属：CTR on serving vs offline AUC gap
- **Calibration**（概率校准 · Platt / Isotonic）

### 层 3 · 业务指标（终极真相）

- CTR · GMV · 转化率 · 留存 · 人均停留时长
- 风控：拒绝率 · 通过率 · 真实欺诈率
- 推荐：曝光多样性 · 新颖度
- **和模型指标对齐**：模型 AUC 涨 · 业务 CTR 是否涨？不对齐必排查（proxy metric 陷阱）

## 4. Label 延迟 · 监控节奏的决定因素

**不同场景的 label 延迟**决定了**监控频率和替代指标**。

| 场景 | Label 延迟 | 能即时监控什么 |
|---|---|---|
| CTR（点击） | 分钟 | 几乎实时 · 看 CTR 曲线 |
| 转化（加购 / 下单） | 小时-天 | 转化滞后 · 用 CTR 做 proxy |
| 订阅留存 | 周-月 | 只能看 prediction drift + churn proxy |
| 贷款违约 | 月-年 | **完全靠 prediction drift + feature drift + segment 稳定性** |
| 医疗诊断长期结果 | 年 | 难监控 · 靠代理指标（例如再入院率）|

**关键实践**：
- Label 延迟场景 → 以 **feature drift + prediction drift** 为主告警 · **pair A/B** 做长期对照
- 有 proxy label 的用 proxy（信用评分以"当期还款"作 proxy · 不等最终违约）
- **Pairwise 对比**：champion vs challenger 同流量下预测一致性 · 不一致即信号

## 5. Fairness Monitoring · 合规必须

### 5.1 核心指标

| 指标 | 定义 | 场景 |
|---|---|---|
| **Demographic Parity** | P(ŷ=1 \| A=a) 在各组相等 | 招聘、信贷 |
| **Equal Opportunity** | TPR 在各组相等 | 欺诈识别 · 医疗 |
| **Equalized Odds** | TPR 和 FPR 均相等 | 更严格要求 |
| **Disparate Impact** | P(ŷ=1 \| A=minority) / P(ŷ=1 \| A=majority) ≥ 0.8 | 美国 EEOC 80% rule |
| **Calibration by Group** | 每组预测概率与真实频率一致 | 通用 |

### 5.2 合规映射

- **EU AI Act**：高风险系统（招聘 / 信贷 / 执法 / 教育）**必须**持续监控 subgroup metric · 技术文档（含 Model Card）归档
- **美国 EEOC**：Uniform Guidelines 80% rule 作为 disparate impact 判定线
- **GDPR Art 22**：自动化决策受影响人有解释权 · 要求模型可解释 + subgroup fairness

### 5.3 工具

- **Evidently AI**：内置 fairness report · data drift + model quality 一体
- **Fiddler**：企业级 · fairness + explainability 完整
- **IBM AI Fairness 360** / **Aequitas**：开源 toolkit
- **Arize**：大厂常用 · trace + fairness

## 6. 工具栈对比 · 2026 视角

| 工具 | 类型 | 优势 | 适合 |
|---|---|---|---|
| **Evidently AI** | OSS · Python | 报告好看 · drift + fairness + quality 一体 | 中小团队 · Notebook / Airflow 嵌入 |
| **NannyML** | OSS · Python | **Concept drift 重点**（基于 DLE / CBPE 估计性能无需 label） | Label 延迟场景强项 |
| **DeepChecks** | OSS · Python | 训练前 / 部署后双侧 check · 更像 "ML 版 Great Expectations" | pipeline 内置校验 |
| **Arize AX** | 商业 SaaS | Trace + embedding monitoring + LLM 兼顾 · 大厂多 | 平台团队 |
| **Fiddler** | 商业 | 可解释性 + fairness + enterprise 合规 | 金融 · 医疗 · 合规重 |
| **WhyLabs** | 商业 / OSS（whylogs）| 低成本 profile · 适合多模型 | 多模型工厂 |
| **Grafana + 自建** | OSS | 灵活定制 · 需要自己写 drift 计算 | 已有 Prometheus 栈团队 |
| **Databricks Lakehouse Monitoring** | 平台托管 | UC 内建 · drift + feature 监控 | Databricks 用户 |

**默认推荐**：
- OSS 小团队：**Evidently** + **NannyML**（label 延迟场景）
- 有 Databricks：**Lakehouse Monitoring** + 必要时叠 Evidently
- 大平台 / 多模型：**Arize** 或 **Fiddler**（预算足）· 或 **WhyLabs** + 自建

## 7. Auto-retrain 契约 · 漂移 ≠ 重训

**最常见错误**："PSI > 0.25 → 自动重训"。这**会**出事。

**正确的 Auto-retrain 契约**（多重守门）：

```
触发条件（满足任一）：
  - 业务 KPI 下降 > 阈值 × N 天
  - 模型 AUC / NDCG 下降 > 阈值（需 label 或 proxy）
  - PSI > 0.25 持续 M 小时 + Prediction drift 确认
  - 人工触发（产品 / 合规决策）

重训守门（新模型必须全部通过才 promote）：
  1. 离线 holdout: 新模型 metric ≥ 旧模型 - ε
  2. Shadow 流量 N 小时: 新模型预测分布 vs 旧模型 KL < 阈值
  3. Canary 1% 流量 N 小时: 业务 KPI 不退化
  4. Fairness 回归: subgroup metric gap 未扩大
  5. 人工 review（高风险场景必走）

Promote 后：
  - MLflow alias champion 切换（champion → 新版 · previous → 旧版保留）
  - Serving 热加载 or 蓝绿切换
  - 监控 30 天回归期
```

### Champion / Challenger 常态化

- **生产跑 champion · 后台持续训练 challenger**
- 每周 / 每月定期比（同一 holdout · 同一时间段）
- Challenger 稳定优于 champion → 触发 promote 流程
- 避免"退化才重训"（事后补救 vs 事前预警）

## 8. Shadow / Canary / Rollback（和 [Model Serving](model-serving.md) 对照）

Model Monitoring 和 Model Serving 的 Shadow / Canary / Rollback 是**一体两面**：

- **Model Serving** §Shadow/Canary/Rollback 讲**怎么切流量 + runbook 操作**
- **本页** 讲**切流后看什么指标决定推进 / 回滚**

### 对账指标 for Shadow

- 预测分布：KL / JS divergence < 阈值
- 排序稳定性：top-K 重合率（推荐 / 搜索）
- 延迟：新模型 p99 在预算内
- Fairness：subgroup gap 未扩大

### Canary 自动 rollback 触发

- 业务 KPI 下降 > X% 持续 > Y 分钟
- 模型 metric（AUC / MAE）下降 > Z%
- 错误率 / 延迟超预算
- Fairness 指标突破 EU AI Act 合规线

## 9. Label Quality · 监控的盲点

**监控的前提是 label 可信**——但 label 本身可能坏：

| 问题 | 症状 | 应对 |
|---|---|---|
| **Bot / 作弊流量** | CTR 异常高但转化低 | 异常检测清洗 · 引入 bot score |
| **Delayed label 前看性 leakage** | 离线 AUC 过好 · 线上崩 | PIT Join 严格 · 训练集快照锁定 |
| **Implicit label 含义漂移** | "停留时长"变成 clickbait 代理 | 业务目标校准 · 多 label 组合 |
| **标注员不一致**（标注数据） | Kappa / Fleiss 低 | 多标注员投票 · 培训 · 裁决流程 |
| **Label 泄露新旧交叉** | 评估集 near-dedup 与训练集重合 | Hard dedup 流程（见 [fine-tuning-data.md](fine-tuning-data.md)）|

### Weak Supervision / Active Learning（简）

- **Weak supervision**（Snorkel）：规则 + 启发式合成 label
- **Active learning**：模型高不确定样本优先送标注
- **Programmatic labeling**：LLM 作 judge 大批初标 · 人工抽检
- 详细见 [fine-tuning-data.md](fine-tuning-data.md)（LLM 场景 · 原理相通）

## 10. 和 Feature Store 的协作

Feature Store 的 drift 监控（§3 机制 5）**是 Model Monitoring 的子集**但不等于全部：

- Feature Store 侧重**特征分布**（PSI / KS · 离线 vs 在线对账）
- Model Monitoring 侧重**模型性能 + 业务 + fairness**
- 两者应 **统一告警策略**（避免 feature drift 告警了但模型告警慢半拍 · 或反之）

## 11. 和 MLOps 生命周期的位置

对照 [mlops-lifecycle](mlops-lifecycle.md) 第 6 环节"监控"：

- 本页是**环节 6 的 canonical 深化**
- mlops-lifecycle §6 给出 3 类监控概览 → 本页给出具体指标 + 工具 + auto-retrain 契约
- 发现问题后的**重训 loop** 回到环节 1-5（数据 / 训练 / 评估 / 部署）

## 12. 陷阱 · 反模式

- **"PSI > 0.25 即重训"**：没有性能守门 → 坏模型替换好模型
- **只看技术指标不看业务 KPI**：延迟 p99 漂亮 · 业务在掉
- **Label 延迟场景只等 label**：事故早已发生
- **Fairness 忘监控**：合规事故 · 高风险系统被停
- **多个模型共享一套阈值**：不同场景数据特性不同 · 阈值应 per-model
- **告警太噪**：运维疲劳 · 真正事故被忽略 → 多级告警（关注 / 警告 / 紧急）+ 聚合
- **Drift 告警但没 runbook**：on-call 不知道该做什么
- **模型监控和应用监控分家**：两套 dashboard 难对账 → 统一 observability 平台
- **没有 champion / challenger 常态化**：退化才重训 · 永远在救火
- **Retrain 没 holdout 守门**：新模型可能更差直接上线
- **Fairness 指标单一**（只看 demographic parity）：多指标才能覆盖
- **把 LLM 监控当 ML 监控做**：LLM 有 token / prompt / tool trace 维度 · 应用 [llm-observability](../ai-workloads/llm-observability.md)

## 13. 相关

- [MLOps 生命周期](mlops-lifecycle.md) §6 监控 —— 本页是深化
- [Feature Store](feature-store.md) §Drift 监控 —— 特征侧
- [Model Serving](model-serving.md) §Shadow/Canary/Rollback —— 切流操作
- [Model Registry](model-registry.md) §alias API —— promote / rollback 机制
- [LLM Observability](../ai-workloads/llm-observability.md) —— LLM 应用侧对偶
- [AI 治理](../ops/compliance.md) —— EU AI Act 合规层

## 14. 延伸阅读

- Evidently AI docs: <https://docs.evidentlyai.com/>
- NannyML docs: <https://nannyml.readthedocs.io/>
- Arize: <https://arize.com/docs/>
- Fiddler: <https://docs.fiddler.ai/>
- *Machine Learning Engineering* (Andriy Burkov) 第 8 章
- *Designing ML Systems* (Chip Huyen) 第 8-9 章
- Google "Rules of ML"
- NIST AI Risk Management Framework（2023）
- EU AI Act 合规指引 · 高风险系统持续监控要求
