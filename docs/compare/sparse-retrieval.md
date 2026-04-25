---
title: 稀疏检索对比 · BM25 / SPLADE / ColBERT / Elser
applies_to: "2024-2026 主流"
type: comparison
level: A
depth: 资深
tags: [comparison, retrieval, sparse, bm25, splade, colbert]
related: [hybrid-search, rerank, vector-database]
status: stable
last_reviewed: 2026-04-22
---

# 稀疏检索对比 · BM25 / SPLADE / ColBERT / Elser

!!! tip "一句话回答"
    **BM25** 仍是 30 年后的基线王者（零训练、毫秒级、可解释）。**SPLADE** 是"学习型稀疏"的代表，在 BEIR 上稳定优于 BM25 约 3-5 点。**ColBERT v2** 是 late interaction 的代表，精度接近 cross-encoder rerank 但存储爆炸。**Elser** 是 Elastic 的 SPLADE 变体。**工业实务**：Hybrid Search 的稀疏侧**多数情况还是 BM25 起步**，SPLADE 是效果进阶选择。

!!! abstract "TL;DR"
    - **BM25**：经典、零训练、倒排索引、毫秒级 · 工业用最广
    - **SPLADE v3**：BERT 学习型稀疏 · +3-5 点 NDCG@10 vs BM25
    - **ColBERT v2**：token 级 late interaction · 精度高但存储 10-20×
    - **Elser**（Elasticsearch Sparse Encoder）：Elastic 产品化，类 SPLADE
    - **混合用法**：BM25 or SPLADE 稀疏侧 + Dense 稠密侧 + Rerank

## 1. 为什么还要稀疏检索

### 纯向量检索不够

向量检索擅长**语义**但：
- **专有名词**（产品名、人名、错误码）命中差
- **低频词**（长尾）向量质量波动
- **可解释性弱**（不知道为什么相关）

稀疏检索互补：**字面匹配强 + 可解释 + 无训练 + 倒排索引极快**。

### 工业共识（2024-2025）

- **纯 BM25**：仍然是 2024 新系统的起步选项
- **Hybrid（Dense + Sparse）**：在多数公开 benchmark 和工业案例中显著优于单路，已在主流 RAG / 搜索栈广泛采用
- **稀疏侧选 BM25 还是 SPLADE** 看成本和精度诉求

## 2. 四家对比

### BM25（1994）

**机制**：
- 基于 TF-IDF 改进
- 词频 + 文档长度归一化
- 经典公式：

$$
\text{score}(D, Q) = \sum_{i=1}^n \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{\text{avgdl}})}
$$

**参数**：
- `k1` ≈ 1.2-2.0：词频饱和度
- `b` ≈ 0.75：长度归一化强度

**优**：
- 零训练
- 毫秒级（倒排）
- 可解释
- 30 年稳定
- Lucene / Elasticsearch / OpenSearch / Solr 等主流全文搜索都内置 BM25

**劣**：
- 不理解同义词
- 对复杂语义失效
- 对拼写 / 变形敏感

**BM25 平均 BEIR NDCG@10 ≈ 0.43**。

### SPLADE v3（2024）

**机制**：
- **BERT 编码**后**稀疏化**（ReLU + log + max pooling）
- 词表是 BERT vocab（30k 词）
- **学习型稀疏向量**：自动扩展同义词 / 上下文相关权重

```
"查询：HNSW 的 M 参数调优"
  ↓ SPLADE encoder
{"hnsw": 0.85, "m": 0.60, "parameter": 0.70, "tuning": 0.55,
 "graph": 0.30, "algorithm": 0.20, "index": 0.15, ...}
```

**优**：
- 比 BM25 效果好 3-5 点
- 仍是稀疏（倒排可索引）
- 一定的可解释性（看激活词）
- 自动扩展同义词

**劣**：
- 推理成本不低（BERT encoder）
- **存储 2-3× BM25**（每 doc 稀疏向量更大）
- 训练 / 微调需要资源

**SPLADE v3 平均 BEIR NDCG@10 ≈ 0.50**。

### ColBERT v2（2022）

**机制**：
- **每个 token 一个向量**
- 查询时 **late interaction**：
  - query tokens × doc tokens → 每对 max-sim
  - score = Σ per-query-token max-sim

```
Query tokens:     [q_1, q_2, q_3]
Doc tokens:       [d_1, d_2, ..., d_n]
MaxSim(q_i, D) = max_j sim(q_i, d_j)
Score(Q, D) = Σ_i MaxSim(q_i, D)
```

**优**：
- **精度接近 Cross-Encoder Rerank**
- 延迟比 Cross-Encoder 低 10-100×
- Token-level 精细度

**劣**：
- **存储 10-20× dense**（每 doc 每 token 一个向量）
- 索引复杂（需 PLAID 等专门索引）
- 训练代价高

**ColBERT v2 BEIR NDCG@10 ≈ 0.53**（接近 Rerank）。

### Elser（Elasticsearch Sparse Encoder，2023）

**机制**：
- Elastic 自家的 SPLADE 变体
- 基于 BERT-like 模型
- 针对 Elasticsearch 深度优化

**优**：
- 已在 Elasticsearch 8.10+ 产品化
- 和 ES 其他特性（BM25 / knn）无缝 hybrid
- 模型小、部署轻

**劣**：
- 绑定 Elasticsearch / OpenSearch 生态
- 效果比 SPLADE v3 略弱（Elser v2 约 0.47）
- 不开放模型权重（商业版功能）

## 3. 能力矩阵

| 维度 | BM25 | SPLADE v3 | ColBERT v2 | Elser |
|---|---|---|---|---|
| 训练需要 | ❌ | ✅ | ✅ | Elastic 预训练 |
| 索引类型 | 倒排 | 倒排 | 专门 index（PLAID） | 倒排 |
| 查询延迟 | 最快（1-10ms） | 10-30ms | 30-100ms | 10-30ms |
| 存储倍数（vs BM25） | 1× | 2-3× | 10-20× | 2-3× |
| NDCG@10（BEIR 平均） | 0.43 | 0.50 | 0.53 | 0.47 |
| 可解释性 | 强 | 中 | 弱 | 中 |
| 语义扩展 | ❌ | ✅ | ✅ | ✅ |
| 多语言 | 靠 tokenizer | 多语版有 | 英文主 | 多语有 |
| 生产成熟度 | 极高 | 中 | 中偏低 | 高（Elastic 内）|
| 开源 | 是 | 是 | 是 | 部分 |

## 4. 选型决策

| 场景 | 推荐稀疏 |
|---|---|
| **快速起步 + Hybrid 首选** | **BM25** |
| **精度敏感 + 可接受推理成本** | **SPLADE v3** |
| **已经在 Elasticsearch** | **BM25 + Elser** |
| **精度极致 + 存储预算足** | **ColBERT v2** |
| **多语言** | BM25（配好 tokenizer）+ SPLADE multilingual |
| **代码 / 错误码** | BM25（字面匹配最准）|

### 组合经验

```
典型生产栈：
  Dense (BGE-large) + Sparse (BM25) + RRF 融合 + Rerank (bge-reranker)
  → 覆盖 90% 场景

精度进阶：
  Dense (BGE-large) + Sparse (SPLADE v3) + RRF + Rerank
  → 提升 3-5 点

极致精度：
  Dense + Sparse + ColBERT v2 + Rerank
  → 再提升 2-3 点，成本显著上涨
```

## 5. 性能对比（实测数据参考）

### BEIR benchmark（NDCG@10 平均）

```
Pure BM25:          0.43
Pure Dense (BGE):   0.47
BM25 + Dense RRF:   0.53
SPLADE v3:          0.50
SPLADE + Dense RRF: 0.55
+ Rerank (bge-large): 0.60
```

### 延迟（单 query，50 docs corpus）

```
BM25:         1-5 ms
SPLADE:      15-30 ms（含编码）
ColBERT v2:  50-100 ms
```

### 索引存储（1M docs × 平均 500 tokens）

```
BM25:         1-2 GB
SPLADE:       3-5 GB
ColBERT v2:  30-60 GB
```

## 6. 工程落地

### Milvus 2.4+ 混合检索

```python
from pymilvus import AnnSearchRequest, RRFRanker, Collection

# Dense
dense_req = AnnSearchRequest(
    data=[query_dense_vec],
    anns_field="dense",
    param={"ef": 100},
    limit=100,
)

# Sparse（BM25 或 SPLADE）
sparse_req = AnnSearchRequest(
    data=[query_sparse_vec],   # dict[word_id, weight]
    anns_field="sparse",
    param={"drop_ratio_search": 0.2},
    limit=100,
)

results = coll.hybrid_search([dense_req, sparse_req], RRFRanker(k=60), limit=10)
```

### LanceDB

```python
import lancedb
db = lancedb.connect("s3://bucket/lance")
table = db.create_table("docs", schema=...)

# LanceDB 2024+ 内置全文 + 向量 Hybrid
table.create_fts_index("text")   # BM25
table.create_index("embedding")  # Dense

results = (table.search(query_type="hybrid")
                .vector(query_vec)
                .text(query_text)
                .rerank(...)
                .limit(10)
                .to_pandas())
```

### Elasticsearch 8+

```json
POST /docs/_search
{
  "retriever": {
    "rrf": {
      "retrievers": [
        {"standard": {"query": {"match": {"content": "HNSW M parameter"}}}},
        {"standard": {"query": {"text_expansion": {"content": {"model_id": ".elser_model_2", "model_text": "HNSW M parameter"}}}}},
        {"knn": {"field": "embedding", "query_vector": [...], "k": 100}}
      ]
    }
  }
}
```

### SPLADE（自建）

```python
from transformers import AutoModelForMaskedLM, AutoTokenizer

model = AutoModelForMaskedLM.from_pretrained("naver/splade-v3")
tok = AutoTokenizer.from_pretrained("naver/splade-v3")

def splade_encode(text):
    inputs = tok(text, return_tensors="pt")
    outputs = model(**inputs)
    # SPLADE 特定的稀疏化
    sparse = torch.max(
        torch.log(1 + torch.relu(outputs.logits)) * inputs.attention_mask.unsqueeze(-1),
        dim=1
    ).values
    return sparse  # dict[word_id, weight]
```

## 7. 现实检视

### 不要搞反的几件事

- **SPLADE 精度好但不免费**：推理 + 存储成本都增加
- **ColBERT 是高端选项**：10× 存储换几个点精度，多数团队 ROI 不够
- **"用最新的就对"**：很多生产系统用 BM25 + Dense + Rerank 就够好
- **只看 BEIR 平均**：自家数据分布不同，可能 BM25 > SPLADE

### 工业实务

- **Pinterest / Airbnb** 等以 BM25 + Dense 混合为主
- **Google / 微软 Bing** 内部有类 SPLADE / ColBERT 但**不公开数据**
- **中国电商 / 短视频** 推荐系统**常用 BM25** 作为召回之一（因为产品名、关键词是硬命中）

### 新趋势（2024+）

- **bge-m3**：一模型三模态（dense + sparse + ColBERT）——**统一模型正在出现**
- **Matryoshka + Binary Dense**：降成本与 SPLADE 竞争
- **Elasticsearch / OpenSearch** 内置 SPLADE 类技术

## 8. 陷阱

- **字面没命中就排到后面**：BM25 对错字 / 拼写变形敏感，要配 tokenizer + 模糊
- **SPLADE 推理部署不当**：每 query BERT 跑 → 延迟爆；要**并发 / 批处理 / 量化**
- **ColBERT 存储估不足**：以为 2× dense，实际 10-20×
- **没做 hybrid 评估**：直接上 SPLADE 替 BM25，可能整体效果下降
- **中文 BM25 不分词**：必须上 jieba / ik-analyzer / pkuseg

## 9. 延伸阅读

- **[*BM25: Probabilistic Relevance Framework* (Robertson & Zaragoza, 2009)](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)**
- **[SPLADE v3 paper (Lassance et al., 2024)](https://arxiv.org/abs/2403.06789)**
- **[ColBERTv2 (NAACL 2022)](https://arxiv.org/abs/2112.01488)**
- **[Elser docs (Elastic)](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html)**
- **[BEIR benchmark (NeurIPS 2021)](https://arxiv.org/abs/2104.08663)**
- **[Quantization](../retrieval/quantization.md) · [Sparse Retrieval](../retrieval/sparse-retrieval.md)** · **[Hybrid Search](../retrieval/hybrid-search.md)** · **[Rerank](../retrieval/rerank.md)**

## 相关

- [Hybrid Search](../retrieval/hybrid-search.md) · [Rerank](../retrieval/rerank.md)
- [向量数据库](../retrieval/vector-database.md) · [ANN 索引对比](ann-index-comparison.md)
- [Quantization](../retrieval/quantization.md) · [Sparse Retrieval](../retrieval/sparse-retrieval.md)
- [Rerank 模型横比](rerank-models.md)
