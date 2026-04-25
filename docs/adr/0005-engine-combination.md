---
title: 0005 查询引擎组合：Spark + Trino + Flink + DuckDB（+ StarRocks 按需）
tags: [adr, decision, governance]
type: adr
status: accepted
date: 2026-04-17
deciders: [wangyong9999]
---

# 0005. 查询引擎组合

## 背景

湖仓事实表已定（[Iceberg + Paimon](0002-iceberg-as-primary-table-format.md)）。每个引擎擅长不同：Trino 交互、Spark 批、Flink 流、DuckDB 开发态、StarRocks MPP 加速。一次性选一个不现实。

## 决策

采用 **4 + 1 组合**：

- **Trino** —— 交互式 BI / 仪表盘 / 临时分析，**首选入口**
- **Spark** —— 重型批 ETL / ML 数据准备 / Bulk Load
- **Flink** —— 流入湖（Paimon 主力）+ 流式聚合
- **DuckDB** —— 开发态 / 单机探索 / CI 测试 / 轻量 API
- **StarRocks**（按需）—— 特定 BI 场景需要 **p95 < 1s** 时的加速副本

**不引入**：ClickHouse（与 StarRocks 重合）、Doris（与 StarRocks 同源）、Hive 作为计算引擎（只保留 HMS 作为过渡）。

## 依据

### Trino 作为 BI 前台

- 交互式查询第一梯队
- Iceberg Connector 成熟
- 联邦查询能力（跨 catalog）有用
- 运维相对 Spark 轻

### Spark 作为批主力

- 批 ETL / 大 shuffle 的标准
- Iceberg / Paimon / Delta native 集成
- 生态最广，迁移成本低
- 团队 Spark 栈历史积累深

### Flink 作为流主力

- Paimon 的一等公民
- 事件时间 / watermark 语义完整
- Flink CDC 覆盖我们入湖所有数据源

### DuckDB 作为开发态

- 本地跑 CI / 探索数据
- 零配置启动
- Python / notebook 友好
- 配合 `iceberg_scan()` / `delta_scan()` 直读湖表

### StarRocks 按需

- 不是默认选，只在 Trino 打不过的场景启用（仪表盘 p95 > 3s）
- 当作"加速副本层"，非权威数据源

### 为什么不 ClickHouse / Doris

- ClickHouse 单表强但 join 弱，不适合我们通用 BI
- Doris 和 StarRocks 同源功能高度重合，团队不支持两套并存

## 后果

**正面**：

- 覆盖所有主要查询场景
- 每个引擎有明确职责，不互相抢
- 读者 / 新人可以学习路径清晰

**负面**：

- 4+1 = 5 套引擎，运维总人力不低
- 多引擎 Catalog 配置要维护一致
- 性能监控要按引擎分别建

**后续**：

- 给每个引擎明确 SLA / 容量预算
- 统一通过 Iceberg REST Catalog 暴露
- 当 Unity Catalog / Polaris 落地，所有引擎切到统一 Catalog
- 评估 12 个月内 StarRocks 是否要升级为必选

## 相关

- 系统页：[Trino](../query-engines/trino.md) / [Spark](../query-engines/spark.md) / [Flink](../query-engines/flink.md) / [DuckDB](../query-engines/duckdb.md) / [StarRocks](../query-engines/starrocks.md)
- 对比：（待写）计算引擎对比
- [ADR-0002 Iceberg](0002-iceberg-as-primary-table-format.md) / [ADR-0004 Catalog](0004-catalog-choice.md)
