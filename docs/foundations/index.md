---
title: 基础
description: 存储、文件格式、计算、分布式等前置知识
---

# 基础

湖仓与多模检索系统的共同"石头地基"。先把这一节过掉，再读后面 Snapshot、ANN、向量化执行就不会卡壳。

## 已有

- [对象存储](object-storage.md) —— S3/GCS/OSS 语义、原子性与一致性
- [Parquet](parquet.md) —— 最主流的列式文件格式
- [ORC](orc.md) —— Hive 生态的列式格式，与 Parquet 平行
- [Lance Format](lance-format.md) —— 为多模 + 向量 + 随机访问重写的列式格式
- [列式 vs 行式存储](columnar-vs-row.md) —— 为什么湖仓 99% 选列式
- [向量化执行](vectorized-execution.md) —— 现代 OLAP 的核心技术
- [MVCC](mvcc.md) —— 多版本并发控制，湖仓 Snapshot 的思想源头

## 待补

- Avro
- OLTP vs OLAP
- 一致性模型（linearizable / sequential / eventual）
- 共识协议（Raft / Paxos 简述）
- SQL 优化器基础 / Codegen
