---
title: 一致性模型
applies_to: "通用基础概念 · 长期稳定"
type: concept
level: B
tags: [foundations, distributed]
aliases: [Consistency Models, CAP]
related: [mvcc, object-storage, lake-table]
systems: [s3, spanner, iceberg]
status: stable
last_reviewed: 2026-04-18
---

# 一致性模型

!!! tip "一句话理解"
    "一致性"不是一个开关，也不是一把单线刻度——它有**两个维度**：
    **单对象** (linearizable / sequential / causal / RYW / eventual) 管"读到什么"，
    **事务** (serializable / snapshot isolation / RR / RC) 管"多操作怎么隔离"。
    SI 和 linearizable **不在同一把尺上**，Jepsen 的分类里 SI 和 serializable 也是 incomparable——SI 允许 write skew、serializable 不允许。

## 两条家族树（Jepsen 分类）

**单对象一致性**（强 → 弱）：Linearizable → Sequential → Causal → Read-your-writes → Eventual

**事务隔离级别**（强 → 弱）：Strict Serializable → Serializable → Snapshot Isolation / Repeatable Read → Read Committed → Read Uncommitted

SI 与 Serializable 互不蕴含——SI 允许 [write skew](mvcc.md)，Serializable 不允许；RR 则禁止 write skew 但允许某些 SI 不允许的异常。

| 级别 | 家族 | 一句话 | 代表系统 |
| --- | --- | --- | --- |
| **Linearizable** | 单对象 | 所有操作像排成一条线，顺序唯一 | Spanner、Raft/Paxos 后端、etcd |
| **Sequential** | 单对象 | 所有进程看到的顺序一致，但不必是实时线 | 早期某些分布式 DB |
| **Causal** | 单对象 | 有因果关系的操作顺序守住 | CouchDB、Cassandra 某些模式 |
| **Read-your-writes** | 单对象 | 自己写的自己能读到 | S3 今天 |
| **Eventual** | 单对象 | 最终一致，但何时到不保证 | S3 早期、DynamoDB 弱读 |
| **Serializable** | 事务 | 结果等价于某个串行顺序 | Postgres SERIALIZABLE (SSI)、Spanner |
| **Snapshot Isolation** | 事务 | 事务各自读固定快照，写冲突检测；**允许 write skew** | Postgres 默认（REPEATABLE READ 实为 SI）、Oracle、Iceberg / Delta |
| **Repeatable Read** | 事务 | 同一行多次读一致；**允许 phantom**（ANSI 定义） | MySQL InnoDB 默认 |

## 湖仓关心的三条

### 1. 对象存储的一致性

湖仓能工作的前提是对象存储提供：

- **Read-after-write**（S3 于 2020 强化为强一致）
- **LIST 强一致**（也是 2020 之后才有）
- **Conditional Write**（S3 2024-08 起，仅 `If-None-Match`——即"只在对象不存在时写"；没有 `If-Match`）

早年 S3 的最终一致让湖表 commit 路径必须绕弯：依赖外部 Catalog（HMS）做"当前指针"的 CAS。这是为什么老 Iceberg 文档总在讲"Catalog 里存 current metadata.json 指针"。

### 2. 湖表的快照隔离

一旦对象存储支持强一致，湖表天然是 **Snapshot Isolation**：

- 每次 commit 产生新 snapshot
- 读者读固定 snapshot，不受写者干扰
- 写冲突通过 Catalog CAS 检测（[MVCC · Iceberg 落地](mvcc.md) 有具体步骤）

**精确说明**：
- **单表内**：Iceberg / Delta 通过 Catalog CAS **全序化**所有 commit（严格单调递增的 snapshot ID）。这一维度可以算近似 Linearizable
- **跨表 / 跨 Catalog**：**没有** Linearizable 保证。两张表同时 commit，外部观察者看到的顺序可能不同
- **SI 的典型 gap**：SI 能挡 Lost Update（同一行写-写冲突），但**允许 Write Skew**——两事务写不同行但读相同 predicate 时。详见 [MVCC](mvcc.md) 里 "SI 允许 Write Skew" 段

```
SI vs Serializable 实际差异：
  两个事务 T1 / T2 都基于 snap_N 读，各自更新不同键：
    T1: UPDATE orders SET paid=true WHERE user='A'
    T2: UPDATE orders SET paid=true WHERE user='B'
  SI 下两 commit 都成功（不同行，不冲突）—— OK
  
  但：
    T1: INSERT INTO fraud_log SELECT * FROM orders WHERE amount > 10000
    T2: INSERT INTO orders (...)  ← 金额 = 50000
  基于 snap_N，T1 读不到 T2 的新行；两 commit 都成功
  但逻辑上应该 T1 要能看到 T2 → SI 下这是"写偏斜"（write skew），Serializable 会 abort 其一
```

湖表目前都是 SI 级别，写偏斜需要在业务层防。

### 3. 向量库的一致性

向量库因为异步索引构建，通常是 **读写最终一致**：

- Milvus：write 后有几秒可见延迟（可配）
- Qdrant：单点强一致，分布式下弱
- LanceDB：Fragment 提交后立即可见，但新索引构建异步

生产环境必须监控"写入 → 可查"的 lag。

## CAP 三选二的实际意义

CAP = Consistency / Availability / Partition tolerance。网络分区是现实（P 必选），所以是 **C vs A 取舍**。

- **CP 系统**：分区时宁可返错不给不一致结果（Spanner、多数 DB）
- **AP 系统**：分区时仍然服务，接受最终一致（Cassandra、DynamoDB 弱读、S3 早期）

湖仓主要依赖对象存储 —— **今天是 CP**（S3 强一致），历史 AP。这条路径改变了湖仓设计的可能性。

## 设计湖仓系统时的两条问法

1. **"commit 谁先"**：靠 Catalog 的 CAS；Catalog 本身要选 CP 后端
2. **"读到新写的数据"**：对象存储 read-after-write 保证；S3/GCS/OSS 都满足

## 陷阱

- **把"强一致"当成"零延迟"** —— 对象存储强一致不代表写完立即全球可见（跨区域复制有传播延迟）
- **向量库的"可见性"和"持久性"分开** —— 写成功不等于可查，要两个指标分别监控
- **多 writer 湖表** —— 没有合格 Catalog CAS 时强行并发写会产生丢失或孤儿文件

## 相关

- [对象存储](object-storage.md) —— 2024 Conditional Writes 如何改变湖仓 CAS 路径
- [MVCC](mvcc.md) —— SI 的行级 / 湖表级实现
- [湖表](../lakehouse/lake-table.md) · [Snapshot](../lakehouse/snapshot.md)

## 延伸阅读

- **《Designing Data-Intensive Applications》** (Kleppmann) —— 第 7 章 Transactions · 第 9 章 Consistency and Consensus
- **[*A Critique of ANSI SQL Isolation Levels*](https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/)** (Berenson et al., SIGMOD 1995) —— 隔离级别异常的权威定义（Lost Update · Write Skew · Phantom）
- **[*Consistency, Availability, and Convergence*](https://www.cs.cornell.edu/~lorenzo/papers/cac-tr.pdf)** (Peter Bailis et al., 2014)
- **[Jepsen · Consistency Models 图](https://jepsen.io/consistency)** —— 可视化层级结构
