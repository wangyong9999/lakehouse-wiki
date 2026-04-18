---
title: 基础
description: 存储、文件格式、计算、分布式等前置知识
---

# 基础

湖仓与多模检索系统的共同"石头地基"。先把这一节过掉，再读后面 Snapshot、ANN、向量化执行就不会卡壳。

## 哲学 / 总论

- [**三代数据系统演进史**](data-systems-evolution.md) ⭐ —— 从关系数据库到数仓到湖仓的 50 年史
- [**Modern Data Stack 全景**](modern-data-stack.md) ⭐ —— 现代数据栈十大环节

## 存储基础

- [对象存储](object-storage.md) —— S3/GCS/OSS 语义、原子性与一致性
- [存算分离](compute-storage-separation.md) —— 现代湖仓的架构原语
- [Parquet](parquet.md) · [ORC](orc.md) · [Lance Format](lance-format.md) —— 三种列式格式
- [列式 vs 行式存储](columnar-vs-row.md)

## 计算基础

- [向量化执行](vectorized-execution.md) —— 现代 OLAP 的核心技术
- [谓词下推](predicate-pushdown.md) —— 湖仓性能的关键机制
- [MVCC](mvcc.md) —— 多版本并发控制，湖仓 Snapshot 的思想源头

## 分布式 / 并发

- [OLTP vs OLAP](oltp-vs-olap.md) —— 两种负载为什么物理底层相反
- [一致性模型](consistency-models.md) —— CAP / SI / Eventual 和湖仓的位置
- [事件时间 · Watermark · 乱序](event-time-watermark.md) —— 流处理的时间维度

## 生态协议

- [Arrow · FlightSQL · ADBC](arrow-ecosystem.md) —— 内存交换与传输的公共层

## 待补

- Avro
- 共识协议（Raft / Paxos 简述）
- SQL 优化器基础 / Codegen
