---
title: 跨模态查询
type: concept
tags: [unified, multimodal, sql]
aliases: [Cross-modal SQL, 多模 Join]
related: [lake-plus-vector, multimodal-data-modeling, multimodal-embedding, hybrid-search]
systems: [iceberg, lancedb, milvus]
status: stable
---

# 跨模态查询

!!! tip "一句话理解"
    一条 SQL 同时涉及**结构化过滤 + 向量相似度 + 多模态**。湖仓一体化的价值在这类查询上最明显 —— 没有它，你得分别查三个系统再应用层 join。

## 一个真实场景

> 找出过去 7 天上传的、owner 是"设计部"、和这张图最相似、并且文字描述包含"秋冬"的图片，按相似度排序取 Top 20。

在**分裂架构**下你要：

1. 先查元数据库拿"过去 7 天 + 设计部"的 id 列表
2. 把 id 列表传给向量库做 ANN（大 IN 查询）
3. 再过滤文字描述
4. 应用层 join、排序

**3 个系统 + 1 次手工 join**。任何一个环节慢或漏都搞得定位困难。

在**一体化**下一条 SQL：

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

## 能做到这种查询的前提

跨模态查询的顺畅度 = **三件事对齐程度**：

1. **表里同时有结构化列 + 向量列 + 元数据**（参考 [多模数据建模](multimodal-data-modeling.md)）
2. **引擎认识向量列与距离函数**（`vec_distance`、`<=>`、`ANN_QUERY` 等）
3. **索引让"过滤先行"**（filter-aware ANN 或 pre-filter）

## 引擎侧现状

### 原生跨模态查询

- **LanceDB** —— 一等公民，`table.search(q).where("...").limit(K)` 组合过滤 + 向量
- **Milvus 2.4+** —— 支持向量 + 标量过滤 + sparse 混合
- **Qdrant** —— filter-aware HNSW，过滤条件嵌入图搜索
- **pgvector** —— PG 优化器把 `WHERE` 和向量查询合并

### 需要外挂胶水的

- **Trino** —— 通过 LanceDB connector（实验）或 Milvus connector
- **Spark** —— LanceDB Spark source；Iceberg + Puffin 的向量查询在演进
- **DuckDB** —— VSS 扩展支持简单 ANN，但生态新

## 查询模式三种

### 模式 A：Pre-filter + ANN

先用 `WHERE` 缩小候选，再在候选里跑 ANN。

- **适合**：过滤条件选择度高（如 tenant_id、日期范围）
- **坑**：过滤后样本 <K 时 ANN 召回失效；要 fallback

### 模式 B：ANN + Post-filter

先 ANN 召回 Top-N，再应用过滤。

- **适合**：过滤条件选择度低（如 `lang = 'zh'` 占 90%）
- **坑**：严格过滤下命中的有效结果太少

### 模式 C：Filter-aware ANN

图搜索 / 倒排遍历时原生考虑过滤条件。

- **代表**：Qdrant、Milvus Iterative Filter、LanceDB
- **优点**：同时兼顾 recall 与正确性
- **代价**：索引构建时需额外元数据标注

**默认首选模式 C**，无法实现时按过滤选择度选 A 或 B。

## 跨模态 Join

更进一步：两个表按"语义相似"join。

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

这种语义 join 只有在**多模 Embedding 空间对齐**时有意义（CLIP 的文图空间可以跨 join，BGE 的纯文空间和 CLIP 的图空间不能直接跨）。

## 性能要点

- **向量查询的代价是"扫索引"而非"扫行"**；所以过滤之前能多裁多少决定速度
- **Top-K 里的 K 最好明确**：K 大意味着索引访问更多邻居
- **分区剪枝**要配合；没分区的跨模态查询会扫全表索引
- **缓存语义重复**（见 [Semantic Cache](../ai-workloads/semantic-cache.md)）

## 陷阱

- **把不同空间的向量当同一空间**：CLIP 的图向量 和 BGE 的文向量**不可直接比**
- **Post-filter 坑**：把 Top-100 过滤后只剩 3 个还觉得"召回太差"
- **ORDER BY 向量距离 + 其他列**：多数引擎优化器在这种组合下规划能力有限，先测性能
- **跨引擎 portability**：向量距离函数名各家不同（`<->`, `vec_distance`, `l2_distance`）

## 相关

- [Lake + Vector 融合架构](lake-plus-vector.md)
- [多模数据建模](multimodal-data-modeling.md)
- [Hybrid Search](../retrieval/hybrid-search.md)
- 场景：[多模检索流水线](../scenarios/multimodal-search-pipeline.md)

## 延伸阅读

- LanceDB SQL + Vector 教程
- Milvus Hybrid Query 文档
- *ColBERT + filters in vector DB*（社区博客）
