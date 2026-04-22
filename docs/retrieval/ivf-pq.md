---
title: IVF-PQ · 倒排 + 量化的 ANN 索引
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-18
applies_to: FAISS 1.8+, Milvus 2.4+, LanceDB 0.8+
tags: [retrieval, vector, ann, index, quantization]
aliases: [Inverted File + Product Quantization]
related: [hnsw, diskann, vector-database]
systems: [milvus, lancedb, faiss, scann]
status: stable
---

# IVF-PQ · 倒排 + 量化

!!! tip "一句话理解"
    **先聚类分桶，再把每个向量压缩成几个字节**。**IVF** 解决"查询不必扫全量"，**PQ** 解决"海量向量装不下内存"。在**亿级规模 + 内存预算紧张**时是 HNSW 最主要的替代方案。

!!! abstract "TL;DR"
    - **IVF**：k-means 聚类分桶 → 查询只扫最近 nprobe 个桶
    - **PQ**：向量切 M 段独立量化 → 每段 1 字节 → 典型 **16-64× 压缩**
    - **规模甜点**：10M - 10B 向量 + 内存有限
    - **精度**：Recall 调到 95-99% 可做到，**不如 HNSW** 的 99%+ 稳
    - **增量写弱**：批建最佳、增量要 retrain
    - **Faiss** 是参考实现，**Milvus / LanceDB / ScaNN** 都内建

## 1. 业务痛点 · HNSW 为什么不够

HNSW 在 < 100M 规模友好，但：

| 规模 | HNSW 内存 | 问题 |
|---|---|---|
| 1M × 768d | 3 GB | 轻松 |
| 100M × 768d | 300 GB | 单机 or 分布式 |
| 1B × 768d | 3 TB | 成本爆 → 必须量化或磁盘化 |

**IVF-PQ 的价值**：用精度略降换**10-30× 内存**，让亿级向量在单机或小集群可行。

## 2. 原理深度

### IVF（Inverted File）· 倒排分桶

```
1. 对全量向量跑 k-means，聚成 nlist 个中心 (centroids)
2. 每个向量分到最近中心的"桶"
3. 查询时：
   - 先算查询向量到所有 centroid 的距离
   - 选最近的 nprobe 个桶
   - 只在这些桶内搜索
```

```mermaid
flowchart LR
  q[Query Vector] --> centroids[nlist 个中心]
  centroids -->|选 top nprobe| buckets[几个桶]
  buckets --> exact[在桶内精确搜索]
  exact --> topK[返回 TopK]
```

**参数意义**：
- `nlist` 越大 → 每桶越小、查询越快、召回率略降
- `nprobe` 越大 → 扫更多桶、召回高、延迟增

**经验**：`nlist = √N` 到 `4√N`，`nprobe = 1-128` 视 recall 目标。

### PQ（Product Quantization）· 乘积量化

向量 $\vec{v} \in \mathbb{R}^D$ 切成 $M$ 段，每段维度 $D/M$：

```
原向量 (D=128 维):
 [v_0, v_1, ..., v_127]
          ↓ 切 M=16 段，每段 8 维
 [v_0..v_7] [v_8..v_15] ... [v_120..v_127]
          ↓ 每段独立 k-means，256 子中心
 [c_0, c_1, ..., c_15]    ← 每个 c_i ∈ [0, 255]
```

每段只需 1 字节存储 → **128 维 float32（512 bytes）→ 16 字节**（32× 压缩）。

### 查询时距离计算（ADC · Asymmetric Distance Computation）

```
Query vector:  [q_0, q_1, ..., q_127]
切成 M=16 段:  [q_0..q_7] [q_8..q_15] ... [q_120..q_127]

对每段预计算查询向量到 256 个子中心的距离 → 表（M × 256）

查询 doc vector (压缩成 M 个字节):
  [c_0, c_1, ..., c_15]

距离(q, doc) = Σ 表[i][c_i]   ← 只查表不再乘加
```

**核心**：距离计算变成**查表累加**，extremely fast。

### 精度损失来源

- 量化丢失**组内精细度**
- PQ 子中心 256 个 → 有固有量化误差
- **ADC 距离是近似**（不等于原始向量的距离）

## 3. IVF-PQ 组合 vs 其他方案

| 指标 | Flat | HNSW | IVF-PQ | DiskANN |
|---|---|---|---|---|
| 内存占用 | 100% | 100% + 图 | **10-30%**（PQ 后）| 10-15% + SSD |
| Recall（典型） | 100% | 99%+ | 95-99% | 95-99% |
| 查询延迟 | 慢 | 最快 | 快 | 慢一些 |
| 构建时间 | 0 | 慢 | 中 | 中 |
| 增量写 | 任意 | 友好 | **不友好** | 批建 |
| 十亿规模 | 不可行 | 需分布式 | **可单机** | **可单机 + SSD** |

## 4. 关键参数调优

| 参数 | 含义 | 典型值 |
|---|---|---|
| `nlist` | IVF 桶数 | $\sqrt{N}$ – $4\sqrt{N}$ |
| `nprobe` | 查询扫几个桶 | 1 – 128 |
| `M`（PQ 段数） | 压缩粒度 | 向量维度 / 4 |
| `nbits` | 每段 bit 数 | 8（256 子中心）标准 |

### 规模 vs nlist 经验

| N（向量数）| nlist |
|---|---|
| 1M | 1,024 - 4,096 |
| 10M | 4,096 - 16,384 |
| 100M | 32,768 - 131,072 |
| 1B | 65,536 - 262,144 |

### Recall vs nprobe 曲线（典型）

```
nprobe=1:   recall ~50%
nprobe=4:   recall ~80%
nprobe=16:  recall ~95%
nprobe=64:  recall ~98%
nprobe=256: recall ~99%
```

选 recall 目标 → 对应 nprobe → 延迟估计。

## 5. 性能数字

### FAISS IVF-PQ（CPU）

| 规模 | 内存 | 构建时间 | 查询 p99 (nprobe=16) |
|---|---|---|---|
| 1M × 128d (SIFT) | 16 MB | 30s | 0.5 ms |
| 100M × 128d | 1.6 GB | 30 分钟 | 5 ms |
| 1B × 128d (BIGANN) | 16 GB | 数小时 | 20 ms |

### Milvus IVF-PQ（典型生产）

- 10 亿向量 + nlist=32768, M=32 + 16-bit PQ
- 单节点 128GB 内存放得下
- p99 < 50ms

## 6. 代码示例

### FAISS

```python
import faiss
import numpy as np

d = 128
nlist = 4096
m = 16       # PQ 段数
nbits = 8

# 构建
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFPQ(quantizer, d, nlist, m, nbits)
index.train(train_vectors)   # 必须先 train
index.add(all_vectors)

# 查询
index.nprobe = 16
D, I = index.search(query_vectors, k=10)
```

### Milvus

```python
from pymilvus import Collection

col.create_index(
  field_name="vec",
  index_params={
    "index_type": "IVF_PQ",
    "metric_type": "IP",
    "params": {
      "nlist": 16384,
      "m": 32,
      "nbits": 8
    }
  }
)

# 查询
col.search(
  data=[query_vec], anns_field="vec",
  param={"nprobe": 16}, limit=10
)
```

### LanceDB

```python
import lancedb
table.create_index(
    metric="cosine",
    num_partitions=4096,   # ~= nlist
    num_sub_vectors=96     # PQ 段数
)
```

## 7. 现实检视 · 2026 视角

### 仍然有价值的场景

- **十亿级向量** + 内存有限（成本敏感）
- **离线 / 半离线**场景（增量写不频繁）
- **Recall 目标 95-98%**（大多数推荐、搜索场景够用）

### 被替代的场景

- **中小规模（< 100M）**：HNSW 精度 + 延迟都更好
- **增量写频繁**：HNSW 动态插入更友好
- **极高 recall（> 99.5%）**：HNSW 或 Flat
- **磁盘化 + 大规模**：DiskANN 更专业

### 2024-2025 新趋势

- **Binary Embedding + Flat** 在某些场景性能**追上** IVF-PQ（极致压缩）
- **新量化方法**（FP8 / OPQ / AQ）精度更好
- **Lance Format 原生支持** 让湖上 IVF-PQ 更实用

### 选型简化

| 场景 | 推荐 |
|---|---|
| < 10M 向量 | HNSW |
| 10M - 100M | HNSW 或 IVF-PQ |
| 100M - 1B | **IVF-PQ** 或 DiskANN |
| 1B+ | DiskANN 或 IVF-PQ + 分片 |
| 极致压缩 | Binary + 分层 |

## 8. 陷阱

- **没 train 就 add**：IVF 需要先训练聚类中心
- **nlist 过大**：桶太多桶本身找最近代价大
- **M 选太大**：压缩过度，recall 掉
- **增量写 IVF 不 retrain**：新数据分布偏离老 centroid → recall 降
- **只看公开 benchmark**：SIFT / DEEP 等 benchmark 分布规整，**自家数据可能更差**
- **不做 ADC 精度评估**：假设 recall 95% 但实际 80%

## 9. 延伸阅读

- **[*Product Quantization for Nearest Neighbor Search* (Jégou et al., TPAMI 2011)](https://hal.inria.fr/inria-00514462v2/document)** —— PQ 原论文
- **[*Billion-scale similarity search with GPUs* (Johnson et al., 2017)](https://arxiv.org/abs/1702.08734)** —— Faiss 论文
- **[Faiss wiki](https://github.com/facebookresearch/faiss/wiki)** · **[Faiss Tutorial](https://github.com/facebookresearch/faiss/tree/main/tutorial)**
- **[Milvus IVF 文档](https://milvus.io/docs/index.md)**
- **[Quantization](quantization.md)** —— SQ / PQ / BQ / Matryoshka 对比

## 相关

- [HNSW](hnsw.md) · [DiskANN](diskann.md) · [向量数据库](vector-database.md)
- [ANN 索引对比](../compare/ann-index-comparison.md)
