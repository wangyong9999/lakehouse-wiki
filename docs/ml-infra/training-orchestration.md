---
title: 训练编排
type: concept
depth: 进阶
prerequisites: [offline-training-pipeline]
tags: [ml-infra, training, kubeflow, ray]
related: [offline-training-pipeline, gpu-scheduling, model-registry]
systems: [kubeflow, flyte, ray-train, pytorch-lightning]
status: stable
---

# 训练编排

!!! tip "一句话理解"
    把**模型训练**作为一个可调度、可重跑、可扩展、可监控的**分布式作业**。核心挑战：数据并行 / 模型并行 / 多 GPU 多 node 同步 / checkpoint / 故障恢复。

!!! abstract "TL;DR"
    - 单机多卡用 **PyTorch DDP / DeepSpeed**
    - 多机多卡 + 编排用 **Ray Train / Kubeflow PyTorchJob / Flyte**
    - LLM 级训练（70B+）需要 **FSDP / ZeRO-3 + Tensor Parallel + Pipeline Parallel** 组合
    - **Checkpoint** 要写到对象存储，不是本地盘
    - 和 [Model Registry](model-registry.md) 闭环：训完自动注册

## 分三个规模

### 规模 A：单机多卡（1 台 8 卡）

**DDP（Distributed Data Parallel）** 够用：

```python
import torch.distributed as dist
dist.init_process_group("nccl")
model = DDP(model, device_ids=[local_rank])
```

大部分 < 7B 的模型在 8×A100 / H100 能跑。编排系统只需"启动 8 个 process"。

### 规模 B：多机多卡（几十台）

需要：

- **NCCL / GLOO** over Infiniband
- 启动协调（每台机启几个 process、互相找）
- Checkpoint 同步

**主流工具**：

- **Kubeflow PyTorchJob** —— K8s CRD，原生 PyTorch 分布式
- **Ray Train** —— Python 原生，集成 Ray Data / Ray Tune
- **Flyte** —— K8s 上的工作流 + ML 一体化

### 规模 C：LLM 级（70B+）

单机装不下整个模型，需要**并行**：

- **Tensor Parallel**（TP）：一层的权重切到多 GPU
- **Pipeline Parallel**（PP）：不同层在不同 GPU
- **FSDP / ZeRO-3**：参数 + 优化器状态 + 梯度全分片

典型组合：**DP × PP × TP = N GPUs**。

工具：

- **DeepSpeed**（微软）—— ZeRO-1/2/3，最成熟
- **Megatron-LM**（NVIDIA）—— TP + PP
- **FSDP**（PyTorch 官方）—— 和 Megatron 有些重合但社区推动快

## 编排系统选择

### Ray Train

```python
from ray.train import ScalingConfig
from ray.train.torch import TorchTrainer

trainer = TorchTrainer(
    train_fn,
    scaling_config=ScalingConfig(num_workers=16, use_gpu=True),
    run_config=RunConfig(
        storage_path="s3://checkpoints/job_123",
    ),
)
result = trainer.fit()
```

**优点**：Python 原生，和 Ray Data 读湖表天然集成；动态 scaling。
**适合**：Spark / Ray 生态。

### Kubeflow

```yaml
apiVersion: kubeflow.org/v1
kind: PyTorchJob
spec:
  pytorchReplicaSpecs:
    Master:
      replicas: 1
      template: {...}
    Worker:
      replicas: 16
      template: {...}
```

**优点**：K8s 原生，和集群治理一套；多框架 CRD（TFJob / MPIJob 同类）。
**适合**：K8s 重、平台团队。

### Flyte

**优点**：工作流 + ML 一体化；Python 友好。
**适合**：数据 + ML 混合场景。

## Checkpoint 策略

- 位置：**对象存储**（S3 / GCS），不能是本地 EBS
- 频率：每 N 步 / 每 epoch；对大模型每 100 步
- 保留：最近 K 个 + 最佳 metric 的
- 异步写：训练不等 checkpoint 写完就继续

**灾难恢复**：一台机挂了，从最近 checkpoint 重启；理想情况能在 10 分钟内恢复。

## 训练数据读取

湖上训练集的两条路：

### 路径 1：Ray Data + Parquet / Lance

```python
ds = ray.data.read_parquet("s3://.../train/")
ds = ds.random_shuffle()
for batch in ds.iter_batches(batch_size=1024):
    train_step(batch)
```

**Lance format** 在随机访问 + shuffle 场景明显优于 Parquet，见 [Lance Format](../foundations/lance-format.md)。

### 路径 2：PyTorch Dataset + Lance

```python
import lance
ds = lance.dataset("s3://.../train.lance")
loader = DataLoader(ds, batch_size=1024, num_workers=8, shuffle=True)
```

Lance 的 per-row random access 让 `shuffle=True` 不再是性能杀手。

## 和 Model Registry 的闭环

训练作业结束的最后一步：

```python
import mlflow
mlflow.log_params(...)
mlflow.log_metrics(...)
mlflow.pytorch.log_model(model, "model", registered_model_name="my_model")
```

自动进 Registry，闭环完整。

## 陷阱

- **Checkpoint 写本地磁盘** —— 机器挂全丢
- **数据加载成瓶颈** —— GPU 空闲等数据（用 `nvidia-smi` 和 `py-spy` 确认）
- **Batch size 太小** —— GPU 跑不饱
- **分布式超参没调** —— DDP 需要调学习率（通常随 world size 线性缩放）
- **没做 gradient clipping** → NaN loss
- **把 debug log 全写出来** → 日志 I/O 拖慢训练

## 监控

- GPU 利用率（`nvidia-smi` → Prometheus node-exporter）
- loss 曲线 / 评估 metric
- 每 step 时间 / 数据加载时间 / 反向传播时间
- Checkpoint 写入延迟
- 通信开销（NCCL all-reduce 时间）

## 相关

- [离线训练数据流水线](../scenarios/offline-training-pipeline.md)
- [Lance Format](../foundations/lance-format.md)
- [Model Registry](model-registry.md)
- [GPU 调度](gpu-scheduling.md)

## 延伸阅读

- Ray Train: <https://docs.ray.io/en/latest/train/>
- Kubeflow Training Operator: <https://www.kubeflow.org/docs/components/training/>
- DeepSpeed: <https://www.deepspeed.ai/>
- *Scaling Distributed Machine Learning with the Parameter Server*（OSDI 2014，历史经典）
