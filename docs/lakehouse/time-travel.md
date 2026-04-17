---
title: Time Travel（时间旅行）
type: concept
tags: [lakehouse, table-format]
aliases: [时间旅行, Table Versioning]
related: [snapshot, lake-table, iceberg]
systems: [iceberg, delta, hudi, paimon]
status: stable
---

# Time Travel（时间旅行）

!!! tip "一句话理解"
    查询表**过去某一时刻或某一版本**的样子。湖仓天生具备，因为旧 Snapshot 没被物理删除；只要 Snapshot 还在，你随时能读回去。

## 两种写法

```sql
-- Iceberg
SELECT * FROM orders VERSION AS OF 123456789;
SELECT * FROM orders TIMESTAMP AS OF '2026-03-01 10:00:00';

-- Delta
SELECT * FROM orders VERSION AS OF 42;
SELECT * FROM orders TIMESTAMP AS OF '2026-03-01';

-- Spark/Python
spark.read.option("snapshot-id", 123456789).table("orders")
```

## 它为什么存在

时间旅行不是"为了酷而加的功能"，是一系列现实痛点的副产品：

- **Bug 回溯** —— 昨晚的报表对不上，能不能看看"出错那个快照里"数据长什么样？
- **审计 / 合规** —— 监管要求你能回放过去某一时刻的账
- **ML 训练** —— 复现训练结果必须有确定性的数据版本
- **回滚** —— 一个坏作业写坏了表？`ROLLBACK` 到上一个 Snapshot
- **AB 对照** —— 老查询跑旧版本、新查询跑新版本，对照差异

## 它的边界

- **受保留策略约束** —— Snapshot 过期后，`expire_snapshots` 会物理删除它引用但无其他 Snapshot 复用的数据文件。**此后时间旅行失效**
- **默认保留窗不一定够** —— Iceberg 默认保留 5 天、Delta 默认 7 天 / 30 天（不同版本）；审计场景要显式拉长
- **"某时刻"不是字节级** —— 精度受 commit 频率约束；如果表一天才 commit 一次，就没有"早上 10 点"这个快照

## 相关操作

```sql
-- Iceberg
SELECT * FROM orders.history;        -- 查所有历史 Snapshot
SELECT * FROM orders.snapshots;      -- 更详细的元信息
CALL system.rollback_to_snapshot('orders', 123);
CALL system.expire_snapshots('orders', TIMESTAMP '2026-01-01');
```

Delta / Hudi / Paimon 都有等价命令，语法略异。

## 和 DB 的差异

传统 DB 的 "as-of query" 靠 WAL + undo 回放，成本高、窗口短（通常几分钟到几小时）。
湖仓靠**不可变快照序列**天然支持长窗口时间旅行，这是湖表格式的"白送功能"。

## 相关概念

- [Snapshot](snapshot.md)
- [湖表](lake-table.md)
- [Apache Iceberg](iceberg.md)

## 延伸阅读

- Iceberg Time Travel: <https://iceberg.apache.org/docs/latest/spark-queries/#time-travel>
- Delta Time Travel: <https://docs.delta.io/latest/delta-batch.html#query-an-older-snapshot-of-a-table>
