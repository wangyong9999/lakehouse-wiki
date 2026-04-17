---
title: Iceberg vs Paimon vs Hudi vs Delta
type: comparison
tags: [comparison, lakehouse, table-format]
subjects: [iceberg, paimon, hudi, delta-lake]
status: stable
---

# Iceberg vs Paimon vs Hudi vs Delta

!!! tip "读完能回答的选型问题"
    四大湖表格式，我在 **BI 为主 / 流式 upsert 为主 / Databricks 生态 / 多引擎开放** 四种场景下到底该选哪个？

## 对比维度总表

| 维度 | Iceberg | Paimon | Hudi | Delta |
| --- | --- | --- | --- | --- |
| **主要生态** | 多引擎中立 | Flink 中心 | Spark 中心 | Databricks 中心 |
| **批分析** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **流式 upsert** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **CDC / Changelog** | 增量读 | 原生 changelog | Incremental Query | CDF（Change Data Feed）|
| **架构思路** | Manifest + Snapshot | LSM + Manifest | Timeline + CoW/MoR | 事务日志 + checkpoint |
| **Schema Evolution** | ⭐⭐⭐⭐⭐（列 ID）| ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Catalog 生态** | 最多（HMS/REST/Nessie/Unity/Polaris/Glue）| Flink / Hive | Hive / Glue | Databricks UC / HMS |
| **多引擎开放** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐（UniForm 改善中）|
| **社区治理** | Apache 中立 | Apache 中立 | Apache 中立 | LF AI（商业主导） |
| **AI 场景友好度** | 高（Puffin + 生态）| 中（LSM 适合流）| 中 | 高（Databricks 生态）|

## 每位选手的关键差异

### Iceberg

**最"协议化"**。整套 spec 独立于任何引擎，新增能力都以 spec 为先。多 Catalog 选项（HMS / REST / Nessie / Glue / Polaris / Unity）让它几乎能嵌入任何生态。Puffin 侧车文件为未来多模扩展预留了口子。

Iceberg 的定位就像 "TCP/IP 之于网络" —— 协议中立，谁都能接。

### Paimon

**流式原生**。LSM 骨架天然支持高吞吐 upsert，`input/lookup/full-compaction` 三种 Changelog 策略给了流式下游很强的灵活度。CDC 入湖 → Flink 流读 → 下游再做聚合——这条链路 Paimon 是最顺手的。

### Hudi

**流批湖仓的先驱**。CoW / MoR 两种表 + 三种查询类型（Snapshot / Read-Optimized / Incremental）组合灵活，但配置复杂度也最高。Spark 生态下老牌选择。

### Delta Lake

**Databricks 的主场**。和 Spark / UC 的集成是一等公民，Structured Streaming 写入、Change Data Feed、Liquid Clustering 都很成熟。UniForm 让一张 Delta 表能被 Iceberg 读取器识别，缓解"选哪个"的焦虑。

## 什么时候选谁

- **选 Iceberg 如果**
    - 你要"多引擎中立 + 面向未来的开放协议"
    - 要接入 Nessie / Polaris / Unity 等现代 Catalog
    - BI 分析 + AI 多模扩展都要考虑（Puffin 友好）

- **选 Paimon 如果**
    - 主负载是 Flink CDC 入湖 + 流批一体
    - 需要分钟级 upsert 新鲜度
    - 下游消费 changelog 是头等需求

- **选 Hudi 如果**
    - 已有 Spark 栈、需要 Incremental Query
    - 愿意接受较高的配置复杂度换 record-level 控制

- **选 Delta Lake 如果**
    - 在 Databricks 平台内
    - 主要引擎是 Spark Structured Streaming
    - 需要 Liquid Clustering / CDF 等已实用化的能力

## 混用 / 迁移路径

- **Iceberg + Paimon 双表**：热的流式 CDC 表放 Paimon；冷的批分析事实表放 Iceberg。两者可以共享 Catalog（同一 Nessie / HMS）
- **Delta → Iceberg**：通过 UniForm（Databricks 主推的元数据双写）或定期 export / re-register
- **Hudi → Iceberg**：需要数据重写；通常一次性迁移而非持续双写

## 相关

- 各系统页：[Iceberg](../lakehouse/iceberg.md) · [Paimon](../lakehouse/paimon.md) · [Hudi](../lakehouse/hudi.md) · [Delta](../lakehouse/delta-lake.md)
- [DB 存储引擎 vs 湖表](db-engine-vs-lake-table.md)

## 延伸阅读

- Onehouse / Tabular / Databricks 各自的对比博客（注意立场）
- *The Open Lakehouse Format Comparison* (独立测评)
