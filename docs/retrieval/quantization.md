---
title: Quantization · 向量压缩策略
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: Milvus 2.x · Qdrant 1.x · pgvector 0.7+ · Faiss / cuVS 通用
tags: [retrieval, quantization, compression, pq, sq, binary, matryoshka]
aliases: [PQ, SQ, Binary Quantization, Matryoshka]
related: [ivf-pq, hnsw, diskann, embedding, vector-database]
systems: [faiss, milvus, qdrant, pgvector, lancedb]
status: stable
---

# Quantization · 向量压缩策略

!!! tip "一句话定位"
    把 **float32 向量**压缩成**更小表示**（float16 / int8 / 1-bit / 更低维）· 代价是精度损失 · 收益是内存/存储/延迟。**决定了亿级以上能不能装下内存**——是向量检索规模化的核心杠杆。

!!! abstract "TL;DR"
    - 4 大量化家族：**Scalar Quantization (SQ)** · **Product Quantization (PQ)** · **Binary Quantization (BQ)** · **Matryoshka Embeddings**
    - **压缩比 × 精度损失** 双曲线 · 选型按"可接受精度 + 内存预算"反推
    - **Matryoshka** 是 2024-2026 新范式 · 从"事后量化"变成"训练时多维"
    - Binary Quantization + rerank 组合是 2024-2026 极致压缩路线（压缩 32× · Recall 损失可接受）
    - 生产要**后验证**——不同数据集上同一 quantization 的效果可能差很多

## 1. 为什么要 Quantization

原始 embedding 的内存代价：

```
1 亿向量 × 1024 维 × 4 bytes (float32)
  = 10^8 × 1024 × 4 B
  = ~400 GB  纯向量内存
  + 索引结构开销(HNSW 典型 1.5-2×) ≈ 600-800 GB

# 单机放不下 → 要么分片分布式 · 要么压缩
```

Quantization 让**单机亿级成为可能**：

| 方案 | 1 亿 × 1024 维 | 压缩比 |
|---|---|---|
| float32 原始 | 400 GB | 1× |
| float16 | 200 GB | 2× |
| int8 SQ | 100 GB | 4× |
| PQ (M=8, 8-bit) | 800 MB | 500× |
| Binary | 12.5 GB | 32× |
| Matryoshka 截断到 256 维 | 100 GB | 4× |

## 2. 四大量化家族

### Scalar Quantization (SQ) · 最轻量

**原理**：把每个 float32 维度映射到更低精度（fp16 / int8 / int4）。

```
原 vec[i] ∈ [-1.0, 1.0]  float32
SQ-8 · 划分 [-1.0, 1.0] 成 256 段 · 每维存 1 byte
SQ-4 · 划分成 16 段 · 每维 0.5 byte
```

**特点**：

- 实现最简单 · 几乎所有向量库都支持
- 压缩比 2-8×
- **精度损失最小**（典型 Recall@10 下降 < 2%）
- **生产常用 fallback**——PQ 太激进时降回 SQ

### Product Quantization (PQ) · 亚空间量化

**原理**：把 d 维向量拆成 M 个子向量 · 每子向量用 k-means 聚类成 256 个码字（8-bit）。详见 [IVF-PQ](ivf-pq.md)。

```
原 1024 维 float32 · 4 KB
PQ (M=16, 8-bit) · 16 bytes · 压缩 256×
```

**特点**：
- 压缩比高（100-500×）· 是超大规模的**主力方案**
- 精度损失**显著**（典型 Recall@10 下降 5-15%）· **通常配 rerank 或 OPQ/AQ 改进**
- 对数据分布敏感——**自家数据上效果差异大**（见 §5）

**2024-2026 改进**：
- **OPQ (Optimized PQ)** · 先做 PCA 旋转再 PQ · 精度提升 3-5%
- **AQ (Additive Quantization)** · 更复杂的码本训练 · 但成本高
- **FP8 PQ** · 8-bit 浮点码字代替 uint8 · 精度更好

### Binary Quantization (BQ) · 1-bit 极致压缩

**原理**：每个维度只保留**符号位**（正负）· 1 bit 一维。

```
原 1024 维 float32 · 4 KB
BQ · 1024 bits = 128 bytes · 压缩 32×
距离用 Hamming distance 替代 L2/cosine
```

**特点**：
- 压缩比 32× · 内存友好
- **Recall 损失较大**（20-40%）· 但**重排 (rerank) 可补回**
- **关键组合**：**BQ + Flat（Hamming scan）快筛 Top-K → 用原始 float32 rerank**——2024-2026 极致省内存路线
- 对 embedding 模型**有要求**——需要各维度"正负分布"均衡的模型（BGE-M3 · Cohere 4 等已适配）

**2024 商业采用**：
- Cohere embed-v3 / embed-v4 · 官方提供 binary 和 int8 变体
- OpenAI text-embedding-3 · 支持 binary 但质量依赖 dimensions 参数
- BGE / Jina 社区模型 · 多数已支持

### Matryoshka Embeddings · 训练时多维 · 2023+ 新范式

**原理**：训练时用**嵌套维度损失**——让同一个向量的**前 256 维 / 前 512 维 / 前 1024 维** 都是有效 embedding。

```
一个 1024 维 Matryoshka 向量:
  前 64 维   → 粗检索                              可用
  前 256 维  → 平衡检索                            可用
  前 512 维  → 好检索                              可用
  前 1024 维 → 最佳检索                            完整
```

**特点**：
- **事后可切**——不需要重新训练 · 直接截断
- 精度 / 成本**动态权衡**——同一索引支持多种精度查询
- 2024 主流模型已支持：**OpenAI text-embedding-3** (1536/3072 可截到 256/512/1024) · **Nomic Embed Text v1.5** · **BGE-M3** · **Jina v3**

**和其他量化的关系**：Matryoshka 是**维度降低**· 其他是**精度降低**· 正交可叠加——例如用 Matryoshka 截到 256 维 + int8 SQ · 双重压缩。

## 3. 压缩比 × 精度损失 矩阵

| 方案 | 压缩比 | Recall 损失（典型）| 内存 1 亿 × 1024 维 | 适用 |
|---|---|---|---|---|
| **float16** | 2× | 接近 0 | 200 GB | 轻度压缩 · 保持近完美精度 |
| **int8 SQ** | 4× | 1-2% | 100 GB | 通用量化默认 |
| **int4 SQ** | 8× | 3-5% | 50 GB | 内存紧 · 可接受轻微精度损 |
| **PQ (M=16, 8-bit)** | ~256× | 5-10% | ~4 GB | 亿级单机 · 需配合 rerank |
| **PQ (M=8, 8-bit)** | ~512× | 10-20% | ~2 GB | 极致省内存 · 精度损较大 |
| **Binary + rerank** | ~32× 内存 + 少量 rerank cost | 恢复到 < 2% | ~12 GB + rerank 外部 | 2024+ 新范式推荐 |
| **Matryoshka 256** | 4× | 3-8% | 100 GB | 维度压缩 · 可和 SQ 叠加 |
| **Matryoshka 256 + int8** | 16× | 5-10% | 25 GB | 叠加组合 · 平衡选择 |

## 4. 选型决策

**Step 1 · 内存预算估算**：原始大小 × 压缩目标比 → 能装下就初步 OK

**Step 2 · 精度要求**：
- 业务要 Recall@10 > 95% → SQ / float16（轻压缩）
- Recall@10 > 85% 可接受 → PQ 或 BQ + rerank
- Recall@10 > 70% 可接受 → 激进 PQ 或纯 BQ

**Step 3 · 数据分布验证**：
- 有自家数据集样本 · 先在 1% 数据上试不同量化组合 · 实测 Recall@K
- **PQ 对数据敏感** · 官方 benchmark 的效果不代表你的数据

**Step 4 · 架构约束**：
- 向量库是否原生支持（Milvus/Qdrant/LanceDB 支持 SQ/PQ/BQ；pgvector 原生 halfvec/bit 类型支持 float16/Binary）
- 是否需要 rerank 阶段（BQ 几乎必配）

## 5. 生产陷阱

- **训练量化码本用线上数据的子样本** · 不要用公开数据 · PQ/OPQ 码本质量决定精度
- **没做 post-verify** · 量化后 Recall 必须**在自家数据上测**——论文数字不可直接移植
- **量化 + 强过滤组合** · Filter-aware ANN 下量化可能丢更多（见 [Filter-aware ANN](filter-aware-search.md)）
- **Binary Quantization 没配 rerank** · 单用 BQ 质量差 · 必须两阶段
- **Matryoshka 截维时 L2 归一化错** · 截完维度要重新归一化 · 否则 cosine 距离错
- **忽视索引构建时量化的开销** · PQ/OPQ 需要训练码本 · 百万级数据十分钟以上 · 提前规划

## 相关

- [IVF-PQ](ivf-pq.md) · PQ 的主要应用场景
- [HNSW](hnsw.md) · 图索引 + 量化组合
- [DiskANN](diskann.md) · 盘上索引天然依赖量化
- [Embedding](embedding.md) · 哪些模型原生支持量化变体
- [Rerank](rerank.md) · 量化后的质量补偿

## 延伸阅读

- **[Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147)** · 原始论文
- **[Facebook AI · Billion-scale similarity search with GPUs](https://arxiv.org/abs/1702.08734)** · Faiss 基础
- **[Cohere · Binary Embeddings](https://cohere.com/blog/int8-binary-embeddings)** · Binary 量化实战
- **[Nomic Embed · 技术报告](https://blog.nomic.ai/posts/nomic-embed-text-v1)** · Matryoshka 商业化
