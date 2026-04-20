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

# 物化视图（Materialized View）

!!! tip "一句话理解"
    把"查询结果预先算好存成表"。MV 不只是老派数仓的事——湖仓里的 MV 可以**跨引擎共享**（Iceberg MV），也可以下沉到 BI 加速层（StarRocks / Doris）。查询加速的主力之一。

## 它解决什么

仪表盘上同一条聚合查询每天被看几千次（比如"本周 GMV 按地区"）。每次都重算：

- 上游扫 TB 级明细
- 多表 join
- 聚合
- 输出几百行

完全重复劳动。MV 把这个结果物化，查询变成读一张小表，**延迟从秒级降到毫秒级**，成本降几个数量级。

## 三类 MV

### 1. 完全刷新 MV

每次按调度全表重算。简单、准确、偏"定时任务派"。

### 2. 增量刷新 MV

只处理上次刷新后的新增数据。依赖湖表的**增量读能力**：

- Iceberg incremental scan
- Paimon changelog
- Hudi incremental query

### 3. 查询时重写（Query Rewrite）

用户还是写原 SQL，优化器识别"这条可以用某个 MV"，**自动改写**去查 MV。Trino / StarRocks 都在做。

## Iceberg MV

Iceberg 1.4+ 引入表级 MV。特点：

- **跨引擎可见**：Spark 建的 MV，Trino 能识别并用
- **自动失效追踪**：上游 Snapshot 变了 MV 被标记为过期
- **partition-level refresh**：只刷新受影响分区
- **元数据在 Catalog 层**

## StarRocks / Doris MV

**"加速副本"思路**：

- MV 物化进 StarRocks 内部存储
- 查询引擎**透明改写**原查询到 MV
- 刷新策略：全量 / 增量 / 事件触发

适合放在 BI 仪表盘前面当加速层。

## 什么时候用 MV

对这三类查询 ROI 最高：

1. **高频相同聚合**（仪表盘固定指标）
2. **固定 join 模式**（事实 + 维度 join 后的宽表）
3. **滚动窗口聚合**（近 7 天 / 近 30 天 dashboard）

## 什么时候别用

- 查询 pattern 每次都变 —— 不如把钱花在加速层
- 数据延迟非常敏感（秒级） —— MV 的刷新延迟可能超过业务容忍度
- 数据量本身已经小 —— 没必要

## 陷阱

- **MV 过期不刷新 → 看到旧数据**：监控 staleness
- **MV 链过长**：MV of MV of MV 维护成本爆炸
- **刷新计算成本 > 查询节省**：冷门 MV 反而是浪费
- **Schema 演化传播**：上游表加列，MV 要同步调整

## 运维清单

- 每个 MV 记录：**owner、上游表、刷新策略、上次刷新时间、命中率**
- 每月盘点低命中率 MV，该删就删
- 和 [Compaction](../lakehouse/compaction.md) 一起作为湖仓常规运维动作

## 相关

- [查询加速](query-acceleration.md)
- [OLAP 建模](olap-modeling.md)
- 场景：[BI on Lake](../scenarios/bi-on-lake.md)

## 延伸阅读

- Iceberg MV design doc（社区）
- StarRocks Materialized View docs
