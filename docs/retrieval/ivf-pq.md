---
title: IVF-PQ
type: concept
tags: [retrieval, vector, ann, index]
aliases: [Inverted File + Product Quantization]
related: [hnsw, vector-database]
systems: [milvus, lancedb, faiss]
status: stable
---

# IVF-PQ（Inverted File + Product Quantization）

!!! tip "一句话理解"
    **先倒排分桶，再把每个向量压缩成几个字节**。IVF 解决"查询不必扫全量"，PQ 解决"把海量向量塞进内存 / 小 SSD"。配合起来是**亿级规模内存预算有限时的首选 ANN 索引**。

## 两件事

### IVF（Inverted File）

对所有向量做一次 k-means，聚成 `nlist` 个中心。每个向量被分到距离最近的中心所在"桶"（bucket）。查询时：

1. 对查询向量也找最近的 `nprobe` 个中心
2. 只在这些桶里搜索

`nprobe` 越大 recall 越高、延迟越高；典型 `nlist=4096, nprobe=16`。

### PQ（Product Quantization）

把 $D$ 维向量切成 $M$ 段，每段 $D/M$ 维；对每一段独立做 k-means，得到 256 个子中心（因此可以用 1 字节编码）。这样 $D=128$ 维 float32（512 字节） → $M=16$ 个字节（16 倍压缩）。

距离计算改成"查表 + 累加"，非常快。精度略有损失，但对召回影响可控。

## IVF-PQ 组合效果

| 指标 | 纯 Flat | HNSW | IVF-PQ |
| --- | --- | --- | --- |
| 内存占用 | 100% | 100% + 图结构 | ~10-20% |
| 构建速度 | 零 | 慢 | 中（k-means） |
| Recall（调参后） | 100% | 99%+ | 95%–99% |
| 查询延迟 | 慢 | 快 | 快 |
| 增量写 | 任意 | 增量加点 | 不友好（批建最佳） |

## 什么时候选 IVF-PQ

- **向量规模大**（亿级）但硬件预算紧张
- **内存不够放全量 float32**，接受压缩损失换容量
- **离线批建索引为主**，增量写不频繁
- **和 [HNSW](hnsw.md) 对比**：HNSW 精度上限更高但内存占用大；IVF-PQ 性价比高

## 关键参数调优

| 参数 | 含义 | 典型值 |
| --- | --- | --- |
| `nlist` | IVF 桶数 | $\sqrt{N}$ – $4\sqrt{N}$ |
| `nprobe` | 查询扫几个桶 | 1–128，按 recall 目标选 |
| `M`（PQ 段数） | 压缩粒度 | 向量维度 / 4 是常见起点 |
| `nbits` | 每段 bit 数 | 8（256 子中心）标准 |

## 在典型 OSS 里

- **Faiss** —— IVF-PQ 的参考实现，调参文档丰富
- **Milvus** —— 大规模向量库的默认推荐（相比 HNSW 的内存节省在亿级规模下很关键）
- **LanceDB** —— 默认 IVF-PQ；湖上海量多模数据的天然选择
- **ScaNN** —— Google 的变体，向量量化 + 重排更精细

## 相关概念

- [HNSW](hnsw.md) —— 另一条主路，图索引
- [向量数据库](vector-database.md)
- [ANN 索引对比](../compare/ann-index-comparison.md)

## 延伸阅读

- *Product Quantization for Nearest Neighbor Search* (Jégou et al., TPAMI 2011)
- *Billion-scale similarity search with GPUs* (Johnson et al., 2017)
- Faiss wiki: <https://github.com/facebookresearch/faiss/wiki>
