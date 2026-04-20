---
title: StarRocks · MPP OLAP 数据库
type: system
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: StarRocks 3.3+ (2024+) · 存算分离模式 3.0+
tags: [query-engine, olap, mpp, mpp-database]
category: query-engine
repo: https://github.com/StarRocks/starrocks
license: Apache-2.0 / Elastic
status: stable
---

# StarRocks

!!! tip "一句话定位 · 独立 MPP OLAP 数据库 · 湖仓可当加速层"
    现代 **MPP 分析型数据库**——**完整数据库**（有自己的存储 + 执行 + Catalog），**可独立部署**作 OLAP 栈；在湖仓环境下也常扮演"**BI 加速层 / 仪表盘专用引擎**"。向量化执行 + 物化视图 + 湖表直读。比 Trino 延迟更低，比 ClickHouse join 更强。

!!! info "向量化 ≠ 向量检索 · 和 retrieval/ 章节的边界"
    StarRocks **3.3+（2024）** 加了**向量索引 + 向量检索函数**（cosine/L2/inner product + HNSW）。注意区分：

    - **"向量化执行"** = SIMD · 是 StarRocks 性能基础（本页正文主要讲这个）
    - **"向量检索"** = ANN 相似度搜索 · 2024+ 向检索侧延伸——详见 [多模检索](../retrieval/index.md)

    **StarRocks 的向量检索定位**：BI 数据表里**附带向量列**做混合查询（SQL 过滤 + ANN 排序）场景合适；纯向量工作负载仍建议 [Milvus / LanceDB](../retrieval/vector-database.md)。

## 它解决什么 · "比 Trino 延迟更低 / 比 ClickHouse join 更强" 的前提

上面 tip 里那句高价值判断**有严格前提**，不补充容易变成口号：

| 判断 | 成立前提 |
|---|---|
| **"比 Trino 延迟更低"** | 仅限 **已在 StarRocks 内表**（本地存储）的数据 · 直读 Iceberg 外表时延迟**和 Trino 同量级甚至更慢** |
| **"比 ClickHouse join 更强"** | 多表 join / shuffle join 场景；但**单表大扫描仍是 ClickHouse 更快**（ClickHouse MergeTree 的甜区不输 StarRocks 内表） |
| **"高并发 BI p95 < 1s"** | 数据已预聚合为 MV / 表设计合理（bucket / colocate join）· 不是所有 query 开箱即达 |

StarRocks 的甜区：

- 复杂多表 join（shuffle + colocate + bucket join 混合优化）
- 高并发（数百–数千 QPS）· **数据在内表 + 有合适 MV / 索引 **
- 毫秒到秒级延迟 · 前提同上
- 直接读 Iceberg / Hudi / Paimon / Delta 外表 · **秒级延迟，用于低频 / 探索场景**（不是仪表盘主路径）

## 架构

```mermaid
flowchart LR
  fe[FE (Frontend)<br/>元数据+调度] --> be1[BE (Backend)]
  fe --> be2[BE]
  fe --> be3[BE]
  be1 -.-> obj[(对象存储<br/>湖表)]
  be2 -.-> obj
  be3 -.-> obj
  be1 -.-> local[本地存储<br/>Primary Key 表]
```

两种表：

- **Internal Table** —— 数据放 BE 本地存储；Primary Key 表支持 upsert
- **External Table / Catalog** —— 直接读 Iceberg / Hudi / Paimon / Hive，不搬数据

## 关键能力

- 向量化执行 + SIMD
- **物化视图（MV）** 跨外部 Catalog（可以把 Iceberg 表预聚合成 StarRocks MV 供 BI 查）
- **Primary Key 表**（upsert / delete）
- Colocate / Shuffle / Bucket join 优化
- 自适应并发控制
- Query Cache / Result Cache

## 在湖仓里的典型用法

两种模式：

### 模式 A：加速副本

BI 仪表盘查询打到 StarRocks，数据**实体化**进 StarRocks 本地存储：

- 从 Iceberg 周期性 refresh MV → StarRocks 内部表
- BI 打 StarRocks，响应毫秒级
- **两份数据**，但查询速度换来了

### 模式 B：直读湖表

StarRocks 以 External Catalog 挂 Iceberg / Paimon，**查询直接读对象存储**：

- 无物化副本，一份数据
- 延迟比模式 A 高（秒级），但架构更简单

两种模式可并存：热查询走 A，冷/探索走 B。

### 湖仓直读 vs 加速副本 · 生产决策关键维度

| 维度 | 直读外表（模式 B）| 加速副本（模式 A · 内表 + MV）|
|---|---|---|
| **延迟** | 秒级（对象存储 I/O + 外部元数据）| 毫秒级（本地 + 预聚合）|
| **新鲜度** | 实时跟源表 snapshot | MV 刷新周期决定（通常分钟级）|
| **数据一致性** | 和源表强一致（读同一 snapshot）| **MV 和源表有 lag** · 上游 commit 后要等刷新 |
| **权限** | 依赖源 Catalog（Polaris / Glue 等）| 走 StarRocks 自己的 RBAC |
| **schema 演化** | 读时感知源表 schema 变更 | **MV 要手动 ALTER 或重建**才跟上 |
| **成本** | 一份数据 · 对象存储 + 计算 | 两份数据 · 内表存储 + MV 刷新计算 |
| **适合** | 低频 / 探索 / 冷数据 | 仪表盘 / 热数据 / 高并发 |

**最危险的误用**：把**直读外表**当仪表盘主路径 · 延迟 / 并发上不去后以为是 StarRocks 不行；实际应该**热路径走 MV 加速副本 · 冷路径走外表**。

## 什么时候选

- BI / 仪表盘 p95 < 1s，高并发
- 复杂多表 join
- 湖仓 + OLAP 数仓"**同一引擎服务两个场景**"

## 什么时候不选

- ETL（选 Spark）
- 事件时间流（选 Flink）
- 单机探索（选 DuckDB）

## 陷阱与坑

- **FE 单主**：多 follower 但活跃主 1 个，切主时短暂不可用
- **物化视图刷新策略**要和上游湖表的 commit 节奏配合
- **内部表 + 外部表双栈**要理清治理：哪些是"权威"表、哪些是"加速"表

## 相关

- 同类：Apache Doris（前身同源）
- 场景：[BI on Lake](../scenarios/bi-on-lake.md)
- [查询加速](../bi-workloads/query-acceleration.md)

## 延伸阅读

- StarRocks docs: <https://docs.starrocks.io/>
- *StarRocks: A New Open-Source Data Warehouse*（官方白皮书）
