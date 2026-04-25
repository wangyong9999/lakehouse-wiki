---
title: 物化视图 · IVM / Query Rewrite / Iceberg MV
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: Iceberg MV spec（incubating）· Delta MV · StarRocks/Doris MV · Trino MV · Materialize · Paimon
tags: [bi, mv, optimization, ivm, query-rewrite]
aliases: [MV, Materialized View, 物化视图, IVM]
related: [query-acceleration, olap-modeling, semantic-layer]
systems: [iceberg, delta, paimon, starrocks, trino, spark, materialize]
status: stable
---

# 物化视图 · IVM / Query Rewrite / Iceberg MV

!!! info "本页是 BI 工程实践视角 (canonical)"
    本页讲 **BI 工程师视角 + IVM 算法家族 + Query Rewrite + 产品选型矩阵** · 是 BI 视角的 canonical 页（按 [ADR-0006](../adr/0006-chapter-structure-dimensions.md)）。
    
    **湖表协议层视角**（spec vs 实现差异 / 协议标准化进展 / Embedding MV 启发）见 [lakehouse/materialized-view](../lakehouse/materialized-view.md)。

!!! tip "一句话定位"
    把"查询结果预先算好存成表"——BI 高频相同聚合的主力加速手段。湖仓 MV 的技术关键是**增量维护（IVM）算法**和**查询改写（Query Rewrite）优化器**——**不是把 MV 建出来**而是让 MV **又新又被用到**。

!!! abstract "TL;DR"
    - **三类机制**：完全刷新 · 增量刷新（IVM）· 查询改写透明路由
    - **IVM 算法家族**：delta-based · change-propagation · differential dataflow · 各有适用窗口
    - **Query Rewrite** · 优化器的 subsumption 判断——老查询自动路由到可用 MV
    - **Iceberg MV 规范** · 2025-2026 仍 incubating · 但 AWS Glue / Trino / Spark 3.5.6+ 各自已有实现
    - **湖仓最强增量 MV** · StarRocks 异步增量 MV + Materialize 流 MV · 各有专长
    - **MV 和 [加速副本](query-acceleration.md#4) 的区别**：MV 是结果物化 · 加速副本是存储物化

## 1. 它解决什么

仪表盘上同一条聚合查询每天被看几千次（"本周 GMV 按地区"）。每次都：

- 上游扫 TB 级明细
- 多表 join
- 聚合
- 输出几百行

完全重复劳动。MV 把结果物化 · 查询变成读一张小表——**延迟从秒级降到毫秒级 · 成本降几个数量级**。

**MV 的价值取决于三件事**：
1. **能不能命中** · Query Rewrite 把老查询路由到 MV
2. **新不新鲜** · 增量刷新机制跟得上
3. **值不值得建** · 刷新成本 < 查询节省 · 命中率要够

## 2. 三类刷新机制

### 2.1 完全刷新 MV

每次按调度**全表重算**。

- **简单** · 实现只需"定时 INSERT OVERWRITE"
- **缺点** · TB 级明细全扫 · 浪费 · 不适合高频刷新

**适合**：小表 · 低频刷新（T+1）· 无 CDC 源的维度聚合。

### 2.2 增量刷新 MV · IVM 核心

**Incremental View Maintenance (IVM)** · 学术问题 40 年研究 · 湖仓场景 3 种落地路径：

#### 路径 A · Delta-based IVM

- 读**上游 snapshot 的 delta**（新增 + 删除行）
- 把 delta 应用到 MV 当前状态
- 湖表天然支持 delta（Iceberg incremental scan · Paimon changelog · Hudi incremental query）

```sql
-- StarRocks 异步增量 MV（最成熟的 Delta-based IVM 之一）
CREATE MATERIALIZED VIEW mv_daily_gmv
REFRESH ASYNC EVERY (INTERVAL 10 MINUTE)
AS
SELECT dt, region, SUM(amount) AS gmv
FROM iceberg_catalog.sales.orders
GROUP BY dt, region;
```

StarRocks 内部自动追踪 Iceberg snapshot 差量 · 只算新增/变更部分。

#### 路径 B · Change-Propagation（Eager）

- 上游变更**立即推到** MV · 基于 CDC 流
- **Paimon 的 Partial Update / Aggregation 表**本质是这路径的物化
- **Flink Dynamic Table** 底层也是 change propagation

#### 路径 C · Differential Dataflow（Materialize 范式）

- 把 SQL 编译成**增量数据流算子 DAG**
- 每个算子维护状态 · 增量计算
- **Materialize 是代表** · 延迟亚秒级 · 但状态成本高
- 类似学术路径：Noria · DBSP

#### 三者选型

| 路径 | 延迟 | 状态开销 | 适合 |
|---|---|---|---|
| **Delta-based** | 分钟-小时 | 低 · 只需上次 snapshot id | 分析型 BI · 大部分 IVM 场景 |
| **Change-Propagation** | 秒 | 中 | CDC + 聚合 · Paimon 主场 |
| **Differential Dataflow** | 亚秒 | 高 | 流式 BI · 实时大屏 |

### 2.3 查询改写（Query Rewrite）· MV 命中的关键

用户还是写原 SQL · **优化器识别"这条可以用某个 MV"**自动改写。

**机制核心**：**subsumption check**——"待执行的查询 Q 的语义是否被 MV M 包含？"

- **列匹配** · Q 的 output columns 都能从 M 导出？
- **谓词匹配** · Q 的 WHERE 是否 M 的 WHERE 的子集？
- **聚合匹配** · Q 的 GROUP BY 是否 M 的 GROUP BY 的上卷？（例：MV 按天 · Q 按月 · 可上卷）
- **Join 匹配** · Q 的 Join 图是否 M 的子图？

**算法难点**：
- SQL 规范化（Calcite 的 RelNode rewrite rules）
- Partial match + residual predicates（Q 的 WHERE 严于 M 时 · 加残余过滤）
- 多 MV 可选时的 cost-based 选择

**产品现状**：
- **StarRocks** · 行业最成熟的 Query Rewrite · 支持部分匹配 + 上卷
- **Trino** · 2024+ 支持 Iceberg MV 自动路由 · 能力仍在追赶
- **Databricks** · Photon + Delta MV 改写
- **Snowflake** · MV + Dynamic Tables 都支持改写
- **PostgreSQL** · 无原生自动改写（手写 MV 查询）

## 3. Iceberg MV 规范 · 2025-2026 现状

!!! warning "规范状态"
    **Iceberg View Spec**（只读视图）自 Iceberg 1.4 稳定。**Iceberg Materialized View Spec** 截至 2026-04 **仍在 incubating**（[Issue #6420](https://github.com/apache/iceberg/issues/6420)）· **未合入 format spec**。但各引擎已基于 spec 草案自行实现：

- **AWS Glue Data Catalog** · 2025-11 发布 "Iceberg-based materialized views" · 自动跟踪源表变化 · 跨 Athena/EMR/Glue
- **Trino 480+** · `CREATE MATERIALIZED VIEW` 底层用 Iceberg storage + view metadata
- **Spark 3.5.6+** · Athena/EMR/Glue 联合发布的新 SQL 语法
- **Dremio** · 2024 起支持
- **Databricks** · Delta MV 成熟 · managed Iceberg 走 V3 Preview

**refresh-state 属性**：每个存储表 snapshot 的 summary 里记录源表状态 · 用于判断 MV 是否 fresh。

**2026 Iceberg ecosystem survey** · MV 是 v4 潜在特性的第一名（37% 呼声）。

### 生产落地建议

- **跨引擎共享 MV** · 目前不现实 · 等 spec 稳定
- **单引擎内用** · Databricks Delta MV · StarRocks MV · Dremio MV 都可靠
- **Glue MV** · AWS 栈偏好 · 跨 Athena/EMR 可见

## 4. 主流产品对比

| 产品 | IVM 路径 | Query Rewrite | 刷新语义 | 生态成熟度 |
|---|---|---|---|---|
| **StarRocks** | Delta-based | 最强 · 支持部分匹配+上卷 | ASYNC / MANUAL / SYNC | 湖上 MV 最成熟之一 |
| **Databricks Delta MV** | Delta-based | 强 | 触发式 / 定时 | 商业生态第一 |
| **Snowflake Dynamic Tables** | Change-Propagation | 强 | lag target 驱动 | 纯 Snowflake 栈 |
| **Materialize** | Differential Dataflow | 无（专用 SQL）| 流 · 亚秒 | 专门流 MV |
| **Trino Iceberg MV** | Delta-based | 发展中 | 触发式 | 新 · 开放 |
| **AWS Glue Iceberg MV** | Delta-based | 跨引擎继承 | 定时 | 2025-11 发布 · 新 |
| **Paimon Aggregation Table** | Change-Propagation | 无（表即 MV）| 流 | 流场景 |
| **PostgreSQL MV** | 全刷新 | 无自动 | 手动 REFRESH | 老派 |

## 5. 代码示例

### 5.1 StarRocks 异步增量 MV

```sql
CREATE MATERIALIZED VIEW mv_shop_daily_gmv
PARTITION BY dt
DISTRIBUTED BY HASH(shop_id) BUCKETS 16
REFRESH ASYNC EVERY (INTERVAL 10 MINUTE)
PROPERTIES (
  "replication_num" = "3",
  "partition_refresh_number" = "4"
)
AS
SELECT
    DATE(order_ts) AS dt,
    shop_id,
    region,
    SUM(amount) AS gmv,
    COUNT(*) AS order_cnt,
    COUNT(DISTINCT user_id) AS active_users
FROM iceberg_catalog.sales.orders
WHERE order_ts >= '2024-01-01'
GROUP BY DATE(order_ts), shop_id, region;
```

- `PARTITION BY dt` · MV 自己分区 · 分区级刷新
- `partition_refresh_number = 4` · 单次刷新最近 4 个分区 · 避免扫全表
- Query Rewrite 自动命中 · 用户写 `SELECT SUM(amount) FROM orders WHERE dt=X GROUP BY region` · StarRocks 自动用 MV

### 5.2 Trino Iceberg MV

```sql
CREATE MATERIALIZED VIEW mv_monthly_revenue
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['year_month']
)
AS
SELECT
    date_trunc('month', order_ts) AS year_month,
    region,
    SUM(amount) AS revenue
FROM iceberg.sales.orders
GROUP BY 1, 2;

REFRESH MATERIALIZED VIEW mv_monthly_revenue;
```

- 底层存为 Iceberg table
- `REFRESH` 触发刷新 · Trino 内部比对源表 snapshot

### 5.3 Databricks Delta MV（SQL Warehouse）

```sql
CREATE MATERIALIZED VIEW mv_user_summary
AS
SELECT
    u.user_id,
    u.region,
    COUNT(o.order_id) AS order_count,
    SUM(o.amount) AS total_spent
FROM users u
LEFT JOIN orders o ON o.user_id = u.user_id
GROUP BY u.user_id, u.region;

-- Delta 自动增量维护 · Photon 加速
```

## 6. 什么时候用 MV

**高 ROI 场景**：

1. **高频相同聚合** · 仪表盘固定指标 · 每天被查 1000+ 次
2. **固定 join 模式** · 事实 + 维度 join 后的宽结果
3. **滚动窗口聚合** · 近 7 天/30 天 · 每天增量
4. **COUNT DISTINCT** · MV 存 HyperLogLog sketch · 查询直读

**低 ROI / 反面**：

- 查询 pattern 每次都变 · 建 MV 多半不命中 · 上加速副本或让引擎自己打
- 数据延迟非常敏感（秒级）· MV 的刷新延迟可能超过业务容忍度 · 走 Materialize / Paimon
- 数据量本身已经小 · 没必要
- 多维分析高维度 cube · MV 的组合爆炸 · 考虑 Rollup 或 Cube 产品

## 7. 陷阱

- **MV 过期不刷新 → 看到旧数据** · 监控 staleness（MV 和源表 snapshot 的 lag）
- **MV 链过长** · MV of MV of MV · 刷新 DAG 难维护 · 2 层是实际上限
- **刷新计算成本 > 查询节省** · 冷门 MV 反而是浪费 · 按命中率定期盘点
- **Schema 演化传播** · 上游表加列 · MV 要同步调整 · 有的产品自动有的不自动
- **没 Query Rewrite 就建 MV** · 用户的查询不会走 MV · 白建 · 用支持自动路由的引擎
- **MV 存储没监控** · 数据量膨胀没人知道 · 加上量级监控
- **增量刷新用在不合适源** · 非 append-only 表的 IVM 正确性微妙 · 删除/更新语义对 MV 的影响要仔细
- **Iceberg MV 跨引擎预期过高** · 2026-Q2 spec 未 ratify · 跨引擎共享仍不现实

## 8. 运维清单

每个 MV 记录：
- **owner** · 问题找谁
- **上游表** · 刷新依赖
- **刷新策略** · ASYNC / SYNC / MANUAL
- **上次刷新时间** · staleness 监控
- **命中率** · 每月盘点 · < 20% 考虑删
- **存储成本** · GB · 每月盘点
- **下游看板** · 谁在用（反向引用）

和 [Compaction](../lakehouse/compaction.md) 一起作为湖仓常规运维动作。

## 9. 相关

- [查询加速](query-acceleration.md) · 扫快 vs MV 的不扫 · 互补
- [OLAP 建模](olap-modeling.md) · ADS 层是 MV 的天然目标
- [语义层](semantic-layer.md) · Cube pre-aggregation 本质是"BI 层 MV"
- [仪表盘 SLO](dashboard-slo.md) · MV 是达 SLO 的常规手段
- [BI on Lake 场景](../scenarios/bi-on-lake.md) · MV 在端到端场景的位置

## 10. 延伸阅读

- **[Iceberg Materialized View Proposal · Issue #6420](https://github.com/apache/iceberg/issues/6420)**
- **[AWS Glue Iceberg MV 发布博客（2025-11）](https://aws.amazon.com/blogs/big-data/introducing-apache-iceberg-materialized-views-in-aws-glue-data-catalog/)**
- **[Trino Iceberg MV 文档](https://trino.io/docs/current/connector/iceberg.html#materialized-views)**
- **[StarRocks 物化视图](https://docs.starrocks.io/docs/using_starrocks/Materialized_view/)**
- **[Materialize · Differential Dataflow](https://materialize.com/docs/)**
- **[Databricks Dynamic Tables / Delta Live Tables](https://docs.databricks.com/delta-live-tables/)**
- **[Incremental View Maintenance Survey (Gupta & Mumick 1995)](https://dl.acm.org/doi/10.1145/210197.210203)** · IVM 经典综述
