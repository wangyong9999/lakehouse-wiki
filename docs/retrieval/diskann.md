---
title: DiskANN
type: concept
tags: [retrieval, vector, ann, index]
aliases: [Vamana]
related: [hnsw, ivf-pq, vector-database]
systems: [milvus, faiss]
status: stable
---

# DiskANN

!!! tip "一句话理解"
    **把向量索引放到 SSD 上**仍然能做到毫秒级检索。核心是 Microsoft 的 **Vamana** 图结构——为"随机读 SSD"优化，内存只放少量图元数据，主力数据在磁盘上。是"十亿级向量 + 成本敏感"场景的最优解。

## 它为什么出现

HNSW 精度高但内存吃满（全部向量 + 图结构在 RAM）；IVF-PQ 省内存但精度有损。**DiskANN 是第三条路**：精度接近 HNSW，但 90% 以上的数据放 SSD。

适用场景：

- **十亿级向量**
- **NVMe SSD 价格远低于 RAM**
- **单机扛（不想分布式）**

## 核心机制：Vamana 图

Vamana 和 HNSW 都是"图 + 贪心搜索"，但：

- **单层图**（HNSW 是分层）—— 简化磁盘布局
- **α 修剪**（pruning）构建时只保留"真正必要"的边，使得搜索路径短
- **磁盘友好的布局**：节点 + 邻居列表 + 原始向量打包在一起，一次 SSD read 拿到够走下一步的信息

查询过程：

1. 内存里存一小部分 navigation 节点（用于入口）
2. 从入口开始贪心走图；每一跳读一块 SSD
3. 典型 10–20 次 SSD read 到达查询点附近
4. 按查询向量对候选做精确距离计算

## 性能特点

| 维度 | HNSW | DiskANN |
| --- | --- | --- |
| 内存 | 全量 | 少量（~10%） |
| 存储 | 内存 | SSD（NVMe 最佳） |
| 查询 latency | p95 < 1ms | p95 2–10ms |
| 构建时间 | 中 | 慢 |
| 规模上限 | ~亿 | ~百亿 |

## 变种

- **FreshDiskANN** —— 支持增量插入
- **Filtered DiskANN** —— 带元数据过滤的图搜索（filter-aware）
- **DiskANN + 量化** —— 结合 PQ 进一步压缩

## 在 OSS 里

- **Faiss** —— 有 DiskANN 风格实现
- **Milvus** —— 原生支持 DiskANN 索引类型
- **LanceDB** —— 路线图中
- **Qdrant** —— 目前主走 HNSW（内存优先）

## 什么时候选 DiskANN

- **向量规模 > 1 亿**，RAM 装不下
- **NVMe SSD 充足**（DiskANN 极依赖 SSD 随机读性能，机械盘完全不可行）
- **能接受较长建索引时间**
- **recall 目标 95%–99%**（稍低于 HNSW 的上限）

## 陷阱

- **不是 NVMe 的 SSD 会很惨**：每次查询十几次 IO，SATA SSD 会打到 100ms 以上
- **增量写支持弱**：主路径仍然是"批量建 + 定期重建"
- **构建内存需求**：建索引时内存不低，可能 > 运行时

## 相关

- [HNSW](hnsw.md) / [IVF-PQ](ivf-pq.md)
- [ANN 索引对比](../compare/ann-index-comparison.md)
- [向量数据库](vector-database.md)

## 延伸阅读

- *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node* (NeurIPS 2019)
- *FreshDiskANN: A Fast and Accurate Graph-Based ANN Index for Streaming Similarity Search* (2021)
