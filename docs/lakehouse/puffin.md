---
title: Puffin（Iceberg 辅助索引文件）
type: concept
tags: [lakehouse, index, iceberg]
aliases: [Puffin Files]
related: [manifest, iceberg, vector-database]
systems: [iceberg]
status: stable
---

# Puffin（Iceberg 辅助索引文件）

!!! tip "一句话理解"
    Iceberg 规格里**放"辅助索引 / 统计 / Sketch"的**侧车文件格式。被 Manifest 引用，和数据文件平级；是向量索引、Theta Sketch、Bloom Filter 未来下沉到湖表的统一载体。

## 它解决什么

Iceberg 数据文件是 Parquet / ORC / Lance，它们自带的统计（min/max/null count）不够用。实际场景需要：

- **列直方图 / Sketch** —— 估算 NDV、分位点，优化器用
- **Bloom Filter** —— 点查谓词下推
- **向量索引** —— 为向量列建 HNSW / IVF-PQ，让湖表直接支持 ANN
- **位图索引 / Bitmap Index** —— 高选择度点查

这些都不适合塞进 Parquet 文件里（格式受限、一次性写死）。Puffin 是给它们专门造的**通用容器**。

## 文件结构

Puffin 是一个**容器格式**，里面可以装若干 **Blob**。每个 Blob 有：

- `type` —— 字符串，标识这块数据的种类。**官方 spec 当前只定义两种 blob type**：`apache-datasketches-theta-v1`（NDV 去重 sketch）、`deletion-vector-v1`（v3 引入的行级删除位图）
- `fields` —— 对应哪些列
- `snapshot-id` —— 属于哪个 Snapshot 的时刻
- `properties` —— 自定义元数据
- `raw bytes` —— 真正的二进制内容

```
┌──────────────────────────┐
│ Puffin File              │
│ ┌──────────────────────┐ │
│ │ Blob 1: Theta Sketch │ │
│ ├──────────────────────┤ │
│ │ Blob 2: Bloom Filter │ │
│ ├──────────────────────┤ │
│ │ Blob 3: HNSW index   │ │   ← 这是关键
│ ├──────────────────────┤ │
│ │ Footer (metadata)    │ │
│ └──────────────────────┘ │
└──────────────────────────┘
```

## 对"多模数据湖"意味着什么

这是 Iceberg 踏入"湖上检索"的关键一块：

- 向量列的 ANN 索引可以**以 Puffin Blob 形式落盘**，与数据文件并存
- 读侧引擎（如 Trino、Spark、或专用向量库）发现 Puffin 里有 HNSW blob，可以直接跳过全量扫描
- 未来"湖上跑 RAG"不再强依赖独立向量服务，Iceberg 本身就能承担"元数据 + 数据 + 索引"三件事

详见一体化方向 [Lake + Vector](../unified/lake-plus-vector.md)。

## 当下状态

- **官方 blob**（Puffin spec 定义）：
  - `apache-datasketches-theta-v1` —— 已稳定，Trino / Spark 消费
  - `deletion-vector-v1` —— v3 引入，取代 v2 的 position-delete file（Roaring bitmap 格式）
- **社区 proposal（未接纳 spec）**：向量索引（HNSW / IVF-PQ）、Bloom Filter、位图索引
- **生态**：Netflix / Tabular / Polaris 等在不同方向推进；湖上向量检索的真正落地仍需等 blob type 标准化（或用 Lance 走另一条路）

## 相关概念

- [Manifest](manifest.md) —— Puffin 文件被 Manifest 引用
- [Apache Iceberg](iceberg.md)
- [Lance Format](../foundations/lance-format.md) —— 另一条路线（索引和数据文件一体）

## 延伸阅读

- Iceberg Puffin spec: <https://iceberg.apache.org/puffin-spec/>
- Iceberg Vector Search proposal（社区讨论）
