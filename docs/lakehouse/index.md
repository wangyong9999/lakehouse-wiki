---
title: 湖仓表格式
description: Lakehouse 表格式的核心概念与主流实现
---

# 湖仓表格式

聚焦"建在对象存储上的表"——它怎么组织元数据、怎么做 ACID、怎么支持演化与时间旅行。

## 核心概念

- [湖表](lake-table.md) —— 为什么它和传统 DB 存储引擎不是一回事
- [Snapshot](snapshot.md) —— 快照如何让"时间旅行"成为可能

## 主流实现

- [Apache Iceberg](iceberg.md)

## 待补

- Apache Paimon / Hudi / Delta Lake 系统页
- Manifest / Manifest List 专页
- Schema Evolution / Partition Evolution
- Streaming Upsert / CDC
- Compaction / File Layout Optimization

## 横向对比

- [DB 存储引擎 vs 湖表](../compare/db-engine-vs-lake-table.md)
