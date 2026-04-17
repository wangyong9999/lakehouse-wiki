---
title: 一致性模型
type: concept
tags: [foundations, distributed]
aliases: [Consistency Models, CAP]
related: [mvcc, object-storage, lake-table]
systems: [s3, spanner, iceberg]
status: stable
---

# 一致性模型

!!! tip "一句话理解"
    "一致性"不是一个开关，是**一把标尺**：从最严的 linearizable（像单机）到最松的 eventual（终究会到），中间有 sequential、causal、snapshot 等。湖仓和对象存储的能力都在这把尺子上某个位置。

## 常见层级（由严到松）

| 级别 | 一句话 | 代表系统 |
| --- | --- | --- |
| **Linearizable** | 所有操作像排成一条线，顺序唯一 | Spanner、Raft/Paxos 后端 |
| **Sequential** | 所有进程看到的顺序一致，但不必是实时线 | 早期某些分布式 DB |
| **Snapshot Isolation** | 事务各自读一个固定快照，写冲突检测 | Postgres、MySQL InnoDB、Iceberg |
| **Causal** | 有因果关系的操作顺序守住 | CouchDB、Cassandra 某些模式 |
| **Read-your-writes** | 自己写的自己能读到 | S3 今天 |
| **Eventual** | 最终一致，但何时到不保证 | S3 早期、DynamoDB 弱读 |

## 湖仓关心的三条

### 1. 对象存储的一致性

湖仓能工作的前提是对象存储提供：

- **Read-after-write**（S3 于 2020 强化为强一致）
- **LIST 强一致**（也是 2020 之后才有）
- **Conditional Write**（S3 2024 之后）

早年 S3 的最终一致让湖表 commit 路径必须绕弯：依赖外部 Catalog（HMS）做"当前指针"的 CAS。这是为什么老 Iceberg 文档总在讲"Catalog 里存 current metadata.json 指针"。

### 2. 湖表的快照隔离

一旦对象存储支持强一致，湖表天然是 **Snapshot Isolation**：

- 每次 commit 产生新 snapshot
- 读者读固定 snapshot，不受写者干扰
- 写冲突通过 Catalog CAS 检测

这等于传统 DB 的 SI，够用了。湖表**不提供 Linearizable**——没有"同一毫秒的两条 commit 谁先谁后"精确定义。

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

- [对象存储](object-storage.md)
- [MVCC](mvcc.md)
- [湖表](../lakehouse/lake-table.md)
- [Snapshot](../lakehouse/snapshot.md)

## 延伸阅读

- *Designing Data-Intensive Applications* (Kleppmann) —— 第 9 章
- *Consistency, Availability, and Convergence* (Peter Bailis 等, 2014)
