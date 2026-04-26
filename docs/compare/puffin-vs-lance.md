---
title: Puffin vs Lance · 向量下沉到湖的两条路
applies_to: "2024-2026 主流"
type: comparison
level: B
depth: 资深
prerequisites: [puffin, lance-format, lake-plus-vector]
tags: [comparison, vector, iceberg, lance, puffin]
related: [puffin, lance-format]
subjects: [iceberg-puffin, lance-format]
status: stable
last_reviewed: 2026-04-17
---

# Puffin vs Lance · 向量下沉到湖的两条路

!!! tip "读完能回答的选型问题"
    "我们要让湖表直接支持向量检索" 这件事 —— 到底选 **Iceberg + Puffin 把 ANN 索引当侧车**，还是 **整表改成 Lance 格式**？两条路背后的架构假设不同，成本与灵活度也不同。

!!! abstract "TL;DR"
    - **Puffin 是 Iceberg 协议里的一个侧车文件类型**；Lance 是一种**独立的列式文件格式**
    - Puffin = 保留 Parquet 数据 + 外挂索引 Blob；**最小侵入，引擎多**
    - Lance = 数据文件 + 索引 + manifest 三位一体；**多模原生，随机访问强**
    - 选 Puffin：已有 Iceberg 栈 + 向量需求轻量 + 看重跨引擎开放
    - 选 Lance：多模主线 + ML 训练重 + 愿接受独立格式的生态成本
    - 非互斥：一家可并存。Puffin 管"BI 事实表上的小向量侧"，Lance 管"多模资产 + 向量大表"

## 两者的本质差异

| 维度 | **Iceberg + Puffin** | **Lance / LanceDB** |
| --- | --- | --- |
| 定位 | 协议扩展（标准 spec 的一部分） | 独立文件格式（新的事实标准候选） |
| 数据文件 | Parquet / ORC（沿用）| Lance Fragment（原生） |
| 索引存放 | **Puffin blob**（独立文件，被 Manifest 引用） | **内嵌 Fragment**（与数据同文件簇） |
| 向量原生字段 | VECTOR\<FLOAT, N\>（Iceberg 类型） | 原生，连带多模二进制 |
| 随机访问 | Parquet 级别（Page 解压）| 原生行级 |
| 更新 / 删除 | Iceberg 的 delete files | Fragment 原子替换 |
| 读端要求 | 引擎认识 Puffin blob 类型 | 需要 Lance reader |
| 最大规模 | 随 Iceberg（表格式层面）| 取决于 LanceDB 部署方式 |
| 治理 / Catalog | Iceberg Catalog（Unity / Polaris / Nessie）原生 | 在 Unity Catalog 支持中；Lance 表注册仍在演进 |

## 架构层面的对比

### Iceberg + Puffin

```
Catalog
  └── metadata.json
       └── Manifest List
            └── Manifest
                 ├── Data file (Parquet)
                 ├── Delete file (Parquet/position deletes)
                 └── Puffin blob (HNSW / IVF-PQ / stats)
```

**关键性质**：
- 数据文件和索引文件**分离**，被同一个 Manifest 引用
- Iceberg 全部能力（Time Travel、Schema Evolution、Partition Evolution）无损继承
- 引擎读取时分两条路径：数据扫描 vs 索引查询，由优化器选择
- Puffin blob **自描述类型**（字符串 kind，如 `apache-datasketches-theta-v1` / `vector-index-hnsw-v1`）

### Lance

```
对象存储
  └── dataset/
       ├── Fragment 1
       │    ├── Data file (Lance format)
       │    └── Index file (ANN, inline with fragment)
       ├── Fragment 2
       │    └── ...
       └── _versions/
            └── manifest.json (version history)
```

**关键性质**：
- 数据 + 索引 + 版本元数据**三位一体**
- 每个 Fragment **自足**，独立 Reader 可直接消费
- 原生支持随机访问（对训练数据 shuffle 重要）
- 多模二进制字段（图 / 音 / 视）作为一等公民

## 生态对比

### 哪些引擎 / 工具能读

| 对象 | Puffin（Iceberg 表的侧车）| Lance |
| --- | --- | --- |
| Spark | ✅ 通过 Iceberg Spark runtime | ✅ lance-spark |
| Trino | ✅ Puffin stats 已用；向量索引 blob 阅读在演进 | ⚠️ 需要 lance reader，实验性 |
| Flink | ✅ Iceberg Sink/Source | ⚠️ 较新 |
| DuckDB | ✅ 通过 Iceberg extension | ✅ lance 扩展 |
| Python / pyiceberg / pyarrow | ✅ | ✅ `lance` 包原生 |
| LanceDB | — | ✅ 原生 |
| Ray / PyTorch 训练 | ✅ 通过 Spark 或 pyiceberg | ✅ **最佳**（随机访问原生） |
| Milvus / Qdrant 迁出 | 不直接 | 可作为落地格式 |

### Catalog 支持

- **Puffin / Iceberg**：Unity / Polaris / Nessie / Gravitino / HMS 全部原生（因为本来就是 Iceberg）
- **Lance**：Unity Catalog 支持向量表的路径；Nessie 尚未明确；Polaris 暂不支持。生态仍在追赶。

### 治理（权限 / 血缘）

- **Puffin**：治理 = Iceberg 治理，现成
- **Lance**：表级权限相对新，跨 Catalog 一致性要自己设计

## 性能场景

### 向量检索本身

| 场景 | Puffin | Lance |
| --- | --- | --- |
| 单个查询 Top-K（内存索引）| HNSW blob 加载到内存后等价 | 等价 |
| 大规模（百亿级）磁盘友好 | Puffin DiskANN blob 理论支持 | Lance + DiskANN 更成熟 |
| 带结构化过滤的 hybrid | Iceberg 的谓词下推 + Puffin | LanceDB filter-aware 更强 |
| 多向量列（CLIP + BGE）| 一列一个 blob，协议统一 | 原生多列，内嵌 |

### ML 训练读取

- **随机 shuffle 读 100M 行训练集**：Lance **明显胜**（随机访问原生）；Parquet 需要解压 Row Group，成本高
- **全量批扫描训练集**：两者接近

### 写入路径

- **流式 upsert（CDC）**：Iceberg+Paimon 组合成熟；Lance 能用但不是核心场景
- **批量 append（新向量）**：两者都高效

## 团队落地建议（和 ADR-0003 一致）

| 场景 | 选择 |
| --- | --- |
| BI 事实表要加个"推荐相似"向量列 | **Puffin**（最小侵入）|
| 多模资产表（图 / 文 / 音 + 向量）| **Lance** |
| 大规模 ML 训练集 | **Lance** |
| 已有 Iceberg 栈，短期验证向量能力 | **Puffin** |
| 长期主线：多模检索 + RAG 支撑 | **Lance**（配合 LanceDB） |
| 小向量量（< 千万）+ 结构化主导 | **Puffin**（避免引新格式） |

## 共存模式（最可能的实际结果）

大多数团队会走**组合拳**：

```
主线多模 asset 表          → Lance / LanceDB
BI 事实表上的"小向量尾巴"  → Iceberg + Puffin
大规模 in-production 向量检索 → Milvus（独立服务）
全部通过 Unity / Polaris 统一 Catalog 注册
```

不要纠结"必须二选一"。Puffin 是 Iceberg 的一个特性；Lance 是一种格式。**它们的竞争不对称**——更准确说 Lance 竞争的是 Parquet，Puffin 是 Iceberg 协议的扩展。

## 陷阱与风险

- **Puffin 向量索引标准仍在演进**：不同引擎支持进度不同，选型时问清楚你用的引擎版本
- **Lance 表迁移到其他格式成本高**：锁定性比 Parquet 强
- **Lance + Iceberg 混合**：一张 Iceberg 表里能不能放 Lance 数据文件？理论上 spec 允许，实现支持仍看引擎
- **Catalog 对 Lance 表的权限模型**：比 Iceberg 晚成熟，权限边界可能有灰色

## 相关

- [Puffin](../lakehouse/puffin.md) · [Lance Format](../foundations/lance-format.md) · [LanceDB](../retrieval/lancedb.md)
- [Lake + Vector 融合架构](../unified/lake-plus-vector.md)
- [ADR-0003 多模向量选 LanceDB](../adr/0003-lancedb-for-multimodal-vectors.md)

## 延伸阅读

- Iceberg Puffin spec: <https://iceberg.apache.org/puffin-spec/>
- Lance 论文 / LanceDB blog 系列
- *A Vector Search Engine for the Data Lake Era*（LanceDB 博客）
- Iceberg Vector Search discussion（社区讨论）
