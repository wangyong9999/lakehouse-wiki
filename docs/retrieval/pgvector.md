---
title: pgvector · PostgreSQL 向量扩展
type: system
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: pgvector 0.7+ / 0.8+（2024-2026 主流）· PostgreSQL 13+
tags: [retrieval, vector, postgres, extension]
category: vector-db
repo: https://github.com/pgvector/pgvector
license: PostgreSQL License
status: stable
---

# pgvector · PostgreSQL 向量扩展

!!! tip "一句话定位"
    **PostgreSQL 扩展** · 让 PG 原生支持 `vector` 类型 + ANN 索引。规模小、结构化主导的场景下 · 它是"**把向量塞进已有 PG**"的最小成本路径。**一个扩展 + 一条 SQL** · 结构化 + 向量就在同一个事务里。

!!! abstract "TL;DR"
    - **甜区**：向量规模 < 千万 · 已有 PG 主数据 · 需要向量 + 事务强一致
    - **核心差异化**：**在 OLTP 栈里做向量** · 和业务表一个事务
    - **2024-2026 进展**：0.5+ HNSW · 0.6+ halfvec / sparsevec · 0.7+ filter + parallel scan 组合显著改善 · 0.8 持续优化
    - **类型矩阵**：`vector` / `halfvec`（FP16）/ `sparsevec`（稀疏）/ `bit`（Binary Quantization 基础）
    - **上限**：单机 PG 瓶颈决定规模上限 · QPS 高需读副本 / 分库 · 超过 → 独立向量库

## 1. 它解决什么

很多团队的主数据库已经是 Postgres · 业务又有"一点点"向量需求（产品相似推荐 / 用户画像匹配）。**引入一整套 Milvus / Qdrant 太重**。pgvector：

```sql
-- 1. 启用扩展
CREATE EXTENSION vector;

-- 2. 表里加向量列
CREATE TABLE documents (
  id BIGSERIAL PRIMARY KEY,
  tenant_id INT,
  title TEXT,
  embedding vector(768)
);

-- 3. 建索引
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 4. 查询 · SQL 原生
SELECT id, title
FROM documents
WHERE tenant_id = 42
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 10;
```

**一个扩展 + 几条 SQL** · 结构化 + 向量就在同一个事务里。

## 2. 关键能力

### 类型矩阵（2026-Q2）

| 类型 | 说明 | 维度 | 存储 |
|---|---|---|---|
| **vector(N)** | 基础 FP32 向量 | N | 4N bytes |
| **halfvec(N)** | FP16 半精度向量 | N | 2N bytes · 2× 压缩 |
| **sparsevec(N)** | 稀疏向量（非零位置 + 值）| N | 非零数 × 8 bytes |
| **bit(N)** | 二进制向量 | N | N/8 bytes · 32× 压缩 · 用 hamming distance |

**Binary Quantization 在 pgvector**：用 `bit` 类型 + hamming distance · 配合 rerank 二阶段 · 详见 [Quantization](quantization.md)。

### 距离函数

- `<->` (L2 Euclidean)
- `<#>` (Negative Inner Product)
- `<=>` (Cosine Distance)
- `<+>` (L1 · 0.7+)
- `<~>` (Hamming · for bit vectors)

### 索引类型

| 索引 | 适合 | 内存 | 备注 |
|---|---|---|---|
| **HNSW**（0.5.0+）| 精度高 · 延迟低 | **大**（~2× 原数据）| 生产默认 |
| **IVF-Flat** | 省内存 · 需 nlist 训练 | 中 | 超大规模 / 内存紧 |

### 和 PG 原生生态结合

- **JOIN** · 向量检索和结构化表 JOIN 一条 SQL
- **外键** · 引用完整性约束
- **事务** · ACID 一条事务里改向量 + 元数据
- **索引扫描合并** · 部分场景把 WHERE 下推到向量索引（详见 §3）

## 3. 2024-2026 关键进展 · Filter-aware 突破

**历史痛点**：`WHERE tenant_id = X ORDER BY embedding <-> q LIMIT 10` 类型的 **filter + vector** 查询 · 老版本 pgvector 要么 pre-filter（过滤后 HNSW 失准）要么 post-filter（扩大 K 召回）· 效果差。

**0.6-0.7+ 突破**：

- **hnsw.ef_search** 参数 + **parallel sequential scan** 组合
- filter 选择性**自动评估** · 高选择性走 seq scan + ANN · 中选择性 HNSW filter-aware
- **结果**：接近 Qdrant / Milvus 的 filter-aware 精度（见 [filter-aware-search](filter-aware-search.md)）

**典型配置**（大 PG 表场景）：

```sql
-- Session 级调参
SET hnsw.ef_search = 100;
SET max_parallel_workers_per_gather = 4;

SELECT id, title
FROM documents
WHERE tenant_id = 42  -- 选择性 10% · 走 filter-aware
ORDER BY embedding <=> '[...]'
LIMIT 10;
```

## 4. 生产调优

### 内存和索引大小

**HNSW 构建** 内存估算：

- 1 千万向量 × 768 维 × float32 = 30 GB 原始数据
- HNSW 索引约 2× 原始 = 60 GB
- PG `maintenance_work_mem` 至少需要**索引大小的 1.5-2 倍**才能一次建完
- 超出则 temp files → 磁盘 IO 拖慢数十倍

**调参**：

```sql
-- 构建 HNSW 前临时调大
SET maintenance_work_mem = '32GB';
SET max_parallel_maintenance_workers = 4;
CREATE INDEX ... USING hnsw ...;
```

### shared_buffers 与 work_mem

- **shared_buffers**：PG 建议 25% 总内存 · 向量重度场景可到 40%
- **work_mem**：查询时每个 sort/hash 算子的内存 · 向量查询建议 64MB-256MB

### 连接池

- **向量查询 CPU 消耗大** · 连接数控制必要
- **pgbouncer** 作为前置连接池 · 避免 PG 进程爆炸
- 典型：`max_connections = 100` + pgbouncer pool_size = 500

### 读副本扩展 QPS

- **QPS > 单机上限**：加读副本
- 主写 + 多读副本架构
- 向量索引在主写完成后**同步到副本**
- 注意：副本有**复制延迟**（通常 < 1s）· 强一致性场景走主

## 5. 和其他选手的定位

| 维度 | pgvector | Milvus | LanceDB | Qdrant |
|---|---|---|---|---|
| **形态** | PG 扩展 | 分布式集群 | 嵌入式 + Cloud | 独立服务 |
| **规模甜区** | 百万-千万 | 亿-百亿 | 千万-亿 | 千万-亿 |
| **事务语义** | ✅ 完整 ACID | ❌ 最终一致 | ⚠️ snapshot | ⚠️ 最终一致 |
| **结构化 + 向量** | ✅ 最强（SQL 原生）| ⚠️ 需扁平化 | ✅ 同表 | ⚠️ payload JSON |
| **运维** | 零（在 PG 栈内）| 重 | 轻 | 中 |
| **Filter-aware** | ✅ 0.7+ 显著改善 | ✅ Filtered Search | ✅ 原生 | ✅ 最强 |

## 6. 迁出策略 · 超过 pgvector 上限后怎么办

**信号**（该考虑迁出）：
- 规模超千万向量 · HNSW 构建内存 hold 不住
- QPS > 数千 · 读副本也扛不住
- 需要多节点分布式（pgvector 本质单机）

**迁出路径**（非破坏性 · 双写过渡）：

```
Phase 1: 主读 pgvector · 影子写 Milvus
  ↓ 用流量对比验证 Milvus 结果和 pgvector 一致
Phase 2: 主读 Milvus · pgvector 作为 fallback
  ↓ 确认稳定
Phase 3: 下线 pgvector 向量列 · 保留结构化列
```

## 7. 什么时候选 / 不选

**选 pgvector**：

- **向量规模 < 千万**（HNSW 内存预算可控）· 或 < 百万用 ivfflat
- **已经在 PG 上跑主数据**
- **向量 + 事务强一致**（一条事务里改 user 属性 + 重算 embedding）
- **运维团队熟 PG** · 不想多学一套系统
- 结构化和向量**强耦合**的查询多

**不选 pgvector**：

- 规模 > 千万且**只有向量** → 独立向量库（[Milvus](milvus.md) / [Qdrant](qdrant.md)）
- 需要**湖原生** + 多模 → [LanceDB](lancedb.md)
- 需要百亿级**分布式** → [Milvus](milvus.md)
- 想用 **GPU 索引** → pgvector 不支持

## 8. 陷阱

- **HNSW 构建内存不够** · 索引生成几小时变几十小时 · 失败还要重来
- **索引大小估算失误** · HNSW 索引可能比原数据还大 · 磁盘 + shared_buffers 双重预算
- **单机 PG 瓶颈没法靠 pgvector 自己扩** · 必须走读副本 / 分库
- **连接池 + 向量查询** · CPU 消耗大 · 不配 pgbouncer 高并发炸连接
- **忘记升级到 0.7+** · filter-aware 改善在 0.7+ · 老版本效果差
- **HNSW 索引的 in-memory 要求** · PG 重启后索引需要重新加载到内存

## 9. 相关

- [向量数据库](vector-database.md) · 通用定位
- [HNSW](hnsw.md) · [IVF-PQ](ivf-pq.md) · [Quantization](quantization.md) · 索引和量化
- [Filter-aware ANN](filter-aware-search.md) · pgvector 0.7+ 的显著改善
- [Milvus](milvus.md) · 迁出的主要目标
- [向量数据库对比](../compare/vector-db-comparison.md) · 详细横比

## 10. 延伸阅读

- **[pgvector README](https://github.com/pgvector/pgvector)**
- **[*Scaling pgvector to 1 Billion Embeddings*](https://supabase.com/blog/pgvector-performance)** · Supabase 博客
- **[Neon pgvector 性能调优](https://neon.tech/blog/pgvector-tuning)**
- **[pgvector 0.7 Release Notes](https://github.com/pgvector/pgvector/releases)**
