---
title: Sparse Retrieval · BM25 / SPLADE / BM42
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: Lucene / Elasticsearch / OpenSearch · Qdrant · Milvus · Weaviate · Vespa
tags: [retrieval, sparse, bm25, splade, bm42, inverted-index]
aliases: [稀疏检索, Lexical Search, Keyword Search]
related: [hybrid-search, rerank, embedding, evaluation]
systems: [elasticsearch, opensearch, vespa, qdrant, milvus]
status: stable
---

# Sparse Retrieval · 稀疏向量检索

!!! tip "一句话定位"
    **稀疏检索 = 词袋模型 + 倒排索引**——向量检索（稠密）的另一条主路径。2023-2026 关键进展是**神经网络稀疏**（SPLADE · BM42）——把 BM25 的"词出现次数"升级为"学习过的权重"——在很多场景**召回和可解释性**都优于纯稠密。

!!! info "和其他页的边界"
    - 本页 · **稀疏算法本身**（BM25 · SPLADE · BM42 · 原理 + 产品）
    - [Hybrid Search](hybrid-search.md) · **稀疏 + 稠密的融合策略**（RRF · Reciprocal Rank Fusion · Convex Combination）
    - [Rerank](rerank.md) · 两阶段的**二阶段**
    - [Embedding](embedding.md) · **稠密向量**的主路径

!!! abstract "TL;DR"
    - **BM25** · 经典 · 20 年沉淀 · 工业级默认 · 精度天花板存在
    - **SPLADE** (2021+) · Learned Sparse Retrieval · 用 MLM 生成稀疏向量 · BEIR 上超 BM25
    - **BM42** (2024) · Qdrant 提出 · 轻量级神经稀疏 · 训练代价低 · 2024-2026 实战渐起
    - **神经稀疏关键点**：不是抛弃倒排索引 · 是**让倒排索引的权重更聪明**
    - **Hybrid 主路径**：BM25 (快 · 可解释) + Dense (语义) 通过 RRF 融合——**是 2024-2026 生产 RAG 里最常见的 1-2 种路径之一**（另一常见路径是 SPLADE + Dense）

## 1. 为什么稀疏检索仍然重要

稠密 embedding 主导了 2018-2023 的检索故事 · 但 **纯稠密有三个硬伤**：

1. **OOV（Out-of-Vocabulary）/ 新词 / 专有名词** 召回差——embedding 模型训练数据没见过 · 向量空间里没好位置
2. **精确匹配** 不如稀疏——搜 "MCP-2024-042" 这类编号 · BM25 能精确命中 · Dense 不保证
3. **可解释性** 弱——为什么返回这条？Dense 说不清 · BM25 能列出"哪些词贡献了多少"

所以**稀疏不会被稠密取代**——**融合（Hybrid）是生产主路径**。

## 2. BM25 · 经典之王

**原理**：给 (query, doc) 打分 · 基于词频 (TF) + 文档频率 (IDF) + 长度归一化：

```
score(q, d) = Σ_{t ∈ q} IDF(t) × (TF(t, d) × (k1+1)) / (TF(t, d) + k1 × (1 - b + b × |d|/avgdl))

  k1 ~= 1.2-2.0  控制 TF 饱和度
  b ~= 0.75      控制长度归一化
```

**工程特性**：

- **20 年沉淀** · Lucene / Elasticsearch / OpenSearch / Solr 都用 BM25 为默认
- **倒排索引** 超高效 · 百万文档 query 亚毫秒
- **中文** 需要分词器（jieba · IK · etc）
- 无需训练

**天花板**：
- 精确词匹配驱动 · **语义理解弱**（"汽车"和"小轿车"的关系学不到）
- 长尾 query 效果差（少词 query · IDF 过大 · 易 overfit）

## 3. SPLADE · Learned Sparse（2021+）

**SPLADE (SParse Lexical AnD Expansion)** 的核心想法：

**从 "词是否出现 + 次数" → "BERT 模型预测每个词的权重"**

```python
# SPLADE 原理（简化）
for each token t in vocabulary:
    logit_t = BERT(query)[t]    # BERT MLM 输出
    weight_t = log(1 + relu(logit_t))  # 稀疏化

# 结果: 每个 query / doc 都是一个稀疏向量
# query_sparse = {"term1": 0.5, "term2": 0.3, "synonym": 0.1, ...}
```

**差异化 vs BM25**：
- **同义词扩展**——模型见过 "汽车 ~ 小轿车" 的语义 · BM25 看不到
- **Query / Doc 两侧都学** · 双向权重优化
- **倒排索引兼容** · 仍用传统倒排查询 · 不是暴力计算

**性能**：
- BEIR benchmark 上 · SPLADE-v2 / SPLADE++ 通常超 BM25 10-20% · 接近 Dense
- 推理延迟：比 BM25 慢一个量级（需要过 BERT）· 比 Dense 相当
- **索引成本**：比 BM25 大 5-10×（每 doc 扩展的词更多）

**产品支持**：
- **Qdrant 2024** · 原生 SPLADE 集成
- **Elastic 8.x** · ELSER 是 Elasticsearch 的类似实现
- **Weaviate** · 支持外部 SPLADE 向量输入

## 4. BM42 · Qdrant 2024 新方案

**背景**：SPLADE 训练复杂 · 推理慢 · 索引膨胀——Qdrant 2024 提出 BM42 作为**轻量神经稀疏**。

**核心想法**：
- 用 Transformer 的 **attention score** 而不是 MLM 输出
- 只做 **query expansion**（查询时扩展词）· 不改索引侧
- 索引侧仍然标准 BM25 / tf-idf

**优势**：
- 训练成本**低**（attention 是预训练模型副产品）
- 推理延迟**接近 BM25**
- 索引可重用 BM25 栈

**劣势**：
- 精度提升**小于 SPLADE**（简化换来速度）
- 社区验证仍在积累

**适合**：已有 BM25 基础设施 · 想低成本升级的团队。

## 5. 选型 · BM25 vs SPLADE vs BM42

| 维度 | BM25 | SPLADE | BM42 |
|---|---|---|---|
| **时间** | 2009+ 经典 | 2021+ | 2024+ |
| **训练要求** | 无 | 需 MLM 训练 | 轻量 · 用预训练 attention |
| **索引成本** | 基础 | 5-10× 基础 | 接近基础 |
| **查询延迟** | 毫秒级 | 10-100× BM25 | 接近 BM25 |
| **BEIR 精度（NDCG@10）**| baseline | +10-20% | +5-10%（估计）|
| **可解释性** | 高 | 中（权重可看）| 高 |
| **产品成熟度** | 所有搜索引擎 | Elasticsearch · Qdrant | Qdrant · 早期 |
| **适合** | 仍是**生产默认** | **有训练资源 + 质量要求高** | **从 BM25 轻量升级** |

**和 Dense 的关系**：

- **单独用稀疏**：规模小 + 词精确匹配多 + 资源紧
- **单独用稠密**：语义重 + 数据量大 + 模型质量高
- **Hybrid** ([详见](hybrid-search.md))：2024-2026 **大多数生产选这个**——稀疏（BM25 或 SPLADE）+ 稠密 两路召回 · RRF 融合

## 6. 工程要点

### 倒排索引的规模

- **10 亿 doc × 英文** · BM25 索引大小 ~数百 GB（文本本体 + 倒排 posting lists）
- **SPLADE** 因扩展词多 · 索引大 5-10× · 需要确认磁盘预算
- **Lucene / Elasticsearch** 是**最主流的倒排索引引擎**（生态最广 · 非唯一）· 规模大的用 OpenSearch 多分片

### 分词器选型（中文尤其关键）

- **中文**：IK / jieba / hanlp · 影响 BM25 召回巨大
- **英文**：Lucene 默认 standard analyzer 够用 · 专业领域加 stemmer
- **多语言**：ICU / language-aware 策略

### 索引更新

- 倒排索引的**增量更新** · Lucene segment merge 机制 · 实时写不如 Dense 方便
- Elasticsearch `refresh_interval` 权衡新鲜度 vs 性能

## 7. 陷阱

- **把 SPLADE 当 Dense 用** · SPLADE 仍走倒排索引 · 别用向量库存（除非显式稀疏向量支持）
- **忽视分词器对 BM25 的影响** · 中文尤其 · 分词错 BM25 召回崩
- **认为 Dense 取代了 BM25** · 2024-2026 生产栈大多 Hybrid 是主路径
- **SPLADE 索引不控制容量** · 扩展词 top-K 要 cap · 否则倒排膨胀失控
- **BM42 无差别替换 BM25** · 要根据自家数据实测 · 精度提升不一定显著

## 相关

- [Hybrid Search](hybrid-search.md) · **稀疏 + 稠密融合 · 生产主路径**
- [Rerank](rerank.md) · 稀疏召回后的二阶段
- [Embedding](embedding.md) · 稠密的对照路径
- [检索评估](evaluation.md) · BEIR · MTEB benchmark

## 延伸阅读

- **[BM25 原始论文 · Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25)**
- **[SPLADE](https://arxiv.org/abs/2107.05720)** · 2021 论文
- **[SPLADE v2++](https://arxiv.org/abs/2205.04733)** · 改进版
- **[Qdrant BM42 博客](https://qdrant.tech/articles/bm42/)**
- **[Elastic ELSER](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html)**
