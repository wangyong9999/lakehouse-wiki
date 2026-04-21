---
title: Experiment Tracking · 研究 → 生产的桥梁
type: concept
depth: 进阶
level: A
last_reviewed: 2026-04-21
applies_to: MLflow 2.9+ · W&B · Neptune · Comet · Aim · ClearML · Optuna · Ray Tune · 2024-2026 实践
prerequisites: [mlops-lifecycle]
tags: [ml-infra, experiment-tracking, mlflow, wandb]
aliases: [实验追踪, Experiment Management]
related: [mlops-lifecycle, model-registry, training-orchestration, ml-evaluation, data-quality-for-ml]
systems: [mlflow, wandb, neptune, comet, aim, clearml, optuna, ray-tune]
status: stable
---

# Experiment Tracking

!!! tip "一句话定位"
    **研究阶段和生产阶段之间的桥梁**。每个训练运行（run）= 一个数据集 snapshot + 一组超参 + 一段代码 + 产出的 metric + artifact 的**可追溯 4 元组**。没有 Tracking = 跑过 1000 次训练后不知道哪次该 promote。

!!! warning "和 Model Registry 的分工"
    - **Experiment Tracking**（本页）：**运行级**（run / experiment）· 参数 · 指标曲线 · artifact 候选 · 多实验对比 · 超参搜索 · 大量 ephemeral 数据
    - **[Model Registry](model-registry.md)**：**模型级**（versioned model）· alias · Model Card · BOM · 合规 · 发布治理 · 长期归档
    - **桥梁**：Tracking 的一个 run 产出 artifact → 选择性 promote 到 Registry 成为 versioned model

!!! abstract "TL;DR"
    - **4 元组契约**：run = dataset snapshot + hparams + code commit + artifact/metric
    - **主流工具**：**MLflow**（OSS 标配）· **W&B**（商业主流 · UI 极好）· **Neptune** · **Comet** · **Aim**（轻量 OSS）· **ClearML**
    - **超参搜索工具**：**Optuna** · **Ray Tune** · **W&B Sweeps** —— 和 Tracking 深度集成
    - **Tracking → Registry 的 promote** 是关键路径设计
    - **保留策略**：99% 的 run 最终死掉 · 但 artifact 存储容易爆 · 需要分层保留
    - 和 [ml-evaluation](ml-evaluation.md) · [data-quality-for-ml](data-quality-for-ml.md) · [model-registry](model-registry.md) 形成闭环

## 1. 为什么独立一页 · 不是 Registry 的子集

一个典型训练团队一年可能跑 **数千 ~ 数万 run**：
- 超参搜索（Optuna · Ray Tune）· 一次 trial 100+ run
- Notebook 探索 · 数据科学家每天几十个
- CI 里跑的 smoke 训练 · 每次 PR 都有
- 模型回归测试 · 定期跑

这些 run **99% 不会成为生产模型**。但它们携带的信息（什么 hparams 没用 · 什么特征组合差 · 什么 random seed 不稳）对下一次**非常有价值**。

**Registry 管"成品"· Tracking 管"过程"**。合并会让 Registry 膨胀到无法管理。

## 2. 核心 4 元组契约

每个 run **必须**记录：

```yaml
run_id: abc123
experiment: recsys_v3_finetune
dataset:
  iceberg_table: lake.events.train
  snapshot_id: 1234567890   # 复现依赖
code:
  git_commit: a1b2c3
  git_dirty: false          # 本地没未提交修改
hparams:
  lr: 3e-4
  batch_size: 128
  model: resnet50
env:
  python: 3.11
  cuda: 12.4
  pytorch: 2.4
metrics:
  - step: 1000
    loss: 0.45
    val_auc: 0.87
  - step: 2000
    loss: 0.32
    val_auc: 0.89
artifacts:
  - model.safetensors
  - confusion_matrix.png
  - feature_importance.csv
status: finished | failed | running
owner: alice@corp
start_time: 2026-04-21T10:00:00Z
duration: 1h23m
```

**不记 `snapshot_id + git_commit` = 这个 run 不可复现** · 等于白跑。

## 3. 主流工具矩阵 · 2026 视角

| 工具 | 类型 | 优势 | 劣势 | 适合 |
|---|---|---|---|---|
| **MLflow** | OSS · 事实标准 | 集成最广 · Registry 一体 · alias API | UI 一般 · 大规模 server 性能瓶颈 | 开源栈默认 |
| **W&B**（Weights & Biases） | 商业 SaaS | **UI 最好** · sweeps + reports · 社区活跃 | 商业 · 数据出境敏感 | 商业预算 · 产品侧重 UI |
| **Neptune** | 商业 | 大规模 run 友好 · meta learning 场景 | 小众 | 大厂 · 实验数量极多 |
| **Comet** | 商业 | CV / NLP 模板多 · 协作好 | 中规中矩 | 中型团队 |
| **Aim** | OSS · 轻量 | 本地优先 · 无依赖 server · 快 | 生态小 | 个人 / 小团队 |
| **ClearML** | OSS + 商业 | 自动化多 · 远程执行 | 复杂 | 需要 pipeline + tracking 一体 |
| **Tensorboard** | OSS · Google | 曲线基础 · 和 PyTorch/TF 集成 | 非实验管理工具 · 只是 logging | 早期 + 补充 |
| **Databricks Tracking** | 托管 · MLflow 背后 | UC 集成 | 锁定 | Databricks 客户 |

**默认推荐**：
- 开源 · 通用 → **MLflow**
- 预算足 · UI 重要 → **W&B**
- 个人 · 无 server → **Aim**

## 4. 典型代码 · MLflow

```python
import mlflow
import mlflow.pytorch
from mlflow.tracking import MlflowClient

mlflow.set_experiment("recsys_v3_finetune")

with mlflow.start_run() as run:
    # 4 元组
    mlflow.log_params({
        "lr": 3e-4,
        "batch_size": 128,
        "model": "resnet50",
    })
    mlflow.log_param("iceberg_snapshot", "1234567890")
    mlflow.log_param("git_commit", os.environ["GIT_COMMIT"])

    # 训练 loop · 每 step log
    for step, (loss, auc) in training_loop():
        mlflow.log_metrics(
            {"loss": loss, "val_auc": auc},
            step=step,
        )

    # artifact
    mlflow.pytorch.log_model(model, "model")
    mlflow.log_artifact("confusion_matrix.png")

    # 不一定要 register 到 Registry · 只是 run 级 artifact
    # 真正 promote 时才去注册：
    # mlflow.register_model(f"runs:/{run.info.run_id}/model", "recsys_v3")
```

**关键**：`log_model`（run 内 artifact）和 `register_model`（Registry 一等 version）**分离**。前者是"探索"· 后者是"发布"。

## 5. 超参搜索 · Optuna / Ray Tune

超参搜索是 Tracking 高产 run 的主要源。典型整合：

### Optuna + MLflow

```python
import optuna
import mlflow

def objective(trial):
    lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
    batch = trial.suggest_categorical("batch_size", [32, 64, 128, 256])

    with mlflow.start_run(nested=True):
        mlflow.log_params({"lr": lr, "batch_size": batch})
        auc = train_eval(lr, batch)
        mlflow.log_metric("val_auc", auc)
        return auc

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
```

### Ray Tune + MLflow

```python
from ray import tune
from ray.air.integrations.mlflow import MLflowLoggerCallback

tuner = tune.Tuner(
    train_fn,
    param_space={
        "lr": tune.loguniform(1e-5, 1e-2),
        "batch_size": tune.choice([32, 64, 128, 256]),
    },
    run_config=tune.RunConfig(
        callbacks=[MLflowLoggerCallback(experiment_name="hpo_recsys")],
    ),
)
results = tuner.fit()
```

### W&B Sweeps

原生的 `wandb sweep + wandb agent` 组合 · UI 内建的超参可视化最强。

## 6. Promote · Tracking → Registry 的关键路径

run 怎么从"探索"变成"生产 artifact"· 是整条管线最关键的设计：

```
所有 run（万级）
    ↓
筛选 · 主 metric 前 N%（Tracking 查询）
    ↓
离线评估完整跑（ml-evaluation）
    ↓
Data Quality 守门（data-quality-for-ml §评估集泄漏）
    ↓
人工 review · 或自动化 gate
    ↓
mlflow.register_model(run_id, name) → Registry version N
    ↓
set_registered_model_alias(name, "challenger", version=N)
    ↓
Shadow / Canary / A/B（model-serving / ml-evaluation）
    ↓
alias champion 切换（model-registry）
```

**反模式**：直接 `mlflow.register_model(..., "my_model")` 训练结束自动注册 · 结果 Registry 被超参搜索的 100 个 trial 塞满 · 根本看不到哪个是真正想要的。

## 7. 组织 run · Experiment / Tag / 分组

### Experiment 层次

- **Project**（ML 问题）· **Experiment**（某版本 / 某实验问题）· **Run**（一次具体跑）
- 例：`recsys` / `v3_lora_finetune` / run abc123

### Tag 规范

每个 run 标签应至少有：
- `team`（哪个 team 的）
- `task`（classification / ranking / generation）
- `model_family`（resnet / xgboost / llama）
- `purpose`（hpo-trial / candidate / smoke-test）
- `ticket`（关联的 JIRA / Linear 卡）

Tag 规范混乱 → 半年后没人能从 UI 里筛出想要的 run。

## 8. 保留策略 · artifact 存储爆炸

**典型现实**：
- 1000 次超参 run × 500MB 每个模型 artifact = **500GB**
- 没有保留策略 → 一年存几 TB · 99% 没人看

**分层保留**：
- **Registered model artifact**（Registry 里的）：**永久** · 合规审计
- **Run-level artifact · 主 metric 前 10%**：保留 6-12 月
- **其他 run artifact**：保留 30 天 · 过期自动删
- **metric / params**：永久（便宜）· artifact（贵）分开对待

### MLflow 实操

```python
# 定期 sweep 清理 · 删除 experiment 下低性能 run 的 artifact
client = mlflow.MlflowClient()
runs = client.search_runs(
    experiment_ids=["123"],
    filter_string="metrics.val_auc < 0.8",
    order_by=["start_time DESC"],
)
for run in runs:
    if is_older_than_30_days(run):
        client.delete_run(run.info.run_id)  # 保留 metadata · 清 artifact
```

## 9. 和 Data Quality / Evaluation 协同

一个严肃的 run 应当在 start / end 调用：

```
run start:
  ↓
  data_quality.validate(dataset_snapshot)   # data-quality-for-ml 守门
  ↓
  training loop + tracking
  ↓
run end:
  ↓
  ml_evaluation.offline_eval(run)           # ml-evaluation 多维指标
  ↓
  ml_evaluation.fairness_audit(run)         # ml-evaluation §Fairness
  ↓
  if all_pass: tag=candidate else: tag=failed-eval
```

三者形成闭环。Tracking 是**数据收集层** · 不是决策层 —— 决策由 Evaluation 做。

## 10. 团队协作视角

- **共享 Experiment Server**：团队用同一 MLflow server（带 DB 后端 · 不是本地 SQLite）
- **Report / Notebook 集成**：W&B Reports · MLflow recipes · 生成可分享 experiment summary
- **Pull Request 联动**：PR 触发 CI run · 结果以 Tracking link 评论回 PR
- **Ownership**：每个 experiment 有 owner · run 3 天无更新自动归档

## 11. 陷阱 · 反模式

- **不记 `git_commit` / `snapshot_id`**：run 不可复现 · 等于白跑
- **Tracking server 本地 SQLite 多人共享**：数据丢 / 锁死
- **把 Tracking 当 Registry**：run 数万个 · 根本找不到哪个 promote
- **超参搜索每 trial 都 register**：Registry 塞满垃圾
- **artifact 无保留策略**：存储几 TB · 99% 没人看
- **只记最终 metric 不记曲线**：debug 时发现过拟合看不出
- **Tag 命名混乱**（`exp1` / `exp_final` / `exp_v2_real`）：半年后不可搜
- **实验命名含义只在作者脑子里**：别人接手猜半天
- **不用 nested run**：超参搜索展平一锅粥 · 分组可视化失效
- **写代码没加 git_dirty 检查**：跑了本地未提交修改 · 代码在别处不存在
- **W&B / MLflow 云版 + 敏感数据**：合规事故（PII 写进 params）· 事前 scrub

## 12. 相关

- [MLOps 生命周期](mlops-lifecycle.md) §3 训练 —— 环节概览
- [Model Registry](model-registry.md) —— Promote 目标
- [ML Evaluation](ml-evaluation.md) —— 离线评估协同
- [Data Quality for ML](data-quality-for-ml.md) —— 数据守门
- [训练编排](training-orchestration.md) —— 训练作业
- [LLM Fine-tuning](fine-tuning-data.md) —— fine-tune 场景 tracking

## 13. 延伸阅读

- MLflow docs: <https://mlflow.org/>
- W&B docs: <https://docs.wandb.ai/>
- Neptune: <https://neptune.ai/>
- Aim: <https://aimstack.io/>
- Optuna: <https://optuna.org/>
- Ray Tune: <https://docs.ray.io/en/latest/tune/>
- *A Large-Scale Study on Regularization and Normalization in GANs*（Lucic et al., 2018 · 实验管理经典案例）
