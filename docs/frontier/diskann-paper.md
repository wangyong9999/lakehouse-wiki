---
title: DiskANN 论文笔记（NeurIPS 2019）
type: paper-note
tags: [frontier, paper-note, vector, ann]
aliases: [Vamana]
related: [diskann, hnsw, ann-index-comparison]
year: 2019
venue: NeurIPS
status: stable
---

# DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node

!!! info "论文信息"
    - **作者**：Suhas Jayaram Subramanya et al. (Microsoft Research India)
    - **会议**：NeurIPS 2019
    - **链接**：<https://papers.nips.cc/paper_files/paper/2019/hash/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Abstract.html>
    - **相关代码**：<https://github.com/microsoft/DiskANN>

## 一句话收获

> 证明了**单台机器 + 一块 SSD** 也能在亿/十亿级向量上做到毫秒级 ANN；为"大规模 + 低成本"向量检索打开了路径。

## 论文解决什么

背景：HNSW 精度高但**全内存**，亿级向量成本难以承受；分布式方案运维复杂且 inter-node 延迟加剧。

作者提出 **Vamana 图 + 磁盘布局优化**，在单机 SSD 上做到：

- **十亿级向量**
- **ms 级查询延迟**
- **recall 95–99%**
- **成本远低于全内存 HNSW**

## 核心创新

### Vamana 图构建

相比 HNSW 的分层随机游走构建：

- **单层图**（简化磁盘布局）
- **α-RNG（robust pruning）**：剪枝邻居时考虑"远方跳点"，使搜索路径短
- 图稀疏度可调（出边 R）

这个图结构的优势在于**搜索路径比 HNSW 短**——每次查询 10–20 跳而不是几十跳。

### 磁盘布局

- **数据 + 图邻居列表 + 原始向量连续放**：一次 SSD 随机读拿到足够信息
- **内存里只放 navigation points**（约 10% 量）做入口
- 查询过程：内存找入口 → SSD 贪心走图 → 精确距离重算

### 近似 + 精确的组合

- 图搜索阶段：用 PQ 压缩向量快速估计距离
- 最终 Top-K：对候选用原始向量精确距离

两阶段让 recall 能冲到 99%+ 而延迟保持 ms 级。

## 实验结论（论文原始）

- **SIFT1B（10 亿）向量**上：recall@10 > 95% 时 p99 < 10ms（单机 NVMe SSD）
- **内存占用**：约原数据的 10%
- **构建时间**：数小时（可并行）

## 对工程的启示

1. **向量检索的"硬件占用"可以比 RAM 低一个数量级** —— 在海量向量场景是决定性的成本差距
2. **SSD 随机读是可以被"驯服"的** —— 靠精心的数据布局 + 少量内存元数据
3. **推动后续演化**：
    - FreshDiskANN（支持增量）
    - Filtered DiskANN（带元数据过滤）
    - 催化了工程侧"向量索引 = 磁盘资产"的观念

## 和后续工作的关系

- **Microsoft 内部**：Bing / Copilot 的大规模向量检索使用 DiskANN
- **Milvus**：内置 DiskANN 索引类型
- **Faiss**：实现了 DiskANN 风格的索引
- **LanceDB** 路线图中

## 对团队的价值

- 我们团队的多模 asset 预期到达**亿级向量**；DiskANN 是 RAM 预算达到瓶颈时的关键选项
- 配合 [Lance Format](../foundations/lance-format.md) / [LanceDB](../retrieval/lancedb.md) 的落盘特性，DiskANN 思路天然契合

## 延伸阅读

- 原论文：<https://papers.nips.cc/paper_files/paper/2019/hash/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Abstract.html>
- *FreshDiskANN*（2021）
- *Filtered DiskANN*（2023）
- Microsoft 博客：*Vector search that scales*
