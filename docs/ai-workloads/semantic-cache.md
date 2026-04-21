---
title: Semantic Cache（语义缓存）
type: concept
tags: [ai, cache, rag]
aliases: [语义缓存, LLM Cache]
related: [rag, embedding, vector-database]
systems: [redis, lancedb, milvus]
status: stable
---

# Semantic Cache（语义缓存）

!!! tip "一句话理解"
    **"语义相近的请求返回相同答案"**的缓存。传统缓存按 key 精确命中；语义缓存按 embedding 距离命中。主要用来**降低 LLM 调用成本和延迟**。**注意区分**：和 **Prompt Caching**（2024+ LLM API 原生的前缀字节 KV cache · 本页末对比）机制完全不同。

## 为什么需要

RAG / LLM 服务的成本与延迟主要来自两处：

1. **LLM 推理**（大头）
2. **向量检索 + rerank**（小头）

线上用户问题有**高度语义重复**："如何安装 X / X 怎么装 / 请教 X 安装步骤"其实是同一个问题。传统 key 缓存完全命中不了。

**语义缓存**：把问题 embedding 一下，查缓存里有没有距离 < 阈值的条目；命中就直接返答案，节省整条 LLM 链路。

## 两种形态

### 精确语义缓存（保守）

- 阈值严格（cosine > 0.95），几乎同义才命中
- 适合**低错误容忍**场景
- 典型节省：10%–30% 请求

### 模糊语义缓存（激进）

- 阈值放宽（cosine > 0.85）
- 更高命中率但可能把"意思相近但答案应该不同"的 query 当相同
- 适合客服 FAQ 这类**答案本就泛化**的场景
- 典型节省：30%–60% 请求

## 工程实现

```mermaid
flowchart LR
  q[用户 Query] --> qe[Query Encode]
  qe --> lookup[向量库<br/>cache collection]
  lookup --> hit{命中?}
  hit -->|是| fast[直接返答案]
  hit -->|否| full[走完整 RAG 链路]
  full --> write[写回 cache]
  write --> fast
```

缓存层通常用：

- **Redis** +  RediSearch 向量字段 —— 低延迟、易运维
- **LanceDB** 嵌入式 —— 简单部署
- **Milvus** —— 如已在跑，复用即可

## 命中阈值怎么定

**不能凭感觉**。流程：

1. 线下跑一批真实问答对
2. 人工标注"语义相同 / 部分相同 / 不同"
3. 画 recall / precision vs 阈值曲线
4. 选业务可接受的 FP 率对应的阈值

典型落点：cosine **0.90–0.95**。

## 带过期与失效

内容会变、模型会变。缓存不是永久的：

- **TTL**：按条目 N 天自动过期
- **版本失效**：Embedding 模型换了整批作废
- **内容 hash 关联**：如果答案来自某个文档，文档 hash 变了同步作废
- **LRU / LFU**：有容量上限时按热度淘汰

## 陷阱

- **把"意图不同但词相近"当相同** —— "学校怎么走" vs "学校怎么申请"
- **时间敏感类问题** —— "今天天气"绝不能缓存
- **个性化 query 泄漏** —— 带用户 ID 的缓存条目不能跨用户命中
- **阈值漂移** —— 模型升级后阈值要重新校准

## 监控

- 命中率（按 query 类型分桶）
- 命中后的用户满意度（错误命中会导致投诉）
- 节省的 LLM token 数 / 成本
- 缓存大小 / 淘汰率

## 代码示例 · GPTCache + LangChain

```python
from gptcache import Cache
from gptcache.adapter.langchain_models import LangChainChat
from gptcache.embedding import Onnx
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation
from gptcache.manager import CacheBase, VectorBase, get_data_manager

cache = Cache()
embedding = Onnx()  # or OpenAI / BGE / Cohere
cache.init(
    pre_embedding_func=lambda data, **_: data["messages"][-1]["content"],
    embedding_func=embedding.to_embeddings,
    data_manager=get_data_manager(
        CacheBase("sqlite"),
        VectorBase("lancedb", dimension=embedding.dimension, top_k=3),
    ),
    similarity_evaluation=SearchDistanceEvaluation(),
)

# 阈值：cosine distance ≤ 0.2 视为命中（等价 cosine similarity ≥ 0.8）
cache.set_openai_key()  # 或其他 provider
llm = LangChainChat(cache=cache, cache_obj=cache)

# 首次调 LLM · 第二次相似 query 直接返回 cache
```

## 和 Prompt Caching（系统级）的区别 · 关键

**2024+ 每家 LLM 厂商都推出 Prompt Caching** · 但**和 Semantic Cache 机制完全不同**：

| | **Semantic Cache**（本页）| **Prompt Caching** |
|---|---|---|
| 层级 | **应用层缓存** · 我方代码 | **LLM 服务端 KV cache** |
| 命中条件 | 语义相近（embedding 距离）| **前缀字节完全相同** |
| 粒度 | Query 级（整个 user query）| Token 级（prompt 前缀） |
| 效果 | **跳过整个 LLM 调用** | 减少**输入 token** 计费 |
| 命中后延迟 | ~10ms（向量库查询）| LLM 仍要生成输出 · 只减少 prefill 延迟 |
| 折扣 | 成本节省 100%（命中那次） | 10-90% 输入 token 成本 |
| 典型命中率 | 10-60%（视业务）| System prompt / tool schema 复用场景 100% |

### 2024-2026 厂商 Prompt Caching

| 厂商 | 机制 | 定价 |
|---|---|---|
| **Anthropic Prompt Caching**（2024-08 GA）| 手动 `cache_control` 标记 · 5min / 1h TTL | 缓存写 +25% · 读 **-90%** |
| **OpenAI Prompt Caching**（2024-10+）| **自动**检测相同前缀（≥ 1024 tokens）| 自动 · 约 **-50%** 命中部分 |
| **Gemini Context Caching** | API 显式创建 cache · TTL 管理 | 按缓存部分 token 折扣 |

### 何时用哪个

- **System prompt 长** / **tool schema 定义长** / **RAG 大文档作 context** · → **Prompt Caching**
- **Q&A 重复高** · 同类问题反复问 → **Semantic Cache**
- **两者叠加用**（推荐）：Semantic Cache 挡语义重复 · Prompt Caching 减剩余调用的 token 成本
- 详见 [Prompt 管理 · Prompt Caching 章节](prompt-management.md)

## 相关

- [RAG](rag.md) · [Prompt 管理](prompt-management.md) · [LLM Gateway](llm-gateway.md) · [LLM Inference](llm-inference.md)
- [Embedding](../retrieval/embedding.md) · [向量数据库](../retrieval/vector-database.md)

## 延伸阅读

- **[GPTCache 开源项目](https://github.com/zilliztech/GPTCache)**
- **[Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)**
- **[OpenAI Prompt Caching](https://platform.openai.com/docs/guides/prompt-caching)**
- **[Gemini Context Caching](https://ai.google.dev/gemini-api/docs/caching)**
- **[LangChain Semantic Cache 文档](https://python.langchain.com/docs/integrations/llm_caching/)**
