---
title: 基础
description: 存储、文件格式、计算、分布式等前置知识
---

# 基础

湖仓与多模检索系统的共同"石头地基"。如果你要理解后面章节里的 Snapshot、ANN、向量化执行，先把这一节过掉。

## 已有

- [对象存储](object-storage.md) —— S3/GCS/OSS 语义、原子性与一致性
- [Parquet](parquet.md) —— 最主流的列式文件格式

## 待补（欢迎认领）

- ORC / Avro / Lance Format
- 列式 vs 行式存储
- 向量化执行
- OLTP vs OLAP
- MVCC 与多版本并发
- 一致性模型（linearizable / sequential / eventual）
- 共识协议（Raft / Paxos 简述）
- SQL 优化器基础 / Codegen
