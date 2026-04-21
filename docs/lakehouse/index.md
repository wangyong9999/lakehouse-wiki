---
title: 湖仓表格式
description: Lakehouse 表格式的核心概念与主流实现
applies_to: Iceberg v2/v3, Paimon 1.4+, Hudi 1.0.2+, Delta 4.0+
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

## 建议阅读顺序

!!! tip "从"第一次接触湖表"到"能做选型"的分层路径"
    **必读主线（前 6 步顺序做）——读完能做湖表选型**：

    1. **[湖表](lake-table.md)** —— 先理解"建在对象存储上的表"到底是什么
    2. **[Snapshot](snapshot.md)** —— 最核心的机制；其他能力都是它的派生
    3. **[Manifest](manifest.md)** —— Snapshot 下一层的索引结构 · 湖表性能基石
    4. 按需读演化能力：[Schema](schema-evolution.md) / [Partition](partition-evolution.md) / [Time Travel](time-travel.md) / [Branching](branching-tagging.md)
    5. 上生产必读运维三件套：[Delete Files](delete-files.md) → [Compaction · 维护生命周期](compaction.md) → [Streaming Upsert / CDC](streaming-upsert-cdc.md)
    6. 对照实现选型：[Iceberg](iceberg.md) / [Paimon](paimon.md) / [Hudi](hudi.md) / [Delta](delta-lake.md)

    **可选扩展（做特定场景再翻）**：

    - 要做 BI 聚合加速 / AI Feature Store → [Materialized View](materialized-view.md)
    - 多模湖仓（向量 / 地理 / Variant / 图） → [多模湖仓](multi-modal-lake.md)

## 核心协议 · 表格式标准化能力（稳定）

- [湖表](lake-table.md) —— 为什么它和传统 DB 存储引擎不是一回事
- [Snapshot](snapshot.md) —— 快照如何让"时间旅行"成为可能
- [Manifest](manifest.md) —— 元数据的二层索引，湖表性能的基石
- [Schema Evolution](schema-evolution.md) —— 不重写历史就能改表结构
- [Partition Evolution](partition-evolution.md) —— 改分区策略也不重写历史
- [Time Travel](time-travel.md) —— 查过去某一时刻 / 版本的样子
- [Branching & Tagging](branching-tagging.md) —— Iceberg 原生分支 / 标签
- [Puffin](puffin.md) —— Iceberg 的辅助索引侧车文件

## 运维机制 · 写后要管的事（稳定）

- [Streaming Upsert / CDC](streaming-upsert-cdc.md) —— 流式变更持续入湖
- [Delete Files](delete-files.md) —— 行级删除背后的机制
- [Compaction](compaction.md) —— 小文件治理 · 含"生产维护生命周期"全景

## 扩展能力 / 前沿延伸 · 非协议核心（成熟度不一）

!!! info "成熟度声明"
    以下两页**不是**表格式协议的稳定核心能力：
    - **Materialized View** 主要是**引擎层实现**（Trino connector / Databricks 商业能力），spec 尚未标准化
    - **多模湖仓** 是**前沿方向**——向量 / 地理 / Variant / 图在湖表上的承载仍在演进

- [Materialized View](materialized-view.md) —— 湖上 MV · 引擎层实现为主 · Feature Store 雏形
- [多模湖仓](multi-modal-lake.md) —— 前沿 · 向量 / 地理 / Variant / 图 的湖表承载

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
