---
title: Embedding · 向量嵌入 · 2026 模型矩阵
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-20
applies_to: 2024-2026 embedding 模型矩阵（BGE-M3 · Jina v3 · Voyage 3 · text-embedding-3 · Cohere embed-v4 · gte-Qwen2 · Nomic v1.5）
tags: [retrieval, vector, embedding, matryoshka, model-selection]
aliases: [向量嵌入, 文本嵌入]
related: [vector-database, multimodal-embedding, quantization, rag, embedding-pipelines]
systems: [bge, e5, jina, openai, cohere, voyage, nomic, gte]
status: stable
---

# Embedding · 向量嵌入

!!! tip "一句话理解"
    把一段语义内容（文本、图像、音频、用户行为）**压缩成一个固定维度的稠密浮点向量**，让"语义相似 ⇔ 向量距离近"成立。Embedding 是所有 AI 检索 / 聚类 / 推荐的**通用货币**——**选对模型决定检索质量上限**。

!!! abstract "TL;DR"
    - 一个 embedding 模型 $f: \text{input} \to \mathbb{R}^d$ · 常见 $d$ = 384 / 768 / 1024 / 1536 / 3072
    - **2024-2026 主流模型家族**：BGE-M3（多语言多粒度）/ Jina v3（多任务）/ Voyage 3（闭源高质量）/ text-embedding-3（OpenAI · Matryoshka）/ Cohere embed-v4（int8/binary 原生）/ Nomic v1.5（开源 Matryoshka）/ gte-Qwen2（中文强）
    - **Matryoshka** · 2024 起主流新模型都支持 · 训练时多维 · 事后截维（详见 [Quantization](quantization.md)）
    - **选型三维**：**任务类型**（检索 / 分类 / 聚类）× **语言覆盖**（英 / 中 / 多语）× **成本/部署**（闭源 API / 开源自部署）
    - **模型切换 = 全量重算** · 版本管理 + 灰度切换必须提前设计

## 1. 它是什么

一个 embedding 模型 $f: \text{input} \to \mathbb{R}^d$ 把任意输入映射为 $d$ 维向量。**好的 embedding 满足**：

- 相似内容的向量 **余弦距离 / 欧式距离小**
- 向量空间"语义连续"（近邻有意义）
- 正交性——**不相关的内容**距离大

### 产生方式

现代 embedding 基本靠**对比学习 / 监督学习**训练的 Transformer 大模型：

| 模态 | 主要模型家族 |
|---|---|
| **文本** | BGE · E5 · Jina · GTE · OpenAI text-embedding-3 · Cohere embed · Voyage · Nomic · SFR |
| **图像** | CLIP · SigLIP · EVA-CLIP |
| **音频** | Wav2Vec · CLAP |
| **代码** | CodeBERT · Jina code · Voyage code |
| **多模** | CLIP / BLIP / Unified models（见 [多模 Embedding](multimodal-embedding.md)）|

## 2. 2026 文本 Embedding 模型矩阵

**模型快变 · 此表为 2026-Q2 快照 · 选型时查 [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) 最新**：

| 模型 | 开源 / API | 维度 | Matryoshka | 多语言 | 典型延迟 | 特色 |
|---|---|---|---|---|---|---|
| **BGE-M3** (BAAI 2024) | 开源 | 1024 | ✅ | ✅（100+ 语）| 中 | 多语言 + 多粒度（稠密+稀疏+ColBERT 一模型）|
| **Jina v3** (2024) | 开源 + API | 1024 | ✅ | ✅ | 中 | 多任务（检索 / 分类 / 聚类）一模型 |
| **Voyage 3 / Voyage 3 Large** | 闭源 API | 1024 / 2048 | ✅ | ✅ | API 延迟 | **闭源里 MTEB 常 top** · 领域特化（金融/法律）版本 |
| **OpenAI text-embedding-3-large** | 闭源 API | 3072（可截到 256/512/1024）| ✅ | ✅ | API 延迟 | Matryoshka 原生 · 稳定 |
| **Cohere embed-v4** (2024+) | 闭源 API | 1536 | ✅ | ✅ | API 延迟 | **原生支持 int8 和 binary 变体** |
| **Nomic Embed v1.5** (2024) | 开源 | 768（Matryoshka 到 64）| ✅ | 英为主 | 快 | 开源 Matryoshka 代表 |
| **gte-Qwen2 系列** (Alibaba 2024) | 开源 | 1024/1536 | 部分 | **中文强** | 中 | 中文场景 top 开源之一 |
| **SFR-Embedding-2** (Salesforce 2024) | 开源 | 4096 | ⚠️ | 英为主 | 慢（大模型）| MTEB 前列 · 但推理重 |

### 开源 vs 闭源 API 的取舍

| 维度 | 开源自部署 | 闭源 API |
|---|---|---|
| **质量** | Top 开源（BGE-M3 / Jina v3 / gte-Qwen2）+- Voyage / OpenAI 中等 | Voyage 3 Large / OpenAI-3-large 仍是**MTEB 事实 top** |
| **成本** | GPU 自担 + 运维 · 大规模便宜 | 按 token 付费 · 小规模便宜 · 亿级贵 |
| **数据隐私** | 数据不出境 · 合规友好 | 数据发 API（部分 API 承诺不训练）|
| **延迟** | 本地部署 · 可控 | 网络 + API 延迟 ~50-200ms |
| **更新** | 换版本要重新部署 + 全量重算 | 厂商透明升级（但**接口承诺稳定**不保证向量空间不变）|

## 3. 选型决策 · 3 步

### Step 1 · 任务类型

Embedding 模型在不同任务上表现**差别巨大**——MTEB 把任务分成 8 类：

- **Retrieval** · RAG / 搜索最常用 · **首要指标** · 查 MTEB Retrieval 分
- **Classification / Clustering** · 分类 / 聚类场景 · 不同模型排名很可能反着的
- **Semantic Similarity (STS)** · 语义对齐 · 推荐 / Dedup 场景
- **Reranking** · 作为 rerank 模型输入 · 看 CrossEncoder

**不要只看 "MTEB 综合分"** · 要看**你具体任务的子榜**。

### Step 2 · 语言覆盖

- **英文 only** · BGE-en / E5-en / OpenAI / 所有闭源 都好
- **中文 only** · **gte-Qwen2** / **BGE-M3**（多语里中文强）/ **Conan-Embedding**（阿里）
- **多语言** · BGE-M3 / Jina v3 / Cohere v4 · 任选

### Step 3 · 成本 / 部署

- **规模 < 百万 doc** · 闭源 API 简单 · 不值得自建
- **规模 > 千万 doc 或日均查询 > 百万** · 开源自部署更经济
- **合规 + 数据敏感** · 必须开源自部署
- **多维度灵活（Matryoshka）** · 2024+ 多数新模型都支持 · 可以一模型多精度部署

## 4. 几个关键工程问题

### 4.1 维度怎么选

- **越高越能表达** · 越慢、越占内存
- 常见折中：文本 **768 或 1024**；图像 **512 或 768**
- **Matryoshka 改变了这个取舍**——**一个模型多维度兼容** · 上线时按场景裁剪（冷路径用 1024 · 热路径用 256 · 详见 [Quantization](quantization.md)）

### 4.2 归一化

余弦相似度 = 归一化后的内积。

**建议所有 embedding 存库前就做 L2 归一化**——查询时只做内积即可 · 所有 ANN 索引（HNSW · IVF · DiskANN）都更友好。

```python
import numpy as np
vec = model.encode(text)
vec_normalized = vec / np.linalg.norm(vec)  # L2 归一化
```

!!! note "Matryoshka 截维后要重新归一化"
    Matryoshka 模型产出的 $d$ 维向量是归一化的 · 但**截取前 $k$ 维后向量不再是单位向量**——**必须重新 L2 归一化**才能用 cosine 距离。

### 4.3 模型迁移 · 最贵的运维

Embedding 模型一旦换了 · **库侧所有历史向量都要重新算** · 且查询侧必须**同源**。

**切换策略**（按风险从低到高）：

**策略 A · 灰度双写双查**：

```
新模型上线 → 双向量列(embedding_v1 + embedding_v2) 同时存
  ↓
查询侧流量灰度 · 1% → 10% → 100% 切到 v2
  ↓
v1 字段保留 1-3 个月做 fallback
  ↓
确认稳定后删 v1 列 · 节省存储
```

**策略 B · 离线重算 + 一键切换**（快但激进）：
- 离线 pipeline 全量重算 embedding_v2 写临时表
- 维护窗口切换 Catalog 指针
- 风险：切换后发现质量问题没有 fallback

**策略 C · 多版本共存 · Catalog 管理**：
- 库里记 `embedding_model_version` 字段
- 查询时显式指定版本
- 新旧 query 可路由到不同模型
- 成本：存储和索引 2 倍

**生产推荐 A**——灰度双写双查。

### 4.4 存储在哪儿

| 方案 | 适合 |
|---|---|
| **向量库**（Milvus / LanceDB / Qdrant） | 在线检索 · 低延迟 · 千万-亿级 |
| **湖表**（Iceberg + Puffin / Iceberg + Lance） | 批次 ML 场景 · 和元数据共存 · 见 [lakehouse/多模湖仓](../lakehouse/multi-modal-lake.md) |
| **双写** | 两个系统各取所长 · 成本翻倍但灵活 |

**一体化架构倾向"湖上就地存"**——用 Puffin（Iceberg 侧车）或 Lance 原生存储 · 避免双写。见 [Lake + Vector 融合架构](../unified/lake-plus-vector.md)。

### 4.5 和 Rerank 的协同

Embedding 的质量和 **rerank 模型的输入质量** 相关：

- Embedding 召回 Top-100 · rerank 选 Top-10
- 如果 embedding 召回质量差（Top-100 里真相关只有 30 个）· **rerank 再强也救不回来**
- 换言之 · **召回质量决定天花板 · rerank 提天花板的接近度**

详见 [Rerank](rerank.md)。

## 5. 陷阱

- **没归一化就做 cosine** · 结果和预期不符
- **Matryoshka 截维后忘归一化** · 距离失真
- **只看 MTEB 综合分** · 不看具体任务子榜 · 选型误判
- **换模型没做灰度** · 一次切换出事故没 fallback
- **忘记更新查询侧 embedding 模型** · query 用旧模型 doc 用新模型 · 两套向量空间对不齐
- **数据库 schema 没带 embedding_version 字段** · 模型版本追溯困难
- **认为闭源 API 向量空间稳定** · OpenAI / Cohere 升级模型版本时向量空间不保证兼容

## 相关

- [多模 Embedding](multimodal-embedding.md) · 跨模态空间
- [Quantization](quantization.md) · Matryoshka + PQ/SQ/BQ 压缩
- [向量数据库](vector-database.md) · 承载 embedding 的存储
- [Rerank](rerank.md) · 召回后的二阶段
- [Embedding Pipelines](../ml-infra/embedding-pipelines.md) · 生成 embedding 的管线
- [RAG](../ai-workloads/rag.md) · embedding 的典型下游
- [Embedding 模型横比](../compare/embedding-models.md) · 详细对比页

## 延伸阅读

**榜单与评估**

- **[MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)** · 文本 embedding 通用 benchmark
- **[C-MTEB](https://huggingface.co/spaces/mteb/leaderboard)** · 中文子榜
- **[MTEB 论文](https://arxiv.org/abs/2210.07316)** (Muennighoff et al., 2023)

**核心方法论文**

- **[*Matryoshka Representation Learning*](https://arxiv.org/abs/2205.13147)** (Kusupati et al., NeurIPS 2022)
- **[*BGE-M3*](https://arxiv.org/abs/2402.03216)** (BAAI, 2024) · 多语言 / 多粒度 / 多功能
- **[*E5 · Text Embeddings by Weakly-Supervised Contrastive Pre-training*](https://arxiv.org/abs/2212.03533)** (Microsoft, 2022)

**模型仓库**

- **[BGE / FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding)** (BAAI)
- **[jina-embeddings-v3](https://huggingface.co/jinaai/jina-embeddings-v3)**
- **[Voyage AI 模型文档](https://docs.voyageai.com/)**
- **[OpenAI text-embedding-3 指南](https://platform.openai.com/docs/guides/embeddings)**
- **[Nomic Embed v1.5](https://blog.nomic.ai/posts/nomic-embed-text-v1.5-resizable-production-embeddings)**
