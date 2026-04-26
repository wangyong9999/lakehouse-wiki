---
title: 参考资料 · 基础理论
type: reference
status: stable
tags: [reference, references, foundations]
description: 数据系统基础 / 列式 / MVCC / 分布式一致性 经典
last_reviewed: 2026-04-25
---

# 参考资料 · 基础理论

## 教科书 / 综述

- **[Designing Data-Intensive Applications](https://dataintensive.net/)** _(2017, book - Kleppmann)_ —— 数据系统圣经。覆盖存储引擎、复制、分区、事务、一致性、批/流处理等。
- **[Database Internals](https://www.databass.dev/)** _(2019, book - Petrov)_ —— 数据库内核深度。
- **[The Architecture of a Database System](https://www.cs.ucsb.edu/~tyang/class/240a17/refs/dbm.pdf)** _(2007, paper - Hellerstein et al.)_ —— 经典 DBMS 架构论文。

## 列式 / 文件格式

- **[C-Store: A Column-oriented DBMS](https://www.vldb.org/conf/2005/papers/p553-stonebraker.pdf)** _(2005, paper)_ —— 列式数据库奠基。
- **[Apache Parquet Format](https://parquet.apache.org/docs/file-format/)** _(official-doc)_ —— Parquet 文件格式 spec。
- **[Apache ORC Specification](https://orc.apache.org/specification/)** _(official-doc)_ —— ORC spec。
- **[Lance Format](https://lancedb.github.io/lance/)** _(official-doc)_ —— Lance 文件格式 + 多模 + 向量。

## MVCC / 一致性

- **[Snapshot Isolation - Generalized](https://dl.acm.org/doi/10.5555/645927.672171)** _(1995, paper - Berenson et al.)_ —— 隔离级别经典论文。
- **[A Critique of ANSI SQL Isolation Levels](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-95-51.pdf)** _(1995, paper - Berenson et al.)_ —— ANSI 隔离级别批判。
- **[Spanner: Google's Globally-Distributed Database](https://research.google/pubs/spanner-googles-globally-distributed-database/)** _(2012, paper)_ —— TrueTime + 分布式事务。

## 存算分离

- **[Building An Elastic Query Engine on Disaggregated Storage](https://www.usenix.org/conference/nsdi20/presentation/vuppalapati)** _(2020, paper - Snowflake)_ —— Snowflake 存算分离架构论文。
- **[Anna: A KVS For Any Scale](https://www.cs.cmu.edu/~pavlo/blog/2018/12/anna-a-kvs-for-any-scale.html)** _(2018, paper)_ —— 多策略一致性 KV。

---

**待补**：分布式系统更经典论文（Paxos / Raft / Calvin）；对象存储一致性模型综述
