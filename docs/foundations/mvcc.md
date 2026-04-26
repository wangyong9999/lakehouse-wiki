---
title: MVCC（多版本并发控制）
applies_to: "通用基础概念 · 长期稳定"
type: concept
depth: 进阶
level: B
tags: [foundations, concurrency]
aliases: [Multi-Version Concurrency Control]
related: [snapshot, lake-table]
systems: [postgres, innodb, iceberg, delta]
status: stable
last_reviewed: 2026-04-18
---

# MVCC（Multi-Version Concurrency Control）

!!! tip "一句话理解"
    **读不加锁，写新版本**。每条数据可同时存在多个版本，读操作按"事务开始时的快照"取版本；写操作生成新版本不覆盖旧的。现代数据库和湖仓**几乎都基于 MVCC**。

## 为什么需要

传统锁式并发（2PL）下，读一行要等写完；写一行要等读完。高并发场景下锁等待链让吞吐崩塌。MVCC 把读写分开：

- **读**不加锁，看一个**固定版本**
- **写**生成新版本，不影响正在读的旧版本
- 只有**写冲突**才需要协调（乐观或悲观）

这让 OLTP 能跑上万并发，也让 OLAP 在大查询中不阻塞写入。

## 关键机制

### 版本链 / 版本号

每行数据带隐藏字段：`created_xid`、`deleted_xid`（或等价的版本号、时间戳）。查询按自己事务的 `xid` 过滤可见版本：

```
一行 user 被修改三次：
  v1 (created=100, deleted=150) → 事务 120 看到 v1
  v2 (created=150, deleted=200) → 事务 170 看到 v2
  v3 (created=200, deleted=NULL)
```

### 快照隔离（Snapshot Isolation）

事务开始时拿一个"全局快照"（读视图），整个事务都按这个快照读。大多数实现等价于 SI，严格 Serializable 要额外机制（SSI / 冲突检测）。

!!! warning "SI 允许 Write Skew（经典陷阱）"
    Snapshot Isolation **不等于** Serializable。SI 按 Berenson 1995 的定义**能防 Lost Update**（同一行的写-写冲突由 first-committer-wins 规则检测），但**允许 Write Skew**——两事务写的是**不同行**，但决策依据的是同一 predicate 读。

    ```
    约束：两医生必须至少一人 on_call。初始 Alice, Bob 都 on_call。
    T1 read count(on_call)=2 → Alice 请假，SET Alice off_call → commit
    T2 read count(on_call)=2 → Bob 请假，SET Bob   off_call → commit
    两事务写不同行、无写-写冲突 → SI 下都成功 → 违反了"至少一人"约束
    ```

    Serializable（例如 Postgres 的 SSI）会检测到 T1/T2 间的读写依赖环，abort 其一。

    **在 SI 下防 Write Skew 的做法**：
    - **显式锁**：`SELECT ... FOR UPDATE` 把读变成写锁
    - **升级到 Serializable**：Postgres 的 SERIALIZABLE 用 SSI 检测
    - **物化约束**：把 predicate 变成一行（例如用一个 `on_call_count` 汇总行），让写 skew 退化成写-写冲突

    湖表 commit 路径也是 SI 级——并发 writer 通过 Catalog CAS 防写-写冲突，但跨表 / 跨 predicate 的 write skew 仍需业务层处理。

### 垃圾回收 / Vacuum

旧版本占空间，需要定期回收：

- Postgres `VACUUM`
- InnoDB 后台 purge 线程
- 湖表的 `expire_snapshots` / `vacuum`

GC 配得不好就"膨胀"——Postgres bloat 是经典问题。

## 在湖仓里

湖表的 [Snapshot](../lakehouse/snapshot.md) 就是 MVCC 思想的应用版：

- 每次 commit = 一个新的表级版本
- 读者固定读一个 Snapshot 不受写者影响
- `expire_snapshots` 就是 VACUUM
- 区别：传统 DB MVCC 粒度在**行**，湖表粒度在**文件 + 表快照**

这也是"湖仓为什么天生支持 [Time Travel](../lakehouse/time-travel.md)"的根源——旧版本**必然保留一段时间**。

### Iceberg 的 MVCC 如何落地

湖表的 MVCC 不能走"行级版本链"——对象存储不可原地改。实际实现：

1. **数据文件不可变**：要修改某行，写新文件（或写 delete file 标记）+ 原文件不动
2. **Manifest 引用集合**：每个 Snapshot = 一组 Manifest = 一组数据文件引用
3. **metadata.json 是指针**：当前表版本 = metadata.json 指向的 Snapshot ID
4. **commit = 原子替换指针**：写新 metadata.json + 通过 Catalog CAS 把"当前指针"切过去

```
T1 commit:  metadata.json v5 (snap_5, parent=snap_4)
             ↑ Catalog CAS: compare-and-set {v4 → v5}
T2 并发:    尝试 {v4 → v5'} → CAS 失败 → 重新基于 v5 rebase → 重试
```

**写冲突检测** = Catalog 层面的 CAS 冲突。这和传统 DB 用隐藏版本号做行级 MVCC 是同一思想的**粒度放大版**（从行 → 表快照）。

详见 [一致性模型](consistency-models.md) 的"湖表的快照隔离"段 与 [湖表](../lakehouse/lake-table.md)。

## 相关

- [Snapshot](../lakehouse/snapshot.md) —— 湖表版 MVCC
- [Time Travel](../lakehouse/time-travel.md)
- [一致性模型](consistency-models.md) —— SI / Serializable / Linearizable 的精确定义
- [湖表](../lakehouse/lake-table.md) —— Catalog CAS 在 commit 路径上的作用

## 延伸阅读

- **[*An Empirical Evaluation of In-Memory Multi-Version Concurrency Control*](https://www.vldb.org/pvldb/vol10/p781-Wu.pdf)** (VLDB 2017)
- **[PostgreSQL · MVCC 章节](https://www.postgresql.org/docs/current/mvcc.html)**
- **[*Serializable Snapshot Isolation* (SSI)](https://drkp.net/papers/ssi-vldb12.pdf)** (Ports & Grittner, VLDB 2012)
- **[Iceberg · Snapshot Spec](https://iceberg.apache.org/spec/#snapshots)** —— 湖表版 MVCC 的一手规范
