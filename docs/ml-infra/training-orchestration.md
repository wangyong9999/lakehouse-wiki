---
title: 训练编排 · 分布式 · Context/Expert Parallel · 2026 刷新
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: Ray Train 2.9+ · Kubeflow Training Operator 1.8+ · Flyte 1.13+ · torchtitan 2024+ · FSDP2 · DeepSpeed 0.15+ · Megatron-LM · Metaflow 2.12+ · ZenML 0.67+ · 2024-2026 实践
prerequisites: [offline-training-pipeline]
tags: [ml-infra, training, kubeflow, ray, fsdp, context-parallel]
aliases: [训练编排, 分布式训练, Distributed Training]
related: [offline-training-pipeline, gpu-scheduling, model-registry, fine-tuning-data]
systems: [kubeflow, flyte, ray-train, torchtitan, deepspeed, megatron, pytorch-lightning, metaflow, zenml]
status: stable
---

# 训练编排

!!! tip "一句话理解"
    把模型训练作为一个**可调度、可重跑、可扩展、可监控**的**分布式作业**。核心挑战：**数据并行 / Tensor 并行 / Pipeline 并行 / Context 并行 / Expert 并行（MoE）/ checkpoint / 故障恢复**。

!!! abstract "TL;DR"
    - **单机多卡**：PyTorch DDP / **FSDP2**（2024 新代 · 替代 FSDP）/ DeepSpeed ZeRO
    - **多机多卡编排**：**Ray Train** / Kubeflow PyTorchJob / Flyte / Metaflow / ZenML
    - **LLM 级（70B+）**：**FSDP2 + TP + PP + Context Parallel + Expert Parallel**（2024-2026 标配）· **torchtitan** 官方 recipe
    - **Checkpoint**：**DCP**（Distributed Checkpoint · PyTorch 2.1+）· 写对象存储 · 异步
    - **数据**：Ray Data + Lance · 和 [feature-store](feature-store.md) / [offline-training-pipeline](../scenarios/offline-training-pipeline.md) 协同
    - **闭环**：训完自动注册到 [model-registry](model-registry.md) + alias

## 1. 分三个规模

### 规模 A · 单机多卡（1 台 8 卡）

**DDP** / **FSDP2** 二选一：

```python
import torch
import torch.distributed as dist
from torch.distributed.fsdp import fully_shard  # FSDP2 · PyTorch 2.4+

dist.init_process_group("nccl")

# DDP · 参数完整复制（简单 · 小模型）
model = torch.nn.parallel.DistributedDataParallel(
    model, device_ids=[local_rank]
)

# FSDP2 · 参数分片（省显存 · 7B+ 推荐）
model = fully_shard(model)  # 新 API · 替代 FSDP wrap_policy
```

- **DDP 适合**：< 7B 模型 · 8×A100/H100 内能完整复制
- **FSDP2 适合**：7B+ 模型 · 显存紧 · 新代 API 比 FSDP1 简洁稳定

### 规模 B · 多机多卡（几十台）

需要：
- **NCCL / GLOO** over InfiniBand / RoCE
- 启动协调（每台机启 N process · 互相找 rendezvous）
- Checkpoint 同步（**DCP** 分布式 checkpoint）
- 故障恢复（Elastic Training）

**编排工具矩阵**：

| 工具 | 定位 | 优势 | 适合 |
|---|---|---|---|
| **Ray Train** | Python-first · 集成 Ray Data/Tune | 动态 scaling · 湖表读取原生 | Python 生态 · Spark/Ray 并存团队 |
| **Kubeflow PyTorchJob** | K8s CRD · 多框架（TFJob / MPIJob）| K8s 原生治理 | 平台团队 · K8s 重 |
| **Flyte** | 工作流 + ML 一体 | DAG 化 · Python 友好 | 数据 + ML 混合场景 |
| **Metaflow**（Netflix）| Pythonic pipeline | 本地-云无缝 · S3 artifact 原生 | 数据科学家友好 |
| **ZenML** | pipeline 抽象层 | 跨工具 adapter（MLflow / Kubeflow / Ray） | 多工具并存想统一接口 |
| **SageMaker / Vertex AI / Azure ML** | 云托管 | 一键 · 不用管集群 | 云锁定已成事实 |

### 规模 C · LLM 级（70B+）· 多维并行

单机装不下整个模型 · 必须并行。2024-2026 典型组合：

**DP × TP × PP × CP × EP = world_size**

| 并行维度 | 作用 | 何时必需 |
|---|---|---|
| **DP**（Data Parallel） | 数据分片 · 每个 rank 跑同一模型 | 通用 |
| **TP**（Tensor Parallel） | 一层权重切到多 GPU · column/row split | 70B+ 模型 |
| **PP**（Pipeline Parallel） | 不同层在不同 GPU · micro-batch 流水 | 多节点跨机 |
| **CP**（Context Parallel · 2024）| 长 sequence 切到多 GPU | **长 context 训练（32K+ · 128K）** |
| **EP**（Expert Parallel · MoE） | MoE 专家切到多 GPU | **MoE 模型** · Mixtral / DBRX |
| **FSDP / ZeRO-3** | 参数 + 优化器状态 + 梯度全分片 | 替代 DP · 更省显存 |

### Context Parallel 的必要性（2024-2026 新）

- 长 context 训练（如 128K · 1M 上下文）· 单 GPU 显存装不下 KV / activation
- CP 把 sequence 维度切分 · 配合 Ring Attention / Flash Attention 3
- **必需于**：Long-context 模型训练 · 评估长文本任务

### Expert Parallel（MoE）

- Mixtral · DBRX · Qwen-MoE · DeepSeek-MoE 等 MoE 模型
- 专家（expert FFN）在不同 GPU 上 · token 路由决定去哪个专家
- 和 TP / PP 组合调优

### 主流训练工具（LLM 大模型向）

| 工具 | 维护者 | 优势 |
|---|---|---|
| **torchtitan**（2024 新）| PyTorch 官方 | 官方大规模训练 recipe · FSDP2 + TP + PP + CP 原生 · 代码简洁 |
| **Megatron-LM / Megatron-Core** | NVIDIA | TP + PP + CP + EP 完整 · 性能极致 · 但代码复杂 |
| **DeepSpeed** | 微软 | ZeRO-1/2/3 · ZeRO++ · 最成熟 · AutoTP |
| **FSDP / FSDP2** | PyTorch 官方 | ZeRO-3 对标 · 2024+ FSDP2 API 简化 |
| **MosaicML Composer**（Databricks）| Databricks | 企业级 · DBRX / Mosaic LLM 背后 |
| **veScale**（字节）| 字节跳动 | MoE 强 · 字节内部大模型 |

**2026 默认推荐**：
- 从 PyTorch 起步 · 追求简洁 → **torchtitan**
- 极致性能 + 已深用 NVIDIA → **Megatron-Core**
- Ecosystem 稳 + ZeRO 策略灵活 → **DeepSpeed**

## 2. 编排工具典型代码

### 2.1 Ray Train（Python 原生）

```python
from ray.train import ScalingConfig, RunConfig
from ray.train.torch import TorchTrainer
from ray.train import Checkpoint, CheckpointConfig

def train_fn(config):
    # 每个 worker 跑的代码
    import torch
    from torch.distributed.fsdp import fully_shard
    model = build_model()
    model = fully_shard(model)  # FSDP2
    # ... train loop ...

trainer = TorchTrainer(
    train_fn,
    scaling_config=ScalingConfig(num_workers=16, use_gpu=True),
    run_config=RunConfig(
        storage_path="s3://checkpoints/job_123",
        checkpoint_config=CheckpointConfig(
            num_to_keep=3,
            checkpoint_score_attribute="eval_loss",
            checkpoint_score_order="min",
        ),
    ),
)
result = trainer.fit()
```

**适合**：Python 原生 · Ray Data 读湖表天然集成 · 动态 scaling。

### 2.2 Kubeflow PyTorchJob

```yaml
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: llama-3-8b-sft
spec:
  elasticPolicy:
    rdzvBackend: c10d
    minReplicas: 4
    maxReplicas: 16
  pytorchReplicaSpecs:
    Worker:
      replicas: 8
      template:
        spec:
          containers:
            - name: pytorch
              image: axolotl:0.4
              resources:
                limits: {nvidia.com/gpu: 8}
```

**适合**：K8s 原生 · 多框架 CRD · Elastic Training 内置。

### 2.3 torchtitan · LLM 大模型训练

```bash
# torchtitan recipe 风格
CONFIG_FILE="./train_configs/llama3_70b.toml" \
  torchrun --nproc_per_node 8 train.py
```

torchtitan 的价值：
- PyTorch 官方维护 · API 跟 PyTorch 主线
- FSDP2 + TP + PP + CP + EP 组合**原生**支持
- recipe 即代码 · 复现容易

## 3. Checkpoint 策略

### 3.1 格式

- **`.safetensors`**（推荐）· 只读张量 · 无代码执行风险
- **`.pt` / `.bin`**（pickle-based）· 安全风险 · 加载恶意 ckpt 可 RCE
- **DCP**（Distributed Checkpoint · PyTorch 2.1+）· 分布式训练必备

### 3.2 DCP 分布式 checkpoint

传统 checkpoint 把分片的模型 gather 到单进程写 · 大模型不可行。**DCP** 让每个 rank 并行写自己的分片：

```python
import torch.distributed.checkpoint as dcp

# 写
dcp.save(
    state_dict=model.state_dict(),
    checkpoint_id="s3://ckpt/step_10000/",
)

# 读
dcp.load(
    state_dict=model.state_dict(),
    checkpoint_id="s3://ckpt/step_10000/",
)
```

好处：
- **并行**：每 rank 独立写 · O(1) 时间随 world size
- **断点续训**：可改变 world_size（训完 16 卡 · 用 8 卡恢复）· DCP 自动 reshard

### 3.3 策略

- 位置：**对象存储**（S3 / GCS）· 不能本地 EBS
- 频率：每 N 步 / 每 epoch · 大模型每 100 步
- 保留：**最近 K 个 + 最佳 metric**
- **异步写**：训练不等 checkpoint 落盘就继续

**灾难恢复**：机器挂 → 从最近 ckpt 重启 · 目标 10 分钟内恢复。

## 4. Elastic Training · 动态加减节点

2024+ PyTorch + Kubeflow 支持 **Elastic Training**：
- 节点突发加入 / 退出不 fail
- 配合 DCP reshard · 自动适配新 world_size
- **适合**：spot 实例 · 抢占式训练 · 节省大成本

## 5. `torch.compile` · 训练加速

PyTorch 2.1+ 的 `torch.compile` 对训练同样有效：

```python
model = build_model()
model = torch.compile(model, mode="reduce-overhead")
```

- 训练 1.3-2× 速度（依 model / batch 规模 `[来源未验证 · 经验值]`）
- 和 FSDP2 / DDP 兼容 · 但和某些自定义 CUDA kernel 可能冲突

## 6. 训练数据读取

### 路径 1 · Ray Data + Parquet / Lance

```python
import ray
ds = ray.data.read_parquet("s3://.../train/")
ds = ds.random_shuffle()

# 直接喂 Ray Train
trainer = TorchTrainer(
    train_fn,
    datasets={"train": ds},
    scaling_config=...,
)
```

**Lance format** 在**随机访问 + shuffle** 场景明显优于 Parquet · 见 [Lance Format](../foundations/lance-format.md)。

### 路径 2 · PyTorch Dataset + Lance

```python
# Lance 提供 torch 子包 · 正确用法：
from lance.torch.data import LanceDataset
from torch.utils.data import DataLoader

ds = LanceDataset(
    dataset="s3://.../train.lance",
    batch_size=1024,
    columns=["features", "label"],
    shuffle=True,
)
loader = DataLoader(ds, batch_size=None, num_workers=8)
```

**注意**：直接把 `lance.dataset(...)` 的返回喂 `DataLoader` 是错用法 · 需经 `lance.torch.data.LanceDataset` 适配。

### 路径 3 · Feature Store 衔接

离线训练从 [Feature Store](feature-store.md) 拉（`get_historical_features` + PIT Join）· 见 [offline-training-pipeline](../scenarios/offline-training-pipeline.md)。

## 7. 和 Model Registry 的闭环

训练作业结束的最后一步：

```python
import mlflow
mlflow.log_params(...)
mlflow.log_metrics(...)
mlflow.pytorch.log_model(
    model, "model",
    registered_model_name="my_model"
)

# MLflow 2.9+ alias（替代 deprecated stage）
client = mlflow.MlflowClient()
client.set_registered_model_alias(
    name="my_model", alias="challenger", version=...
)
```

然后走 [model-monitoring](model-monitoring.md) §Auto-retrain 契约 · 守门通过后 promote 到 champion。

## 8. 监控

- **GPU 利用率**（`nvidia-smi` → Prometheus node-exporter · dcgm-exporter）
- loss 曲线 / 评估 metric（MLflow / W&B 实时）
- 每 step 时间 · 数据加载时间 · 反向传播时间
- Checkpoint 写入延迟
- 通信开销（NCCL all-reduce / all-gather 时间）
- **Elastic**：节点加减事件

## 9. 陷阱 · 反模式

- **Checkpoint 写本地磁盘**：机器挂全丢
- **数据加载成瓶颈**：GPU 空闲等数据（`nvidia-smi` + `py-spy` 确认）
- **Batch size 太小**：GPU 跑不饱
- **分布式超参没调**：DDP / FSDP 需要调学习率（通常随 world size 线性缩放 · warmup 关键）
- **没做 gradient clipping**：NaN loss（大模型必做）
- **debug log 全开**：I/O 拖慢训练
- **用 `torch.save` 存 ckpt**：pickle CVE 风险 · 改用 DCP + safetensors
- **FSDP1 写法没迁 FSDP2**：2024+ 新代码应用 FSDP2（`fully_shard`）
- **Ray Train API 用老 `storage_path` 但没 `checkpoint_config`**：Ray 2.8+ 推荐显式 `CheckpointConfig`
- **长 context 训练不用 CP**：OOM · 或 activation 超载
- **MoE 训练不用 EP**：路由计算瓶颈
- **Lance + 原生 `DataLoader` 错用**：见 §6 路径 2 正确写法

## 10. 相关

- [离线训练数据流水线](../scenarios/offline-training-pipeline.md)
- [Feature Store](feature-store.md) —— 特征来源
- [Lance Format](../foundations/lance-format.md)
- [Model Registry](model-registry.md) —— 训完去哪
- [Model Monitoring](model-monitoring.md) —— 上线后
- [GPU 调度](gpu-scheduling.md) —— 底层资源
- [LLM Fine-tuning](fine-tuning-data.md) —— PEFT 训练专题

## 11. 延伸阅读

- torchtitan: <https://github.com/pytorch/torchtitan>
- Ray Train: <https://docs.ray.io/en/latest/train/>
- Kubeflow Training Operator: <https://www.kubeflow.org/docs/components/training/>
- DeepSpeed: <https://www.deepspeed.ai/>
- Megatron-Core: <https://github.com/NVIDIA/Megatron-LM>
- FSDP2 docs: PyTorch 2.4+ 文档
- DCP: <https://pytorch.org/docs/stable/distributed.checkpoint.html>
- *Ring Attention with Blockwise Transformers*（Liu et al., 2023 · Context Parallel 基础）
- *Switch Transformer*（Fedus et al., 2021 · MoE / Expert Parallel）
