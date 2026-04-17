---
title: ANN 参数速查
description: HNSW / IVF-PQ / DiskANN 调参 + 选择表
tags: [cheatsheet, ann, vector]
---

# ANN 参数速查

## 1. 怎么选索引

| 规模 | 内存预算 | 推荐 |
| --- | --- | --- |
| < 100万 | 不紧 | **Flat**（暴力，recall=1.0） |
| 100万–1千万 | 充足 | **HNSW** |
| 1千万–1亿 | 紧 | **IVF-PQ** |
| 1亿–10亿 | SSD 足 | **DiskANN** |
| > 10亿 | 成本敏感 | **DiskANN** 或**分片 HNSW** |

## 2. HNSW 参数

| 参数 | 作用 | 典型值 | 调优方向 |
| --- | --- | --- | --- |
| `M` | 每节点邻居数 | 16–64 | 图质量，越大越准越占内存 |
| `efConstruction` | 建图搜索队列 | 100–500 | 越大建图慢、质量高 |
| `ef` / `efSearch` | 查询搜索队列 | 16–512 | **实时可调**，拿 recall 换延迟 |

**典型配方**：

```
标准（延迟 ms 级 + 高 recall）:  M=32,  efConstruction=200,  ef=128
内存受限:                        M=16,  efConstruction=100,  ef=64
极致 recall:                     M=64,  efConstruction=400,  ef=256
```

## 3. IVF-PQ 参数

| 参数 | 作用 | 典型值 |
| --- | --- | --- |
| `nlist` | IVF 桶数 | `√N` – `4√N` |
| `nprobe` | 查询扫桶数 | 1–128 |
| `M`（PQ 段数） | 向量切分段 | `D/4` 起 |
| `nbits` | 每段 bits | 8（256 子中心） |

**典型配方**（1 亿 × 768 维）：

```
nlist = 16384,  nprobe = 32,  M = 96,  nbits = 8
→ 每向量压缩到 ~12 字节，recall ~97%
```

## 4. DiskANN 参数

| 参数 | 作用 | 典型 |
| --- | --- | --- |
| `R` | 每节点出边数 | 32–64 |
| `L`（构建）| 构建队列 | 100–200 |
| `L`（查询）| 查询队列 | 50–200 |
| `alpha` | 剪枝系数 | 1.2 |

## 5. 距离度量

| 度量 | 何时用 |
| --- | --- |
| **Cosine** | 文本 / CLIP embedding（L2 归一化后等价于内积） |
| **L2 / Euclidean** | 已归一化的一般用 cosine，未归一化且带量纲用 L2 |
| **Inner Product** | 推荐系统评分向量 |
| **Hamming** | 二值化向量（LSH / 低精度） |

**规则**：归一化 + cosine 几乎永远是最稳选择。

## 6. 过滤策略

| 场景 | 推荐 |
| --- | --- |
| 过滤条件选择度高（> 50% 命中） | **post-filter** 也能接受 |
| 过滤条件选择度低（< 10%） | **pre-filter** 必须 |
| 过滤 + 向量都严格 | **filter-aware ANN**（Qdrant / Milvus iterative） |

## 7. 性能目标参考

| 场景 | p99 目标 | 硬件 |
| --- | --- | --- |
| 在线检索（推荐 / 搜索） | < 20ms | GPU 或内存 HNSW |
| RAG 检索阶段 | < 100ms | 内存 HNSW / 小规模 |
| 离线批检索 | < 10s / 1k queries | 任意 |

## 8. 内存估算

```
HNSW 内存 ≈ N × D × 4 (float32) × 1.3 (图开销)
           = 1亿 × 768 × 4 × 1.3 ≈ 400GB  ← 放不下，考虑 IVF-PQ

IVF-PQ 内存 ≈ N × (M × nbits / 8)   + centroids
            = 1亿 × 96 × 1 / 8 + 小量 ≈ 1.2GB  ← 轻松
```

## 9. Recall 目标的调参

- Recall 95% → 默认配置多数能到
- Recall 99% → HNSW `ef=256`，IVF `nprobe=64`，接受延迟涨
- Recall 99.9% → 只能 Flat 或 HNSW `ef>=512` + 大 M

## 10. 坑

- **向量没归一化**：cosine 行为不对
- **索引建太大 `ef`**：上线内存挤爆
- **`nlist` 选太小**：每桶过大，nprobe 要更高
- **多线程构建 IVF k-means**：某些实现有 race
- **增量写入 HNSW 不 optimize**：图越来越稀

## 相关

- [HNSW](../retrieval/hnsw.md) · [IVF-PQ](../retrieval/ivf-pq.md) · [DiskANN](../retrieval/diskann.md)
- [ANN 索引对比](../compare/ann-index-comparison.md)
- [向量数据库](../retrieval/vector-database.md)
