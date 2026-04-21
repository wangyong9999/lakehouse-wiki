---
title: LLM Inference · 推理栈与服务引擎
type: system
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: vLLM 0.10+ · SGLang 0.4+ · TensorRT-LLM / Triton · Dynamo · 2024-2026 生态
tags: [ai, llm, inference, serving, vllm, sglang]
status: stable
---

# LLM Inference · 推理栈与服务引擎

!!! tip "一句话定位"
    **让 LLM 跑得更快、更便宜、支持更多并发**。过去两年推理侧工程创新（PagedAttention / Continuous Batching / Flash Attention / Speculative Decoding / MoE / Quantization）让同样硬件吞吐提升 **5-30 倍**。**生产 LLM 负载的成本关键** · **LLM Gateway 的后端**。

!!! abstract "TL;DR"
    - **吞吐关键**：Continuous Batching + PagedAttention（vLLM 首创 · SOSP 2023）· 2026 vLLM 0.10+ 加 async scheduling + zero-bubble speculative overlap
    - **延迟关键**：Flash Attention + Speculative Decoding · Prefix / Prompt Caching
    - **成本关键**：量化（INT8 / INT4 / FP8 / AWQ / GPTQ）+ MoE
    - **主流引擎**：vLLM（OSS 主流）· SGLang（RadixAttention + 结构化输出最快）· TensorRT-LLM（NVIDIA 官方极致）· Triton（多模型企业级）· TGI（HF 生态）
    - **Serverless**：Modal · Replicate · Together · Anyscale · Bedrock / Azure Foundry 托管推理
    - **和 LLM Gateway 分工**：**Gateway 是代理层**（路由 · 限流 · 审计）· **Inference 是执行层**（模型 · KV · batch）

!!! info "本页说明"
    本页从 `frontier/llm-inference-opt.md` 下沉而来（按 [ADR 0009](../adr/0009-frontier-to-main-migration.md) · vLLM 2025 过 1.0 · 主流生产工具链 · 已满足下沉门槛）。原 frontier 页保留为 superseded stub。

## 1. 业务痛点 · 直接跑 Transformers 为什么慢

### HuggingFace Transformers 原生跑推理

```python
model = AutoModel.from_pretrained("Llama-70B")
output = model.generate(input_ids, max_new_tokens=500)
```

**问题**：

| 问题 | 后果 |
|---|---|
| **KV Cache 连续内存** | GPU 内存碎片 / OOM |
| **固定 batch size** | 短请求等长请求 · GPU 利用率 ~ 20% |
| **Attention 全计算** | O(n²) 随 context 长度爆 |
| **单 token 单步** | 生成 500 token 要 500 次前向 |
| **FP16 全量** | 70B × 2 bytes = **140 GB** 显存 |

典型吞吐对比（H100 单卡 Llama-3-70B AWQ · tokens/s · 报告来源不同 · 差异可能大）：
- HF Transformers：~30
- vLLM 0.10：**300-500**
- SGLang 0.4：**400-700**（含 prefix cache · 前缀共享场景）
- TensorRT-LLM：**500-800**

## 2. 五大核心优化

### 技术 1 · PagedAttention + Continuous Batching（vLLM 首创）

**PagedAttention**（类比 OS 虚拟内存分页）：
- KV Cache 分固定 block（默认 16 tokens / block）
- 不要求连续内存 · 消除碎片
- 动态分配 + **Prefix Caching**（多请求共享公共前缀 KV）

**Continuous Batching**：
- 不按固定 step 推进 · 每一步都合并新请求 / 踢出完成请求
- GPU **永远**忙 · 吞吐提升 5-10× · 尾延迟大幅改善

**2026 增强（vLLM 0.10+）**：
- **async scheduling** 与 speculative decoding **zero-bubble overlap** · 显著提高投机解码吞吐
- **Model Runner V2** + piecewise CUDA graphs（含 pipeline parallelism 路径）
- **Vision encoders 完整 CUDA graph capture**（多模态场景收益明显）

### 技术 2 · Flash Attention（v3 2024 定稿 · FP8 支持）

IO-aware attention：tiling + recomputation 减少 HBM ↔ SRAM 传输。v3 加 FP8。**2-4× 加速 · > 2× 长 context 支持**。几乎所有现代推理引擎内置。

### 技术 3 · Speculative Decoding（投机采样）

用**小模型（draft）**先预测 K 个 token · 大模型**一次并行验证**：

```
draft: Llama-3-8B 快速出 5-10 tokens
target: Llama-3-70B 一次前向并行验证
  → 接受前 k 个一致
  → 大模型 1 次前向得 k 个 token · 总加速 2-3×
```

2026 变体：
- **EAGLE-3**（training-based · 接受率高）
- **Medusa**（多 head 投机 · 无需 draft model）
- **Lookahead Decoding** / **RetrievalLLM**（基于前文 n-gram 检索）
- vLLM 0.10 的 async scheduling + zero-bubble 专门优化这条路径

### 技术 4 · 量化（Quantization）

| 精度 | 内存减 | 质量损失（典型） |
|---|---|---|
| FP16（baseline）| 1× | - |
| BF16 | 1× | ≈ 0 |
| **FP8（H100+ / B200 原生）** | 2× | 长生成任务仍在评估 · 代码 / 数学轻微 |
| **INT8（SmoothQuant / W8A8）** | 2× | < 1% 任务质量 |
| **INT4（AWQ / GPTQ）** | 4× | < 2% 一般任务 · 代码 / 数学可掉 5-10% |
| **2-bit（研究阶段）** | 8× | 大幅降质 · 不生产 |

- **GPTQ**：Post-training · 量化校准简单 · 工具多
- **AWQ**：Activation-aware · 精度更好 · 当下首选开源
- **FP8**：H100 / B200 硬件原生 · 2025-2026 主流训练推理闭环

### 技术 5 · MoE（Mixture of Experts）

- 模型有 N 个"专家" + 路由 · 每 token 激活 2-4 个
- **激活参数**只有总参数 1/4 - 1/8 · 推理算力降
- 代表：**Mixtral 8×7B**（总 47B · 激活 13B）· **DeepSeek-V3**（671B · 激活 37B）· **Qwen3 MoE** · **Google Gemma 4**（vLLM 2026 已支持）

**生产挑战**：**显存占用不减**（所有专家都要 load）· 只减**计算** · 多卡切分策略（Expert Parallel）复杂。

## 3. 引擎对比 · 2026 主流

### vLLM（OSS 主流 · 事实默认）

- UC Berkeley 开源（2023-06 发布 · 2025 过 1.0 · 当前 0.10+）
- **PagedAttention 原创** · SOSP 2023 论文
- Python + CUDA · 易用性好 · OpenAI-compatible API
- 2026 支持 **Gemma 4 完整架构**（含 MoE / 多模态 / reasoning / tool-use）
- 支持 Llama / Mistral / Qwen / DeepSeek / GLM / Yi / Phi 等主流模型
- **适合**：中等规模 · 快速起步 · 生态最全 · 通用场景

### SGLang（2024 新星 · 结构化输出王者）

- LMSYS 开源 · NeurIPS 2024 论文
- **RadixAttention** · 前缀共享 cache 极致优化
- **Compressed FSM 结构化输出**：JSON 解码最高 **6.4× 吞吐**（vs 其他引擎）
- 前端 DSL 优化复杂 prompt（Agent Tree / RAG 多 hop）
- **适合**：RAG / Agent 复杂 pattern · 高并发前缀共享场景 · **JSON / 结构化输出为主**

### TensorRT-LLM（NVIDIA 官方 · 极致性能）

- NVIDIA 官方 · C++ + CUDA 深度优化
- 量化内核最快 · FP8 支持完整
- 部署复杂 · 文档门槛
- **适合**：纯 NVIDIA 栈 · 极致吞吐 · H100+ 硬件

### Triton + TensorRT-LLM Backend

- NVIDIA 工业级推理服务器 · 多模型 / 多框架统一
- 运维复杂但稳
- **适合**：企业多模型共用 · 现有 Triton 栈

### NVIDIA Dynamo（2025 新 Inference Server）

- NVIDIA 2025 发布 · 替代 Triton 路线的下一代 · 专为 LLM 推理设计
- Disaggregated Prefill / Decode · KV Cache Store（跨节点共享）
- 当前主要 NVIDIA 生态推广 · 社区 adoption 还在早期
- **适合**：2026-2027 评估方向 · 大厂 PoC 起步

### Hugging Face TGI

- HF 官方 · Rust + Python · 易集成
- 性能稍逊 vLLM · 但 HF 生态内最平滑
- **适合**：已有 HF 栈深度用户

### Serverless LLM 托管

| 方案 | 定位 |
|---|---|
| **Modal** | Python-native · 快速部署 · 按执行计费 |
| **Together AI** | 100+ 开源模型 API · 按 token 计费 |
| **Replicate** | 模型 marketplace · 按执行计费 |
| **Anyscale** | Ray 生态 · 企业分布式 |
| **AWS Bedrock** | 托管 + enterprise 合规 |
| **Azure AI Foundry** | Microsoft 栈整合 |
| **OpenRouter** | 200+ 模型聚合 · 开发者友好 |

**典型路径**：**先托管跑起来 · 成本 / 延迟痛了再自建**。

## 4. 选型决策

| 场景 | 推荐 |
|---|---|
| 快速起步 · OSS · 生态 | **vLLM** |
| JSON / 结构化输出为主 | **SGLang** |
| Agent / 复杂 prompt · 前缀共享 | **SGLang** |
| 极致吞吐 · H100+ / B200 | **TensorRT-LLM** |
| 企业多模型管理 | **Triton + TRT-LLM** · 或评估 Dynamo |
| HF 生态深度用户 | **TGI** |
| POC / 不想运维 | Modal · Together · Bedrock |
| 研发阶段 · 成本敏感 | OpenRouter · Together |

## 5. 工程细节

### vLLM 生产部署

```bash
docker run --gpus all \
  --shm-size=10g \
  -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model meta-llama/Llama-3.3-70B-Instruct \
  --quantization awq \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192 \
  --tensor-parallel-size 2 \
  --enable-prefix-caching
```

**关键参数**：
- `tensor-parallel-size`：跨 GPU 切模型 · 不是越多越好（通信开销）
- `gpu-memory-utilization`：默认 0.9 · KV cache 预算留给它
- `max-model-len`：最大 context 长度 · 影响 KV cache 规模
- `quantization`：`awq` / `gptq` / `fp8`（H100+）
- `enable-prefix-caching`：多请求共享公共前缀 KV · 对 RAG / Agent 有用

### 长 Context 特殊挑战

- **KV Cache 爆炸**：70B + 128k context 需要几十 GB KV
- **Prefix Caching**：vLLM 自动共享公共前缀 · 显著减重复计算
- **Sliding Window / YaRN / RoPE scaling**：扩展 context 长度的工程技巧
- **Anthropic Prompt Caching / OpenAI Prompt Caching**：**系统级缓存**（API 侧）· 和 PagedAttention 是两层（详见 [Semantic Cache](semantic-cache.md)）

### Speculative 使用

```python
# vLLM speculative
llm = LLM(
    model="meta-llama/Llama-3.3-70B-Instruct",
    speculative_model="meta-llama/Llama-3.2-3B-Instruct",
    num_speculative_tokens=5,
)
```

## 6. 性能数字 · 2026 典型

### H100 80G 单卡 · Llama-3.3-70B AWQ（tokens/s）

| 引擎 | 吞吐 | p99 延迟 | 备注 |
|---|---|---|---|
| HF Transformers | ~30 | 高 | baseline · 不生产 |
| vLLM 0.10 | 300-500 | 中 | OSS 主流 |
| SGLang 0.4（含 prefix cache）| 400-700 | 低 | 前缀共享场景 |
| TensorRT-LLM | 500-800 | 最低 | NVIDIA 原生 |

（数字依 prompt 分布 / batch / context 长度变化 · 见各引擎 benchmark 报告 · 不同来源差异可能 > 30%）

### Speculative 加速比（典型）

| draft + target | 加速 |
|---|---|
| Llama-3-8B draft + Llama-3-70B target | 2-3× |
| Llama-3-70B draft + Llama-3-405B target | 1.5-2× |
| Medusa 4 heads | 2-3× |

## 7. 现实检视 · 商业 × 技术 × 硬件

### 商业驱动 vs 技术价值

LLM 推理优化领域**商业博弈和技术演进交织** · 读文档时要辨别：

- **厂商"N× 提速"** 多数**特定场景 + 特定硬件 + 特定模型**下最优 · 未必适合你的负载
- **闭源最佳**：TensorRT-LLM 的某些优化**只在 H100+ FP8** · 换代 GPU 效果可能倒退
- **硬件锁定**：NVIDIA 生态全但贵 · AMD MI300 / Groq / Cerebras 有性价比但**生态不完整** · 迁移成本高

### 工业真实瓶颈分布

不是每个团队都在"跑 70B 推理 QPS 上不去"。更常见：

| 瓶颈 | 频率 | 主要解决路径 |
|---|---|---|
| **LLM 调用账单爆** | 🔥🔥🔥 | 选模型 + prompt caching + 限流（见 [LLM Gateway](llm-gateway.md)）|
| **首 token 延迟（TTFT）** | 🔥🔥 | 流式输出 + prefix caching + 模型选型 |
| **GPU 利用率低** | 🔥🔥 | batching + continuous batching |
| **并发抖动** | 🔥 | 队列 + 预留资源 |
| **真正极致 TPS** | 🔥（大厂专属） | vLLM → TRT-LLM → FP8 → Dynamo |

### 绝大多数团队的正确路径

1. 先用**托管 API**（OpenAI / Anthropic / Bedrock / Together）跑起来
2. 成本 / 延迟真成问题再自建
3. 自建**先选 vLLM** · 跑到瓶颈考虑 TensorRT-LLM
4. 硬件**租比买** · 需求稳定再议自采

### 已验证技术 vs 营销口号

| 技术 | 2026 状态 |
|---|---|
| **PagedAttention**（vLLM） | 工业标准 · 强推 |
| **Continuous Batching** | 标准 |
| **Flash Attention 2/3** | 所有主流框架内置 |
| **Speculative Decoding** | 主流采用 · vLLM 0.10 async scheduling 加速 |
| **MoE**（Mixtral / DeepSeek / Qwen3 / Gemma 4）| 主流 · 但显存节省有限 |
| **FP8** | H100+ 主流 · 训推闭环 · 长生成质量仍需评估 |
| **2-bit 量化** | 研究阶段 · 精度掉明显 |
| **"无损 8× 量化"** | ⚠️ 警惕 · 需自家任务 benchmark |

## 8. 陷阱与反模式

- **直接用 HF Transformers 做 Production 服务**：10× 慢还无法控制尾延迟
- **tensor_parallel_size 设错**：不是越多越好 · 通信开销会吃掉收益 · 70B 典型 2-4
- **KV Cache 预算不够**：大并发 OOM · 监控 `gpu-memory-utilization`
- **量化后不评估质量**：INT4 在代码 / 数学任务可掉 5-10% · 生产前必须 benchmark 自家 task
- **Speculative draft 选错**：draft 太大反而慢 · draft 和 target 同家族
- **无批处理**：一条一条发 → GPU 利用率 < 20%
- **忽视硬件差异**：A100 vs H100 有 2-3× 差异 · FP8 只在 H100+
- **Serverless 当 Self-hosted**：按 token 计费模式长期跑比自建贵 3-5×

## 9. 横向对比 · 延伸阅读

- [LLM Gateway](llm-gateway.md) —— 代理层 · Inference 是其后端
- [Semantic Cache](semantic-cache.md) —— 系统级 Prompt Caching 对比 KV cache
- [RAG](rag.md) · [Agent Patterns](agent-patterns.md) —— 主要消费者
- [ml-infra/model-serving](../ml-infra/model-serving.md) —— 通用 ML serving（vs LLM-specific）

### 权威阅读

- **[vLLM: *Efficient Memory Management for Large Language Model Serving with PagedAttention* (SOSP 2023)](https://arxiv.org/abs/2309.06180)** · **[vLLM 官方文档](https://docs.vllm.ai/)**
- **[Flash Attention 系列](https://arxiv.org/abs/2205.14135)**（v1/v2/v3）
- **[SGLang: *Efficient Execution of Structured Language Model Programs* (NeurIPS 2024)](https://arxiv.org/abs/2312.07104)** · **[SGLang 结构化输出](https://docs.sglang.io/advanced_features/structured_outputs.html)**
- **[TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)**
- **[NVIDIA Dynamo](https://github.com/ai-dynamo/dynamo)**（2025 新 Inference Server）
- **[vLLM 2026: In-depth](https://www.programming-helper.com/tech/vllm-2026-high-performance-inference-serving-ai-models-python)**

## 相关

- [LLM Gateway](llm-gateway.md) · [Semantic Cache](semantic-cache.md) · [Guardrails](guardrails.md)
- [RAG](rag.md) · [Agent Patterns](agent-patterns.md) · [MCP](mcp.md)
- [frontier/llm-inference-opt](../frontier/llm-inference-opt.md) —— 本页前身 · 已 superseded
