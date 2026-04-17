---
title: Snapshot（快照）
type: concept
tags: [lakehouse, table-format]
aliases: [快照, Table Snapshot]
related: [lake-table, iceberg]
systems: [iceberg, paimon, hudi, delta]
status: stable
---

# Snapshot（快照）

!!! tip "一句话理解"
    一个 Snapshot 是**表在某一时刻的完整视图** —— 一串不可变的元数据文件，引用一组不可变的数据文件。读者读一个固定 Snapshot；提交 = 切换到新 Snapshot。

## 它是什么

Snapshot 是湖表的"时间片"。每次 commit（insert / update / delete / schema change 都算）产生一个新 Snapshot：

- 有一个单调递增的 `snapshot-id`
- 指向一个 `manifest-list`（再指向若干 manifest，再指向若干数据文件）
- 记录 parent snapshot、提交时间、提交者摘要信息

一张表在某一时刻"看起来是什么样"，完全由当前 Snapshot 决定。

## Snapshot 为什么让"时间旅行"成为可能

因为旧 Snapshot 没有被**物理删除**，只是不再是"current"。你可以：

```sql
-- Iceberg
SELECT * FROM orders VERSION AS OF 12345;
SELECT * FROM orders TIMESTAMP AS OF '2026-03-01 10:00:00';
```

Snapshot 天生支持：

- **时间旅行查询**（审计、debug、回放）
- **Roll-back** —— 出错了把 `current-snapshot-id` 指回旧的
- **增量读取** —— 给我 `snapshot A → B` 之间新增的数据（CDC / 增量拉取的基础）

## 生命周期

Snapshot 不会永远保留，否则对象存储会无限膨胀。典型策略：

| 阶段 | 动作 |
| --- | --- |
| 创建 | 每次 commit 产生一个 |
| 保留 | 根据保留策略（例如近 7 天、最多 100 个） |
| 过期 | 被标记 expired 后，元数据仍可见但不再是 current |
| 回收 | `expire_snapshots` / `vacuum` 物理删除不再被引用的数据文件和 manifest |

**坑**：过早回收会让时间旅行失效；过晚回收会浪费存储。团队需要有明确的回收策略并做成定时任务。

## 在典型 OSS 里

- **Iceberg** —— Snapshot 是一等公民，所有操作都围绕它；spec 里明确定义了 `parent-id`、`summary`、`sequence-number`
- **Delta Lake** —— 叫 "version"，底层由 `_delta_log/*.json` 的单调序列维护
- **Paimon** —— 叫 "snapshot"，同时支持流式消费 changelog
- **Hudi** —— 叫 "instant"，时间线（Timeline）由 `.hoodie/` 下的 instant 文件组成

概念名字不同，本质相同：**不可变元数据文件序列 + 当前指针**。

## 相关概念

- [湖表](lake-table.md) —— Snapshot 是湖表 ACID 与时间旅行的基石
- [Apache Iceberg](iceberg.md)

## 延伸阅读

- Iceberg spec v2 - Snapshots: <https://iceberg.apache.org/spec/#snapshots>
- Delta Lake Protocol: <https://github.com/delta-io/delta/blob/master/PROTOCOL.md>
