---
title: 查询加速（Zone Maps / Liquid Clustering / Z-order）
type: concept
tags: [bi, optimization, lakehouse]
aliases: [查询加速, 数据布局优化]
related: [materialized-view, olap-modeling, lake-table, compaction]
systems: [iceberg, delta, paimon, starrocks]
status: stable
---

# 查询加速（数据布局优化）

!!! tip "一句话理解"
    **把物理数据按查询 pattern 重新排**，让谓词下推能跳过绝大部分数据。不改 SQL、不加机器，也能把查询从 30s 降到 3s。湖仓性能调优的头等招式。

## 核心原理

湖表的查询瓶颈通常不是"扫得慢"，而是"扫了太多没必要扫的"。每个 Parquet 文件的 footer 里有**列级 min/max 统计**；每个 Iceberg manifest 里有**分区值范围**。优化器靠这些在**打开文件之前**就跳过不相关的：

- 查询 `WHERE ts > '2026-04-01'`
- 某个文件 footer 说"这列 max = '2026-03-20'"
- 引擎直接跳过整个文件

**加速的核心**就是让数据排列方式**匹配查询 pattern**，从而让 min/max 有效。

## 四类加速机制

### 1. 分区（Partitioning）

粗粒度按列值切目录/文件组。典型 `PARTITIONED BY (dt, region)`。

- **有效条件**：查询 `WHERE dt = X` 能直接剪枝
- **坑**：分区粒度不对（太细 → 小文件爆炸 / 太粗 → 剪枝无效）

Iceberg 的 **Hidden Partitioning + Partition Evolution** 是目前最优雅的分区抽象。

### 2. Zone Maps（列级 min/max）

每个 data file 每列自带 min/max 统计。天然生效，不需要特殊配置。

**使它有效的前提：数据得在文件层面是"聚集"的**。如果同一个 `user_id` 分散在 1000 个文件，min/max 都是 `[0, max_user]`，完全没剪枝。

### 3. Sort Order / Z-order

把数据按某几列**全局排序**再重写。排序后同值的行聚集，Zone Maps 变得极有效。

- **单列 sort**：按 `ts DESC` 排序，时间查询极快；对其他列没帮助
- **Z-order**：多维 Morton 曲线排序；多个列的范围查询都受益（但每个都不如单列 sort）

Delta `OPTIMIZE ... ZORDER BY`、Iceberg 的 `rewrite_data_files(sort_order=...)` 都是这招。

### 4. Liquid Clustering（Delta 新物种）

Databricks 提出的新方法——**不预定义**分区键，系统根据查询历史**自动聚集**数据。

- 解决"分区键选错就卡住"的老痛
- 允许多键聚集、自动重平衡
- 目前 Delta 独有；Iceberg 社区有类似讨论

## 什么查询能加速

| 查询类型 | 有效机制 |
| --- | --- |
| `WHERE dt = '2026-04-01'` | 分区 + Zone Maps |
| `WHERE user_id = 12345` | Sort / Z-order on user_id |
| `WHERE region = 'cn' AND kind = 'image'` | 多列 Z-order / Liquid Clustering |
| `ORDER BY ts LIMIT 100` | Sort on ts + 谓词下推 |
| `SELECT count(*) FROM table` | Manifest 元数据直接回答，无需扫 |

## 实战配方

1. **找 Top 10 查询**（BI 系统访问日志）
2. 看它们的 `WHERE` / `JOIN` 涉及哪些列
3. 按访问频率选 **1–3 列**做 sort 或 Z-order
4. 写 `rewrite_data_files` / `OPTIMIZE` 任务作为定期作业
5. Benchmark 前后对比 —— 通常 **3–10 倍**加速

## 陷阱

- **不 compact 就不生效**：新写入文件还是乱的，要靠定期 rewrite
- **排序列选得多**：全选 = 谁都不好；Z-order 也就 3–5 列合理
- **和分区互斥思维**：分区是粗粒度，Z-order 是细粒度，两者互补不互斥
- **忽略写入 cost**：Z-order / Liquid Clustering 写入更贵；要按收益衡量

## 相关

- [Compaction](../lakehouse/compaction.md) —— rewrite/sort 的载体
- [物化视图](materialized-view.md) —— 另一条加速路径
- [OLAP 建模](olap-modeling.md)
- [性能调优](../ops/performance-tuning.md)

## 延伸阅读

- Iceberg sort order: <https://iceberg.apache.org/docs/latest/maintenance/#rewrite-data-files>
- Delta Liquid Clustering: <https://docs.delta.io/latest/delta-liquid.html>
- *Data Skipping Index* （ClickHouse 的对等机制）
