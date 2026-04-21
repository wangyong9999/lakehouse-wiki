---
title: Model Serving · 通用 ML 服务 + 生产运维
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: Ray Serve 2.9+ · KServe 0.13+ · Triton 24.x · BentoML 1.2+ · TorchServe · ONNX Runtime 1.17+ · Modal / Replicate / RunPod · 2024-2026 实践
prerequisites: [model-registry]
tags: [ml-infra, serving, inference-graph, canary]
aliases: [模型部署, 在线推理]
related: [model-registry, model-monitoring, llm-inference, rag, agents-on-lakehouse, gpu-scheduling]
systems: [ray-serve, kserve, triton, torchserve, bentoml, modal, replicate, onnx-runtime]
status: stable
---

# Model Serving · 通用 ML 服务 + 生产运维

!!! tip "一句话定位"
    模型部署成**低延迟、高吞吐、稳定**的在线服务，以及 **Inference Graph / Shadow / Canary / Rollback 的生产运维**契约。**通用 ML（embedding · rerank · 推荐 · 分类 · CV）是本页重心**；LLM 推理的 engine 级深度（vLLM / SGLang / PagedAttention / speculative / 量化）canonical 在 [ai-workloads/llm-inference.md](../ai-workloads/llm-inference.md)，本页只给顶层指引。

!!! warning "和 LLM Inference 的分工"
    - **本页**：通用 ML serving 框架选型 · Inference Graph / Ensemble · Shadow / Canary / Rollback 运维 · 延迟预算 · 流式输出 · 和 Registry 集成 · BentoML / Modal / Replicate 2026 托管选项
    - **[ai-workloads/llm-inference.md](../ai-workloads/llm-inference.md)**：LLM 特有技术（continuous batching / PagedAttention / KV cache / speculative decoding / 量化 GPTQ/AWQ/FP8 / MoE）· vLLM vs SGLang vs TRT-LLM vs Dynamo 深度对比 · H100/H200/B200 基线
    - 本页在 §LLM Serving 概述只做**顶层定位 + 选型入口**，不重复 LLM engine 内核。

!!! abstract "TL;DR"
    - **两类模型两套范式**：传统 DNN / GBDT（Ray Serve · Triton · KServe · TorchServe · BentoML · ONNX Runtime）· LLM（参见 llm-inference）
    - **Inference Graph** 是生产的一等抽象 —— 召回 · 粗排 · 精排 · 重排 · 业务规则 组成 DAG，不是单个模型
    - **Shadow + Canary + Rollback** 三件套是上线的标准动作 · Shadow 对账用 KL divergence · Canary 基于指标自动回滚
    - **延迟预算**拆解到毫秒 · 流式输出用 SSE · 超时 / 熔断 / 限流必备
    - **和 Registry 集成**：热加载 or 蓝绿切换
    - 2026 新托管选项：**Modal / Replicate / RunPod / Anyscale** —— 跳过 K8s 的另一条路

## 1. 两类模型 · 两套范式

### 类 1 · 传统 DNN / 经典 ML（本页重心）

- 对象：Embedding · Rerank · 分类 · 回归 · 推荐（召回 / 精排）· CV 目标检测 · 语音
- 输入输出 tensor **尺寸固定** · latency 目标 **1-50ms**
- 批量**Static batching** 够用（或短 window dynamic batching）
- 主力框架：**Ray Serve / Triton / KServe / TorchServe / BentoML / ONNX Runtime**

### 类 2 · LLM（生成式 · 详见 [llm-inference](../ai-workloads/llm-inference.md)）

- 输出变长 · 自回归 · 长 context
- Latency 目标：**TTFT** + **tokens-per-second**
- 需要 **continuous batching · PagedAttention · KV cache 管理 · speculative decoding**
- 主力框架：**vLLM / SGLang / TGI / TensorRT-LLM / Dynamo**（详见 llm-inference）

**本页对 LLM**只保留§5 的顶层选型指引。想深入 vLLM 内部 / 量化 / speculative 请去 llm-inference。

## 2. 通用 ML Serving 框架选型

### Ray Serve（Python 原生 · 灵活度最高）

```python
from ray import serve
from sentence_transformers import SentenceTransformer

@serve.deployment(num_replicas=4, ray_actor_options={"num_gpus": 1})
class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-large-zh-v1.5")
    async def __call__(self, texts: list[str]):
        return self.model.encode(texts, normalize_embeddings=True).tolist()

app = EmbeddingService.bind()
serve.run(app)
```

- **优点**：Python 原生 · Ray 生态集成（Train / Data / Tune）· 异构资源 · 支持 deployment graph
- **适合**：Embedding / Rerank / CV / 多模型组合 · Python-first 团队
- **坑**：Ray 集群自身治理 · OOM 诊断比 K8s pod 麻烦

!!! note "代码校正 · sentence-transformers vs transformers"
    bge / e5 等 embedding 模型**必须用 sentence-transformers `SentenceTransformer`**（有 `.encode()` 方法），而不是 HuggingFace `AutoModel`（`AutoModel` 只返回 hidden states · 没有 `.encode()`）。这是常见实现 bug。

### Triton Inference Server（NVIDIA 官方 · 多后端）

- 一台 GPU 同时跑 PyTorch + TensorFlow + ONNX + TensorRT 模型
- **Dynamic batching** · **Model ensemble**（原生 DAG）· **Business Logic Scripting**（Python 胶水）
- **适合**：GPU 利用率要榨极致 / 多模型混布 / 企业 GPU 集群
- 2024+ 集成 TensorRT-LLM backend 作 LLM serving

### KServe（K8s 原生 CRD）

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: bge-embedder
spec:
  predictor:
    model:
      modelFormat:
        name: pytorch
      storageUri: "s3://models/bge/v3/"
```

- **优点**：K8s 原生 · 自动扩缩（含 scale-to-zero）· Canary 内置 · 2024+ ModelMesh 多模型共享 pod
- **新能力**：**Inference Graph CRD**（原生 DAG 定义）· 可编排"召回 → rerank → 精排"
- **适合**：K8s 重的平台团队 · 多租户 SaaS

### TorchServe

- PyTorch 官方 · 简单 · 不如 Triton 性能激进 · 不如 Ray Serve 灵活
- **适合**：纯 PyTorch 团队不想引入 Ray / K8s

### BentoML（2024 起 OSS 主力后起）

- Python decorator 打包 · 一条命令构建 OCI 镜像
- 内置 adaptive batching · 和 Yatai（K8s operator）/ BentoCloud 配套
- **适合**：中小团队想要"打包即部署"· 以应用开发为主的 serving

### ONNX Runtime

- 跨框架 · CPU/GPU 通用 · ORT Web / Mobile 覆盖端侧
- **适合**：边缘 / CPU-only / 多框架统一运行时

### 2026 托管选项（跳过 K8s）

| 托管 | 定位 | 适合 |
|---|---|---|
| **Modal** | Python-first · 秒级冷启动 · 按用量计费 | 周期性 batch + 低 QPS 推理 · 团队不想管 K8s |
| **Replicate** | 模型即 API · 容器化简化 | 快速把开源模型变 API |
| **RunPod** | GPU spot 市场 · 显存灵活 | 成本敏感的训练 + 推理 |
| **Anyscale**（Ray 官方）| Ray Serve 托管 | Ray 生态团队 |
| **Databricks Model Serving** | UC Models 一键部署 | Databricks 客户 |
| **SageMaker / Vertex AI / Azure ML Endpoints** | 云厂商全托管 | 云锁定已成事实的团队 |

## 3. Inference Graph · Ensemble · 多模型 DAG（生产一等抽象）

!!! danger "生产现实"
    一个推荐系统的 serving 链路**不是一个模型**，是 DAG：
    
    ```
    请求 → 召回 N 路（双塔 + ANN + 规则）→ 去重 → 粗排（GBDT）→ 精排（DNN）→ 重排（打散 / 曝光过滤）→ 业务规则 → 返回
    ```
    
    搜索 / 欺诈 / 多模检索都是类似结构。**把每个节点单独部署 = N 个服务 · 延迟叠加 · 运维爆炸**。

**解法 · Inference Graph**（三种实现）：

### 方案 A · Triton Ensemble + BLS

- Ensemble 定义 DAG config · BLS（Business Logic Scripting）用 Python 胶水
- **优点**：所有模型同 GPU 进程 · 延迟最低
- **缺点**：DAG 调试困难 · 跨进程不方便

### 方案 B · Ray Serve Deployment Graph

```python
from ray import serve

@serve.deployment
class Recall: ...

@serve.deployment
class Rank: ...

@serve.deployment
class Combine:
    async def __call__(self, query):
        candidates = await self.recall.remote(query)
        return await self.rank.remote(candidates)
```

- **优点**：Python 原生 DAG · 异构硬件可混布（Recall 用 CPU · Rank 用 GPU）
- **缺点**：Ray 集群自身治理

### 方案 C · KServe Inference Graph CRD

- K8s 原生 · DAG 用 CRD 声明 · 可视化好
- **缺点**：延迟比进程内 DAG 高（跨 pod HTTP 调用）

**选择准则**：极致延迟选 Triton Ensemble · 灵活性选 Ray Serve · K8s 治理一致性选 KServe。

## 4. Shadow / Canary / Rollback 运维契约

### 4.1 Shadow Deployment（影子流量）

**目的**：新模型并行跑、**不影响用户决策**，对账预测分布。

- **流量镜像**方式：L7（ingress 级，如 Istio `mirror`）· 应用层 fork（serving 框架内复制请求）
- **对账指标**：
  - **预测分布对比**：新老模型输出的 KL / JS divergence 阈值（< 0.1 稳定，> 0.25 明显漂移 · 数字为经验阈值 `[来源未验证 · 示意性]`）
  - **排序稳定性**：推荐 top-K 重合率 / NDCG gap
  - **延迟分布**：新模型 p99 是否在预算内
- **观察窗口**：至少 24-72 小时 · 覆盖日 / 周周期

### 4.2 Canary Progressive Delivery

**流量逐级切**：1% → 5% → 25% → 50% → 100% · 每级稳定 N 小时才进下一级。

**关键设计**：
- **分流 Key 不要用 user_id hash 均匀** —— 会污染 A/B 实验信号；用 **request-id hash** 或 **独立 canary traffic 池**
- **自动 rollback 触发**：业务 KPI（CTR / GMV / 转化率）下降 > 阈值 × N 分钟 · 延迟 p99 > 预算 · 错误率 > 基线
- **冷却窗口**：rollback 后至少 1 小时不再推 canary · 防止抖动循环

### 4.3 Rollback Runbook（最关键的生产契约）

**MTTR 目标**：发现问题 → 流量切回旧版 **< 5 分钟**。

```
1. 告警触发（model-monitoring 触发 · 详见对应章）
2. on-call 决策：是否切流（看是否是模型问题还是数据上游问题）
3. 切流操作（三选一 · 取决于 serving 框架）：
   a. MLflow alias 切换：champion → 前一版 · serving 进程订阅 alias 热加载
   b. K8s traffic split：KServe canaryTrafficPercent = 0
   c. Registry stage 回退（2026 推荐用 alias · stage API deprecated）
4. 确认：灰度 pod 彻底下线 · 新请求全走旧版
5. 监控：10 分钟内指标恢复确认
6. Postmortem：24 小时内写复盘 · 更新 runbook
```

**常见错误**：
- 切流后没重启 serving pod → 旧 pod cache 的 model 还在用
- Model Registry 只改 stage 没同步 alias → serving 进程看不到
- 分流规则挂在 CDN 层没更新 → 流量切不回

## 5. LLM Serving 概述（深度看 [llm-inference](../ai-workloads/llm-inference.md)）

!!! abstract "本节 = 顶层选型入口 · 不是 engine 内核深度"

- **vLLM** —— OSS 事实默认 · PagedAttention 原创 · OpenAI 兼容 API · 最活跃社区
- **SGLang** —— 2024 新星 · 结构化输出 / 复杂调度场景优 · CFSM JSON 吞吐优势
- **TensorRT-LLM** —— NVIDIA 官方 · 极致吞吐 H100/H200 · 模型支持慢半拍
- **Dynamo**（2025 NVIDIA）—— 新一代 Inference Server · 评估中
- **TGI**（HuggingFace）· **LMDeploy**（OpenMMLab / 上海 AI Lab）· **MLC-LLM**（端侧）

**默认推荐**：vLLM（除非有具体约束 · 如结构化输出用 SGLang · H100 极致吞吐用 TRT-LLM）。

**详细的**：continuous batching · KV cache · PagedAttention · speculative decoding · 量化（GPTQ / AWQ / FP8）· engine 对比 matrix · 2026 硬件基线 —— 全部在 [ai-workloads/llm-inference.md](../ai-workloads/llm-inference.md)，本页不重复。

## 6. 服务设计工程点

### 延迟预算拆解

RAG 端到端 p95 < 1.5s 示例（数字为典型经验 `[来源未验证 · 示意性]` · 依模型 / 硬件 / 规模差异大）：

| 阶段 | 预算 |
|---|---|
| 检索（向量 + Hybrid） | 100-300ms |
| Rerank | 50-150ms |
| LLM TTFT | 200-500ms |
| LLM 剩余 tokens | 500-1000ms |

推荐系统端到端 p99 < 200ms 示例：

| 阶段 | 预算 |
|---|---|
| 特征拉取（FS online） | 10-30ms |
| 召回（ANN + 规则 N 路并行） | 30-80ms |
| 粗排（GBDT） | 10-30ms |
| 精排（DNN）| 30-80ms |
| 重排 + 业务规则 | 5-20ms |

**TTFT**（Time to First Token）是 LLM UX 关键；推荐系统是整体 p99。两者预算哲学不同。

### 流式输出（SSE / WebSocket）

LLM 生成时流式返前端 —— vLLM 的 OpenAI 兼容 API 默认支持。推荐系统一般不流式（一次返 top-K）。

### 超时 · 熔断 · 限流

- Request timeout：推荐 50-100ms · LLM 30-60s
- Queue timeout：5-10s（拒绝 > 饿死）
- 熔断：底层 GPU 挂 → 503（比让客户等死好）
- 限流：token bucket 按租户 / API key · 防止单租户打爆集群

### 冷启动

- 模型加载耗时（GB 级 artifact · 对象存储冷读几十秒 · 甚至几分钟）
- **解法**：本地 SSD cache · NVMe · K8s PVC 预拉 · scale-up 时预热
- 滚动升级时避免短暂不可用 → **蓝绿** > **滚动**

### 成本监控

- GPU 小时 × 价格 · GPU 利用率（应 > 60% 数字为经验目标 `[来源未验证 · 示意性]`）· tokens/sec per GPU
- 每 1K token 成本 · 对比商业 API（自建 break-even 公式）
- **TCO break-even**：`tokens/day × (API_price − self_host_cost_per_token) vs GPU_monthly_fixed`

## 7. 和 Model Registry 的集成

### 7.1 模型加载

服务启动时从 Registry 拉：

```python
# MLflow 2.9+ 用 alias（替代 deprecated stage API）
import mlflow
model_uri = f"models:/recsys_v3@champion"  # alias · not stage
model = mlflow.pyfunc.load_model(model_uri)
```

### 7.2 热加载 vs 蓝绿

| 方案 | 优点 | 缺点 |
|---|---|---|
| **热加载** | 无流量中断 | 新旧模型内存叠加 · 需显存预留 |
| **蓝绿** | 切换瞬时 · 回滚简单 | 需双倍资源 |
| **滚动** | 资源节省 | 短暂不一致 · 冷启动可见 |

生产推荐 **蓝绿**（配合 rollback runbook）· 显存紧张时用热加载。

## 8. 陷阱 · 反模式

- **Embedding 模型塞进 LLM serving 框架**：vLLM 是 decoder-only · 不适合 encoder · 用 Ray Serve / Triton
- **`AutoModel.encode()` 错误用法**：transformers `AutoModel` 无 `.encode()` · 用 `SentenceTransformer` 或 `AutoModel` + mean pooling 手工实现
- **LMDeploy 归属**：OpenMMLab / 上海 AI Lab 主导（常被误说成商汤单家）
- **单 replica 撞 OOM**：减小 max context / 加显存 / 拆 replica
- **没做 request queue 限流**：高峰打爆 GPU
- **冷启动未考虑**：滚动升级短暂不可用
- **分流 key 用 user_id hash**：污染 A/B 实验信号
- **rollback 没 runbook**：事故时 on-call 手忙脚乱
- **Shadow 只看延迟不对预测分布**：新模型慢慢偏但不被发现
- **模型切换后没清 pod cache**：旧模型还在跑

## 9. 相关

- [Model Registry](model-registry.md) —— 起点
- [Model Monitoring](model-monitoring.md) —— 上线后的眼睛
- [LLM Inference](../ai-workloads/llm-inference.md) —— LLM engine 深度 canonical
- [RAG](../ai-workloads/rag.md) · [Agents on Lakehouse](../ai-workloads/agents-on-lakehouse.md)
- [GPU 调度](gpu-scheduling.md) —— 底层资源

## 10. 延伸阅读

- Ray Serve: <https://docs.ray.io/en/latest/serve/>
- KServe: <https://kserve.github.io/website/>
- Triton Ensemble / BLS: NVIDIA 官方
- BentoML: <https://docs.bentoml.com/>
- ONNX Runtime: <https://onnxruntime.ai/>
- *Designing ML Systems* (Chip Huyen) 第 7-8 章
- KServe Inference Graph RFC
