---
title: Rerank 模型横比 · bge / Cohere / Jina / Voyage / LLM-as-Reranker
type: comparison
depth: 进阶
tags: [comparison, rerank, cross-encoder]
related: [rerank, rag, hybrid-search]
status: stable
---

# Rerank 模型横比

!!! tip "一句话回答"
    **bge-reranker-v2-m3** 在开源多语场景综合最强。**Cohere Rerank 3** 是商业 API 最稳。**Jina Reranker v2** 长文本 + 多语平衡好。纯英场景有 **Voyage Rerank**。**LLM-as-Reranker**（GPT-4 / Claude）精度最高但贵 10-100×。

!!! abstract "TL;DR"
    - **开源首选**：**bge-reranker-v2-m3**（多语、BAAI）或 **v2-gemma**（最高精度）
    - **商业 API**：**Cohere Rerank 3**（语种全 + SLA）
    - **长文本**：**Jina Reranker v2**（8k context）
    - **LLM 作 reranker**：复杂 query 精度最高、延迟成本最高
    - **选型核心**：**语种 · 长度 · 延迟预算 · 开源/商业**

## 1. Rerank 在管线中的位置

```
召回（Hybrid）→ Rerank → LLM / 展示
  Top 50-100   → Top 5-10
```

详见 [Rerank 概念页](../retrieval/rerank.md)。

## 2. 五大方案

### 1. bge-reranker 系列（BAAI 开源）

| 模型 | 参数 | 语种 | 延迟 / doc (A100) |
|---|---|---|---|
| `bge-reranker-base` | 110M | 中英 | 3ms |
| `bge-reranker-large` | 335M | 中英 | 10ms |
| **`bge-reranker-v2-m3`** | 560M | **100+** | 20ms |
| `bge-reranker-v2-gemma` | 2B | 多语、最强 | 60ms |
| `bge-reranker-v2-minicpm` | 2.4B | 多语 | 70ms |

**优**：开源、本地部署、无调用费、BAAI 持续更新
**劣**：需自建 GPU 推理服务
**适合**：私有化、成本敏感、中文为主

### 2. Cohere Rerank

| 模型 | 语种 | 延迟（API）| 价格 |
|---|---|---|---|
| `rerank-3.5` | 多语 | 150ms | $0.002 / search |
| `rerank-english-3.0` | 英文 | 100ms | $0.002 / search |
| `rerank-multilingual-3.0` | 100+ 语 | 150ms | $0.002 / search |

**优**：商业 API、无运维、语种覆盖最广
**劣**：数据出境（合规考量）、成本按 API 算
**适合**：中小团队、多语场景、无自建 GPU

### 3. Jina Reranker v2

- **[jinaai/jina-reranker-v2-base-multilingual](https://huggingface.co/jinaai/jina-reranker-v2-base-multilingual)**
- **开源 + API 双版本**
- **8192 tokens 输入**（长文档）
- 多语支持好

**优**：开源 + 长文本 + 多语
**劣**：相对 bge 社区小一些
**适合**：长文档 RAG、多语

### 4. Voyage AI Rerank

- **voyage-rerank-2** / **voyage-rerank-2-lite**
- **代码 / 法律领域**有专门优化
- 商业 API

**优**：领域特化（代码 / 法律 / 金融）效果突出
**劣**：小众、价格不明
**适合**：特定领域场景

### 5. LLM-as-Reranker

用 Claude / GPT-4 直接 Prompt：

```
Rate the relevance of each document to the query on 0-10:
Query: {query}
Doc 1: {content_1}
Doc 2: {content_2}
...
```

**变体**：
- **RankGPT**：list-wise 排序
- **RankZephyr**：开源小模型精调

**优**：零样本能力强、复杂 query 最准
**劣**：延迟高（每批 500ms+）、成本 × 10-100 vs Cross-Encoder
**适合**：低 QPS 高精度场景（法务 / 研究）

---

## 3. 精度对比（BEIR 子集平均）

| 管线 | NDCG@10 | 相对 baseline |
|---|---|---|
| BM25 + Dense | 0.47 | baseline |
| + `bge-reranker-base` | 0.55 | +8 |
| + `bge-reranker-large` | 0.57 | +10 |
| + `bge-reranker-v2-m3` | 0.59 | +12 |
| + `bge-reranker-v2-gemma` | 0.60 | +13 |
| + `Cohere Rerank 3` | 0.60 | +13 |
| + `Jina Reranker v2` | 0.58 | +11 |
| + `LLM-as-Reranker (GPT-4)` | 0.62 | +15 |

（数据非绝对，**以自家数据为准**。）

## 4. 延迟与成本

### 延迟（10 候选，单 query）

| 模型 | 延迟 |
|---|---|
| bge-reranker-base | 30ms |
| bge-reranker-large | 50ms |
| bge-reranker-v2-m3 | 80ms |
| bge-reranker-v2-gemma | 200ms |
| Cohere Rerank（API）| 100-200ms |
| Jina Reranker v2 | 80ms |
| LLM-as-Reranker (GPT-4) | 500-1500ms |

### 100 候选成本（估算，月 1M searches）

| 方案 | 成本 |
|---|---|
| bge-reranker-base 本地 | ~$500（GPU 摊）|
| bge-reranker-v2-m3 本地 | ~$2000 |
| Cohere Rerank 3 | $2000 |
| LLM-as-Reranker (GPT-4o) | **~$100k** |

## 5. 决策矩阵

| 场景 | 推荐 |
|---|---|
| 中文 + 成本敏感 | **bge-reranker-v2-m3** 本地 |
| 多语言 + API 方便 | **Cohere Rerank 3** |
| 长文本（> 512 tokens） | **Jina Reranker v2** 或 **bge-reranker-v2-gemma** |
| 代码 / 法律领域 | **Voyage** 或 **bge + 领域 fine-tune** |
| 极致精度，低 QPS | **LLM-as-Reranker** |
| 精度 / 延迟 / 成本平衡 | **bge-reranker-large** 或 **Cohere Rerank 3** |

## 6. 部署参考

### bge-reranker 本地服务（TEI）

```bash
docker run --gpus all -p 8080:80 \
  -v $PWD/data:/data \
  ghcr.io/huggingface/text-embeddings-inference:latest \
  --model-id BAAI/bge-reranker-v2-m3 \
  --revision main
```

```python
import requests

r = requests.post("http://localhost:8080/rerank", json={
    "query": "HNSW 的 M 参数如何调优",
    "texts": [doc1, doc2, ...],
    "return_scores": True,
})
```

### Cohere API

```python
import cohere
co = cohere.Client("...")
result = co.rerank(
    model="rerank-3.5",
    query=query, documents=docs, top_n=10
)
```

### LLM-as-Reranker（Claude）

```python
prompt = f"""Rank these documents by relevance to the query (most relevant first).
Query: {query}
Documents:
{format_docs(docs)}
Output JSON list of doc indices in order."""

response = claude.messages.create(model="claude-3-5-sonnet", messages=[{"role": "user", "content": prompt}])
ranked_indices = parse_json(response.content[0].text)
```

## 7. 陷阱

- **没加 Rerank**：RAG 效果失败 #1 原因
- **Rerank 模型和 embedding 模型语种不匹配**
- **候选数固定不调**：50 vs 100 候选对精度影响大
- **Cross-Encoder fp32**：没必要，fp16 能省 50% 延迟
- **批量不够**：一对一对跑，GPU 10% 利用率
- **LLM-as-Reranker 没控延迟**：生产 p99 炸
- **只信 BEIR 数据**：自家业务必测
- **模型版本更新慢**：bge 每 3-6 个月有新版，不跟进效果漂移

## 8. 延伸阅读

- **[bge-reranker Hugging Face](https://huggingface.co/BAAI/bge-reranker-v2-m3)**
- **[Cohere Rerank 文档](https://docs.cohere.com/docs/reranking)**
- **[Jina Reranker v2](https://jina.ai/news/jina-reranker-v2/)**
- **[MTEB Reranking Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)**（下拉 Reranking 标签）
- **[RankGPT paper (Sun et al., 2023)](https://arxiv.org/abs/2304.09542)**
- [Rerank 概念页](../retrieval/rerank.md) · [RAG](../ai-workloads/rag.md)

## 相关

- [Rerank](../retrieval/rerank.md) · [Hybrid Search](../retrieval/hybrid-search.md)
- [Embedding 模型横比](embedding-models.md)
- [RAG on Lake](../scenarios/rag-on-lake.md)
