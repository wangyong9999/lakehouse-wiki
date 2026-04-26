---
title: 参考资料 · 多模检索 / 向量
type: reference
status: stable
tags: [reference, references, retrieval]
description: ANN 算法 / Embedding / Hybrid / 多模检索 论文与权威博客
last_reviewed: 2026-04-25
---

# 参考资料 · 多模检索 / 向量

## ANN 算法论文

- **[Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs](https://arxiv.org/abs/1603.09320)** _(2016/2018, paper - Malkov & Yashunin)_ —— HNSW 奠基论文，工业最广泛部署的 ANN 算法。**工业验证**。
- **[Product Quantization for Nearest Neighbor Search](https://hal.inria.fr/inria-00514462/document)** _(2011, paper - Jégou et al.)_ —— PQ 量化基础。
- **[DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node](https://www.microsoft.com/en-us/research/publication/diskann-fast-accurate-billion-point-nearest-neighbor-search-on-a-single-node/)** _(2019, paper - Microsoft)_ —— Disk-based ANN，10亿向量单机方案。
- **[FAISS: A Library for Efficient Similarity Search](https://engineering.fb.com/2017/03/29/data-infrastructure/faiss-a-library-for-efficient-similarity-search/)** _(2017, blog)_ —— Meta FAISS 库设计。

## Embedding 与多模

- **[BGE: BAAI General Embedding](https://github.com/FlagOpen/FlagEmbedding)** _(official-doc)_ —— 中文/多语言 SOTA 开源 embedding。
- **[Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147)** _(2022, paper - Kusupati et al.)_ —— 嵌套维度 embedding，可裁剪降维。
- **[CLIP: Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020)** _(2021, paper - OpenAI)_ —— 多模 embedding 奠基。
- **[SigLIP: Sigmoid Loss for Language Image Pre-Training](https://arxiv.org/abs/2303.15343)** _(2023, paper - Google)_ —— 改进 CLIP 的对比学习损失。

## Hybrid Search 与 Sparse

- **[BM25: Probabilistic Relevance Framework](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)** _(2009, paper - Robertson & Zaragoza)_ —— 经典稀疏检索基础。
- **[SPLADE v3: New baselines for SPLADE](https://arxiv.org/abs/2403.06789)** _(2024, paper)_ —— Learned sparse 最新版本。
- **[ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction](https://arxiv.org/abs/2112.01488)** _(2021, paper - Stanford)_ —— Late interaction 方案。
- **[RRF: Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)** _(2009, paper)_ —— Hybrid 融合的经典无参方法。

## 评估与 Benchmark

- **[BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://arxiv.org/abs/2104.08663)** _(2021, paper)_ —— 检索的标准 benchmark。
- **[MTEB: Massive Text Embedding Benchmark](https://github.com/embeddings-benchmark/mteb)** _(official-doc)_ —— Embedding 模型综合 benchmark。
- **[MS MARCO](https://microsoft.github.io/msmarco/)** _(official-doc)_ —— passage / document ranking 标准数据集。

## 工业博客

- **[Pinecone Learning Center](https://www.pinecone.io/learn/)** _(blog)_ —— 向量检索入门到进阶系列。**厂商主张**（Pinecone 视角）但教学质量高。
- **[Anthropic - Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)** _(2024, blog)_ —— Contextual Retrieval 把检索失败率降低 35%（带可复现数据）。
- **[Vespa Blog - Search & Recommendation](https://blog.vespa.ai/)** _(blog)_ —— Vespa 团队的检索深度内容。

## 综述

- **[Dense Text Retrieval based on Pretrained Language Models: A Survey](https://arxiv.org/abs/2211.14876)** _(2022, survey)_ —— Dense retrieval 综述。
- **[Large Language Models for Information Retrieval: A Survey](https://arxiv.org/abs/2308.07107)** _(2023, survey)_ —— LLM 在 IR 中的应用综述。

---

**待补**：2026 ColBERT 后续 / Matryoshka 工业部署案例 / RAG 向量层最新综述
