---
title: ClickHouse · MPP OLAP 数据库
type: system
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: ClickHouse 25.x+（2025 末主流）· 湖读走 24.10+ iceberg()/s3() 表函数
tags: [query-engine, olap, columnar, mpp-database]
category: query-engine
repo: https://github.com/ClickHouse/ClickHouse
license: Apache-2.0
status: stable
---

# ClickHouse

!!! tip "一句话定位 · 不是查询引擎，是 MPP OLAP 数据库"
    **MPP OLAP 数据库**——**有自己的存储**（MergeTree 家族），不是 Trino/DuckDB 那种"纯查询引擎"。**单表大扫描 + 高并发聚合**场景几乎无对手。在湖仓里通常作为"BI 热数据加速层"或"事件分析专用引擎"——但**也完全可以独立部署**（有大量不碰湖仓的 ClickHouse 栈）。

!!! info "向量化 ≠ 向量检索 · 和 retrieval/ 章节的边界"
    ClickHouse 2024+ 加了**向量相似度函数**（`cosineDistance` / `L2Distance` 等）和**向量索引**（Annoy / HNSW）。这两件事不要混：

    - **"向量化执行"** = SIMD · 列式批处理 · 是 ClickHouse 本身的**性能基础**
    - **"向量检索"** = ANN 相似度搜索 · 是 ClickHouse **向检索侧的延伸**——详见 [多模检索](../retrieval/index.md)

    **但 ClickHouse 不是专业向量数据库**：百万到千万级向量可以用；亿级向量 + 高并发 ANN 走 [Milvus / LanceDB](../retrieval/vector-database.md)。

## 它解决什么

ClickHouse 在**"单个大事实表 + 高吞吐写 + 毫秒级聚合"** 的甜区无对手：

- 日志 / 埋点 / 监控时序
- 广告点击流 / 归因分析
- 实时运营看板
- 高并发（数千 QPS）的仪表盘 backend

缺点一样明显：多表 **join 能力较弱**（近年有改进但仍不是强项）。

## 架构（简）

- **MergeTree 家族**存储引擎 —— 类 LSM 但按分区 + 排序键组织
- **向量化执行 + SIMD + codegen**
- **稀疏索引**（非 B+Tree，按排序键的 granule 粒度）
- **Shard + Replica**：原生分布式，但相对去中心（没有"master"）

## 和湖仓的三种关系

### 模式 A：独立加速层（最常见）

ClickHouse 作为湖仓的**镜像**：

- Iceberg → 周期导出 Parquet → ClickHouse
- BI 仪表盘打 ClickHouse，延迟毫秒级
- 两份数据，但极低延迟值回票价

### 模式 B：直读 Parquet / Iceberg

ClickHouse 24.10+ 的 `iceberg()` / `s3()` 表函数能直接读湖上 Parquet 和 Iceberg 表：

- 不搬数据
- 延迟比模式 A 高（秒级）
- 架构更简单

### 模式 C：完全独立

一些团队对 ClickHouse 单独建数据流，不和湖仓对齐——这种更像"独立分析栈"而非湖仓组件。

## 关键能力（对湖仓场景有用的）

- **MergeTree + ReplacingMergeTree / SummingMergeTree / AggregatingMergeTree** —— 按键合并 / 预聚合
- **Projections** —— 同一表多种物化视图（自动选最优）
- **Dictionary** —— 外部维度表常驻内存 join
- **Kafka Engine** —— 流式入库
- **S3 / Iceberg / Delta / Hudi Table Functions** —— 直读
- **Async Insert** —— 高并发小批写入

## 什么时候选

- 日志 / 埋点 / 监控时序**单表查询为王**
- BI 高并发毫秒级延迟目标
- 数据量超出 Trino / DuckDB 的单机能力又不想上 Spark
- 愿意接受"多一份数据"的管理成本

## 什么时候不选

- 多表复杂 join 为主（选 Trino / Spark）
- ACID 强事务（它不是 DB）
- 写入模式高频 upsert（它不擅长）

## 现代能力边界 · "join 弱" 到底弱到什么程度

"ClickHouse join 弱" 是标签化说法 · 2024-2026 的现代 ClickHouse 能力边界要细看：

| 场景 | 当前 ClickHouse（25.x）的能力 |
|---|---|
| **小表 broadcast join** | ✅ 够用 · 小表几十 MB 内走 `joinAlgorithm='hash'` · 表现不错 |
| **Dictionary join**（维度表常驻内存） | ✅ **推荐路径** · 维度 < GB 级 · join 延迟接近单表 |
| **Projection 预聚合** | ✅ 同一表多种物化视图（自动选最优）· 减少 join 需求 |
| **两张大表 shuffle join** | ⚠️ 可以但**慢 + 资源消耗大** · 不是甜区 |
| **star schema 多表 join** | ⚠️ 3-5 表 OK · 超过后性能明显下滑 |
| **多级 join + 复杂 CTE** | ❌ 选 Trino / Spark / StarRocks |

**湖仓里的正确定位**：

- **镜像系统（加速层）** · 源数据在 Iceberg · ClickHouse 做高并发 BI 看板——常见且合理
- **热数仓（事件分析专用）** · 直接落 ClickHouse · Kafka engine 流式入库——甜区
- **直读外表**（Iceberg / Parquet 表函数）· 秒级延迟 · **只适合低频 / 探索**——别当仪表盘主路径

### 湖仓直读 vs 加速副本 · 和 StarRocks 类似但逻辑不同

| 维度 | 直读 `iceberg()` / `s3()` | 本地 MergeTree 加速层 |
|---|---|---|
| **延迟** | 秒级 | 毫秒级 |
| **数据新鲜度** | 跟源表 snapshot | 导出周期决定 |
| **推荐用途** | 探索 / 冷数据 / ad-hoc | 仪表盘 / 事件分析主路径 |
| **ClickHouse 特有差异点** | **没有 MV 自动刷新概念**（StarRocks MV 有）· ClickHouse 加速层通常靠**外部 ETL**（Airflow / 应用层）定期导出 Parquet | MergeTree + Projection 的组合本身足以做预聚合 |

**最容易踩的坑**：在 Iceberg 表上用 `iceberg()` 表函数跑仪表盘 query · 期望毫秒级 · 实际秒级——**ClickHouse 的杀手锏是它的本地 MergeTree + Projection · 不是外表直读**。

## 陷阱

- **ReplacingMergeTree 的"去重"是异步的**：查询时可能看到重复，要用 `FINAL` 关键字（但慢）
- **无真正的事务**：跨表原子性靠不住
- **join 顺序敏感**：小表放右边 + Dictionary 常常是唯一的高性能做法
- **分布式表 vs 本地表**：要想清楚"写哪、读哪"

## 相关

- [StarRocks](starrocks.md) —— 同生态竞争者，join 更强
- [Trino](trino.md) —— 交互式查询另一选
- 场景：[BI on Lake](../scenarios/bi-on-lake.md)
- 概念：[查询加速](../bi-workloads/query-acceleration.md)

## 延伸阅读

- ClickHouse docs: <https://clickhouse.com/docs>
- *ClickHouse - Lightning Fast Analytics for Everyone*（官方白皮书）
