---
title: 湖仓表格式
description: Lakehouse 表格式的核心概念与主流实现
---

# 湖仓表格式

聚焦"建在对象存储上的表"——它怎么组织元数据、怎么做 ACID、怎么支持演化与时间旅行。

## 核心概念

- [湖表](lake-table.md) —— 为什么它和传统 DB 存储引擎不是一回事
- [Snapshot](snapshot.md) —— 快照如何让"时间旅行"成为可能
- [Manifest](manifest.md) —— 元数据的二层索引，湖表性能的基石
- [Schema Evolution](schema-evolution.md) —— 不重写历史就能改表结构
- [Time Travel](time-travel.md) —— 查过去某一时刻 / 版本的样子
- [Puffin](puffin.md) —— Iceberg 的辅助索引侧车文件（向量索引下沉的关键）

## 主流实现

- [Apache Iceberg](iceberg.md) —— 最"协议化"的湖表格式
- [Apache Paimon](paimon.md) —— 流式原生，LSM 骨架
- [Apache Hudi](hudi.md) —— 湖上 upsert 的先驱
- [Delta Lake](delta-lake.md) —— Databricks 主推

## 横向对比

- [DB 存储引擎 vs 湖表](../compare/db-engine-vs-lake-table.md)
- [Iceberg vs Paimon vs Hudi vs Delta](../compare/iceberg-vs-paimon-vs-hudi-vs-delta.md)

## 待补

- Streaming Upsert / CDC 专页
- Compaction / File Layout Optimization
- Partition Evolution
- Delete Files（Merge-on-Read 详解）
