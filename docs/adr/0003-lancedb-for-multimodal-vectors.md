---
title: 0003 多模向量存储选 LanceDB（辅以 Milvus）
type: adr
status: accepted
date: 2026-04-17
deciders: [wangyong9999]
---

# 0003. 多模向量存储选 LanceDB（辅以 Milvus）

## 背景

团队的一体化湖仓路线要求**向量数据和湖表共生**，不想长期维护两套存储。主要候选：

- LanceDB（嵌入式、湖原生）
- Milvus（分布式、独立服务）
- Qdrant（Rust、强过滤）
- Weaviate（Module 生态丰富）
- pgvector（PG 扩展）
- Iceberg + Puffin（实验中，靠 Puffin blob 存向量索引）

各自适用面见 [向量数据库对比](../compare/vector-db-comparison.md)。

## 决策

**多模场景主用 LanceDB；大规模 / 高 QPS 在线检索辅以 Milvus**。

- **多模资产表 + 训练用向量表** —— LanceDB（数据和索引都在湖上，Lance format）
- **在线 RAG / 高并发毫秒级检索**（预计 > 1000 QPS） —— Milvus 集群
- 中小规模 / PG 共存场景 —— pgvector 作为最小成本路径

## 依据

### 为什么 LanceDB 是主角

1. **湖原生** —— 数据以 Lance 格式直接落对象存储，和 Iceberg / Parquet 在同一个 bucket；**没有"向量库和湖两份数据"的同步痛点**
2. **多模原生** —— 二进制字段 + 向量列 + 元数据一表处理，天然适合我们的 `multimodal_assets` 表设计
3. **嵌入式** —— 没有独立集群要运维；任何 Spark / Python / Ray 作业都能直接读
4. **Lance format** —— 随机访问友好，训练时打乱洗牌成本低
5. **和 Iceberg 可共生** —— 路线图指向 "一张 Iceberg 表能被 LanceDB 当向量表读"
6. **开源 + 商业支持** —— OSS 加 LanceDB Cloud 托管，不绑死

### 为什么 Milvus 是备选

LanceDB 的嵌入式形态在**极高并发 + 严苛 p99 延迟**下需要自己做服务化包装。Milvus 天生分布式、集群成熟，亿级以上向量 + 千 QPS 以上场景仍是它的主场。

在线 RAG / 多模检索服务预期会到这个规模，提前留好迁移路径。

### 为什么不 Qdrant / Weaviate

- **Qdrant** —— Filter-aware 很强，但湖仓集成不是主线。如果未来某场景需要极强过滤，单独引入不排斥
- **Weaviate** —— Module 生态适合快速原型但数据 / 模型绑定较深，不适合长期事实源

### 为什么暂不主推 Iceberg + Puffin

路线上最终会到这里，但当前状态：
- Puffin 向量索引 blob 类型在社区化进展中，**协议未稳定**
- 生产级引擎支持（Trino / Spark 读 Puffin 向量索引）仍需等待
- LanceDB 今天能完成同样的诉求

计划 12 个月后重新评估切换。

### 为什么不 pgvector

对**小规模 + 结构化主导**场景依旧推荐，但不适合多模主线（PG 不是对象存储原生、二进制资产管理弱）。

## 后果

**正面**：

- 一体化架构顺畅落地：多模 asset 表即向量表
- 运维成本低（LanceDB 无服务端）
- 和湖表 Catalog 统一：Unity / Polaris 能把 Lance 表纳入
- Embedding 流水线输出直接是 Lance 表，零搬运

**负面**：

- LanceDB 生态较新，踩坑风险比 Milvus 高
- 未来到大规模时需要迁移到 Milvus 或等 Puffin
- 团队要同时熟悉 Lance format 与 Parquet

**后续**：

- 建立 `multimodal_assets` 表的标准 schema（已在 [多模数据建模](../unified/multimodal-data-modeling.md)）
- Embedding 流水线首选 LanceDB sink
- 12 个月后重新评估 Puffin 成熟度
- 如果线上 QPS 增长至 1000+，启用 Milvus 集群并建立同步

## 相关

- [向量数据库对比](../compare/vector-db-comparison.md)
- [LanceDB](../retrieval/lancedb.md) / [Milvus](../retrieval/milvus.md)
- [Lake + Vector 融合架构](../unified/lake-plus-vector.md)
- 上一条：[ADR-0002 选择 Iceberg](0002-iceberg-as-primary-table-format.md)
