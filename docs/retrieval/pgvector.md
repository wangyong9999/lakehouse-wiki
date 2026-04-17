---
title: pgvector
type: system
tags: [retrieval, vector, postgres]
category: vector-db
repo: https://github.com/pgvector/pgvector
license: PostgreSQL License
status: stable
---

# pgvector

!!! tip "一句话定位"
    **PostgreSQL 扩展**，让 PG 原生支持 `vector` 类型 + ANN 索引。规模小、结构化主导的场景下，它是"**把向量塞进已有 PG**"的最小成本路径。

## 它解决什么

很多团队的主数据库已经是 Postgres，业务又有"一点点"向量需求（产品相似推荐、用户画像匹配）。引入一整套 Milvus / Qdrant 太重。pgvector：

- `CREATE EXTENSION vector;`
- 表里加 `embedding vector(768)` 一列
- 建索引 `CREATE INDEX ... USING hnsw (embedding vector_l2_ops)`
- SQL 原生查 `ORDER BY embedding <-> '[...]' LIMIT 10`

**一个扩展 + 一条 SQL**，结构化 + 向量就在同一个事务里。

## 关键能力

- **类型**：`vector`、`halfvec`（半精度）、`sparsevec`
- **距离**：`<->` (L2)、`<#>` (inner product)、`<=>` (cosine)
- **索引**：
    - **HNSW**（0.5.0+）—— 精度高、内存大
    - **IVF-Flat** —— 省内存、需要训练
- **结合 PG 原生**：JOIN、外键、事务、索引扫描合并都能用

## 典型查询

```sql
SELECT id, title
FROM documents
WHERE tenant_id = 42
  AND lang = 'zh'
ORDER BY embedding <=> $1
LIMIT 10;
```

PG 优化器**能把 `WHERE` 条件下推到索引**（部分场景下），真·pre-filter。

## 什么时候选

- **向量规模 < 千万**（HNSW 内存预算可控）
- 已经在 PG 上跑主数据
- 向量 + 事务一致性要求强（一条事务里改 user 属性 + 重算 embedding）
- 运维团队熟 PG，不想多学一套系统

## 什么时候不选

- 规模 > 千万且只有向量 → 独立向量库
- 需要"湖原生"（多模资产）→ LanceDB
- 需要百亿级分布式 → Milvus

## 陷阱

- **HNSW 构建内存**：千万向量级建索引时 PG 需要大量 `maintenance_work_mem`
- **索引大小**：HNSW 索引可能比原数据还大；磁盘与 shared_buffers 都要评估
- **单机 PG 瓶颈**：QPS 上不去时没法靠 pgvector 自己扩；要走读副本 / 分库
- **连接池 + 向量查询**：向量查询 CPU 消耗大，要用 pgbouncer + 连接数控制

## 和其他选手的定位

- **pgvector vs Milvus** —— pgvector 是"关系主、向量辅"；Milvus 是"向量主，结构化辅"
- **pgvector vs LanceDB** —— pgvector 小而稳；LanceDB 湖原生
- **pgvector vs Elasticsearch** —— ES 的 kNN 更偏 log/search 生态；pgvector 在 OLTP 生态

## 相关

- [向量数据库](vector-database.md)
- [向量数据库对比](../compare/vector-db-comparison.md)
- [HNSW](hnsw.md) / [IVF-PQ](ivf-pq.md)

## 延伸阅读

- pgvector README: <https://github.com/pgvector/pgvector>
- *Scaling pgvector to 1 Billion Embeddings* —— Supabase / Neon 等博客
