---
title: Embedding
type: concept
tags: [retrieval, vector, embedding]
aliases: [向量嵌入]
related: [vector-database, multimodal-embedding, rag]
systems: [bge, e5, jina, openai, cohere, voyage]
applies_to: 2024-2026 模型矩阵（bge-m3 · gte-Qwen2 · jina-v3 · voyage-3 · text-embedding-3）
last_reviewed: 2026-04-18
status: stable
---

# Embedding（向量嵌入）

!!! tip "一句话理解"
    把一段语义内容（文本、图像、音频、用户行为）**压缩成一个固定维度的稠密浮点向量**，让"语义相似 ⇔ 向量距离近"成立。Embedding 是所有 AI 检索 / 聚类 / 推荐的通用货币。

## 它是什么

一个 embedding 模型 $f: \text{input} \to \mathbb{R}^d$ 把任意输入映射为 $d$ 维向量（常见 $d$ = 384 / 768 / 1024 / 1536）。好的 embedding 满足：

- 相似内容的向量**余弦距离 / 欧式距离小**
- 向量空间"语义连续"（近邻有意义）

## 产生方式

现代 embedding 基本靠**对比学习 / 监督学习**训练的大模型：

- **文本**：BGE、E5、Jina、GTE、OpenAI `text-embedding-3-*`、Cohere embed
- **图像**：CLIP、SigLIP、EVA-CLIP
- **音频**：Wav2Vec、CLAP
- **代码**：CodeBERT、Jina code embeddings
- **多模**：CLIP / BLIP / Unified models（见 [多模 Embedding](multimodal-embedding.md)）

## 几个关键工程问题

### 1. 维度怎么选

- 越高越能表达，越慢、越占内存
- 常见折中：文本 **768 或 1024**；图像 **512 或 768**
- "Matryoshka Embeddings"：一个模型多维度兼容，上线时可按场景裁剪

### 2. 归一化

余弦相似度 = 归一化后的内积。
**建议所有 embedding 存库前就做 L2 归一化**，查询时只做内积即可，所有 ANN 索引（HNSW、IVF）都更友好。

### 3. 模型迁移

Embedding 模型一旦换了，**库侧所有历史向量都要重新算**，且查询侧必须同源。这是最大的运维成本来源。因此：

- 模型上线前要做离线评估
- 切换时必须准备增量再 embedding 流水线（见 embedding-pipelines，待补）
- 库里最好记 `embedding_model_version` 字段

### 4. 存储在哪儿

- **向量库**（Milvus / LanceDB / Qdrant）—— 在线检索
- **湖表**（Iceberg + Lance / Iceberg + Puffin）—— 批次场景，和元数据共存
- 两条路并非互斥，一体化架构倾向于**湖上就地存**，避免双写

## 相关概念

- [多模 Embedding](multimodal-embedding.md) —— 跨模态空间
- [向量数据库](vector-database.md) —— 承载 embedding 的存储
- [RAG](../ai-workloads/rag.md) —— embedding 的典型下游

## 延伸阅读

**榜单与评估**

- **[MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)** —— 文本 embedding 通用 benchmark
- **[C-MTEB](https://huggingface.co/spaces/mteb/leaderboard)**（中文子榜）
- **[MTEB 论文](https://arxiv.org/abs/2210.07316)** (Muennighoff et al., 2023)

**核心方法论文**

- **[*Matryoshka Representation Learning*](https://arxiv.org/abs/2205.13147)** (Kusupati et al., NeurIPS 2022) —— 一模型多维度
- **[*Text and Code Embeddings by Contrastive Pre-Training*](https://arxiv.org/abs/2201.10005)** (OpenAI, Neelakantan et al., 2022)
- **[*BGE-M3*](https://arxiv.org/abs/2402.03216)** (BAAI, 2024) —— 多语言 / 多粒度 / 多功能
- **[*E5 · Text Embeddings by Weakly-Supervised Contrastive Pre-training*](https://arxiv.org/abs/2212.03533)** (Microsoft, 2022)

**模型仓库**

- **[BGE / FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding)** (BAAI) · **[jina-embeddings-v3](https://huggingface.co/jinaai/jina-embeddings-v3)**
- **[Voyage AI 模型文档](https://docs.voyageai.com/)** · **[OpenAI text-embedding-3 指南](https://platform.openai.com/docs/guides/embeddings)**
