---
title: Time Travel（时间旅行）
type: concept
depth: 进阶
last_reviewed: 2026-04-18
applies_to: Iceberg v2+, Delta 3+, Hudi 0.14+, Paimon 0.9+
tags: [lakehouse, table-format, time-travel]
aliases: [时间旅行, Table Versioning]
related: [snapshot, lake-table, iceberg, branching-tagging]
systems: [iceberg, delta, hudi, paimon]
status: stable
---

# Time Travel（时间旅行）

!!! tip "一句话理解"
    查询表**过去某一时刻或某一版本**的样子。湖仓天生具备——旧 Snapshot 的元数据 + 数据文件还在，就能读回去。**Time Travel = 读**；**Rollback / Restore = 写**（换当前指针）——这两件事不是一回事，容易混。

!!! abstract "TL;DR"
    - Time Travel **读一个过去 snapshot**，不改当前表
    - Rollback / Restore **把当前指针切到过去 snapshot**——是一次新的 commit
    - 能读多久 = **snapshot 未 expire + 数据文件未 vacuum**（两个条件都得满足）
    - 精度 = commit 频率；一天 commit 一次就没有"早上 10 点"
    - **各家默认窗口差异大**：Iceberg 5 天 / Delta 实际 7 天（受 vacuum 约束）/ Paimon 1h；合规场景必须显式拉长或用 tag 锁定
    - **合规审计**：用 tag 固定关键 snapshot，避免被 expire 清走

## 1. 两种写法

```sql
-- Iceberg
SELECT * FROM orders VERSION AS OF 123456789;                     -- by snapshot id
SELECT * FROM orders TIMESTAMP AS OF '2026-03-01 10:00:00';       -- by timestamp
SELECT * FROM orders FOR SYSTEM_VERSION AS OF 123456789;          -- SQL:2011 风格

-- Delta
SELECT * FROM orders VERSION AS OF 42;
SELECT * FROM orders TIMESTAMP AS OF '2026-03-01';

-- Paimon
SELECT * FROM orders /*+ OPTIONS('scan.snapshot-id' = '42') */;

-- Spark / Python (Iceberg)
spark.read.option("snapshot-id", 123456789).table("orders")
spark.read.option("as-of-timestamp", "1735689600000").table("orders")
```

## 2. 它为什么存在

Time Travel 不是"为了酷而加的功能"，是一系列现实痛点的副产品：

- **Bug 回溯** —— 昨晚的报表对不上，能不能看看"出错那个快照里"数据长什么样？
- **审计 / 合规** —— 监管要求能回放过去某一时刻的账
- **ML 训练** —— 复现训练结果必须有确定性的数据版本
- **回滚** —— 一个坏作业写坏了表？`ROLLBACK` 到上一个 snapshot
- **AB 对照** —— 老查询跑旧版本、新查询跑新版本，对照差异

## 3. Time Travel vs Rollback / Restore（读 vs 写）

最容易混的一对概念。**它们不是一件事**：

| | Time Travel | Rollback / Restore |
|---|---|---|
| 本质 | 读 | 写（新 commit） |
| 是否改当前指针 | ❌ | ✅ |
| 原子性要求 | 无（只读） | 需 CAS |
| 典型命令 | `VERSION AS OF` · `TIMESTAMP AS OF` | `rollback_to_snapshot` · `RESTORE TABLE` |
| 撤销难度 | 无副作用 | 要再 rollback / restore 一次 |

**各家 restore 语义差异**：

- **Delta `RESTORE`**：软回滚——生成一个新 commit，内容等同目标 snapshot，**不删除中间的 snapshot**（仍可 time travel 回来）
- **Iceberg `rollback_to_snapshot`**：切指针——当前 snapshot 指向过去；被跳过的 snapshot 保留到 expire 为止，之后可以被 cleanup
- **Paimon**：类似 Iceberg，`CALL rollback_to('db.t', 42)`

## 4. Snapshot 选取策略

选哪个 snapshot 读有多种维度：

- **按 snapshot ID**：精确但需要事先知道 ID —— 查 `<table>.snapshots` 或 `<table>.history`
- **按 timestamp**：找"早于或等于该时刻的最新 snapshot"——commit 频率决定精度
- **按 tag**（Iceberg only）：给关键 snapshot 打 tag（如 `release-2026-01`），tag **不随 retention 过期**
- **按 branch**（Iceberg only）：WAP 工作流——开 branch 写、读 branch head、验证后快进合并

```sql
-- 查 snapshot 列表
SELECT snapshot_id, parent_id, committed_at, operation, summary
FROM orders.snapshots
ORDER BY committed_at DESC;

-- 打 tag 固定审计点
ALTER TABLE orders CREATE TAG `year-end-2026` AS OF VERSION 123456;

-- 按 tag 读
SELECT * FROM orders VERSION AS OF 'year-end-2026';
```

## 5. 和 expire / vacuum 的联动（关键边界）

Snapshot 过期是一个**危险操作**——会让 time travel 永久失效。关键参数：

| 系统 | 保留元数据 | 保留数据文件 | 实际 time travel 窗口 |
|---|---|---|---|
| **Iceberg** | `history.expire.max-snapshot-age-ms`（5 天默认）+ `min-snapshots-to-keep` | 同 snapshot 保留 | 取决于 expire 调度 |
| **Delta** | `delta.logRetentionDuration`（30 天）| `delta.deletedFileRetentionDuration`（7 天）| **min(log retention, file retention) ≈ 7 天默认** |
| **Paimon** | `snapshot.time-retained`（1h）+ `snapshot.num-retained.min`（10）| 同 snapshot | 约 1 小时默认（常要拉长）|
| **Hudi** | `hoodie.cleaner.commits.retained` | 同 commit | 自定义策略 |

**重要**：Delta 的 log 保留 30 天**不等于**能 time travel 30 天。`VACUUM` 按 `deletedFileRetentionDuration` 默认 7 天清理数据文件——**默认实际 time travel 窗口 ≈ 7 天**。要拉长必须同时调这两个。

**合规 / 审计场景**：用 **tag 或 branch 固定关键 snapshot**，让它不受 expire 影响。例如年末账、季度末报表、ML 训练数据版本。

## 6. 相关操作

```sql
-- Iceberg · 完整运维
SELECT * FROM orders.history;        -- 所有历史 snapshot
SELECT * FROM orders.snapshots;      -- 含 summary 的详情
CALL system.rollback_to_snapshot('orders', 123);
CALL system.expire_snapshots(
  table => 'orders',
  older_than => TIMESTAMP '2026-01-01',
  retain_last => 100
);
CALL system.remove_orphan_files('orders', TIMESTAMP '2026-01-01');

-- Delta
DESCRIBE HISTORY orders;
RESTORE TABLE orders TO VERSION AS OF 42;
RESTORE TABLE orders TO TIMESTAMP AS OF '2026-03-01';
VACUUM orders RETAIN 168 HOURS;  -- 至少 168h = 7 天
```

## 7. 和传统 DB 的差异

传统 DB 的 "as-of query"（Oracle Flashback / SQL Server Temporal Tables）靠 **undo 日志 + WAL 回放**，成本高、窗口短（通常几分钟到几小时）。

湖仓靠**不可变快照序列**天然支持长窗口时间旅行，这是湖表格式的"白送功能"——代价是存储（snapshot 不清理会无限膨胀）。

## 8. 陷阱

- **"VERSION AS OF 昨天" 但 vacuum 已跑** → 数据文件已物理删除 → 读失败
- **合规要求回到 3 年前** → 没关 expire → 数据早被清 → 应**提前建 tag**
- **把 rollback 当 undo** → rollback 后又 commit → 原 snapshot 被跳过成孤立节点，再回去需要 rollback 链
- **流消费者追不上保留窗** → 默认 1h 的 Paimon snapshot retention 对慢消费者不够 → 调 `snapshot.num-retained.min` 大些
- **Time travel 到 schema 不同的 snapshot** → schema evolution 后老 snapshot 的数据按当时 schema 读，新增列返回 null
- **跨 catalog 的 snapshot id 不通用** → snapshot id 是表级的，不是全局的

## 9. 相关概念

- [Snapshot](snapshot.md) —— 时间旅行的底层机制
- [Branch & Tag](branching-tagging.md) —— 固定关键 snapshot 的正确姿势
- [湖表](lake-table.md) · [Apache Iceberg](iceberg.md)

## 10. 延伸阅读

- **[Iceberg Time Travel](https://iceberg.apache.org/docs/latest/spark-queries/#time-travel)**
- **[Delta Time Travel](https://docs.delta.io/latest/delta-batch.html#query-an-older-snapshot-of-a-table)**
- **[Paimon Time Travel](https://paimon.apache.org/docs/master/maintenance/manage-snapshots/)**
- [Iceberg Branching & Tagging](https://iceberg.apache.org/docs/latest/branching/)
