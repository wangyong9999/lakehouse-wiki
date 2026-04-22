---
title: DiskANN · 磁盘友好的十亿级 ANN
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-18
applies_to: Microsoft DiskANN 0.7+, Milvus 2.4+ DiskANN 索引
tags: [retrieval, vector, ann, index, ssd]
aliases: [Vamana]
related: [hnsw, ivf-pq, vector-database]
systems: [milvus, faiss, diskannpy]
status: stable
---

# DiskANN · 磁盘友好的十亿级 ANN

!!! tip "一句话理解"
    **把 ANN 索引放到 NVMe SSD 上仍然毫秒级检索**。Microsoft 2019 NeurIPS 论文 + Vamana 图结构。HNSW 精度高但吃内存；IVF-PQ 省内存但精度损失；**DiskANN 是十亿级 + 成本敏感场景的第三条路**。

!!! abstract "TL;DR"
    - **核心**：**Vamana 图** + 磁盘友好布局，内存只放 ~10% 索引元数据
    - **规模甜点**：**1 亿 - 100 亿向量**、NVMe SSD 可用
    - **精度**：Recall 95-99%（略低于 HNSW 的 99%+）
    - **延迟**：p99 2-10ms（比 HNSW 慢几倍，但内存省 10×）
    - **硬件要求**：**NVMe 必须**，SATA SSD / HDD 完全不可行
    - **增量弱**：FreshDiskANN 变种支持，但主路径仍是批建

## 1. 为什么需要 DiskANN

### 十亿级向量的规模墙

| 方案 | 1B × 768d 需要 |
|---|---|
| HNSW in-memory | **3 TB RAM** → 需分布式或放弃 |
| IVF-PQ（压缩 20×）| 150 GB RAM → **单机可行但精度降** |
| **DiskANN** | ~200 GB NVMe + **30 GB 内存** → 单机、高精度 |

**DiskANN 的价值**：**在普通商用硬件上（单机 + NVMe）搞定十亿级向量检索**。

### Microsoft 的贡献

DiskANN 论文（NeurIPS 2019）提出：
- **Vamana 图** 作为可磁盘化的图索引
- **α-RNG pruning**（极端值修剪）让图稀疏
- **随机入口点 + 贪心搜索**
- **布局优化**让每次 SSD 读效率最大化

后续扩展（FreshDiskANN / Filtered DiskANN / OOD-DiskANN 等）持续发展。

## 2. Vamana 图结构

HNSW 和 Vamana 都是"图 + 贪心搜索"，但：

### HNSW vs Vamana

| | HNSW | Vamana（DiskANN） |
|---|---|---|
| 层数 | 多层（log N 层） | **单层** |
| 边选择 | 最近邻 M 个 | **α-RNG 修剪** |
| 查询入口 | 固定顶层 entry | 随机 / 特定 entry |
| 布局 | 指针散乱 | **邻居 + 原向量打包** |
| 适合 | 内存 | **SSD** |

### α-RNG Pruning（核心创新）

构建边时不是简单取最近 M 个邻居，而是**修剪"冗余"边**：

```
对每个节点 v，候选邻居按距离排序
对每个候选 c：
  如果 c 距离 < α × (现有邻居到 c 的距离)：
    加 c 为邻居
  否则：
    跳过（冗余）
```

**效果**：图稀疏但"覆盖方向"完整——搜索跳几次就能到达。

`α` 越大图越稀疏（α=1.0 是严格 RNG，2024 典型 α=1.2-1.4）。

### 磁盘友好布局

每个节点在磁盘上的记录：
```
[node_id] [num_neighbors] [neighbor_id × K] [original_vector (float)]
```

一次随机读 SSD（~4KB 页）拿到：
- 当前节点的邻居列表（下一跳候选）
- 当前节点的原始向量（精确距离计算）

每跳只需 1 次 SSD read → **总查询 = 10-20 次 SSD read**。

### 内存侧（PQ-compressed）

完整原向量只在 SSD，内存仅存：
- **PQ 压缩版本**（用于搜索时快速距离估计）
- 少量 entry 点（导航起点）

**典型内存占用 = 总数据的 10-15%**。

## 3. 查询流程

```
1. Query vector q 进来
2. 用 PQ 版本在内存中快速找到几个候选 entry 点
3. 从 entry 点开始贪心搜索：
   a. 对当前节点：读 SSD 拿邻居列表
   b. 计算 q 到邻居 PQ 压缩向量的距离（快）
   c. 取 top ef 候选进入 next iter
   d. 每 K 次迭代，用完整向量（读 SSD）验证一次
4. 终止：ef 队列里全是已访问节点
5. 返回 topK
```

**关键**：
- **大部分迭代只用 PQ 距离**（快）
- **少量迭代用精确距离**（从 SSD 拿原向量）
- **总 SSD I/O**：10-50 次

## 4. 性能对比

| 维度 | HNSW | IVF-PQ | DiskANN |
|---|---|---|---|
| 内存 | 全量 | 全量（压缩）| **~10% + PQ** |
| 存储 | 内存 | 内存 | **SSD** |
| 查询 p99 | < 1ms | 5-20ms | **2-10ms** |
| 构建时间 | 中 | 中 | **慢** |
| 增量 | 友好 | 不友好 | 弱（FreshDiskANN 支持）|
| 规模上限 | ~亿（单机）| ~百亿 | **~百亿单机** |
| Recall 上限 | 99%+ | 95-99% | 95-99% |

## 5. 工程要点

### 硬件要求（必看）

- **NVMe SSD**：随机读 IOPS > 100k（SATA SSD **只有 10k**，DiskANN 查询会崩到 100ms+）
- **NVMe 模型**：Intel Optane / Samsung 980 Pro / Micron 9400 等
- **内存**：总向量 × d × 4 的 10-20%（PQ 压缩后 + 图元数据）
- **CPU**：查询是 CPU-bound 的距离计算 + SSD I/O

### 核心参数

| 参数 | 含义 | 典型 |
|---|---|---|
| `R` (max degree) | 图每个节点最大邻居数 | 64-128 |
| `L` (build) | 构建时候选队列大小 | 100-200 |
| `α` | 修剪参数 | 1.2-1.4 |
| `Ls` (search) | 查询时候选队列大小 | 50-200 |
| `B` | PQ 每向量字节数 | 64-128 |

### 规模 vs 资源

| 规模 | 内存 | NVMe 存储 | 构建时间 |
|---|---|---|---|
| 1 亿 × 128d | 5-8 GB | 50 GB | 1-2 小时 |
| 10 亿 × 128d | 30-50 GB | 500 GB | 10-15 小时 |
| 100 亿 × 128d | 200-300 GB | 5 TB | 分布式或几天 |

## 6. 变种

### FreshDiskANN（2021）

- 支持**在线插入 / 删除**
- 内存 delta + 后台合并
- 工业生产场景必备

### Filtered DiskANN（2023）

- 带 metadata filter 的搜索（类似 HNSW filter-aware）
- 支持 pre-filter / in-filter 策略

### OOD-DiskANN

- 针对"查询分布 ≠ 索引分布"的场景优化

## 7. 代码示例

### diskannpy (Python)

```python
import diskannpy as dap

# 构建（批）
dap.build_disk_index(
    data_file="vectors.fbin",
    index_prefix_path="index/",
    complexity=100,
    graph_degree=64,
    search_memory_maximum=50,
    build_memory_maximum=100,
    vector_dtype=dap.VectorDType.FLOAT32,
    distance_metric="l2",
)

# 查询
index = dap.StaticDiskIndex(
    index_directory="index/",
    num_threads=16,
    num_nodes_to_cache=10000,
    distance_metric="l2"
)
neighbors, distances = index.search(
    query=q_vec, k_neighbors=10, complexity=50
)
```

### Milvus

```python
col.create_index(
  field_name="vec",
  index_params={
    "index_type": "DISKANN",
    "metric_type": "L2",
    "params": {
      "search_list": 100,
      "beam_width_ratio": 4.0
    }
  }
)
```

## 8. 现实检视 · 2026 视角

### 适用场景

- **百亿级向量**：DiskANN 几乎是**唯一的单机可行方案**
- **成本敏感**：NVMe 价格 1/10 RAM
- **离线 / 半离线**：批建索引、查询为主
- **Recall 95-99%** 业务可接受

### 不适合

- **实时 upsert 频繁**：FreshDiskANN 有用但成本高
- **Recall > 99.5%**：选 HNSW
- **硬件受限**：没有 NVMe 别尝试
- **中小规模**：< 1 亿用 HNSW 就够

### 工业实际部署

- **Microsoft**：Bing / Azure Cognitive Search 用
- **Milvus DiskANN**：2024+ 成熟，企业级
- **Pinecone / Weaviate**：走内存路线为主，未采用 DiskANN

### 2024-2025 进展

- **SPANN (SIGMOD 2021)** 是 DiskANN 的竞争者，思路类似但结构略有差异
- **ScaNN + SSD** 变体也在研究
- 主流向量库**把 DiskANN 作为可选索引**而非默认

## 9. 陷阱

- **SATA SSD 以为能用**：随机读 IOPS 不够，性能完全崩
- **RAM 不够存 PQ**：实际上 PQ 也要内存（10-15% 数据量）
- **构建内存估不足**：建索引时峰值内存 > 运行
- **增量写用批 DiskANN**：重建成本爆；用 FreshDiskANN
- **NVMe 共享文件系统**：I/O 延迟上涨，影响查询
- **调参照搬 HNSW 思路**：R / α / Ls 有各自最佳实践

## 10. 延伸阅读

- **[*DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node* (NeurIPS 2019)](https://www.microsoft.com/en-us/research/publication/diskann-fast-accurate-billion-point-nearest-neighbor-search-on-a-single-node/)** —— 原论文：SIFT1B 10 亿向量 · recall@10 > 95% 时 p99 < 10ms · 内存仅原数据 ~10%
- **[*FreshDiskANN* (2021)](https://arxiv.org/abs/2105.09613)**
- **[Filtered DiskANN (SIGMOD 2023)](https://dl.acm.org/doi/10.1145/3588931.3615606)**
- **[DiskANN GitHub](https://github.com/microsoft/DiskANN)**

## 相关

- [HNSW](hnsw.md) · [IVF-PQ](ivf-pq.md) · [向量数据库](vector-database.md)
- [ANN 索引对比](../compare/ann-index-comparison.md)
