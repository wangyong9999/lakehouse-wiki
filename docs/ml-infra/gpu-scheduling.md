---
title: GPU 调度 · 多租户 · Topology · FinOps
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: Kubernetes 1.30+ · Volcano 1.9+ · YuniKorn 1.5+ · Run:ai · Karmada 1.11+ · AWS Capacity Blocks · GCP DWS · NVIDIA GB200/H200/B200 · AMD MI300X · 2024-2026 实践
prerequisites: [training-orchestration, model-serving]
tags: [ml-infra, gpu, scheduling, k8s, finops, multi-tenancy]
aliases: [GPU 调度, GPU Scheduling, Multi-tenant GPU]
related: [training-orchestration, model-serving, model-monitoring, fine-tuning-data, cost-optimization]
systems: [kubernetes, ray, volcano, yunikorn, run-ai, karmada]
status: stable
---

# GPU 调度

!!! tip "一句话理解"
    把有限的 GPU 资源**公平、高效、可抢占**地分给训练、推理、微调、探索四类负载。LLM 时代 GPU 成本是 AI 基础设施的最大头（具体占比依团队构成差异很大 · 不要直接套用某"50%+"数字 `[来源未验证]`）· 调度效率直接 = **成本效率 + 能否合规**。

!!! warning "覆盖范围 · 非 LLM 场景同样需要"
    本页**不是只服务 LLM / 大模型训练**：
    
    - **传统 ML 在线推理 GPU**：推荐精排 · CTR / CVR 预测 · 风控模型 · CV 检测 · embedding serving —— 都需要 MIG / 调度 / 碎片处理
    - **中小模型训练**：GBDT（CPU）+ DNN 召回（A10 / L4）· 不需要 H100 级 · 但多租户调度诉求一样
    - **LLM 推理 / 微调**：H100 / H200 / B200 主力
    
    本页**大量 2024-2026 新硬件**（GB200 NVL72 / MI300X / Disaggregated）主要服务大模型场景 · tabular / 中小模型团队**只看§3 共享隔离 + §5 Volcano + §10 多租户 + §11 FinOps** 就够 · 跳过硬件矩阵细节。

!!! abstract "TL;DR"
    - **四类负载诉求不同**：在线推理（独占）· 训练（gang）· 微调（半在线）· 探索（共享）
    - **K8s 原生 GPU 支持够用但**：gang scheduling 缺 · queue/priority 弱 · 抢占精细度不够
    - **补充调度器**：**Volcano** · YuniKorn · **Run:ai**（NVIDIA 2024 收购 · 企业主流）
    - **GPU 共享**：MIG（硬隔离 A100+）· MPS（软隔离 · 有互相影响）· time-slicing（K8s 简）
    - **2026 新硬件**：H200 / B200 / GB200 NVL72 rack-scale / AMD MI300X / Intel Gaudi 3
    - **Topology-aware**：NVLink / NVSwitch / NUMA / PCIe · GB200 rack-scale 调度粒度变化
    - **多租户**：Namespace + RBAC + ResourceQuota + cost attribution tag 链路
    - **FinOps**：per-team / per-model / per-request 归因 · Kubecost · AWS Capacity Blocks / GCP DWS 预留市场

## 1. 四类 GPU 负载（2024-2026 更新）

| 负载 | 特点 | 调度诉求 |
|---|---|---|
| **在线推理** | 持续运行 · 延迟敏感 · SLO 明确 | 独占 + 高可用 + 快速扩缩 |
| **训练**（大模型预训练 / 长周期）| 长任务 · N 卡同时就位 | Gang scheduling + 抢占（可从 ckpt 恢复）|
| **微调 / RLHF**（"半在线"· 2024+ 新类别）| 中等时长 · 对 data/eval 有互动 · 可能批量并行 | 介于训练和探索之间 · 支持 Elastic |
| **探索 / 开发 / Notebook** | 短 · 可中断 · 碎片化 | 共享 + 快速回收 + MIG |

**核心冲突**：推理不能被抢 · 训练要一次多卡 · 微调有交互 · 探索希望随时上。**单池混跑 = SLA 做不出**。

## 2. GPU 硬件 · 2026 视角

### 2.1 NVIDIA 现代卡

| 卡 | 显存 | 发布 | 定位 |
|---|---|---|---|
| A100 | 40GB / 80GB | 2020 | 上一代主力 · 训练 / 推理通用 |
| H100 | 80GB SXM / 94GB HBM3e | 2022 | LLM 时代事实默认 |
| H200 | 141GB HBM3e | 2024 | 更大显存 · 长 context |
| B100 / B200 | 192GB HBM3e | 2024-2025 | Blackwell 架构 · FP4 支持 |
| **GB200 NVL72**（rack-scale） | 72×B200 + 36×Grace | 2024-2025 | **rack 级统一调度** · 调度粒度从 GPU 变成 node/rack |

### 2.2 AMD / Intel / 国产

| 卡 | 定位 |
|---|---|
| AMD **MI300X** | 192GB HBM3 · 2024+ LLM 训练 / 推理替代选项 · ROCm 生态 |
| AMD MI325X | MI300X 升级 · HBM3e |
| Intel **Gaudi 3** | 训练 + 推理 · Synapse AI 软件栈 |
| 华为**昇腾 910B / 910C** | 国内主力 · CANN 软件栈 |
| 摩尔线程 / 寒武纪 / 壁仞 | 国产多家 · 生态仍在建设 |

**调度影响**：
- **GB200 NVL72** 是 rack 级统一 · NVLink domain 扩展到 72 卡 · Topology-aware 粒度改变
- **MI300X** 和 NVIDIA 混布需要**异构调度**策略（Volcano 支持多 device plugin）
- 国产卡生态**软件栈不统一** · 混合集群 SREer 多套驱动 / runtime

## 3. GPU 共享与隔离

### 3.1 MIG（Multi-Instance GPU）

NVIDIA A100 / H100 / H200 / B200 硬件级切分：一张卡切成最多 7 个子 GPU · 各自独立内存 + SM。

- **隔离最好**（性能不互相影响）
- **灵活性差**（切分模式预设 · 需重配生效）
- **适合**：混合推理 · 探索 · Notebook
- 2024+ GB200 **NVL72 domain 内 MIG + NVLink 共享**仍在演进

### 3.2 MPS（Multi-Process Service）

多个 CUDA 进程共享一张卡 · 上下文隔离但 SM 共享。

- 更灵活
- **有互相影响**（一个大作业挤小的）
- 推理 batch 场景可用 · 训练不推荐

### 3.3 Time-Slicing（K8s Device Plugin）

NVIDIA Device Plugin 的 `time-slicing` 模式：K8s 把一张卡声明为 N 份 · 轮转调度。

- 最简单
- **不是真并行**（不适合高吞吐推理）
- 开发 / CI 场景用得多

### 3.4 Fractional GPU（Run:ai）

Run:ai 等企业调度器支持**分数 GPU**（0.3 GPU）· 软隔离 + quota。比 time-slicing 精细。

## 4. K8s 调度器的局限

原生 K8s Scheduler 基于 **pod-at-a-time** · 对 AI 不友好：

- **Gang scheduling 缺**：PyTorchJob 16 worker 需要同时启动 · K8s 默认可能只排到 15 个等第 16 个（死锁）
- **Queue / Priority 弱**：训练队列 / 推理队列 / 探索队列 SLA 不同
- **抢占策略**：默认 priority 抢占不够精细
- **拓扑感知弱**：同 node 的 NVLink / 同 rack 的 NVSwitch 考虑不足

## 5. 补充调度器 · 2026 选型

### 5.1 Volcano（OSS · K8s 原生批调度）

- **Gang scheduling**（PodGroup · minAvailable）· Queue / Priority / Fair share
- 插件体系：binpack · topology-aware · deviceshare · numa-aware
- **适合**：K8s 原生团队 · 训练作业多 · 开源优先

```yaml
apiVersion: batch.volcano.sh/v1alpha1
kind: Job
metadata:
  name: llama-70b-training
spec:
  minAvailable: 16
  queue: training
  priority: high-priority
  plugins:
    env: []
    svc: []
  policies:
    - event: PodEvicted
      action: RestartJob
  tasks:
    - replicas: 16
      name: worker
      template:
        spec:
          containers:
            - resources:
                limits: {nvidia.com/gpu: 8}
```

### 5.2 YuniKorn（OSS · Apache）

- Queue / Fair / DRF / Gang · 多来源调度
- **适合**：多工作负载混合（Spark + Flink + AI）团队

### 5.3 Run:ai（**NVIDIA 2024 收购** · 企业主流）

- 分数 GPU · 弹性训练 · 跨节点 pool
- **AI workload 原生抽象**（不是"改造的 K8s 调度"）
- 商业 · 付费 · **但 2024 起 NVIDIA 在多家大客户强推**
- **适合**：NVIDIA 深度合作 · 企业 ML 平台团队

### 5.4 Karmada · 跨集群

- K8s 多集群编排 · GPU 池跨 region 调度
- **适合**：大规模 · 多地 data center · 容灾

### 5.5 Ray 自调度

Ray 在 K8s 分到资源块后 · 内部做 actor 级调度 · **适合 Ray 原生团队**。

### 5.6 Slurm（HPC 传统）

- HPC 世界的经典调度器 · 2024+ 在 LLM 大规模训练仍有位置
- Meta / OpenAI 等训练 GPT-4 / Llama 系用 Slurm（非 K8s）
- **K8s 化的传统 HPC 集群**：SUSE Rancher · ParallelCluster 的方向
- **适合**：超大规模训练 · 和 K8s 二选一或混用

## 6. 抢占策略

多租户必备：

| 负载类型 | 可否被抢占 |
|---|---|
| 在线推理 P0 | ❌ |
| 在线推理 P1（可降级） | ⚠️ 降级而非抢占 |
| 批训练（短） | ✅ 从 ckpt 恢复 |
| 批训练（长） | ⚠️ 只能夜间 / 周末抢 |
| 微调 / RLHF | ✅ 支持 Elastic 的话友好 |
| 交互式探索 | ✅ 秒级抢 |

**训练作业必须支持 ckpt + 断点续训**（详见 [training-orchestration](training-orchestration.md) §DCP）· 否则抢占成本爆。

## 7. Topology-aware 调度

### 7.1 NVLink / NVSwitch 拓扑

- **A100 / H100 单 node 8 卡** · NVLink 全互连 · 带宽 > PCIe 一个量级
- **GB200 NVL72** · rack 内 72 卡 NVLink domain · 超级节点
- **关键**：TP（Tensor Parallel）需要**同 node / 同 NVLink domain** · 跨 node 通过 InfiniBand 慢 10×+
- **必须**：调度器感知拓扑 · 把 TP 组调到一起

### 7.2 InfiniBand / RoCE 拓扑

- 跨 node 通信 · IB 400G / 800G（H100 NDR）· RoCE v2 替代方案
- **SHARP**（Scalable Hierarchical Aggregation and Reduction Protocol）· IB 内原生 all-reduce 加速
- NCCL 2024+ 集成 SHARP · 大规模训练必备

### 7.3 NUMA / PCIe 拓扑

- 跨 CPU socket 通信比同 socket 慢 · PCIe 拓扑影响 GPU ↔ CPU
- Volcano 的 **numa-aware** 插件 / Run:ai 的 NUMA binding

### 7.4 实操建议

- Volcano `topology-plugin` · Run:ai `topology scheduler` · Kubernetes **TAS**（Topology Aware Scheduling）
- 训练作业的 TP group 必标 `topologyKey: kubernetes.io/hostname` 或 更细

## 8. Disaggregated GPU · 2024-2026 新趋势

传统架构：CPU + GPU + 本地 NVMe + 网卡 **一节点绑死**。

**Disaggregated**（解耦）架构：
- GPU 池 / CPU 池 / 存储池 / 网络 **分离** · 按需组合
- **代表**：NVIDIA **GB200 NVL72** 的 NVLink Switch domain（rack 级共享）· CXL 2.0/3.0 内存池化 · Disaggregated inference（prefill / decode 分离）
- **调度变化**：资源单元从"一张 GPU"变成"GPU compute + 远程 HBM + 远程 KV cache"

**Disaggregated LLM Inference**（vLLM / Dynamo 2024-2025）：
- **Prefill 节点**（计算密集）vs **Decode 节点**（内存带宽密集）分开部署
- 调度器需感知 · 路由请求到合适的池

## 9. 碎片问题 · 经典但仍重要

64 张 H100 · 4 台 × 16 卡。3 作业：
- A · 16 卡（整台）
- B · 8 卡
- C · 12 卡

A 占满一台 · 剩 48 卡（3 台）：
- B 放 1 台 · 剩 8 卡
- C 要 12 卡 · 任何一台都不够 → **碎片**

**碎片整理**：
- **装箱算法**（best-fit / worst-fit）
- **Topology-aware**（同 NVLink domain 优先）
- **预判式调度**（看 queue 里未来作业）
- **Defrag 时机**：作业结束时重新摆

Volcano 的 `binpack` 插件 · Run:ai 内置。大规模团队往往自研。

## 10. 多租户隔离 · 详解

生产 ML 平台 = 多租户。**只讲 GPU 抢占是不够的** · 要完整：

### 10.1 三层隔离

| 层 | 机制 |
|---|---|
| **算力隔离** | MIG / MPS / time-slicing / fractional GPU / 独占 |
| **网络隔离** | K8s NetworkPolicy · namespace 级 · service mesh |
| **数据隔离** | PVC / RBAC · object storage bucket 级 · Catalog ACL |

### 10.2 Namespace + RBAC + Quota

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-a-quota
  namespace: team-a
spec:
  hard:
    requests.nvidia.com/gpu: "16"
    persistentvolumeclaims: "10"
```

```yaml
apiVersion: scheduling.volcano.sh/v1beta1
kind: Queue
metadata:
  name: team-a
spec:
  weight: 3
  capability:
    nvidia.com/gpu: 16
  reclaimable: true  # 允许借用空闲资源
```

### 10.3 Cost Attribution Tag 链路

每个 pod 带 team / project / model / cost-center tag · 便于成本分摊：

```yaml
metadata:
  labels:
    team: recommender
    project: recsys-v3
    model-name: churn_predictor
    cost-center: "CC-1234"
```

下游 Prometheus / Kubecost / Grafana / 厂商 billing API 按 tag 聚合。

## 11. FinOps for ML

**GPU 账单是董事会级话题（2024-2026 所有大厂砍成本）**。

### 11.1 关键指标

- **GPU 利用率**（经验目标 > 60% `[来源未验证 · 示意性]`）· < 60% 通常说明瓶颈在数据 / 代码
- **Tokens/sec per GPU**（LLM）
- **$ per 1K token**（推理）· 对比商业 API break-even
- **$ per training run**（训练）
- **Per-team / per-model 归因**

### 11.2 成本控制招数

- **混部**：低优先级推理 + 批训练错峰
- **Spot 实例**：训练跑 spot（配 Elastic + 频 ckpt）· 推理不 spot
- **预留市场**：**AWS Capacity Blocks for ML**（2023+）· **GCP DWS**（Dynamic Workload Scheduler · 2024+）· 成本低于按需但需要提前锁定时间窗
- **弹性扩缩**：夜间降推理规模 · 把卡让给训练
- **Cache 模型权重**：pod 重启不从对象存储重拉（local SSD / NVMe / DRA）
- **合适的量化 / 蒸馏**：小模型复现大模型能力 · 成本大降

### 11.3 工具

- **Kubecost** · Cloud Cost Optimizer（OSS）· Karpenter（AWS · K8s 节点 autoscaler）
- 厂商 billing API：AWS CUR · GCP Billing Export · Azure Cost Management
- **Grafana 归因 dashboard**（自建 · 基于 tag）

## 12. 典型部署拓扑

```
集群划分：
- 推理池：H100 / H200 × N · 独占 · 24/7
- 训练池：B200 / GB200 × N · 可抢占 · spot 友好
- 微调池：A100 × N · 半独占 · Elastic
- 探索池：A10 / L4 / 消费卡 · 共享 MIG
  
跨池借用：
- 夜间训练池借推理池
- 推理低峰借探索池（MIG）
```

**不要所有 GPU 混一池** · SLA 做不出。

## 13. 陷阱 · 反模式

- **MIG 切了但配置不同步**：K8s 认为还是整张卡
- **NCCL 跨节点慢**：没配 IB 或 RoCE · 或 NCCL_TOPO_FILE 没设
- **训练作业不做 ckpt**：抢占 = 白干几小时
- **推理 HPA 基于 CPU 扩**：GPU 100% 但 CPU 不紧张 → 基于 GPU utilization（DCGM）或 request queue depth
- **忽略 NUMA / PCIe 拓扑**：分配的 GPU 跨 socket 通信慢
- **多租户共用 cluster-admin**：权限越界事故
- **没有 cost attribution**：GPU 账单月末爆 · 不知道谁花的
- **长作业 + 短作业同队列**：短作业总是等死
- **量化没考虑调度影响**：W4A16 模型推理比 FP16 快 · 但量化过程 GPU 密集 · 应调度到训练池
- **GB200 时代还用单 GPU 粒度调度**：rack-scale 要求新思路
- **Spot 实例训练没 Elastic**：节点突然收回 · 任务直接 fail

## 14. 相关

- [训练编排](training-orchestration.md) —— Elastic Training + DCP
- [Model Serving](model-serving.md) —— 推理侧资源需求
- [Model Monitoring](model-monitoring.md) —— GPU 监控维度
- [LLM Inference](../ai-workloads/llm-inference.md) —— LLM 推理 GPU 最大消费方
- [LLM Fine-tuning](fine-tuning-data.md) —— 微调负载调度
- [成本优化](../ops/cost-optimization.md) —— 通用成本

## 15. 延伸阅读

- Volcano: <https://volcano.sh/>
- YuniKorn: <https://yunikorn.apache.org/>
- Run:ai: <https://www.run.ai/>
- Karmada: <https://karmada.io/>
- NVIDIA MIG docs · GB200 NVL72 架构白皮书
- AWS Capacity Blocks for ML · GCP Dynamic Workload Scheduler docs
- *Heterogeneity-Aware Cluster Scheduling*（OSDI 2020）
- *Gandiva*（OSDI 2018 · GPU 集群调度经典）
- Kubecost: <https://www.kubecost.com/>
