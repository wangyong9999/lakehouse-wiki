---
title: ClickHouse
type: system
tags: [query-engine, olap, columnar]
category: query-engine
repo: https://github.com/ClickHouse/ClickHouse
license: Apache-2.0
status: stable
---

# ClickHouse

!!! tip "一句话定位"
    **明细事实表 OLAP 的极致**。单表大扫描 + 高并发聚合场景里几乎没有对手。在湖仓里通常作为"BI 热数据加速层"或"事件分析专用引擎"。

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

ClickHouse 24.x+ 的 `iceberg()` / `s3()` 表函数能直接读湖上 Parquet 和 Iceberg 表：

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
