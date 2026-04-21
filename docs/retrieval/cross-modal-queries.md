---
title: 跨模态查询 · Filter × 向量 · 一条 SQL 三能力
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: LanceDB 0.20+ · Milvus 2.5+ · Qdrant 1.12+ · pgvector 0.8+ · Elastic 8.x · DuckDB VSS · Trino · Spark · 2024-2026 实践
prerequisites: [vector-database, hybrid-search, filter-aware-search]
tags: [retrieval, cross-modal, sql, hybrid, filter]
aliases: [Cross-modal SQL, 多模 Join, 跨模态检索]
related: [hybrid-search, filter-aware-search, multimodal-retrieval-patterns, multimodal-embedding, vector-database, lancedb, milvus]
systems: [lancedb, milvus, qdrant, pgvector, elasticsearch, trino, spark, duckdb]
status: stable
---

# 跨模态查询

!!! tip "一句话定位"
    **一条 SQL 同时做结构化过滤 + 向量相似度 + 多模态检索**。湖仓一体化时代最有生产力的查询模式 —— 没有它 · 你要分别查三个系统（Meta 库 / 向量库 / 文本搜索）再在应用层 join。

!!! warning "和姊妹页的分工"
    - **本页**：**跨模态查询语义 + SQL 表达 + 执行模式**（Pre-filter / Post-filter / Filter-aware）· 跨模态 Join 独特语义
    - **[hybrid-search](hybrid-search.md)**：**稀疏 + 稠密混合** 检索（BM25 + dense）· 融合策略（RRF / CC / weighted）
    - **[filter-aware-search](filter-aware-search.md)**：**过滤感知的 ANN 索引构建** · HNSW / DiskANN 的 filter-aware 实现深度
    - **[multimodal-retrieval-patterns](multimodal-retrieval-patterns.md)**：**检索架构模式**（文本主线 vs 跨模态主线 · 6 种架构）· 本页是架构落地后的**查询表达**
    - **[multimodal-embedding](multimodal-embedding.md)**：embedding 模型 · 跨模态对齐原理

!!! abstract "TL;DR"
    - **典型查询**：一条 SQL 同时带 `WHERE`（结构化）+ `ORDER BY vec_distance(...)`（向量）+ 可能的 `LIKE`（文本）
    - **三种执行模式**：Pre-filter · Post-filter · **Filter-aware**（默认首选）
    - **跨模态 Join**：两表按"语义相似"join · 前提是 embedding 空间对齐
    - **引擎原生支持**：LanceDB · Milvus 2.4+ · Qdrant · pgvector（PG 优化器）
    - **需胶水**：Trino / Spark 通过 connector · DuckDB VSS 扩展
    - **关键陷阱**：不同空间向量不能直接 join · Post-filter 召回失效 · 分区剪枝必须配合

## 1. 一个真实场景

> 找出过去 7 天上传的、owner 是"设计部"、和这张图最相似、并且文字描述包含"秋冬"的图片，按相似度排序取 Top 20。

### 1.1 分裂架构下

```
1. 查元数据库（Postgres / Iceberg）拿"过去 7 天 + 设计部"的 asset_id 列表（5000 条）
2. 把 id 列表 IN 传给向量库（Milvus / Qdrant）做 ANN（5000 个候选）
3. 应用层 join 回元数据 · 拿 caption
4. 应用层过滤 caption LIKE '%秋冬%'
5. 排序 + 取 Top 20
```

**3 个系统 + 1 次手工 join + 多次网络往返**。任何一环慢或漏都定位困难。

### 1.2 一体化架构下

```sql
SELECT asset_id, raw_uri,
       vec_distance(clip_vec, :q_vec) AS sim
FROM multimodal_assets
WHERE owner = '设计部'
  AND ts > current_date - INTERVAL 7 DAY
  AND caption LIKE '%秋冬%'
ORDER BY sim
LIMIT 20;
```

引擎负责：谓词下推 → 向量索引检索 → 合并 → 排序 → 返回。

## 2. 跨模态查询的前提

跨模态查询的顺畅度 = **三件事对齐程度**：

1. **表里同时有结构化列 + 向量列 + 元数据**（参考 [unified/multimodal-data-modeling](../unified/multimodal-data-modeling.md)）
2. **引擎认识向量列与距离函数**（`vec_distance`、`<=>`、`<->`、`ANN_QUERY` 等）
3. **索引让"过滤先行"**（filter-aware ANN 或 pre-filter）

## 3. 三种执行模式

### 3.1 模式 A · Pre-filter + ANN

先用 `WHERE` 缩小候选 · 再在候选里跑 ANN。

```
query → 谓词下推（结构化过滤）→ 候选集 → ANN on 候选 → 排序
```

- **适合**：过滤条件选择度**高**（如 `tenant_id = 123` 过滤到 1%）
- **坑**：过滤后样本 < K 时 ANN 召回失效 · 要 fallback（扩大候选或直接线性扫）
- **代表**：pgvector（PG 优化器）· Elastic Vector

### 3.2 模式 B · ANN + Post-filter

先 ANN 召回 Top-N · 再应用过滤。

```
query → ANN（全索引）→ Top-N → 应用 WHERE 过滤 → Top-K（≤ N）
```

- **适合**：过滤条件选择度**低**（如 `lang = 'zh'` 占 90%）
- **坑**：严格过滤下命中的有效结果太少 · 需要把 N 调很大（10×K 甚至更多）
- **代表**：早期向量库默认 · FAISS 原始用法

### 3.3 模式 C · Filter-aware ANN

图搜索 / 倒排遍历时**原生考虑过滤条件**。

```
query → filter-aware ANN（遍历时即时过滤）→ Top-K
```

- **代表**：Qdrant · Milvus Iterative Filter · LanceDB · Weaviate · Turbopuffer
- **优点**：同时兼顾 recall 与正确性 · 自适应过滤选择度
- **代价**：索引构建时需额外元数据标注 · 工程复杂度高

**默认首选模式 C** · 无法实现时按过滤选择度在 A / B 间选。深度机制见 [filter-aware-search](filter-aware-search.md)。

### 3.4 三模式对比表

| 模式 | 延迟 | 召回 | 选择度适应 | 索引要求 | 典型用例 |
|---|---|---|---|---|---|
| Pre-filter | 看过滤后规模 | 可能过低（样本不足） | 高选择度最佳 | 普通 ANN + 标量索引 | tenant_id 过滤 |
| Post-filter | 看 N 多大 | 低选择度最佳 | 低选择度最佳 | 普通 ANN | 语言 / 类型过滤 |
| **Filter-aware** | **自适应** | **最稳定** | **适应所有** | **专用索引构建** | **通用生产首选** |

## 4. 引擎侧原生支持 · 2026 现状

### 4.1 一等公民支持

| 引擎 | 跨模态查询能力 |
|---|---|
| **LanceDB** | `table.search(q).where("...").limit(K)` 组合过滤 + 向量 · filter-aware ANN |
| **Milvus 2.4+** | 向量 + 标量过滤 + sparse 混合 · Iterative Filter |
| **Qdrant** | **filter-aware HNSW** · 过滤条件嵌入图搜索 · 性能领先 |
| **Weaviate** | Class + property 过滤 + 向量 · GraphQL 接口 |
| **pgvector 0.8+** | PG 优化器把 `WHERE` 和向量查询合并 · 和 PG 生态一体 |
| **Elasticsearch 8+** | BM25 + dense + filter 混合 · `knn_search` + `query` |
| **Turbopuffer** | 2024 起 · 自研 filter-aware · S3 原生 |

### 4.2 需胶水 / 扩展

| 引擎 | 情况 |
|---|---|
| **Trino** | 通过 LanceDB connector（实验）或 Milvus connector · SQL 层支持有限 |
| **Spark** | LanceDB Spark source · Iceberg + Puffin 的向量查询在演进 |
| **DuckDB** | **VSS 扩展**支持简单 ANN · 适合本地开发 / 小规模 |
| **ClickHouse** | 2024 起加 vector index · 仍在完善 |
| **StarRocks / Doris** | 2024 起陆续加向量索引 |

## 5. 向量距离函数 · 不同引擎的方言

**跨引擎 portability 差** · 函数名各家不同：

| 引擎 | 余弦距离函数 | L2 距离函数 | 内积函数 |
|---|---|---|---|
| pgvector | `<=>` 运算符 | `<->` | `<#>` |
| Milvus | `COSINE` · `L2` · `IP` metric | 同 | 同 |
| LanceDB | `vec_distance(...)` | 同 | 同 |
| DuckDB VSS | `array_cosine_similarity` | `array_distance` | — |
| ClickHouse | `cosineDistance` | `L2Distance` | `dotProduct` |
| Elastic | `cosine` · `l2_norm` · `dot_product` | 同 | 同 |

**工程建议**：
- 单引擎绑定时用原生函数
- 跨引擎（业务层抽象）时定义统一 wrapper
- 不指望"SQL 标准"有跨模态查询（SQL 2023 仍未标准化向量）

## 6. 跨模态 Join · 更进一步

两个表按"语义相似"join：

```sql
-- 找每张图对应的最相关的一段文档
SELECT i.asset_id, d.doc_id, vec_distance(i.clip_vec, d.text_vec) AS sim
FROM images i
CROSS JOIN LATERAL (
  SELECT doc_id, text_vec
  FROM docs
  ORDER BY vec_distance(i.clip_vec, text_vec)
  LIMIT 5
) d;
```

### 6.1 语义 Join 的前提

**只有在 embedding 空间对齐时有意义**：
- **CLIP / SigLIP 的文图空间**可以跨 join（两端都是对齐的跨模态空间）
- **BGE / e5 的纯文空间** 和 CLIP 的图空间**不能直接跨 join**（向量空间根本不同）
- **Voyage multimodal / Cohere multimodal**（2024-2026 新）也支持跨模

### 6.2 常见错误

- ❌ 把 BGE 文向量和 CLIP 图向量直接 cosine · 结果随机 · 看起来"工作"但没有语义
- ✅ 两端用 **同一模型或同一跨模对齐家族**

### 6.3 语义 Join 的用例

- **图-文检索**：用图查对应文档
- **视频-字幕对齐**：视频帧 embedding 和字幕 embedding 匹配
- **推荐系统**：用户最近浏览 item → 推相似 item
- **多模 RAG**：用图片搜相关段落 · 详见 [ai-workloads/rag](../ai-workloads/rag.md)

## 7. 性能要点

### 7.1 过滤前置的价值

- **向量查询的代价是"扫索引"而非"扫行"** · 所以过滤**之前**能多裁多少决定速度
- **分区剪枝**必须配合 · 没分区的跨模态查询会扫全表索引

### 7.2 Top-K 选择

- **K 最好明确**：K 大意味着索引访问更多邻居
- 常见陷阱：K = 1000 但实际业务只需要 Top 10 · 浪费巨大

### 7.3 语义缓存

- Query embedding 计算耗时 · 热门查询应缓存
- 详见 [ai-workloads/semantic-cache](../ai-workloads/semantic-cache.md)

### 7.4 ORDER BY 向量距离 + 其他列

- `ORDER BY vec_distance(...), created_at DESC LIMIT 20` —— 多数引擎优化器在这种组合下**规划能力有限**
- **建议**：先测性能 · 必要时分步（先向量取 Top 100 · 再 app 层二次排序）

## 8. 混合检索 · BM25 + Vector（和 hybrid-search 协同）

实际生产里跨模态查询经常伴随**混合检索**：
- BM25（关键词精确匹配）+ Dense vector（语义相似）
- 融合策略：RRF / CC / weighted fusion
- 详见 [hybrid-search](hybrid-search.md)

**结合跨模态查询**：
```sql
SELECT asset_id, raw_uri,
       0.5 * bm25_score(caption, :keywords)
     + 0.5 * vec_similarity(clip_vec, :q_vec) AS hybrid_score
FROM multimodal_assets
WHERE owner = '设计部'
ORDER BY hybrid_score DESC
LIMIT 20;
```

## 9. 陷阱 · 反模式

- **把不同空间的向量当同一空间**：CLIP 图向量 和 BGE 文向量**不可直接比**
- **Post-filter 召回坑**：把 Top-100 过滤后只剩 3 个还觉得"召回太差"
- **ORDER BY 向量 + 其他列**：优化器规划能力有限 · 先测再用
- **跨引擎 portability**：向量距离函数名各家不同 · 业务层抽象
- **分区剪枝忘配**：跨模态查询扫全表索引
- **K 设太大**：业务只要 10 · 索引访问 1000 个邻居
- **语义缓存不做**：query embedding 重复计算
- **Filter-aware 索引构建忽略元数据更新**：标签变了但索引没感知 · 召回失效
- **一条 SQL 包所有模态**：CLIP 的向量空间和 BGE 的不能同查 · 分 column 分语义

## 10. 相关

- [Hybrid Search](hybrid-search.md) —— 稀疏 + 稠密混合
- [Filter-aware Search](filter-aware-search.md) —— ANN 过滤感知索引
- [多模检索架构模式](multimodal-retrieval-patterns.md) —— 架构层
- [多模 Embedding](multimodal-embedding.md) —— 模型层
- [向量数据库](vector-database.md) —— 引擎概览
- [多模检索流水线](../scenarios/multimodal-search-pipeline.md) —— 场景端到端
- [Lake + Vector 融合架构](../unified/lake-plus-vector.md) —— 存储侧架构

## 11. 延伸阅读

- LanceDB SQL + Vector 教程
- Milvus Hybrid Query 文档
- Qdrant filter-aware HNSW paper / 博客
- pgvector 0.8 发布说明（PG 优化器集成）
- *ColBERT + filters in vector DB*（社区博客系列）
