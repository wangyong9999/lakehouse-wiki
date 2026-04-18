---
title: LLM 推理优化 · vLLM / Flash Attention / Speculative / MoE
type: concept
depth: 资深
level: A
applies_to: vLLM 0.6+, SGLang, TensorRT-LLM, Flash Attention 3, 2024-2025 前沿
tags: [frontier, llm, inference, gpu, optimization]
aliases: [LLM Inference Optimization]
related: [rag, mcp, agents-on-lakehouse]
systems: [vllm, sglang, tensorrt-llm, triton, tgi]
status: stable
---

# LLM 推理优化

!!! tip "一句话理解"
    **让 LLM 跑得更快、更便宜、支持更多并发**。过去两年推理侧的工程创新（PagedAttention / Continuous Batching / Flash Attention / Speculative Decoding / MoE / Quantization）让同样硬件吞吐提升 **5-30 倍**。生产 LLM 工作负载的成本关键。

!!! abstract "TL;DR"
    - **吞吐关键**：Continuous Batching + PagedAttention（vLLM 首创）
    - **延迟关键**：Flash Attention + Speculative Decoding
    - **成本关键**：量化（INT8 / INT4 / FP8 / AWQ / GPTQ）+ MoE
    - **服务选型**：vLLM / SGLang / TensorRT-LLM / Triton / TGI
    - **典型提升**：同 H100 上 Llama-70B 从 5 QPS → 50 QPS + p99 减半
    - 2024 新热点：**SGLang 的 RadixAttention** · **FP8 训练推理闭环**

## 1. 业务痛点 · 直接跑 Transformers 为什么慢

### HuggingFace Transformers 原生跑推理

```python
model = AutoModel.from_pretrained("Llama-70B")
output = model.generate(input_ids, max_new_tokens=500)
```

**问题**：

| 问题 | 后果 |
|---|---|
| **KV Cache 连续内存** | GPU 内存碎片、OOM | 
| **固定 batch size** | 短请求等长请求、GPU 利用率 20% |
| **Attention 全计算** | O(n²) 随 context 长度爆 |
| **单 token 单次** | 生成 500 token 要 500 次前向 |
| **FP16 全量** | 参数占显存 × 2（70B × 2 = 140GB）|

实际生产量化对比（H100 单卡 Llama-70B）：
- HF Transformers：~5 QPS
- vLLM：**~50 QPS**（10× 提升）
- SGLang + cache：**~80 QPS**（16×）

## 2. 五大优化技术

### 技术 1 · PagedAttention + Continuous Batching（vLLM 首创）

**PagedAttention**（类比虚拟内存分页）：
- KV Cache 分成固定大小 block（16 tokens）
- 不要求连续内存
- 动态分配、共享（prefix caching）

**Continuous Batching**：
- 不按固定 step 推进
- 每个 step 动态合并新请求、踢出完成请求
- GPU **永远**忙

**效果**：吞吐 5-10× 提升，尾延迟大幅改善。

### 技术 2 · Flash Attention（v3 2024）

优化 GPU 上 Attention 计算的 **IO 感知**算法：
- Tiling + Recomputation 减少 HBM ↔ SRAM 传输
- v3 加入 FP8 支持
- **2-4× 速度**，**> 2× 长 context 支持**

基本所有现代推理引擎内置。

### 技术 3 · Speculative Decoding（投机采样）

用**小模型（draft model）**先预测 K 个 token，大模型**一次性验证**：

```
小模型: Llama-8B 快速出 10 tokens
大模型: Llama-70B 并行验证
  → 接受前 k 个一致的
  → 大模型整体前向 1 次得到 k 个 tokens
```

**加速 2-3×**（视 draft 接受率）。变体：
- **EAGLE**（training-based）
- **Medusa**（多 head 投机）
- **Lookahead Decoding**（2024）

### 技术 4 · 量化（Quantization）

| 精度 | 内存减 | 效果损失 |
|---|---|---|
| FP16 (baseline) | 1× | - |
| BF16 | 1× | 几乎无 |
| **FP8 (H100+)** | 2× | 几乎无（H100 / B200 原生）|
| **INT8** | 2× | < 1% 任务质量 |
| **INT4 (AWQ / GPTQ)** | 4× | < 2% |
| 2-bit | 8× | 大幅降质 |

典型路径：
- **GPTQ**：Post-training，量化校准简单
- **AWQ**：Activation-aware，精度更好
- **FP8**：H100 / B200 新硬件原生支持

### 技术 5 · MoE（Mixture of Experts）

- 模型有 N 个 "专家" + 路由
- 每 token 只激活 2-4 个专家
- **激活参数只有总参数的 1/4-1/8** → 推理成本降

代表：**Mixtral 8x7B**（总 47B、激活 13B）· **DeepSeek-V2 / V3** · **Qwen MoE**

生产挑战：**显存占用不减**（所有专家都要 load），只减**计算**。

## 3. 架构对比 · 主流推理引擎

### vLLM（OSS 事实标准）

- UC Berkeley 开源（2023.06）· PagedAttention 原创
- Python + CUDA，易用性好
- 支持 Llama / Mistral / Qwen / DeepSeek 等主流模型
- **适合**：中等规模、快速起步、生态最全

### SGLang（2024 新星）

- **RadixAttention**（前缀共享 cache）
- 前端 DSL 优化复杂 prompt pattern（如 Agent Tree）
- **同硬件比 vLLM 快 30-50%**
- **适合**：RAG / Agent 复杂 pattern、高并发

### TensorRT-LLM（NVIDIA）

- NVIDIA 官方，C++ + CUDA 深度优化
- 量化内核最快
- 部署复杂
- **适合**：纯 NVIDIA 栈、极致性能

### Hugging Face TGI (Text Generation Inference)

- HF 官方，Rust + Python
- 生态最广，易集成
- 性能稍逊 vLLM
- **适合**：已有 HF 栈

### Triton + TensorRT-LLM Backend

- NVIDIA 工业级推理服务器
- 多模型、多框架统一
- 运维复杂但稳
- **适合**：企业多模型共用

## 4. 工程细节

### 选型决策

| 场景 | 推荐 |
|---|---|
| 快速起步、OSS | **vLLM** |
| 追求极致性能、H100+ | **TensorRT-LLM** |
| Agent / RAG 复杂 prompt | **SGLang** |
| 生产企业、多模型管理 | **Triton + TRT-LLM** |
| HF 生态深度用户 | **TGI** |

### 典型 vLLM 部署

```bash
docker run --gpus all \
  --shm-size=10g \
  -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model meta-llama/Llama-3-70B-Instruct \
  --quantization awq \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192 \
  --tensor-parallel-size 2
```

**关键参数**：
- `tensor-parallel-size`：多卡切模型（跨 GPU）
- `gpu-memory-utilization`：默认 0.9
- `max-model-len`：最大 context（影响 KV cache 大小）
- `quantization`：`awq` / `gptq` / `fp8`

### 长 Context 的特殊挑战

- **KV Cache 爆炸**：70B 模型 + 128k context 需要几十 GB KV
- **Prefix Caching**：vLLM 自动共享公共前缀
- **PagedAttention 分页**：支持超长 context 不 OOM

### Speculative 使用

```python
# vLLM 开启 speculative
llm = LLM(
    model="Llama-3-70B-Instruct",
    speculative_model="Llama-3-8B-Instruct",
    num_speculative_tokens=5,
)
```

## 5. 性能数字

### H100 80G 单卡 · Llama-3-70B AWQ

| 引擎 | 吞吐（tokens/s） | p99 延迟 |
|---|---|---|
| HF Transformers | 30 | 高 |
| vLLM 0.6 | 300-500 | 中 |
| SGLang | 400-700 | 低（含 cache） |
| TensorRT-LLM | 500-800 | 最低 |

### 双 H100 · Llama-3-405B FP8

| 引擎 | 吞吐 |
|---|---|
| vLLM | 100 tokens/s |
| TensorRT-LLM | 150-200 tokens/s |

### Speculative 加速比（典型）

| 模型组合 | 加速倍数 |
|---|---|
| Llama-70B + Llama-8B draft | 2-3× |
| Llama-405B + Llama-70B draft | 1.5-2× |
| Medusa 4 heads | 2-3× |

## 6. 代码示例

### vLLM OpenAI-compatible API

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")

response = client.chat.completions.create(
    model="meta-llama/Llama-3-70B-Instruct",
    messages=[{"role": "user", "content": "..."}],
    max_tokens=500,
    stream=True,
)
for chunk in response:
    print(chunk.choices[0].delta.content, end="")
```

### SGLang 并发 Agent

```python
import sglang as sgl

@sgl.function
def tool_agent(s, query):
    s += "User: " + query + "\n"
    s += "Assistant: " + sgl.gen("thought", max_tokens=128)
    s += "Action: " + sgl.gen("action", choices=["search", "calc", "done"])
    if s["action"] == "search":
        s += "Result: " + call_search(s["thought"])
    # ...

# 并发执行
state = tool_agent.run_batch([{"query": q} for q in queries], concurrency=16)
```

## 7. 陷阱与反模式

- **直接用 HF Transformers 做 Production 服务**：10× 慢还未收尾延迟
- **tensor_parallel_size 设错**：不是越多越好，通信开销会压住收益
- **KV Cache 预算不够**：大并发 OOM
- **量化后不评估质量**：INT4 在某些任务（代码 / 数学）掉 5-10% 性能
- **Speculative draft 选错**：draft 模型太大反而慢
- **无批处理**：一条一条发 → GPU 利用率 < 20%
- **忽视硬件**：A100 vs H100 有 2-3× 差异，FP8 只在 H100+

## 8. 横向对比 · 延伸阅读

- [RAG](../ai-workloads/rag.md) —— LLM 推理的主要消费者
- [Agents on Lakehouse](../ai-workloads/agents-on-lakehouse.md)
- [MCP](../ai-workloads/mcp.md)

### 权威阅读

- **[vLLM 论文: *Efficient Memory Management for Large Language Model Serving with PagedAttention* (SOSP 2023)](https://arxiv.org/abs/2309.06180)**
- **[Flash Attention 系列论文](https://arxiv.org/abs/2205.14135)**（v1/2/3）
- **[SGLang: RadixAttention](https://arxiv.org/abs/2312.07104)**
- **[vLLM 官方](https://docs.vllm.ai/)** · **[SGLang](https://github.com/sgl-project/sglang)** · **[TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)**
- **[*The Illustrated Transformer* (Jay Alammar)](https://jalammar.github.io/illustrated-transformer/)**
- **[Simon Willison LLM 推理博客](https://simonwillison.net/tags/llms/)**
