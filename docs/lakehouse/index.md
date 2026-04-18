---
title: 湖仓表格式
description: Lakehouse 表格式的核心概念与主流实现
---

# 湖仓表格式

聚焦"建在对象存储上的表"——它怎么组织元数据、怎么做 ACID、怎么支持演化与时间旅行。

!!! info "和 `foundations/` 的分界 · 湖表的物理底座"
    本节是**逻辑表协议层**（Snapshot / Manifest / CAS 提交 / Schema 演化 / 具体产品）。它**建在物理文件之上**——物理层（对象存储 + 列式文件 + 编码）归到 `foundations/`：

    - [对象存储](../foundations/object-storage.md) —— 湖表的地基（读写语义、CAS、Conditional PUT）
    - [Parquet](../foundations/parquet.md) · [ORC](../foundations/orc.md) —— Iceberg / Paimon / Hudi / Delta 最常用的数据文件格式
    - [Lance Format](../foundations/lance-format.md) —— 为多模 + 向量 + ML 训练重写的列式格式（也是 LanceDB 的底座）
    - [压缩与编码](../foundations/compression-encoding.md) · [列式 vs 行式](../foundations/columnar-vs-row.md) —— 文件内部的组织方式

    如果还没读过上面这些物理层，建议先过一遍 [基础模块的主线](../foundations/index.md)。

## 核心概念

- [湖表](lake-table.md) —— 为什么它和传统 DB 存储引擎不是一回事
- [Snapshot](snapshot.md) —— 快照如何让"时间旅行"成为可能
- [Manifest](manifest.md) —— 元数据的二层索引，湖表性能的基石
- [Schema Evolution](schema-evolution.md) —— 不重写历史就能改表结构
- [Partition Evolution](partition-evolution.md) —— 改分区策略也不重写历史
- [Time Travel](time-travel.md) —— 查过去某一时刻 / 版本的样子
- [Branching & Tagging](branching-tagging.md) —— Iceberg 原生分支 / 标签
- [Puffin](puffin.md) —— Iceberg 的辅助索引侧车文件
- [Streaming Upsert / CDC](streaming-upsert-cdc.md) —— 流式变更持续入湖
- [Compaction](compaction.md) —— 小文件治理，运维必修
- [Delete Files](delete-files.md) —— 行级删除背后的机制

## 主流实现

- [Apache Iceberg](iceberg.md) —— 最"协议化"的湖表格式
- [Apache Paimon](paimon.md) —— 流式原生，LSM 骨架
- [Apache Hudi](hudi.md) —— 湖上 upsert 的先驱
- [Delta Lake](delta-lake.md) —— Databricks 主推

## 横向对比

- [DB 存储引擎 vs 湖表](../compare/db-engine-vs-lake-table.md)
- [Iceberg vs Paimon vs Hudi vs Delta](../compare/iceberg-vs-paimon-vs-hudi-vs-delta.md)
- [Parquet vs ORC vs Lance](../compare/parquet-vs-orc-vs-lance.md)

## 团队决策

- [ADR-0002 选择 Iceberg 作为主表格式](../adr/0002-iceberg-as-primary-table-format.md)

## 速查

- [Iceberg 速查](../cheatsheets/iceberg.md)
