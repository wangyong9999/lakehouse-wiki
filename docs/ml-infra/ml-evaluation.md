---
title: ML Evaluation · 离线 / Calibration / Fairness / A/B / Shadow / 显著性
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: 传统 ML（分类 / 回归 / 排序 / 推荐 / 风控 / 广告 / CV 等）· scikit-learn · statsmodels · scipy · 业务实验平台 · 2024-2026 实践
prerequisites: [mlops-lifecycle]
tags: [ml-infra, evaluation, ab-testing, fairness, calibration, significance]
aliases: [ML 评估, Model Evaluation, A/B Testing]
related: [mlops-lifecycle, model-monitoring, model-serving, model-registry, feature-store, rag-evaluation]
systems: [scikit-learn, statsmodels, scipy, optuna, fairlearn, airbnb-experimentation-platform]
status: stable
---

# ML Evaluation

!!! tip "一句话定位"
    **模型上线前的守门 + 上线后的对账**。离线评估（指标 · Calibration · Fairness）· 业务模拟 / 回放 · **Shadow 对账** · **A/B 显著性** · Canary 推进契约 —— 这是 ML 生命周期**独立的一等支柱** · 不是训练和监控之间的一段流程。

!!! warning "和其他页的分工"
    - **本页**：**传统 ML**（分类 / 回归 / 排序 / 推荐 / 风控 / 广告 / CV）离线 + 在线评估 canonical
    - **[rag-evaluation](../ai-workloads/rag-evaluation.md)**：LLM / RAG / Agent 评估（RAGAS · TruLens · DeepEval · LLM-as-Judge · MT-Bench · SWE-bench）
    - **[model-monitoring](model-monitoring.md)**：**持续监测** drift / PSI / 业务 KPI 退化 —— 上线**之后**
    - **[mlops-lifecycle](mlops-lifecycle.md) §4 评估**：环节概览 → 本页是深化 canonical

!!! abstract "TL;DR"
    - **三层守门**：**离线指标** → **业务模拟 / 回放** → **Shadow** → **Canary** → **A/B** → 全量
    - **离线 ≠ 业务**：AUC 涨 0.02 不一定 CTR 涨（proxy metric 陷阱）· 必须跑业务模拟
    - **Calibration** 常被忽略但生产关键（预测 0.8 实际 0.5 · 无法做 ensemble / 决策阈值）
    - **Fairness** 是一等评估维度 · 不是事后合规补丁（EU AI Act / EEOC 80% rule）
    - **A/B 显著性**不是"看曲线"—— 是 sample size + power + effect size + 多重比较校正
    - **Shadow 对账**用 KL / JS divergence + top-K 重合率 · 不只看延迟
    - 工具：**scikit-learn** · **statsmodels** · **scipy** · **fairlearn** · **业务实验平台**（Airbnb / Uber / 自建）

## 1. 为什么评估应作独立支柱

不少团队把"评估"当成训练 loop 的末尾一节：
```python
# 常见但不充分
y_pred = model.predict(X_test)
print(f"AUC: {roc_auc_score(y_test, y_pred_proba):.3f}")
# ... 就没了
```

**这离生产可用的评估纪律差很远**。完整评估是：

```
训练 → 离线指标多维（不只 AUC）
     → Calibration 检查
     → Fairness 分组指标
     → 业务模拟 / 回放（历史数据跑 what-if）
     → Shadow（新流量并行跑 · 不决策）
     → Canary（小流量真决策 · 守门回滚）
     → A/B（严格实验设计 · 显著性判据）
     → 全量
```

**每一步守门失败都应该可以 block 上线**。现在很多团队直接从"离线 AUC 好"跳到"上线" · 事故就在中间。

## 2. 三层评估守门矩阵

### 层 1 · 离线评估（多维）

| 维度 | 分类 | 回归 | 排序 | 推荐 |
|---|---|---|---|---|
| **核心** | AUC · Precision · Recall · F1 · log-loss | MAE · RMSE · MAPE · R² | NDCG · MAP · MRR | Recall@K · HitRate · NDCG@K |
| **Calibration** | Brier score · ECE · Reliability diagram | 残差分析 | — | — |
| **Fairness** | 分组 TPR/FPR · Demographic parity | 分组 MAE | 分组 NDCG | 分组 Hit rate |
| **Uncertainty** | 置信度分布 · 熵 | Prediction interval | 排名稳定性 | Coverage |

**关键原则**：**一张 metric dashboard 不够**。至少看 3 维：主指标（AUC 等）+ Calibration + Fairness。

### 层 2 · 业务模拟 / 回放

**离线 AUC 涨 ≠ 业务会涨**。必须跑**业务模拟**：
- **Counterfactual replay**：历史流量 · 用新模型重打分 · 估算业务 KPI 变化
- **Proxy metric 对齐**：AUC 涨了 · CTR 涨不涨（需要 CTR 模拟函数 / Reward model）
- **长尾 slice**：不只看总体 metric · 按用户分群 / 商品分群 / 时段切片看

### 层 3 · Shadow · Canary · A/B（线上）

见 §5-7。

## 3. Calibration · 常被忽略但关键

**Calibration**（校准）= 预测概率与真实频率匹配程度。

预测 0.8 · 实际 80% 为 positive → 校准好；预测 0.8 · 实际 50% → 过度自信。

### 为什么重要

- **决策阈值**：风控要"> 0.7 拒绝"· 未校准则阈值失效
- **Ensemble**：多模型融合需要可比概率
- **业务可解释**：给产品说"这用户 80% 概率流失"必须真的 80%

### 指标

| 指标 | 定义 |
|---|---|
| **ECE**（Expected Calibration Error） | 分桶计算 \|mean(pred) - true_rate\| 加权平均 |
| **Brier score** | MSE on probabilities · 越低越好 |
| **Reliability Diagram** | 可视化 · x 轴预测概率桶 · y 轴真实频率 |

### 校准方法

- **Platt Scaling**（logistic 后处理）
- **Isotonic Regression**（非参数 · 更灵活 · 需足数据）
- **Temperature Scaling**（DNN 常用 · 单参数）

## 4. Fairness · 分组评估 · EU AI Act 对齐

### 4.1 核心指标

| 指标 | 定义 | 场景 |
|---|---|---|
| **Demographic Parity** | P(ŷ=1\|A=a) 在各组相等 | 招聘 · 信贷 |
| **Equal Opportunity** | TPR 在各组相等 | 欺诈识别 · 医疗 |
| **Equalized Odds** | TPR 和 FPR 均相等 | 更严格 |
| **Disparate Impact** | P(ŷ=1\|A=minority) / P(ŷ=1\|A=majority) ≥ 0.8 | 美国 EEOC 80% rule |
| **Calibration by Group** | 每组预测概率与真实频率一致 | 通用 |

### 4.2 工具

- **fairlearn**（Microsoft · Python）· **IBM AIF360** · **Aequitas** · **Fairkit-learn**
- 内置分组指标 + 缓解算法（reweighting / post-processing）

### 4.3 多指标权衡 · 不可能定理

多个 fairness 指标**数学上不可兼得**（Kleinberg et al. 2016：base rate 不等时 Calibration + Equalized Odds 不可同时成立）。**业务需要选择**哪些 fairness 指标优先 · 而不是一味追求"全都做到"。

## 5. Shadow Deployment · 对账指标

Shadow = 新模型并行跑 · 不决策。对账**不能只看延迟** · 需多维：

| 对账维度 | 指标 | 阈值经验 `[来源未验证 · 示意性]` |
|---|---|---|
| **预测分布** | KL / JS divergence | < 0.1 稳定 · > 0.25 告警 |
| **排序稳定性**（推荐 / 搜索） | top-K 重合率 · rank correlation | > 0.7 可接受 |
| **延迟** | p99 | 在 SLO 预算内 |
| **Fairness** | subgroup gap | 未扩大 |
| **资源** | GPU / CPU / 内存占用 | 未超预算 |

**窗口**：至少 24-72 小时 · 覆盖日 / 周周期。

## 6. Canary Progressive Delivery · 守门

流量逐级切 · 每级看指标决定推进 / 回滚：

| Stage | 流量 | 守门指标 | 冷却窗口 |
|---|---|---|---|
| Canary v0 | 1-5% | 业务 KPI + 延迟 + 错误率 + fairness | 24h |
| Canary v1 | 10-25% | + 长尾 slice | 24h |
| Canary v2 | 50% | + 真实 A/B 显著性初值 | 24-48h |
| 全量 | 100% | 30 天回归监控 | — |

**自动回滚触发**：业务 KPI 下降 > X% 持续 > Y 分钟 · 模型 metric 下降 > Z% · fairness 突破合规线。

## 7. A/B Testing · 统计显著性不是看曲线

### 7.1 样本量与 Power

**错误做法**：两组跑一周 · 看谁 CTR 高。

**正确做法**：
- 事前算**所需样本量**：给定基线 CTR · 最小可检测 effect · power（通常 80%）· alpha（0.05）
- 达到样本量**再看结果**（不提前偷看 · Peeking Problem）
- scipy / statsmodels 有公式：

```python
from statsmodels.stats.power import NormalIndPower
power = NormalIndPower()
n = power.solve_power(
    effect_size=0.02,   # 最小可检测 effect（Cohen's h 等）
    alpha=0.05,
    power=0.80,
    alternative="two-sided",
)
# n ≈ 样本量 per variant
```

### 7.2 显著性检验

- **两样本 t 检验**（连续 · 均值对比）
- **Chi-square / z-test for proportions**（离散 · 转化率对比）
- **Mann-Whitney U**（非参数 · 分布不对称）

### 7.3 多重比较校正

同时测多个 variant 或多个 metric · 需要校正：
- **Bonferroni**（保守）· **Holm-Bonferroni**（较优）· **Benjamini-Hochberg FDR**（大规模常用）

### 7.4 常见陷阱

- **Peeking**（中途偷看）→ 用 Sequential Testing / SPRT
- **SRM**（Sample Ratio Mismatch）· 分流偏差 → 每日 chi-square 检测
- **Novelty effect** · 新 UX 初期兴趣高 · 后衰减 → 延长窗口
- **Proxy metric 陷阱** · CTR 涨 GMV 不涨 → 多指标组合判断
- **Segment heterogeneity** · 总体不显著但某群显著 → 谨慎跨 segment 决策

## 8. 实验平台 · 工程视角

### 8.1 核心能力

- **分流**：hash 算法 · salt · 一致性（同用户进同组）
- **holdout**：保留部分流量永不实验（全局 ref）
- **实验互斥 / 叠层**：多实验同时跑互不干扰
- **指标计算**：实时 / 批 · Kafka → Flink → 看板
- **报告**：显著性 + 置信区间 + 效应量 + 细分维度

### 8.2 典型栈

| 工具 | 类型 | 备注 |
|---|---|---|
| **自建**（Airbnb ERF · Uber Morpheus · Microsoft ExP） | 大厂标配 | 功能最全 |
| **GrowthBook** | OSS | 中小团队 · OpenAPI |
| **Optimizely · VWO · Statsig** | 商业 SaaS | 前端实验为主 |
| **Eppo · Split.io** | 商业 | 数据侧实验重点 |

### 8.3 和 ML Registry / Serving 集成

- 每个 variant 绑 model version / alias
- Alias 切换（`champion` / `challenger` / `canary`）和分流规则映射一致
- 详见 [model-registry §审批工作流](model-registry.md) + [model-serving §Canary](model-serving.md)

## 9. 场景特定评估要点

### 9.1 推荐系统

- **离线**：Recall@K / NDCG@K / HitRate / Coverage / Diversity
- **业务模拟**：历史曝光回放 · Counterfactual IPS (Inverse Propensity Scoring)
- **上线**：CTR · GMV · 停留时长 · 多样性指标（Gini 等）

### 9.2 风控 / 欺诈

- **离线**：AUC · KS · Lift · Precision@Recall（漏报 vs 误报权衡）
- **业务**：拒绝率 · 真欺诈率 · 人群公平性
- **Calibration 特别重要**：不同风险阈值决策

### 9.3 广告 CTR / CVR

- **离线**：AUC · log-loss · Calibration
- **业务模拟**：竞价模拟（第二价拍卖下 ranking score → revenue）
- **延迟 label** · CVR 到天级

### 9.4 CV / 图像分类

- **离线**：Top-1 / Top-5 · mAP · IoU
- **长尾 slice**：低频类 · OOD 类
- **对抗鲁棒性**：FGSM / PGD

### 9.5 时序预测

- **离线**：MAE / RMSE / MAPE · seasonal naive baseline 对比
- **分 horizon**：1 步 / 7 步 / 30 步分别评估
- **back-testing**：rolling window

## 10. 和 rag-evaluation 的边界

|  | ml-evaluation（本页）| [rag-evaluation](../ai-workloads/rag-evaluation.md) |
|---|---|---|
| 对象 | 传统 ML 模型（分类 / 回归 / 排序 / 推荐 / 风控 / CV） | LLM / RAG / Agent |
| 指标 | AUC / NDCG / MAE / Calibration / Fairness | Groundedness / Faithfulness / LLM-as-Judge / MT-Bench |
| 显著性 | 经典 AB 检验 | AB + 人工评估 |
| 工具 | scikit-learn / statsmodels / fairlearn | RAGAS / TruLens / DeepEval / Phoenix |

**大型平台**两套并存 · 共享 A/B 实验平台底座。

## 11. 陷阱 · 反模式

- **只看 AUC 不看 Calibration**：决策阈值错乱
- **Fairness 只测一个指标**：单一指标通过不等于公平
- **Shadow 只看延迟**：预测漂移没发现
- **Canary 自动 rollback 阈值太松**：坏模型堆积 · 太紧则假警不断
- **A/B 提前偷看结果**（Peeking）：显著性失效
- **不算样本量**：小流量跑几天 · 假阳 / 假阴都可能
- **Novelty effect 下决策**：新 UX 初期兴奋 → 误判胜出
- **业务指标对齐缺失**：AUC 涨业务没涨
- **评估集泄漏**：详见 [data-quality-for-ml §评估集泄漏](data-quality-for-ml.md)
- **不做业务模拟直接 A/B**：A/B 时才发现模型实际破坏体验
- **把评估当训练末尾**：应当是独立环节 · 带独立守门
- **Fairness 当"事后补丁"**：应全程参与 · 训练时加约束 / 校准

## 12. 相关

- [MLOps 生命周期](mlops-lifecycle.md) §4 评估 —— 本页是深化
- [Model Monitoring](model-monitoring.md) —— 上线后持续监测
- [Model Serving](model-serving.md) §Shadow/Canary/Rollback —— 切流操作
- [Model Registry](model-registry.md) §审批工作流 —— alias 切换和分流映射
- [Feature Store](feature-store.md) §PIT —— 评估集 PIT 正确性
- [Data Quality for ML](data-quality-for-ml.md) —— 评估集泄漏防御
- [rag-evaluation](../ai-workloads/rag-evaluation.md) —— LLM / RAG / Agent 评估
- [AI 治理](../frontier/ai-governance.md) —— EU AI Act Fairness 合规

## 13. 延伸阅读

- *An Introduction to Statistical Learning*（James et al.）—— 经典
- *Trustworthy Online Controlled Experiments*（Kohavi et al., 2020）—— A/B 实验圣经
- Microsoft ExP · Airbnb ERF · Uber Morpheus 技术博客
- fairlearn docs: <https://fairlearn.org/>
- *Inherent Trade-Offs in the Fair Determination of Risk Scores*（Kleinberg et al., 2016）
- *Calibration of Modern Neural Networks*（Guo et al., 2017 · Temperature Scaling）
- *Netflix Experimentation Platform* series
