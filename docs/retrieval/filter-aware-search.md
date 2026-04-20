---
title: Filter-aware ANN · 结构化谓词 + 向量组合查询
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: Milvus 2.x · Qdrant 1.x · pgvector 0.7+ · LanceDB
tags: [retrieval, filter, ann, hybrid, structured-predicate]
aliases: [带过滤的 ANN, filtered-vector-search, 结构化检索]
related: [hnsw, ivf-pq, qdrant, milvus, hybrid-search]
systems: [qdrant, milvus, pgvector, lancedb]
status: stable
---

# Filter-aware ANN · 结构化谓词 + 向量组合

!!! tip "一句话定位"
    **"找相似商品 AND price < 1000 AND category = '电子'"**——结构化 WHERE 过滤和向量相似度查询**组合执行**的问题。看起来简单 · 实际上**是生产向量检索最常见的难题之一**。

!!! info "和其他页的边界"
    - 本页 · **结构化谓词 + 向量搜索组合** 的算法和工程问题
    - [Hybrid Search](hybrid-search.md) · **稀疏 + 稠密 向量融合**（不是同一个问题！）
    - [HNSW](hnsw.md) / [IVF-PQ](ivf-pq.md) · **向量索引本身**的算法

    **两个 Hybrid 别混**——业界有时笼统都叫 "hybrid search"：
    - **Vector + Filter** = 本页（结构化谓词 + ANN）
    - **Sparse + Dense** = hybrid-search.md（两种 embedding 融合）

!!! abstract "TL;DR"
    - **三种实现策略**：**Pre-filter** · **Post-filter** · **In-filter (Filterable HNSW)**
    - 选哪种取决于**过滤选择性**：过滤后剩 < 5% 用 pre · > 50% 用 post · 中间用 in-filter
    - **Filterable HNSW**（2023+ · Qdrant 最早商业化 · Milvus / pgvector 0.7+ 跟进）是 2024-2026 中等选择性场景的常见方案
    - **pgvector 2024 hnsw.ef_search + parallel seq scan** 是 PG 场景新突破
    - **量化和 filter-aware 互相影响** · 组合设计要一起考虑

## 1. 问题定义 · 为什么"看起来简单"不简单

### 典型业务场景

```sql
-- 找"和这张图片相似 + 价格 < 1000 + 有库存 + 分类是电子"的商品
SELECT id, name
FROM products
WHERE category = 'electronics'
  AND price < 1000
  AND stock > 0
ORDER BY vector_distance(embedding, :query_vec) 
LIMIT 10;
```

### 为什么难？

纯 ANN 索引（HNSW / IVF / DiskANN）建立时**不知道结构化字段**。查询时：
- 如果**先过滤再 ANN**（pre-filter）· 过滤后的集合可能**破坏 ANN 索引的连通性** · 图走不到 Top-K
- 如果**先 ANN 再过滤**（post-filter）· 可能要拉出超多候选（10,000+ 才能剩下 10 个）· 成本高
- 过滤选择性**天然动态** · 同一 query "category = 电子" 过滤率 20% · "category = 罕见二级分类" 过滤率 0.01%——**一种策略不可能都最优**

## 2. 三种实现策略

### Pre-filter（先过滤再 ANN）

```
Step 1: 走结构化索引(B-tree / bitmap) · 得到满足过滤的 doc_id 集合 S
Step 2: 在 S 内做 ANN
```

**问题**：
- S 小（< 5% 全集）· 有效 —— ANN 索引里大部分点被 mask · **但图索引的连通性被破坏** · 往往走完全图或失败
- S 中等（5-50%）· 经常最差——既不能用索引剪枝 · 又破坏 ANN 遍历
- S 大（> 50%）· 浪费——其实不需要提前过滤

**适合**：过滤**极严格**（剩 < 5%） · 或者数据量小可以暴力扫 S

### Post-filter（先 ANN 再过滤）

```
Step 1: 走 ANN 索引 · 取 Top-K*扩展 (比如 K=10 · 扩 100-1000)
Step 2: 在结果里过滤出满足 WHERE 的
Step 3: 保留前 K 个
```

**问题**：
- 过滤选择性高（保留 < 1%）· 需要扩到**几千几万** · 成本爆
- ANN Top-K 顺序和过滤后顺序**不严格一致** · 扩展倍数不够**可能漏真正的近邻**
- "扩多少" 是**查询时猜** · 业务 query 分布变了就失准

**适合**：过滤**宽松**（保留 > 50%）· 简单查询

### In-filter (Filterable HNSW) · 2023+ 主流

**思路**：让 HNSW 图在遍历时**感知过滤**——遇到不满足 WHERE 的点 · **跳过但继续**探索邻居 · 不破坏图连通。

```
HNSW 图遍历:
  candidate = get_neighbor(current)
  if matches_filter(candidate):
      add_to_result(candidate)
  else:
      continue_to_neighbors(candidate)  # 不剪枝 · 只是不加结果
```

**工程落地**：

- **Qdrant 的 Filterable HNSW (2023+)** · 较早商业化 · 通过在图构建时考虑过滤场景 · 或动态调整图遍历
- **Milvus 2.3+ 的 Filtered Search** · 支持 bitmap / expression-based
- **pgvector 0.6-0.7+** · `hnsw.ef_search` + parallel seq scan 组合 · PostgreSQL 场景新突破
- **LanceDB** · filter 推到 Lance 文件层做 pruning

**优势**：
- **选择性通用**（5-70% 过滤都好用）
- 延迟接近纯 ANN

**劣势**：
- **索引构建时间**可能增加
- 不是所有 ANN 库都实现

## 3. 选型决策

**按过滤选择性（filter 后保留的比例）分**：

| 过滤选择性 | 推荐策略 | 典型产品 |
|---|---|---|
| **< 5%**（极严格 · 结果极少） | Pre-filter | 所有向量库都支持 |
| **5-50%**（中等选择性） | **In-filter / Filterable HNSW** | Qdrant / Milvus / pgvector 0.7+ |
| **> 50%**（宽松 · 过滤少数排除） | Post-filter + 合适扩展倍数 | 所有向量库都支持 |

**动态策略**：生产场景**无法知道 query 的选择性** · 两种应对：

1. **运行时评估**（Qdrant / Milvus 在做）· query planner 先估算过滤命中数 · 自动选策略
2. **多索引并行**（复杂）· pre-filter 和 post-filter 都跑 · 看谁先出结果 · 不推荐

## 4. 和其他机制的组合

### Filter + Quantization

量化（见 [Quantization](quantization.md)）会降低精度 · 叠加 filter 风险放大：

- PQ + post-filter · 精度双重打折——**扩展倍数要更大**
- Binary Quantization + pre-filter · 过滤后余量小 · Hamming 距离失真——**不推荐组合**
- **组合验证** · 自家数据上实测 Recall@K · 不要假设

### Filter + Hybrid Search

[Hybrid Search](hybrid-search.md)（稀疏+稠密融合）和 filter 组合时：

- 各路 retrieval 都要各自处理 filter（BM25 自然支持 · Dense 走 filter-aware ANN）
- **RRF 融合在 filter 后**· 不要先融合再 filter

### Filter + Rerank

两阶段架构（详见 [Rerank](rerank.md)）：

```
Stage 1: Filter-aware ANN · Top 100 (filter 已应用)
Stage 2: Rerank 模型 · Top 10
```

一阶段的 filter 推进**减少了二阶段 rerank 的候选数**· 延迟优化关键。

## 5. 陷阱

- **假设 post-filter 够用** · 过滤选择性高时**会漏真近邻** · 必须评估扩展倍数
- **pre-filter 破坏 HNSW 连通** · 用在中等选择性 · 得到的 Top-K 其实不是真的 Top-K
- **忘记索引重建** · 加新的过滤字段 · filter-aware HNSW 要重新构图（不是所有库自动）
- **没做选择性估算** · 让一个 query 同时走极端场景（一次 10% 一次 0.01%）· 延迟 P99 飞
- **把 WHERE 丢到向量库而非用外部数据库预筛** · Qdrant/Milvus 的 filter 对字段索引能力有限 · 复杂 WHERE 效率低
- **混淆 Hybrid 的两种含义** · Filter-aware ≠ Sparse+Dense

## 相关

- [HNSW](hnsw.md) · Filterable HNSW 的算法底座
- [Quantization](quantization.md) · 量化和 filter 的组合影响
- [Hybrid Search](hybrid-search.md) · Sparse+Dense 融合（**不同**概念别混）
- [Qdrant](qdrant.md) · Filterable HNSW 的领跑者
- [pgvector](pgvector.md) · PG 场景 filter-aware 0.7+
- [Milvus](milvus.md) · Filtered Search 支持

## 延伸阅读

- **[Qdrant · Filterable HNSW](https://qdrant.tech/articles/filtrable-hnsw/)**
- **[Milvus · Scalar Filtering](https://milvus.io/docs/scalar_field_index.md)**
- **[pgvector · Indexing with Filter](https://github.com/pgvector/pgvector#filtering)**
- **[Wang et al. · Filtered ANN Survey](https://arxiv.org/abs/2402.02024)**（2024 综述）
