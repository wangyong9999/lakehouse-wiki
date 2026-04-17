---
title: MVCC（多版本并发控制）
type: concept
tags: [foundations, concurrency]
aliases: [Multi-Version Concurrency Control]
related: [snapshot, lake-table]
systems: [postgres, innodb, iceberg, delta]
status: stable
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

## 相关

- [Snapshot](../lakehouse/snapshot.md) —— 湖表版 MVCC
- [Time Travel](../lakehouse/time-travel.md)

## 延伸阅读

- *An Empirical Evaluation of In-Memory Multi-Version Concurrency Control* (VLDB 2017)
- PostgreSQL MVCC 章节
