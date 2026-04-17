---
title: StarRocks
type: system
tags: [query-engine, olap, mpp]
category: query-engine
repo: https://github.com/StarRocks/starrocks
license: Apache-2.0 / Elastic
status: stable
---

# StarRocks

!!! tip "一句话定位"
    现代 **MPP 分析型数据库**，向量化执行 + 物化视图 + 直接读湖表。在湖仓上扮演"**BI 加速层 / 仪表盘专用引擎**"——比 Trino 延迟更低，比 ClickHouse join 更强。

## 它解决什么

Trino 交互式够用但在"仪表盘 p95 < 1s + 高并发"场景下吃力；ClickHouse 单表查询极快但多表 join 差。StarRocks 的甜区正好在这两者中间：

- 复杂多表 join
- 高并发（数百–数千 QPS）
- 毫秒到秒级延迟
- 直接读 Iceberg / Hudi / Paimon / Delta（湖表 connector 成熟）

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
