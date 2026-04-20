---
title: 数据处理与分析引擎
description: 湖仓之上做 SQL / 批 / 流 / 分析的三类引擎——纯查询引擎 · 通用处理框架 · MPP OLAP 数据库
last_reviewed: 2026-04-20
---

# 数据处理与分析引擎（章节里简称"查询引擎"）

!!! warning "读这一章前先分清三类 · 否则容易选错"
    **"查询引擎"是 umbrella term**——这一章实际覆盖 **3 类定位完全不同**的产品，混成一类看容易选错：

    ```
    纯查询引擎（联邦 SQL · 无自己存储）
      ├── Trino · 交互式 SQL 分析 / BI 前台
      └── DuckDB · 嵌入式 OLAP · 单机 / 开发态

    通用数据处理框架（SQL 只是 API 之一）
      ├── Apache Spark · 批 ETL + Structured Streaming + ML + SQL 多面手
      └── Apache Flink · 流优先 · DataStream + SQL · CDC 入湖主力

    MPP OLAP 数据库（有自己存储 · 也能读湖仓外表）
      ├── StarRocks · 独立 OLAP DB / 湖仓 BI 加速层
      ├── ClickHouse · 单表大扫描 + 高并发聚合极致
      └── Apache Doris · StarRocks 同源 · 湖仓融合方向投入大
    ```

    **每类的正确用法**：
    - **纯查询引擎**：零存储 · 秒级交互 · 跨多 Catalog 联邦；**不做 ETL / 不做流**
    - **通用处理框架**：跑任意数据流水线（ETL / 流 / ML）· **不是"只做查询"**；Spark/Flink 的首要职责是"处理"而不是"查询"
    - **MPP OLAP 数据库**：完整数据库（自己存储 + 执行 + Catalog）· 可独立运维 · 也可兼做湖仓加速层

!!! info "和 `retrieval/` 章节的边界 · 很多人会混"
    **"向量化执行"** ≠ **"向量检索"**——是两个完全不同的概念：

    | 术语 | 含义 | 所属章节 |
    |---|---|---|
    | **向量化执行** (Vectorized Execution) | SIMD · 列式批处理的 CPU 优化 · Parquet/ORC 扫描加速的底层 | 本章所有引擎（Trino/Spark/Flink/DuckDB/StarRocks/ClickHouse/Doris）都有 |
    | **向量检索** (Vector Search · ANN) | 高维 embedding 向量的相似度搜索 · HNSW/IVF-PQ/DiskANN 索引 | [多模检索](../retrieval/index.md) 章节 |

    ClickHouse / StarRocks / DuckDB / Doris 等 2024+ 加了**向量检索能力**——但那是**本章产品向"检索"侧延伸**，详细请看 [retrieval/](../retrieval/index.md)。本章以 **SQL / DataFrame / Streaming 数据流水线**为主轴，向量检索能力只做指针性提及。

## 产品页 · 按三类组织

### 纯查询引擎（联邦 SQL · 无自己存储）

- [Trino](trino.md) —— 交互式 SQL 联邦 · BI 前台 · 多 Catalog 跨源查询
- [DuckDB](duckdb.md) —— 嵌入式 OLAP · 单机分析 · 开发态 / notebook 利器

### 通用数据处理框架（SQL + 批 + 流 + ML）

- [Apache Spark](spark.md) —— 大数据时代最主流计算引擎 · 湖仓里主要跑批 ETL + 集市层
- [Apache Flink](flink.md) —— 有状态流处理事实标准 · 和 Paimon 组合是**准实时湖仓典型路线之一**（Spark Structured Streaming / Kafka + OLAP DB 仍是生产常见路径）

### MPP OLAP 数据库（自己存储 + 读湖）

- [StarRocks](starrocks.md) —— 现代 MPP 分析型数据库 · BI 加速首选（也可独立栈）
- [ClickHouse](clickhouse.md) —— 单表大扫描 + 高并发聚合极致 · 和 Trino/Spark 是不同物种
- [Apache Doris](doris.md) —— StarRocks 同源 · 湖仓融合方向 2024-2026 持续投入

## 多引擎组合打法 · 单引擎思维是陷阱

现代湖仓**很少单引擎打天下**。真实生产栈更常是"**一类用法对应一个引擎**"的组合：

| 组合 | 典型场景 | 分工 |
|---|---|---|
| **Spark + Trino** | 批 ETL + 交互查询分层 | Spark 跑 ETL 构建集市层 → Trino 对外提供 BI 查询 |
| **Flink + Paimon + Trino** | 准实时湖仓 | Flink 流入湖 → Paimon 表持续刷新 → Trino 做交互 BI |
| **Trino + StarRocks** | 交互式 BI 加速分层 | Trino 联邦多源 · StarRocks 对最热核心表做低延迟加速 |
| **DuckDB + Iceberg** | 本地 / 开发态 | 单机 DuckDB 直读 Iceberg · 不拉起集群 |
| **Spark + Databricks Photon + UC** | 托管一体栈 | Spark 处理 + Photon 加速 + UC 治理 · Databricks 生态闭环 |
| **Kafka + ClickHouse / Pinot / Druid** | 流式 OLAP（非湖仓路径）| 跳过湖表 · 直接 Kafka → OLAP DB · 毫秒级仪表盘 |

**核心取舍**：

- **Spark / Flink（处理框架）** 负责"**数据进 + 流水线**"——ETL 复杂 / 状态有状态 / ML 管道
- **Trino / DuckDB（纯查询引擎）** 负责"**联邦 + 交互**"——跨源查 / 秒级 ad-hoc
- **StarRocks / ClickHouse / Doris（MPP OLAP DB）** 负责"**加速 + 高并发**"——仪表盘 p95 / 数千 QPS

**不要一个引擎打通所有场景**——每类都在自己甜区才高效。

## 选型速览 · 4 步决策

!!! tip "先问自己 4 件事"
    **Step 1 · 要做什么？**

    - 交互式 BI / ad-hoc SQL → **Trino / StarRocks / ClickHouse**
    - 批 ETL / 构建集市层 → **Spark**
    - 流式 CDC 入湖 / 准实时 → **Flink + Paimon**
    - 本地开发 / 单机 / notebook → **DuckDB**

    **Step 2 · 有没有自己的存储需求？**

    - 要独立 OLAP DB（有自己表 + upsert + MV）→ **StarRocks / ClickHouse / Doris**
    - 只读湖仓表（不要数据落自己存储）→ **Trino / DuckDB / Spark / Flink**

    **Step 3 · 规模 + 并发？**

    - 亿行 / 百并发 BI → **StarRocks / ClickHouse**
    - 跨多数据源 federated → **Trino**
    - 万亿行批处理 → **Spark**
    - 单机 GB-TB → **DuckDB**

    **Step 4 · 湖表格式的匹配？**

    - Paimon 流读重度 → **Flink**（最佳集成）
    - Iceberg 读多引擎 → 基本都 OK · **Trino / Spark / StarRocks / DuckDB** 最成熟
    - Delta → **Spark + Databricks** 生态最深

## 相关

- **底座**：[湖仓表格式](../lakehouse/index.md) · [Catalog](../catalog/index.md)
- **场景**：[BI on Lake](../scenarios/bi-on-lake.md) · [流式入湖](../scenarios/streaming-ingestion.md)
- **相邻章节**：[多模检索](../retrieval/index.md)（向量 / ANN）· [数据管线](../pipelines/index.md)（ETL 流水线）
