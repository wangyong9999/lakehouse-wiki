---
title: ML 平台
type: reference
status: stable
tags: [index, ml-infra]
description: 湖仓一等公民化 ML 资产 · 数据 / 特征 / 模型 / 训练 / 部署 / 监控 六环节闭环
applies_to: 2024-2026 MLOps · MLflow 2.9+ · Feast 0.40+ · Ray 2.9+ · Kubeflow 1.8+ · Databricks UC Models · Tecton · Hopsworks 4.x
last_reviewed: 2026-04-21
---

# ML 平台

!!! info "本章组织"
    本章按 3 个子组（按 ML 生命周期）：
    
    - **数据与特征**：[Feature Store](feature-store.md) / [Data Quality for ML](data-quality-for-ml.md) / [Embedding 流水线](embedding-pipelines.md) + [Feature Store 横比](../compare/feature-store-comparison.md)
    - **模型生命周期**：[MLOps 生命周期](mlops-lifecycle.md) / [Experiment Tracking](experiment-tracking.md) / [Model Registry](model-registry.md) / [ML Evaluation](ml-evaluation.md) / [Model Serving](model-serving.md) / [Model Monitoring](model-monitoring.md)
    - **训练基础设施**：[训练编排](training-orchestration.md) / [GPU 调度](gpu-scheduling.md) / [LLM Fine-tuning](fine-tuning-data.md)
    
    外部权威：[`docs/references/ml-infra/`](../references/ml-infra/index.md)（Google MLOps Maturity · MLflow / Kubeflow / Feast 文档 · Chip Huyen 教科书）。**Google MLOps 关键 components**（Data validation / Feature stores / ML metadata / Pipeline orchestration / Model registries / Monitoring）与本章三组分布对齐。

!!! tip "一句话定位"
    **把 ML 资产放进湖仓一等公民体系的工程层**。数据是 Iceberg 表、特征是 Feature Store View、模型是 Registry 里带 snapshot 血缘的 artifact —— **六环节闭环（数据/特征/训练/评估/部署/监控）全部带版本、可审计、可回滚**。这是相对 Chip Huyen 2022、Google MLOps Maturity、Databricks MLOps Stacks 的差异化叙事。

!!! abstract "TL;DR"
    - **核心叙事**：**湖仓一等公民化 ML 资产** —— Iceberg snapshot 锁数据 · Feature Store View 管特征 · Model Registry + alias 管模型 · 六环节全链可追溯
    - **三组结构**：**数据与特征 / 模型生命周期 / 训练基础设施**
    - **和 AI 应用章分工**：本章讲**传统 ML 平台 + LLM 训练/微调底座**；LLM 应用层（RAG / Agent / Prompt / Inference / Guardrails）在 [ai-workloads/](../ai-workloads/index.md)
    - **和场景章分工**：本章讲**工程底座**（怎么做一个 Feature Store / 怎么训练）；端到端业务链路（推荐系统 / 欺诈检测 / 离线训练流水线）在 [scenarios/](../scenarios/index.md)
    - **和检索章分工**：本章讲**embedding pipeline**（怎么持续生成向量）；**embedding 模型选型 / ANN 算法 / rerank**在 [retrieval/](../retrieval/index.md)

!!! warning "边界声明 · 避免走错章"
    本章**不讲**以下话题 · 请去对应章：

    - **LLM 推理优化**（vLLM / SGLang / PagedAttention / 量化 / speculative）→ [ai-workloads/llm-inference.md](../ai-workloads/llm-inference.md)
    - **LLM Gateway**（LiteLLM / Portkey / 统一代理）→ [ai-workloads/llm-gateway.md](../ai-workloads/llm-gateway.md)
    - **Prompt 管理 / LLM Observability / RAG / Agent / Guardrails**→ [ai-workloads/](../ai-workloads/index.md) 层 3 工程纪律
    - **Embedding 模型选型 / ANN / Rerank 算法**→ [retrieval/](../retrieval/index.md)
    - **端到端业务场景**（推荐 / 风控 / 离线训练流水线 / Feature Serving）→ [scenarios/](../scenarios/index.md)
    - **治理与合规细节**（Catalog RBAC / 数据血缘工具）→ [catalog/](../catalog/index.md)

## 三组结构

### 组 1 · 数据与特征

工程化 ML 数据资产 —— 训推一致 / PIT 正确 / 数据契约 + label 质量 / 持续 embedding。

- [**Feature Store**](feature-store.md) ⭐ —— 统一定义 · PIT Join · 双存储 · SSOT 主定义（PIT / Train-Serve Skew）
- [**Data Quality for ML**](data-quality-for-ml.md) ⭐ —— Data Contract · Quality Gates（GE / Soda / Monte Carlo）· Label Quality · 评估集泄漏防御
- [**Embedding 流水线**](embedding-pipelines.md) —— 批 / 流 / 模型版本治理 / CDC 增量
- [Feature Store 横比](../compare/feature-store-comparison.md) —— Feast / Tecton / Hopsworks / 云厂商 / 自建

### 组 2 · 模型生命周期

模型从实验到注册到上线到评估到监控的完整生命 —— MLOps 伞 + 五根支柱。

- [**MLOps 生命周期**](mlops-lifecycle.md) ⭐ —— **贯穿叙事 · 六环节闭环总览** · 成熟度 L0-L3 · 同时覆盖 LLMOps 分支
- [**Experiment Tracking**](experiment-tracking.md) —— MLflow / W&B / Neptune / Comet / Aim · 研究 → 生产的桥梁
- [**Model Registry**](model-registry.md) —— 版本 / alias / Model Card / BOM · MLflow / UC Models / W&B Artifacts · ≠ 完整发布控制面
- [**ML Evaluation**](ml-evaluation.md) ⭐ —— 离线指标 · Calibration · Fairness · A/B · Shadow 对账 · 显著性 · 传统 ML canonical（LLM/RAG eval 看 [rag-evaluation](../ai-workloads/rag-evaluation.md)）
- [**Model Serving**](model-serving.md) —— 通用 ML serving（Ray Serve / KServe / Triton / BentoML）· Inference Graph / Shadow / Canary / Rollback runbook · LLM 推理深度看 [llm-inference](../ai-workloads/llm-inference.md)
- [**Model Monitoring**](model-monitoring.md) ⭐ —— Drift / PSI / KS / Fairness · Evidently / Arize / Fiddler · Auto-retrain 契约

### 组 3 · 训练基础设施

模型训练从单机多卡到 LLM 级并行 —— 引擎 · 资源 · 微调。**本组对 LLM 训练有较多覆盖**（2024-2026 训练主战场）· **但传统 ML / tabular / CV 场景同样适用** · 各页正文都标注了适用边界。

- [**训练编排**](training-orchestration.md) —— Ray Train / Kubeflow / Flyte · FSDP2 / Context Parallel / torchtitan · DCP checkpoint · 通用 DDP / 小中模型场景
- [**GPU 调度**](gpu-scheduling.md) —— K8s / Volcano / Run:ai · MIG / MPS · B200/GB200/H200/MI300X · 多租户 + FinOps · tabular / 推荐在线调度
- [**LLM Fine-tuning**](fine-tuning-data.md) —— 数据 · 方法（SFT/DPO/ORPO/KTO/LoRA/QLoRA/PEFT）· 工具（Axolotl/LLaMA-Factory/unsloth）· 评估 · 部署一体（**LLM 场景专属**）

## 叙事角度 · 一种值得考虑的路线：湖仓一等公民化

!!! warning "这是一种路线 · 不是唯一答案"
    本章用"湖仓一等公民化 ML 资产"作为**叙事主线** · 是因为它在**数据已经在 Iceberg/Paimon/Delta**的团队里能让 ML 治理显著简化（共用 RBAC / 血缘 / time-travel / snapshot）。但**这不是 ML 平台的唯一路线**：
    
    - **部分解耦架构仍然大量成立且合理**：数据在湖 · 模型元数据在 MLflow · Feature Store 独立 · Serving 另成平台 —— 这在很多成熟团队**不是落后**，而是出于组织边界 / 演进历史 / 性能 / 合规 / 法务需要。
    - **完全不走湖仓路径也能做好**：基于 Postgres + S3 + MLflow 的经典栈可以支撑中等规模 ML · Databricks / SageMaker / Vertex 全托管也各成一体。
    - **判断什么时候走到什么程度**：本章的每页提供"组件视角"· 你要组合哪一套 · 取决于组织成熟度 + 业务形态 + 团队能力，**不应把"一体化到底"当成默认终点**。
    
    下面的湖仓一等公民化描述是**一种达成终态的路径**· 读者把它当**差异化视角**理解 · 不是判定其他路径为错。

传统 MLOps 工具（MLflow、Kubeflow、SageMaker）把 ML 资产放在**独立系统**里：metadata 存 MySQL · artifact 存 S3 · 权限走 IAM · 血缘散在 W&B/MLflow。结果往往是**数据治理和模型治理两套系统**。

湖仓一体化（Iceberg + Unity/Polaris）提供了**另一条可选的路**：

| ML 资产 | 湖仓一等公民化形式 |
|---|---|
| 训练数据 | Iceberg 表 + `VERSION AS OF snapshot_id` 锁版本 |
| 特征 | Feature Store View（离线 Iceberg + 在线 KV）· 带血缘 |
| 模型 | Unity Catalog Models / 带 `training_dataset_snapshot_id` 绑定 |
| Embedding | Iceberg / Lance 表 · 带 `embedding_model_version` + `source_snapshot_id` |
| 微调数据集 | Iceberg / Lance 表 · `dataset_version` 字段 |
| 推理日志 | 回写 Iceberg · 作下一轮训练数据源 |

**可能的好处**（走到什么程度算有收益）：
- 数据 ACL / 模型 ACL / 特征 ACL **一套 RBAC**（前提：Catalog 本身成熟）
- 时间旅行机制可以作模型复现契约（前提：snapshot 保留策略能支撑）
- 血缘跨 ML 和 BI 统一（前提：BI 也在同一 Catalog）
- 审计 / EU AI Act / GDPR 落地（前提：合规需求确实跨数据 + 模型）

**什么时候可能不划算**：
- 数据根本不在湖仓（部分还在 OLTP / 数仓）
- Catalog（UC / Polaris）还没铺开 · 先做 ML 一体化会变成孤岛
- 模型跨多种数据源（湖 + 数仓 + 三方 API）· 强绑湖仓反而限制
- 只有 1-2 个模型 · MLflow + S3 够用 · 一体化投入 ROI 低

## 章节边界再声明 · 平台基础能力 vs 场景专属能力

**本章 10 页的定位不是齐平的**：

| 类别 | 页面 | 说明 |
|---|---|---|
| **平台基础能力**（场景无关） | MLOps Lifecycle · Experiment Tracking · Feature Store · Model Registry · Model Serving · Model Monitoring · ML Evaluation · Data Quality · 训练编排 · GPU 调度 | 适用于 tabular / 推荐 / 风控 / CV / 小中模型 / LLM 所有场景 |
| **LLM 时代特定能力** | LLM Fine-tuning · Embedding 流水线（部分） | 绑定 LLM 或向量检索 · 不是通用 ML 平台硬通货 |

**注意**：ml-infra 的重心是**平台基础能力** · LLM-specific 的深度内容（推理引擎 · Prompt · Agent · RAG · Guardrails）全部在 [ai-workloads/](../ai-workloads/index.md)。本章的 LLM 相关只保留**和训练/微调/底层**直接相关的最小集。

## 角色速查

| 角色 | 首读路径 |
|---|---|
| **AI 平台工程师** | mlops-lifecycle → feature-store → model-registry → model-serving → model-monitoring · 然后 training-orchestration + gpu-scheduling |
| **传统 ML 工程师**（推荐 / 风控 / 个性化） | feature-store → mlops-lifecycle → model-registry → model-monitoring · 配套 scenarios/recommender-systems / fraud-detection |
| **LLM 应用工程师做微调** | fine-tuning-data（LLM Fine-tuning 一体页）→ training-orchestration → gpu-scheduling → model-registry · 上游对接 [ai-workloads/](../ai-workloads/index.md) |
| **数据 / BI 工程师接触 ML** | mlops-lifecycle → feature-store → embedding-pipelines · 再看 [scenarios/offline-training-pipeline](../scenarios/offline-training-pipeline.md) |
| **SRE / 平台 ops** | gpu-scheduling → model-monitoring → model-serving · 成本归因看 gpu-scheduling §FinOps |

## 症状 → 页面反向索引

| 症状 | 去哪读 |
|---|---|
| 线上 AUC 比离线暴跌 | [feature-store](feature-store.md) §Train-Serve Skew |
| 模型悄悄退化两个月才发现 | [model-monitoring](model-monitoring.md) §Drift + Auto-retrain |
| 重跑训练结果不一致 | [mlops-lifecycle](mlops-lifecycle.md) §数据 snapshot + [feature-store](feature-store.md) §PIT |
| 模型要回滚但版本混乱 | [model-registry](model-registry.md) §alias API + [model-serving](model-serving.md) §Rollback runbook |
| GPU 利用率 < 60% | [gpu-scheduling](gpu-scheduling.md) §碎片 + [model-serving](model-serving.md) §Batching |
| 多租户 GPU 队列冲突 | [gpu-scheduling](gpu-scheduling.md) §抢占 / 隔离 |
| GPU 账单失控 | [gpu-scheduling](gpu-scheduling.md) §FinOps |
| 特征离线在线不对账 | [feature-store](feature-store.md) §Materialization + [model-monitoring](model-monitoring.md) §Drift |
| 新 embedding 模型上线怎么回填 | [embedding-pipelines](embedding-pipelines.md) §模型版本管理 |
| LoRA 微调要选哪个工具 | [fine-tuning-data](fine-tuning-data.md) §工具生态 |
| 推理链路是多模型 DAG 怎么部署 | [model-serving](model-serving.md) §Inference Graph |
| Model Card / EU AI Act 合规字段 | [model-registry](model-registry.md) §合规 artifact |
| 上线前离线 eval 该跑哪些指标 | [ml-evaluation](ml-evaluation.md) §离线指标矩阵 |
| A/B 实验结果怎么判显著 | [ml-evaluation](ml-evaluation.md) §统计显著性 |
| Fairness / 公平性怎么系统化测 | [ml-evaluation](ml-evaluation.md) §Fairness + [model-monitoring](model-monitoring.md) §Fairness |
| 训练 run 多到管不过来 | [experiment-tracking](experiment-tracking.md) §组织实验 |
| 超参搜索的 artifact 爆炸 | [experiment-tracking](experiment-tracking.md) §保留策略 |
| 训练集里混入脏数据 / bot | [data-quality-for-ml](data-quality-for-ml.md) §Quality Gates |
| 上游 schema 突然变了 | [data-quality-for-ml](data-quality-for-ml.md) §Data Contract |
| 标注员打标不一致 | [data-quality-for-ml](data-quality-for-ml.md) §Label Quality |
| 评估集泄漏到训练集 | [data-quality-for-ml](data-quality-for-ml.md) §泄漏防御 |
| 该不该上 Feature Store | [feature-store](feature-store.md) §何时不需要 FS |
| 是该中央平台还是业务自服务 | 本页 §平台边界与组织成本 |

## 典型生产栈 matrix

不同场景对应不同栈组合 —— 这是平台 lead 最常被问的问题。

| 场景 | 数据底座 | 特征 | 训练 | Registry | Serving | 监控 |
|---|---|---|---|---|---|---|
| **开源湖仓栈**（中型团队 · 自运营） | Iceberg | Feast + Redis | Ray Train / Kubeflow | MLflow | Ray Serve + Triton | Evidently + Grafana |
| **Databricks 全托管栈** | Delta + UC | Databricks FS / Online Tables | Databricks Runtime + MosaicML | UC Models | Model Serving（Databricks） | Lakehouse Monitoring |
| **K8s 原生栈** | Iceberg / Paimon | Feast on Trino | Kubeflow + Volcano | MLflow / KServe ModelMesh | KServe | Prometheus + 自建 drift |
| **LLM-only 栈**（微调 + 服务） | Lance + HF datasets | — | Axolotl / unsloth + Ray | HF Hub + MLflow | vLLM（详见 [ai-workloads](../ai-workloads/llm-inference.md)） | Langfuse + [llm-observability](../ai-workloads/llm-observability.md) |
| **推荐 / 风控场景** | Iceberg | Feast + Aerospike / Redis | Ray Train + Spark | MLflow | Ray Serve（召回）+ Triton（精排） | Evidently + 业务 KPI 看板 |

**选择指南**：
- 数据已经在 Iceberg / Delta → 优先开源湖仓栈或 Databricks 全托管
- K8s 重、平台团队独立 → K8s 原生栈
- LLM 场景为主 → LLM-only 栈 + 和 ai-workloads 章深度集成
- 多场景混布 → 以开源湖仓栈为骨架 · LLM 部分接入 LLM-only

## 平台边界与组织成本 · 不是所有能力都该中央化

**ML 平台团队最大的误区是"什么都自己做"**。什么该中央平台维护 · 什么该业务团队 self-serve · 什么时候只做 guardrails + golden path —— 这比工具选型更重要。

### 推荐的分层

| 能力 | 中央平台 | 业务团队 self-serve | Guardrails + Golden Path |
|---|---|---|---|
| **Feature Store 在线 store + Registry 维护** | ✅ | | |
| **GPU 调度 + 成本归因 tag 体系** | ✅ | | |
| **Model Monitoring 底座（metric pipe）** | ✅ | | |
| **Compliance 合规 artifact schema** | ✅ | | |
| **训练 pipeline 模板** | | | ✅ 给模板 + 自由定制 |
| **模型评估** | | | ✅ 工具 + 默认 eval · 业务自加维度 |
| **特征定义（domain-specific）** | | ✅ | |
| **超参调优 / 模型选择** | | ✅ | |
| **Prompt / Agent 设计** | | ✅ | |

### 什么时候**不**该做平台

- **业务规模小**（1-2 个模型）：中央 FS + Registry + Monitoring 投入回不来 · 让业务团队用 MLflow + S3 先跑起来
- **组织还没准备好**：平台团队 2 人 · 业务团队 20 人 · 平台被业务拖垮 → 先做 golden path + 文档
- **场景差异过大**：推荐 / 风控 / LLM 各自独立 · 强统一平台变成最小公倍数
- **合规 / 法务独立管**：某些行业（金融 / 医疗）数据 ACL 和 ML 平台本该隔离

### 过度平台化的代价

- **冻结创新**：业务团队想换工具 · 平台团队"要求统一"
- **平台团队成了瓶颈**：所有模型上线走平台队列
- **黑箱累积**：平台团队离职 · 业务团队不懂底层
- **成本虚高**：平台本身的运维 + 演进 + 支持成本

**正确姿态**：平台做**最小有用集** + **宽松的 golden path** + **少数合规强约束** · 剩下让业务团队自己做决策。

## 学习路径

**新手（任意角色起步）**：
1. 读 [mlops-lifecycle](mlops-lifecycle.md) 建立六环节全局
2. 挑一个最贴业务的场景页（[scenarios/recommender-systems](../scenarios/recommender-systems.md) / [fraud-detection](../scenarios/fraud-detection.md) / [offline-training-pipeline](../scenarios/offline-training-pipeline.md)）
3. 回来深挖 feature-store + model-registry + model-monitoring 三核心
4. 最后看 training-orchestration + gpu-scheduling 基础设施层

**资深 ML 平台工程师**：
- 全章通读 · 重点关注 model-monitoring 的 Auto-retrain 契约和 model-serving 的 Inference Graph
- 跨章：[ai-workloads](../ai-workloads/index.md)（LLMOps 对应闭环） + [scenarios](../scenarios/index.md)（端到端）

## 和其他章节的关系

- **上游依赖**：[lakehouse/](../lakehouse/index.md)（Iceberg / Paimon / Delta）· [catalog/](../catalog/index.md)（Unity / Polaris · 模型作一等公民）· [retrieval/](../retrieval/index.md)（embedding 模型）
- **平行姊妹**：[ai-workloads/](../ai-workloads/index.md)（LLM 应用层 · 本章是其底座）
- **下游消费**：[scenarios/](../scenarios/index.md)（推荐 / 风控 / 离线训练流水线 / Feature Serving 端到端业务）
- **横向对比**：[compare/feature-store-comparison](../compare/feature-store-comparison.md)

## 相邻章节

- [AI 合规](../ops/compliance.md) —— EU AI Act / NIST AI RMF / 中国生成式 AI 管理办法（本章 model-registry §合规字段是工程落地）
- [Guardrails §7 Red Teaming](../ai-workloads/guardrails.md) —— 工程护栏 + 对抗测试方法
- [LLM Inference](../ai-workloads/llm-inference.md) —— LLM 推理栈（vLLM / SGLang 等）
