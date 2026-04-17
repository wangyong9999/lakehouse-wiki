---
title: FAQ · 常见问题速答
description: 跨目录的具体问题与速答
---

# FAQ · 常见问题速答

跨越多个目录的真实问题集中在这里。每条都是"一句话答 + 深链到对应页"。

---

## 湖仓基础

### 湖表和数据库存储引擎到底有什么根本区别？

它们解决**不同的问题**：DB 是"把表藏在进程后"面向高频小事务；湖表是"把表摊在对象存储上"面向 PB 级分析和跨引擎开放。
→ [DB 引擎 vs 湖表](compare/db-engine-vs-lake-table.md)

### 湖仓上怎么做 ACID？

靠两件事：**Snapshot 隔离** + **原子指针切换**（HDFS rename / S3 conditional write / Catalog CAS）。
→ [湖表](lakehouse/lake-table.md) · [一致性模型](foundations/consistency-models.md)

### 我的查询明明 `WHERE` 了一个分区值，为什么还扫了 TB？

谓词没下推。99% 是以下原因之一：UDF 包住了过滤列 / 类型不匹配 / 数据本身没按该列聚集。
→ [谓词下推](foundations/predicate-pushdown.md) · [性能调优](ops/performance-tuning.md)

### 小文件问题怎么治？

核心是**定期 Compaction**。流式写入必须配合独立的 Compaction 作业，触发阈值通常是小文件数 > 10k 或 delta/base > 30%。
→ [Compaction](lakehouse/compaction.md)

### Schema 改了能保留历史数据吗？

能，前提是用支持 Schema Evolution 的湖表格式（Iceberg / Paimon / Delta）。底层靠**列 ID** 而不是列名映射数据。
→ [Schema Evolution](lakehouse/schema-evolution.md)

---

## 表格式选型

### Iceberg / Paimon / Hudi / Delta 到底选哪个？

- BI + 多引擎中立 → **Iceberg**
- 流式 CDC + upsert 主导 → **Paimon**
- Databricks 生态内 → **Delta**
- 不推荐从零开始选 **Hudi**（除非你已有 Spark 深度栈 + Incremental Query 强需求）

→ [四大表格式对比](compare/iceberg-vs-paimon-vs-hudi-vs-delta.md) · [ADR-0002](adr/0002-iceberg-as-primary-table-format.md)

### 我要流式 CDC 入湖又要 BI 批分析，能同一张表吗？

可以做，但**分开更健康**：Paimon Primary Key 表承担流式 upsert；下游聚合到 Iceberg 批表给 BI。
→ [Streaming Upsert / CDC](lakehouse/streaming-upsert-cdc.md) · [流式入湖](scenarios/streaming-ingestion.md)

---

## 多模与向量

### 我的向量规模 X，应该选哪个向量库？

- **< 千万 + PG 已在用** → pgvector
- **千万 – 亿，湖一体化** → LanceDB
- **千万 – 亿，强过滤** → Qdrant
- **亿 – 百亿** → Milvus
- **十亿 + SSD 成本敏感** → DiskANN（Milvus / Faiss 实现）

→ [向量数据库对比](compare/vector-db-comparison.md) · [ANN 索引对比](compare/ann-index-comparison.md)

### HNSW 和 IVF-PQ 怎么选？

- 内存够 + 要高召回 → HNSW
- 内存紧 + 规模大 → IVF-PQ
- 磁盘友好 → DiskANN

→ [ANN 索引对比](compare/ann-index-comparison.md)

### 一张表我要存几种 embedding，怎么建？

**一列一种**。用 frontmatter / 字段名区分 `clip_vec` / `text_vec` / `audio_vec`，每列独立建索引。**不要**把不同模型 / 不同空间的向量塞一列。
→ [多模数据建模](unified/multimodal-data-modeling.md)

### Embedding 模型换代怎么办？

加一列新 embedding，旧列保留。批任务回填历史；双索引 A/B；稳定后切流量，老列保留 N 天再删。**永远不要覆盖旧向量列**。
→ [Embedding 流水线](ai-workloads/embedding-pipelines.md)

### 纯向量检索召回不好，怎么办？

几乎一定要加 **[Hybrid Search](retrieval/hybrid-search.md)**（dense + BM25 / SPLADE）+ **[Rerank](retrieval/rerank.md)**。"召回 100 → 精排 10" 是实用起点。

### 怎么量化我的检索好不好？

构造 **golden set**（≥ 100 条 query + 相关文档标注），算 **Recall@K / MRR / nDCG**。把指标接进 CI / 上线流程。
→ [检索评估](retrieval/evaluation.md)

---

## AI 负载

### RAG 答错怎么排查？

按顺序：

1. 召回有没有把相关文档拿回来？（看 Recall）
2. Rerank 有没有把对的排前面？
3. Prompt 有没有明确约束"只基于材料答"？
4. 模型本身能力？

→ [RAG](ai-workloads/rag.md)

### LLM 调用太贵，怎么降本？

- **Semantic Cache** 接到前面
- 简单问题走小模型
- **Rerank + 短 context** 替代"Top 20 全喂"
- 批处理 / 异步

→ [Semantic Cache](ai-workloads/semantic-cache.md)

### Train-serve skew 怎么避免？

上 **Feature Store**，同一份特征定义离线在线共用 + **Point-in-Time Join**。
→ [Feature Store](ai-workloads/feature-store.md) · [离线训练数据流水线](scenarios/offline-training-pipeline.md)

---

## BI 负载

### 仪表盘 p95 > 5 秒，怎么优化？

按顺序排查：

1. **扫了多少字节**（看计划）——远超预期就改数据布局
2. 加分区 / 排序 / Z-order
3. 建物化视图
4. 还不够 → 引入加速副本（StarRocks / ClickHouse）

→ [性能调优](ops/performance-tuning.md) · [查询加速](bi-workloads/query-acceleration.md) · [物化视图](bi-workloads/materialized-view.md)

### 数仓分层应该几层？

ODS / DWD / DWS / ADS 四层是实用默认：业务库 CDC → 宽表 → 汇总 → 面向 BI 的集市。
→ [OLAP 建模](bi-workloads/olap-modeling.md)

### 星型还是宽表？

湖仓时代**默认宽表**（列式 + 列剪裁），除非维度变化极频繁。
→ [OLAP 建模](bi-workloads/olap-modeling.md)

---

## 运维与治理

### 对象存储凭证怎么管最安全？

不下发长期 key。Catalog 颁发**短时 STS token**（15–60min），最小权限。
→ [安全与权限](ops/security-permissions.md)

### Snapshot 保留多久？

默认 5–7 天够大多数场景；审计 / 合规场景至少 90 天。别忘了也给关键事件打 **tag**，tag 不会被 expire。
→ [Time Travel](lakehouse/time-travel.md)

### 账单涨得太快怎么查?

三个地方看：**存储 / 计算 / 对象存储 API 调用**。前两个常见；第三个是小文件 / 频繁 LIST 的隐形坑。
→ [成本优化](ops/cost-optimization.md)

### 治理要一步到位吗？

不要。按：owner → tag → 质量规则 → 血缘 → 契约顺序来。半年到一年搭建一个最小可用治理平面。
→ [数据治理](ops/data-governance.md)

---

## 一体化架构

### 为什么要把 BI 和 AI 跑在同一个湖上？

数据在湖，同一份数据既是 BI 事实表也是 AI 训练语料；分裂架构意味着双写和不一致。一体化路线的核心动机就在这里。
→ [Lake + Vector 融合架构](unified/lake-plus-vector.md)

### 一体化三条范式怎么选？

- 已有 Iceberg，规模中等 → **Puffin** 下沉（等协议更稳定）
- 多模 + ML 重 → **Lance / LanceDB**
- 已有 Milvus / Qdrant → **Catalog 统一**（Unity / Polaris）

→ [Lake + Vector 融合架构](unified/lake-plus-vector.md) · [ADR-0003](adr/0003-lancedb-for-multimodal-vectors.md)

### 跨模态 SQL 真能写吗？

LanceDB / Milvus 2.4+ 已支持。Trino / Spark 通过 connector 或自定义 UDF 也在进化。
→ [跨模态查询](unified/cross-modal-queries.md)

---

!!! note "找不到你想问的？"
    在 [Issue 区](https://github.com/wangyong9999/lakehouse-wiki/issues/new/choose)用 "勘误 / 内容修订" 模板提一条，或直接 PR 补充到本页。
