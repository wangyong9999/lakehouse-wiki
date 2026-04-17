---
title: Model Serving
type: concept
depth: 进阶
prerequisites: [model-registry]
tags: [ml-infra, serving, llm, gpu]
related: [model-registry, rag, agents-on-lakehouse]
systems: [vllm, tgi, ray-serve, kserve, triton, sglang]
status: stable
---

# Model Serving

!!! tip "一句话理解"
    模型部署成**低延迟、高吞吐、稳定**的在线服务。LLM 时代这件事比以往复杂得多——batching、KV cache、GPU 内存管理、continuous batching 都是必修课。

!!! abstract "TL;DR"
    - **LLM 推理选型**：vLLM / SGLang 是 OSS 主力；TGI 商业背书稳；Triton 多后端
    - **Continuous batching** 是 LLM 吞吐的关键（vs 传统 static batching）
    - **KV cache** 是 LLM 的秘密占用源
    - **量化 + 投机解码 + 张量并行**是三大加速手段
    - 非 LLM 模型（CLIP / BGE / rerank）用 **Ray Serve / Triton / KServe**

## 模型分两类，服务方式不同

### 类 1：传统 DNN（embedding / rerank / 推荐 / 分类）

- 输入输出 tensor 固定
- Latency 目标 **1–50ms**
- 主力框架：**Ray Serve / Triton / KServe / TorchServe**

### 类 2：LLM（生成式）

- 输出变长，自回归
- Latency 目标 **p99 时长 / tokens-per-second**
- 主力框架：**vLLM / SGLang / TGI / LMDeploy**

## LLM Serving 的四件关键事

### 1. Continuous Batching

传统 static batching：一批内请求等最慢的完成。LLM 输出变长 → 浪费严重。

**Continuous batching**：每个请求以 step 为粒度持续加入/移出 batch；GPU 几乎永不空闲。vLLM / TGI / SGLang 都实现了。

这**一项改进**就让 LLM 吞吐 3-5 倍。

### 2. KV Cache 管理

自注意力的 KV 缓存随上下文线性增长。长 context 场景一个请求可能吃 G 级显存。

**PagedAttention**（vLLM 提出）把 KV cache 分 page 管理，碎片归零。

### 3. 量化

- FP16 → INT8 → INT4 / FP4
- 吞吐 1.5-3×，精度小损失
- GPTQ / AWQ / SmoothQuant 是主流算法

### 4. 投机解码（Speculative Decoding）

用小模型先"猜" N token，大模型一次验证。吞吐 2-3 倍，完全不损精度。

## 主流 LLM Serving 选择

| 工具 | 优点 | 缺点 |
| --- | --- | --- |
| **vLLM** | PagedAttention 原创；OpenAI 兼容 API；社区最大 | 无官方商业支持 |
| **SGLang** | 结构化生成 + 更快调度；创新活跃 | 相对新 |
| **TGI** | Hugging Face 官方；商业支持 | 性能略逊 vLLM |
| **TensorRT-LLM** | NVIDIA 官方；极致吞吐 | 闭源部分；模型支持慢 |
| **LMDeploy** | 国产系（商汤），中文好 | 英文生态略小 |

**默认推荐 vLLM**，除非有具体约束。

## 非 LLM 模型的服务

### Ray Serve

```python
from ray import serve
from transformers import AutoModel

@serve.deployment(num_replicas=4, ray_actor_options={"num_gpus": 1})
class EmbeddingService:
    def __init__(self):
        self.model = AutoModel.from_pretrained("BAAI/bge-large-zh")
    def __call__(self, texts):
        return self.model.encode(texts).tolist()

app = EmbeddingService.bind()
serve.run(app)
```

**优点**：Python 原生、Ray 生态深度集成、异构资源调度。
**适合**：Embedding、Rerank、CV 模型。

### KServe

K8s 上 CRD 形态的模型服务：

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
      storageUri: "gs://models/bge/v3"
```

**优点**：和 K8s 治理一致，自动扩缩。
**适合**：K8s 原生团队。

### Triton Inference Server

NVIDIA 官方，多模型多框架：

- 一台 GPU 能跑 Pytorch + TF + ONNX + TensorRT 模型
- 动态 batching
- 性能极致

**适合**：GPU 利用率要极致、多模型混布。

## 服务设计的工程点

### 延迟预算拆解

比如 RAG 端到端 p95 < 1.5s：

| 阶段 | 预算 |
| --- | --- |
| 检索（向量 + Hybrid）| 100–300ms |
| Rerank | 50–150ms |
| LLM 生成（TTFT）| 200–500ms |
| LLM 生成（剩余 tokens）| 500-1000ms |

**TTFT（Time to First Token）**是 UX 关键——用户看到第一个字越快越好。

### 流式输出（SSE / WebSocket）

LLM 生成时要流式返给前端，不要等完整。vLLM 的 OpenAI 兼容 API 默认支持。

### 超时与熔断

- Request timeout：30-60s 合理
- Queue timeout：5-10s（拒绝比让它等死好）
- 熔断：底层 GPU 挂了，直接 503

### 成本监控

LLM 服务成本 = GPU 小时 × 价格。监控：

- GPU 利用率（应 > 60%）
- Token 吞吐（tokens/sec per GPU）
- 每 1K token 成本
- 对比商业 API 价格（自建省不省）

## 和 Catalog / Registry 的集成

服务启动时从 Registry 拉模型：

```python
model_uri = registry.get_latest_model_uri(
    name="recsys_v3",
    stage="Production"
)
```

模型切换不用重启服务——设计成**热加载**或**双实例蓝绿切换**。

## 陷阱

- **把 Embedding 模型塞进 LLM serving 框架**：vLLM 不是为 encoder 设计的，用 Ray Serve 合适
- **单 replica 撞 OOM** → 减小 max context 或增加 GPU memory
- **中小模型跑 TRT-LLM** → 编译时间 > 模型调用时间
- **没做 request queue 限流** → 高峰把 GPU 打爆
- **不考虑冷启动**（模型加载耗时）→ 滚动升级时短暂不可用

## 相关

- [Model Registry](model-registry.md)
- [RAG](../ai-workloads/rag.md)
- [Agents on Lakehouse](../ai-workloads/agents-on-lakehouse.md)
- [GPU 调度](gpu-scheduling.md)

## 延伸阅读

- vLLM: <https://docs.vllm.ai/>
- *Efficient Memory Management for Large Language Model Serving with PagedAttention* (SOSP 2023)
- *Speculative Decoding* 系列论文
- Ray Serve docs: <https://docs.ray.io/en/latest/serve/>
