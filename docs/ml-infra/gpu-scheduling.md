---
title: GPU 调度
type: concept
depth: 资深
prerequisites: [training-orchestration, model-serving]
tags: [ml-infra, gpu, scheduling, k8s]
related: [training-orchestration, model-serving, cost-optimization]
systems: [kubernetes, ray, volcano, yunikorn]
status: stable
---

# GPU 调度

!!! tip "一句话理解"
    把有限的 GPU 资源**公平、高效、可抢占**地分给训练、推理、探索三类负载。LLM 时代 GPU 成本占 AI 基础设施 50%+，调度效率直接 = 成本效率。

!!! abstract "TL;DR"
    - K8s 原生 GPU 支持够用但**不擅长 gang scheduling**（需要多卡同时就位）
    - **Volcano / YuniKorn** 填 K8s 在批任务调度的缺
    - **GPU 共享**：MIG（NVIDIA A100+）硬隔离；**time-slicing** / **MPS** 软隔离
    - **抢占** 是多租户关键：训练可中断、推理不可中断
    - 碎片整理比想象中重要：N 张 4 卡节点 vs 1 张 32 卡节点差很多

## 三类 GPU 负载的诉求不同

| 负载 | 特点 | 调度诉求 |
| --- | --- | --- |
| **在线推理** | 持续运行、延迟敏感 | 独占 + 高可用 |
| **训练** | 长任务（几小时到几天）、需要 N 卡同时就位 | Gang scheduling + 抢占 |
| **探索 / 开发** | 短、可中断、碎片化 | 共享 + 快速回收 |

**核心冲突**：推理不能被抢，训练要一次要多卡，探索希望随时上车。

## GPU 共享与隔离

### MIG（Multi-Instance GPU）

NVIDIA A100 / H100 硬件级切分：一张卡切成 7 个"子 GPU"，各自独立内存 + SM。

- **隔离最好**（性能不互相影响）
- **灵活性差**（切分模式预设）
- 适合混合推理负载

### MPS（Multi-Process Service）

多个 CUDA 进程共享一张卡，上下文隔离但 SM 共享。

- 更灵活
- **有互相影响**（一个大作业挤小的）

### Time-Slicing（K8s Device Plugin）

NVIDIA Device Plugin 的 `time-slicing` 模式：K8s 把一张卡声明为 N 份，轮转调度。

- 最简单
- **不是真并行**（不适合高吞吐推理）

## K8s 调度器的局限

原生 K8s Scheduler 基于 **pod-at-a-time**。对 AI 不友好：

- **Gang scheduling 缺**：PyTorchJob 的 16 个 worker 需要同时启动，K8s 默认可能只排到 15 个等第 16 个（死锁）
- **Queue / Priority** 弱：训练队列、推理队列、探索队列的 SLA 不同
- **抢占策略**：默认 priority 抢占不够精细

## 补充调度器

### Volcano

K8s 原生的**批调度器**：

- **Gang scheduling**：要么全启动要么都不启动
- **Queue** + **Priority**
- **Fair share** 保障多租户
- PodGroup 抽象

```yaml
apiVersion: batch.volcano.sh/v1alpha1
kind: Job
spec:
  minAvailable: 16
  plugins:
    env: []
    svc: []
  tasks:
    - replicas: 16
      name: worker
      template: {...}
```

**适合**：K8s 原生团队、训练作业多。

### YuniKorn

另一个批调度器，Queue / Fair / DRF 等策略。

### Ray

Ray 自己调度，K8s 只给它分资源块。Ray 内部做 actor 级调度，适合 Ray 原生团队。

## 抢占策略

多租户必备：

| 负载类型 | 可否被抢占 |
| --- | --- |
| 在线推理 P0 | ❌ |
| 在线推理 P1（可降级） | ⚠️ 降级而非抢占 |
| 批训练（短） | ✅ 从 checkpoint 恢复 |
| 批训练（长）| ⚠️ 只能周末抢 |
| 交互式探索 | ✅ 秒级抢 |

**训练作业必须支持 checkpoint + 断点续训**，否则抢占成本爆。

## 碎片问题

假设集群 64 张 H100，4 台节点 × 16 卡。有 3 个作业：
- A：16 卡（刚好一整台）
- B：8 卡
- C：12 卡

如果 A 占满一台，剩下 3 台共 48 卡：
- B 放进一台，剩 8 卡
- C 要 12 卡，任何一台都不够（碎片！）

**碎片整理**：
- **装箱算法**（best-fit / worst-fit）
- **Topology-aware scheduling**（考虑 NVLink 拓扑）
- **预判式调度**（看队列里未来作业）

Volcano 支持一些 binpack 插件；大规模团队往往自研。

## 成本控制的几招

- **混部**：低优先级推理 + 批训练错峰
- **Spot 实例**：训练跑 spot（checkpoint 频繁就行）；推理不跑 spot
- **弹性扩缩**：夜间降推理规模，把卡让给训练
- **Cache 模型权重**：pod 重启不从对象存储重拉（nfs / local ssd cache）
- **监控 GPU 利用率**：< 60% 说明调度或代码有问题

## 典型部署拓扑

```
集群划分:
- 推理池:     A10 × N, 独占
- 训练池:     H100 × N, 可抢占
- 探索池:     A10 / 消费卡 × N, 共享 MIG
  
跨池借用: 夜间训练池借推理池
```

**不要所有 GPU 混一池**——SLA 做不出来。

## 陷阱

- **MIG 切了但配置不更新** —— K8s 认为还是整张卡
- **NCCL 跨节点慢** —— 没配 IB 或 RoCE
- **训练作业不做 checkpoint** —— 抢占 = 白干几小时
- **推理 HPA 基于 CPU 扩**（GPU 100% 但 CPU 不紧张）—— 基于 GPU utilization 或 request queue depth
- **忽略 NUMA / PCIe 拓扑** —— 分配的 GPU 跨 socket 通信慢

## 相关

- [训练编排](training-orchestration.md)
- [Model Serving](model-serving.md)
- [成本优化](../ops/cost-optimization.md)

## 延伸阅读

- Volcano: <https://volcano.sh/>
- NVIDIA MIG docs
- *Heterogeneity-Aware Cluster Scheduling Policies for Deep Learning Workloads*（OSDI 2020）
- *Gandiva*（OSDI 2018，GPU 集群调度经典）
