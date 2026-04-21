---
title: Model Registry · 版本 · Alias · Model Card · 合规
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: MLflow 2.9+（alias API）· Unity Catalog Models · W&B Artifacts · HF Hub · OCI Model Artifacts · Databricks Model Registry · 2024-2026 实践
prerequisites: [feature-store, unified-catalog-strategy]
tags: [ml-infra, model, registry, model-card, compliance]
aliases: [模型注册中心, Model Registry, Model Card]
related: [feature-store, model-serving, model-monitoring, unity-catalog, data-governance, fine-tuning-data, ai-governance]
systems: [mlflow, unity-catalog, wandb, databricks, huggingface-hub, oci]
status: stable
---

# Model Registry

!!! tip "一句话定位"
    模型的 Catalog —— 每个模型是一个**带版本 · alias · 血缘 · Model Card · BOM · 审批**的一等资产。没有 Registry = 模型部署全靠 Wiki + 口口相传 + 合规事故。

!!! abstract "TL;DR"
    - **核心六件事**：artifact 存储 · 版本 · **alias**（MLflow 2.9+ 取代 deprecated stage）· 元数据 · 血缘 · 审批
    - **三大主流**：**MLflow**（开源事实标准）· **Unity Catalog Models**（数据模型同治）· **W&B Artifacts**（experiment 衔接）
    - **2026 新趋势**：OCI Model Artifacts · Iceberg-managed model · HF Hub 作企业 registry · ModelCar（KServe）
    - **LLM-specific artifacts**：LoRA adapter · merged model · prompt template · quantized variant · embedding model 都应作 first-class
    - **合规必需**：Model Card（EU AI Act 高风险系统）· Model BOM / SBOM · 许可链路（Llama / Gemma）
    - **序列化安全**：pickle CVE 实锤 · 推荐 safetensors
    - **alias API 是 2026 默认**：champion / challenger 替代 Staging / Production

## 1. Registry 至少做六件事

1. **artifact 存储** —— 权重文件（`.safetensors` / `.bin` / `.gguf` / tar.gz）存对象存储 · URI 进元数据
2. **版本管理** —— `v1, v2, v3` · 不可覆盖 · 每次训练新版
3. **Alias 流转**（2026 推荐）—— `champion` / `challenger` / `canary` / `production` 任意命名 · 动态指向 version
4. **元数据** —— 训练指标 · dataset snapshot · 超参 · 训练时间 · 代码 commit
5. **血缘** —— 上游 Iceberg snapshot · 训练作业 · 代码 commit · 训练者身份
6. **审批 + 合规** —— Model Card · BOM · License · 权限 · 推送 gate

## 2. Alias API · MLflow 2.9+ 的范式迁移

!!! warning "范式变化 · 不可忽略"
    **MLflow 2.9+ 起 `transition_model_version_stage` 与 stages 语义（None/Staging/Production/Archived）已 deprecated** · 2026 默认用 **alias**。老仓库大量 `stage="Production"` 写法要迁移。

### 2.1 旧（deprecated）

```python
# ❌ 2.9+ 已不推荐
client.transition_model_version_stage(
    name="recsys_v3", version=5, stage="Production"
)
model = mlflow.sklearn.load_model("models:/recsys_v3/Production")
```

### 2.2 新（推荐）

```python
# ✅ alias API · 灵活命名 · 动态切换
client.set_registered_model_alias(
    name="recsys_v3", alias="champion", version=5
)
model = mlflow.sklearn.load_model("models:/recsys_v3@champion")

# 多 alias 并存（champion + challenger + canary）
client.set_registered_model_alias("recsys_v3", "challenger", 6)
client.set_registered_model_alias("recsys_v3", "canary", 6)
```

### 2.3 Alias 用途 · 和 Canary / Rollback 协同

- `champion` → 线上主版本
- `challenger` → 常态化训练的挑战者（见 [model-monitoring](model-monitoring.md) §champion/challenger）
- `canary` → 灰度流量指向
- `previous` → 回滚目标
- `staging` → 预发环境

**Rollback 一行切回**：`set_registered_model_alias("recsys_v3", "champion", PREVIOUS_VERSION)`。详见 [Model Serving §Rollback runbook](model-serving.md)。

## 3. 工具选型 · 2026 视角

| 工具 | 类型 | 优势 | 适合 |
|---|---|---|---|
| **MLflow** | OSS · 事实标准 | 最广集成 · alias API 齐全 | 通用 · 开源栈默认 |
| **Unity Catalog Models**（Databricks OSS）| 湖仓一等 | **模型 / 数据 / 特征一套 RBAC** · 血缘跨 ML/BI | Databricks 客户 · 强合规 |
| **W&B Artifacts** | 商业 · experiment 衔接 | experiment + model 一体 · artifact 依赖图 | W&B 已用户 |
| **Hugging Face Hub**（企业版）| 社区 + 商业 | 模型卡 · 社区生态 · 直接推理 | LLM / 开放模型为主 |
| **SageMaker Model Registry** | AWS 托管 | 和 SageMaker 生态集成 | AWS 深度用户 |
| **Vertex AI Model Registry** | GCP 托管 | 和 Vertex pipelines 集成 | GCP 深度用户 |
| **KServe ModelMesh / ModelCar** | K8s 原生 | 多模型共享 pod · OCI 格式 | 大规模多模型 K8s |
| **自建**（S3 + Postgres） | 手工 | 极简可控 | 小团队 · 不推荐长期 |

**默认推荐**：
- 开源湖仓栈 → **MLflow**
- Databricks 用户 → **Unity Catalog Models**
- LLM 开放模型 → **HF Hub** + **MLflow**（hybrid）

## 4. 主流工具代码 · MLflow

```python
import mlflow

# 训练后注册
with mlflow.start_run():
    mlflow.log_params(params)
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(
        model, "model",
        registered_model_name="churn_predictor"
    )

# MLflow 2.9+ alias
client = mlflow.MlflowClient()
client.set_registered_model_alias(
    name="churn_predictor", alias="champion", version=5
)

# 下游加载
model = mlflow.sklearn.load_model(
    "models:/churn_predictor@champion"
)
```

## 5. Unity Catalog Models · 治理强

```python
# 模型作为 UC 资产（三段式 catalog.schema.name）
mlflow.set_registry_uri("databricks-uc")
mlflow.register_model(
    model_uri="runs:/abc123/model",
    name="main.ml_models.churn_predictor"
)
```

**治理价值**：
- 权限、血缘、审计**和数据表一套**（同一 RBAC）
- 行列级 policy 对应到"哪个角色能读 / 部署这个模型"
- 跨环境（dev / staging / prod catalog）提升流程统一

**适合**：一体化湖仓 · 强合规（金融 · 医疗 · 政府）。

## 6. 2026 新趋势 · Model Artifact 格式

### 6.1 OCI Model Artifacts（Container 即 Model）

- 模型打包为 OCI 镜像 · 用 Docker / ORAS 推送
- **ModelCar**（KServe 2024）：OCI artifact + init container 加载到 serving pod
- **优势**：复用容器生态（镜像扫描 · SBOM · signature · Cosign 签名）
- **适合**：K8s 重、要求 artifact 供应链安全的团队

### 6.2 Iceberg-managed Model Artifact（2025+ 方向）

- Databricks / 部分平台把**模型权重作 Iceberg 表**存储
- 好处：和数据共用 snapshot / time travel / ACL / 血缘
- 争议：大权重（几百 GB）存 Iceberg 是否高效 · 业界未收敛

### 6.3 安全格式 · safetensors 替代 pickle

!!! danger "安全红线 · pickle 反序列化 CVE"
    `pickle.load()` / `torch.load()`（默认）本质是**执行代码** · 加载恶意 `.pkl` / `.pt` 可任意代码执行。
    
    - HuggingFace Hub 已强制扫描 pickle · 推荐 **safetensors**（只读张量 · 无代码路径）
    - 企业 Registry 应**阻断 pickle 上传**或强制扫描
    - 历史 `.pt` / `.pkl` 要 audit 来源

```python
# ✅ 推荐
from safetensors.torch import save_file, load_file
save_file(state_dict, "model.safetensors")

# ⚠️ 风险
torch.save(state_dict, "model.pt")  # pickle-based · 加载 = 执行代码
```

## 7. LLM-specific Artifact 治理

LLM 时代 · Registry 要治的"模型"远不止"单一权重文件"：

| Artifact 类型 | 存储 | 元数据要点 |
|---|---|---|
| **Base model** | safetensors / GGUF | license（Llama Community · Gemma 条款） |
| **LoRA adapter** | safetensors（几 MB-几百 MB） | **绑 base model 版本** · rank · target modules · 训练数据版本 |
| **Merged model** | 完整权重 | merged source（base + adapter 来源追溯） |
| **Quantized variant** | GGUF / AWQ / GPTQ | 量化方法 · 精度损失 metric |
| **Prompt template** | JSON / YAML | version · owner · 评估集（见 [prompt-management](../ai-workloads/prompt-management.md)） |
| **Embedding model** | safetensors | 模型版本（BGE / e5 / jina）· 维度 · MTEB |
| **Reward model** | safetensors | RLHF 用 · 训练偏好数据版本 |

### 7.1 LoRA adapter 绑 base 版本

```python
mlflow.log_artifact("lora_adapter/", "adapter")
mlflow.log_params({
    "base_model": "meta-llama/Meta-Llama-3.1-8B",
    "base_model_sha": "6a0e6e1...",  # 关键：锁 base 版本
    "adapter_type": "lora",
    "lora_rank": 64,
    "lora_alpha": 32,
    "lora_target_modules": "q_proj,k_proj,v_proj,o_proj",
    "training_dataset_version": "customer_sft_v3",
})
```

**关键**：adapter 不绑 base 版本 → base 升级 adapter 行为变（甚至失效）。

### 7.2 Multi-LoRA serving（vLLM 2024+）

Registry 要支持"一个 base + N 个 adapter"的注册模式 · 部署时按请求切换 adapter。

## 8. Model Card · EU AI Act 合规必需

**Model Card** 是 Registry 里的**合规 artifact** · 不是可选 · 不是 marketing。

### 8.1 最小 schema

```yaml
# 示例 model_card.yaml
model:
  name: customer_support_v3
  version: 12
  task: text-generation
  base_model: meta-llama/Meta-Llama-3.1-8B
  license: llama-3.1-community-license

intended_use:
  primary: 客服多轮对话辅助
  out_of_scope: [医疗诊断, 法律建议, 金融交易决策]
  user_groups: [企业内部客服 · 非终端消费者直接使用]

training_data:
  sources: [客服对话日志 2024-Q3 · 合成 Evol-Instruct]
  size: 50000 SFT + 8000 DPO pair
  snapshot: "iceberg.finetune.sft_v3@snapshot-1234567890"
  pii_scrubbing: enabled
  consent: "用户条款 v2.3"

evaluation:
  benchmarks:
    - mt-bench: 8.1 / 10
    - domain_golden_set: 85% pass rate
  known_failures: [金融术语容易错 · 多语言混杂时变差]

fairness:
  subgroup_metrics:
    - demographic_parity_gap: 0.03
    - equalized_odds_gap: 0.05
  audit: "2026-04-15 · 第三方审计报告 #AX-1203"

safety:
  red_teaming: "2026-04-10 · Red-team report #RT-22"
  known_jailbreaks_patched: [prompt_injection_v1, role_hijack]

compliance:
  eu_ai_act_classification: "limited risk（非高风险）"
  gdpr_pii_inventory: "见附件 data_inventory.pdf"
  unlearning_tickets: "遵守被遗忘权 · 合规接口 /unlearn"

maintenance:
  owner: team-ai-platform@corp
  slo: "p99 < 500ms · uptime 99.9%"
  next_review: 2026-07-01
```

### 8.2 合规法规映射

- **EU AI Act**（2024-08 生效 · 2026 全量合规窗口）：高风险系统**必须**有技术文档 · Model Card 是核心组成
- **美国 NIST AI RMF**：推荐 model documentation
- **中国《生成式 AI 服务管理办法》**：模型备案 + 安全评估
- **GDPR**：自动化决策可解释性 + 数据来源透明

## 9. Model BOM / SBOM

类比软件 SBOM · **Model BOM** 记录：
- Base model + 许可
- 依赖库版本（transformers / peft / trl）
- 训练数据版本
- 推理依赖（CUDA / TensorRT / vLLM）
- 供应链签名（Cosign / Sigstore）

**作用**：
- 安全漏洞响应（某 base model 被曝问题 → 快速查谁在用）
- 许可合规（Llama Community 许可限制 · 自动 scan）
- 供应链攻击防御（artifact 签名验证）

## 10. 模型 ↔ 训练集绑定 · 复现契约

训练出模型时必须在 metadata 里记：

```yaml
model_name: recsys_v3
model_version: 12
source_code: https://github.com/.../commit/abc123
training_dataset_id: recsys-v3-2026-03
training_dataset_snapshots:
  facts: 12345      # Iceberg snapshot-id
  features: 54321
trained_at: 2026-04-01T10:30:00Z
trained_by: user@corp
trained_with:
  framework: pytorch
  hparams: {...}
metrics:
  recall@10: 0.87
  mrr: 0.74
```

一年后复现该模型时 · 这条 metadata 就是契约。

## 11. 许可与商用限制

**Llama / Gemma / Mistral 等开源 LLM 的商用条款不是都一样**：

| 模型 | 许可 | 商用限制 |
|---|---|---|
| Llama 3 / 3.1 | Llama Community License | **7 亿 MAU 以上需单独授权** · 不得用于训练竞品 LLM |
| Gemma | Gemma Terms of Use | 相对宽松 · 但有使用政策 |
| Mistral / Mixtral（开源系列） | Apache 2.0 | 商用友好 |
| Qwen | 多种许可 · 分版本 | 看具体版本 |
| DeepSeek 系列 | MIT / 自有许可 | 看版本 |

**Registry 的作用**：
- 每个模型挂许可字段
- 派生模型（fine-tuned / merged）继承限制
- 自动扫描告警（某 LoRA 基于 Llama 3 · MAU 快到 7 亿）

## 12. Stage 流转 vs Environment（澄清）

老式 stage（Staging / Production / Archived）概念**不等于 environment**（dev / staging / prod）。MLflow 2.9+ 推荐**解耦**：

- **Environment 隔离**：用不同 **tracking server** 或不同 **UC catalog**（main_dev / main_prod）
- **模型生命状态**：用 **alias**（champion / challenger / canary）
- **不要**在一个 server 里用 stage 表示 env（老做法 · 权限和血缘都不纯）

## 13. 和 Feature Store / Serving 协作

```
Feature Store        ← online + offline 特征
        ↓
Model Registry       ← 模型 + 版本 + alias + Model Card
        ↓
Model Serving        ← 部署 alias@champion + 拉特征
        ↓
Model Monitoring     ← 监控 + 漂移告警 → 回 Registry 推 challenger
```

## 14. 审批工作流 runbook

高风险场景（风控 · 医疗 · HR · 金融决策）**必须**有人工审批：

```
1. 训练完成 · 注册 version N · 默认 alias=none
2. 自动化测试（单测 · inference smoke · fairness check）通过 → alias=candidate
3. Shadow 24h · 对账通过 → alias=challenger
4. Canary 1% × 24h · 业务 KPI 不退化 → **人工审批 gate**
5. 审批通过 → alias=champion（rollback 旧版 alias=previous）
6. 30 天稳定 → alias=stable
7. 被替换的旧版 → alias=archived（不立刻删 · 便于回滚）
```

**审批 gate 最少**：
- 负责业务指标的产品 PM
- 负责模型质量的 ML Lead
- 高风险领域还需要合规 / 法务

## 15. 陷阱 · 反模式

- **不注册直接部署**：复现不了、责任不清
- **Registry 和 Serving 分裂**（开发 MLflow · 部署用别的）：版本错位
- **元数据缺训练集版本**：一年后不知道训的什么数据
- **用 "latest" 部署**：昨晚某人训了个坏模型悄悄上线
- **Stages 还在用**（MLflow 2.9+）：迁 alias
- **LoRA adapter 不绑 base 版本**：base 升 adapter 失效
- **pickle 作 artifact**：反序列化 CVE 风险
- **忽略许可扫描**：Llama MAU 超限 · 法律风险
- **Model Card 敷衍**：审计 / 事故时没文档
- **新模型无守门直接 champion**：坏模型上线
- **archived 立即硬删**：回滚不了
- **Dev / Prod 没 catalog 隔离**：权限越界 · 事故锅难背
- **训练者身份不记**：事故追责困难

## 16. 相关

- [Feature Store](feature-store.md) —— 姊妹（训推一致的另一半）
- [Model Serving](model-serving.md) —— 起点（alias 热加载 / Rollback）
- [Model Monitoring](model-monitoring.md) —— 上线后守门
- [LLM Fine-tuning](fine-tuning-data.md) —— LoRA adapter 生产
- [Unity Catalog](../catalog/unity-catalog.md) —— UC Models
- [AI 治理](../frontier/ai-governance.md) —— EU AI Act 法规层
- [离线训练数据流水线](../scenarios/offline-training-pipeline.md)

## 17. 延伸阅读

- MLflow docs: <https://mlflow.org/>
- MLflow 2.9 release notes（alias API 引入）
- Unity Catalog Models: Databricks 文档
- safetensors: <https://huggingface.co/docs/safetensors>
- KServe ModelCar: <https://kserve.github.io/website/>
- EU AI Act 2024-08 · Annex IV 技术文档要求
- *Model Cards for Model Reporting*（Mitchell et al., FAT* 2019）
- Google People + AI Research Model Card Toolkit
