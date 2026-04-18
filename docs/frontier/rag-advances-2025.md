---
title: RAG 前沿 2025 · CRAG / Self-RAG / Agentic RAG / Contextual Retrieval
type: concept
depth: 资深
level: A
applies_to: 2024-2025 主要进展
tags: [frontier, rag, retrieval, llm]
aliases: [Advanced RAG]
related: [rag, hybrid-search, rerank, agentic-workflows]
status: stable
---

# RAG 前沿 · 2024-2025 重要进展

!!! tip "一句话理解"
    2023 年 RAG 主要是"向量检索 + 拼 Prompt"。**2024-2025 年 RAG 进化成多种高级范式**：上下文压缩、反馈循环、自适应检索、Agent 化。效果上 recall 相对 vanilla RAG 提升 **20-50%**，幻觉率降至 < 2%。

!!! abstract "TL;DR"
    - **Contextual Retrieval**（Anthropic 2024.09）：chunk 前置补上下文，recall +35%
    - **CRAG**（Corrective RAG）：检索质量不够时自动回退到 Web / 其他源
    - **Self-RAG**：模型自己决定"要不要检索 / 检索质量如何"
    - **Agentic RAG**：RAG 作为 Agent 的 Tool，支持多跳推理
    - **Multi-Query / HyDE**：用 LLM 改写 / 构造假设答案再检索
    - **ColBERT v2**：Late Interaction，精度最高但贵

## 1. 从 Vanilla RAG 到 Advanced RAG

Vanilla RAG（2020-2023）：
```
query → encode → vector search TopK → prompt → LLM
```

问题：
- **检索精度**：向量可能找不到相关段落
- **幻觉**：找到不相关段落，LLM 仍然瞎编
- **复杂推理**：多跳、需要迭代的问题做不了
- **上下文有限**：填满 context 不代表效果好

2024-2025 的演进方向 → **让检索更智能、让流程更自适应**。

## 2. 关键进展

### 进展 1 · Contextual Retrieval（Anthropic 2024.09）

**核心思想**：每个 chunk 前置补一段"这个 chunk 在整个文档里的上下文"，再 embed。

```
原 chunk:
"Apple's revenue grew 15% in Q3."

Contextual chunk:
"From Apple Q3 2024 Earnings Report - Regional Performance:
 Apple's revenue grew 15% in Q3."
```

**做法**：用 LLM（Claude / GPT）预处理每个 chunk，生成 50-100 token 的 context。

**效果**（Anthropic 实测 BEIR 子集）：
- Chunk recall 提升 35%
- 配 rerank 再提升额外 5%
- **最佳组合**：Contextual Embedding + BM25 + Rerank → 相比 baseline +67%

**成本考量**：
- 一次性预处理成本（每文档 LLM 调用）
- Prompt caching 让成本降 90%
- 生产可控：$1 / 1M tokens 级别

### 进展 2 · CRAG (Corrective RAG, Yan et al. 2024)

对检索质量**自动打分 + 纠正**：

```
检索 → Retrieval Evaluator 打分
    ↓
高质量 → 直接用
中等   → Query 重写 + 重检索 / Web 搜索补
低质量 → Web 搜索 / 其他 fallback
```

关键：**Retrieval Evaluator**——一个小模型判断检索结果是否相关。

### 进展 3 · Self-RAG (Asai et al. 2023)

让**模型自己**在生成时决定：
- **[Retrieve?]**：需不需要检索？
- **[Relevant?]**：这些检索到的片段相关吗？
- **[Grounded?]**：我的输出有没有基于 context？
- **[Useful?]**：答案有用吗？

通过**特殊 reflection tokens** 让 LLM 自监督训练。效果：
- 幻觉率明显降低
- 不需要检索的问题不浪费时间
- 长答案各段都有 grounding

### 进展 4 · Agentic RAG

把 RAG 做成 **Agent 的 Tool**，而不是单次调用：

```
Agent（LLM + Loop）
  │
  ├── Think：问题分解
  ├── Tool: vector_search → 初步答案
  ├── Think：不够完整，需要补数据
  ├── Tool: SQL 查库 → 具体数字
  ├── Tool: vector_search（改写 query）→ 对比信息
  └── Synthesize：综合回答
```

特点：
- **多跳推理**：复杂问题能拆解
- **动态检索**：不是一次 TopK，而是按需多次
- **结果验证**：自我检查

实现：LangGraph / LlamaIndex / AutoGen / LangChain LCEL 都支持。

### 进展 5 · HyDE (Hypothetical Document Embeddings, Gao et al. 2022)

**先让 LLM 假设答案**，用假设答案的 embedding 检索：

```
Query: "HNSW 的 M 参数如何调优"
      ↓
LLM 生成假设答案：
"HNSW 的 M 参数通常在 16-64 之间，具体调优..."
      ↓
用假设答案的 embedding 检索
```

**直觉**：假设答案和真实答案**分布接近**，比 query embedding 更准。

2024 年已广泛集成，LlamaIndex / LangChain 都原生支持。

### 进展 6 · Multi-Query RAG

LLM 把 query 改写成多个变体：

```
Query: "怎么提升 RAG 的 recall"
  ↓
Multi-Query:
  - "如何优化 RAG 检索的召回率"
  - "Hybrid search 怎么提升 recall"
  - "Rerank 对 RAG 效果的影响"
  ↓
并行检索 + 融合
```

### 进展 7 · ColBERT v2 / Late Interaction

每个 token 保留独立向量，检索时**token 级交互**：

```
query tokens × doc tokens → max-sim 矩阵 → 相关性
```

**效果**：精度接近 Cross-Encoder Rerank、延迟显著低于 Rerank。

代价：存储是普通 dense 的 10× 以上。

### 进展 8 · LLMLingua / Contextual Compression

用小模型**压缩** retrieved contexts：

```
100 个 chunk（100k tokens）
  ↓
Small LLM 压缩器
  ↓
50 个高信息密度 chunk（30k tokens）
  ↓
主 LLM 生成
```

**效果**：Token 成本降 60-80%，质量下降 < 5%。

## 3. 性能对比 · 相对 Vanilla RAG 提升

（基于 BEIR、RAGAS、自建评估集的综合）

| 技术 | NDCG@10 提升 | 延迟开销 | 推荐优先级 |
|---|---|---|---|
| **Hybrid Search（基础）** | +10 | 低 | ★★★★★ |
| **Rerank（基础）** | +15 | 中 | ★★★★★ |
| **Contextual Retrieval** | +35 (叠加 Hybrid+Rerank) | 一次性高 | ★★★★ |
| **HyDE** | +5-10 | 中（多一次 LLM） | ★★★ |
| **Multi-Query** | +5-8 | 中（并发）| ★★★ |
| **CRAG** | +5-10 | 中 | ★★★ |
| **Self-RAG** | +8-15 | 中（训练代价）| ★★ |
| **Agentic RAG** | +10-30（复杂问题）| 高 | ★★★（复杂场景）|
| **LLMLingua 压缩** | ~0 | 降延迟 | ★★★（省成本）|

## 4. 工程选型

### 2025 推荐的现代 RAG 管线

```
Indexing 阶段：
  文档 → Contextual Chunking（用 LLM 加前缀）→ 双 Embedding（dense + SPLADE）→ 存储

Query 阶段：
  Query → [可选 HyDE / Multi-Query]
        → Hybrid Search（RRF 融合）
        → Cross-Encoder Rerank
        → [可选 LLMLingua 压缩]
        → Prompt → LLM
```

### 分场景选择

| 场景 | 最佳组合 |
|---|---|
| 企业知识问答 | Hybrid + Contextual + Rerank |
| 代码助手 | Hybrid + ColBERT + 代码感知 chunk |
| 法务 / 合规 | Agentic RAG + 多源验证 + 强引用 |
| 客服 FAQ | Hybrid + Rerank（成本敏感）|
| 科研 / 论文分析 | Agentic RAG + 多跳 |
| 长文档处理 | Contextual + LLMLingua 压缩 |

## 4.5. 现实检视 · 哪些"被验证"哪些"仅在论文"

面对前沿 RAG 的风潮，**需要分清三类信号**：

### 已在工业规模验证（可以上）

- **Hybrid Search（BM25 + Dense + RRF）**—— 多家公司产品化、BEIR 稳定
- **Cross-Encoder Rerank** —— 2023+ 全行业标配
- **Contextual Retrieval**（Anthropic）—— Anthropic 自己产品 + 多个云厂商复现报告；**但 +35% 的数字**依赖数据 + 领域，自家数据可能 +10%-+25%

### 论文结论好、工业复现有限

- **CRAG**：检索打分 + Web fallback 思想好，但"Retrieval Evaluator 小模型"在企业闭域效果差异大，**很多团队复现不出论文级提升**
- **Self-RAG**：需要专门 fine-tune、零样本上难、落地门槛高
- **Agentic RAG**：多跳推理理论好，**延迟与成本实际吃不消**；单个 p99 经常 > 10s，LLM 调用费指数涨
- **HyDE**：在 factoid 问题有效、在复杂问题可能误导；**实测提升常 < 5%**

### 学术信号但商业化尚未

- **ColBERTv2**：精度好但存储成本 10-20×，规模上不去
- **LLM-as-Reranker**：精度高但延迟成本难承受

### 实务建议

1. **先上 Hybrid + Rerank + Contextual Retrieval** —— 这三个组合已是 2025 "新 baseline"
2. **复杂范式（CRAG / Agentic）先 POC、测自家 recall/cost/latency 再决定**
3. **警惕 benchmark 数字**：论文报告 +30%，自家业务可能只 +5% 或 0%；**必做自测**
4. **成本预算先算清**：Contextual chunking 一次性 LLM 成本可以接受；Agentic RAG 每次 query N 倍 LLM call 要算账

### 坏信号识别

- 论文 NDCG 提升 20%+ 但**没提及推理成本** → 警惕
- 论文声称通用，但**只在 Wikipedia / 新闻数据集**验证 → 自家企业闭域可能失效
- 博客文案"我们用 XXX RAG 把准确率做到 95%"但**不说 baseline** → 几乎无信息

## 5. 陷阱

- **加完所有进展还没好**：检查 evaluation 数据真实性、**baseline 是否测对**
- **Contextual 成本没算**：100k 文档 × LLM 预处理 = 非零成本
- **Agentic RAG 延迟失控**：多轮调用 p99 可能 10+s
- **ColBERT 存储爆**：每 doc × 512 token × 768 dim = × 512 空间
- **Self-RAG 需要 fine-tune**：不能零样本上
- **HyDE 在 factoid 问题上有效**，**在探索性问题上可能误导**

## 6. 延伸阅读

- **[Anthropic Contextual Retrieval (2024.09)](https://www.anthropic.com/news/contextual-retrieval)** —— 必读
- **[CRAG (Yan et al., 2024)](https://arxiv.org/abs/2401.15884)**
- **[Self-RAG (Asai et al., 2023)](https://arxiv.org/abs/2310.11511)**
- **[HyDE (Gao et al., 2022)](https://arxiv.org/abs/2212.10496)**
- **[ColBERTv2 (Santhanam et al., NAACL 2022)](https://arxiv.org/abs/2112.01488)**
- **[LLMLingua (Jiang et al., 2023)](https://arxiv.org/abs/2310.05736)**
- **[LlamaIndex RAG Cookbook](https://docs.llamaindex.ai/en/stable/optimizing/production_rag/)**
- **[LangChain RAG patterns](https://python.langchain.com/docs/tutorials/rag/)**

## 相关

- [RAG](../ai-workloads/rag.md) —— 基础概念
- [Hybrid Search](../retrieval/hybrid-search.md) · [Rerank](../retrieval/rerank.md)
- [RAG on Lake 场景](../scenarios/rag-on-lake.md)
- [Agentic Workflows](../scenarios/agentic-workflows.md)
