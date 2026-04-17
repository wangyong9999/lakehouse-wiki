---
title: 一月 BI 方向路径
type: learning-path
tags: [learning-path, bi, olap]
audience: 完成新人路径后、想深入 BI / OLAP 方向的工程师
duration: 1 月
status: stable
---

# 一月 BI 方向路径

!!! tip "目标"
    一个月后能独立**设计并上线一个 BI on Lake 方案**：从数据建模、物化视图、查询加速、到加速副本选型，每一步都清楚 why，能给出 p95 预算和成本评估。

## 前置

- 已完成 [一周新人路径](week-1-newcomer.md)
- 写过 SQL（窗口、join、聚合至少熟练）
- 对 Iceberg / Parquet 有基本认识

## 节奏表

### Week 1 —— OLAP 建模与分层

- [ ] 读 [OLAP 建模](../bi-workloads/olap-modeling.md)
- [ ] 读 [湖表](../lakehouse/lake-table.md) / [Snapshot](../lakehouse/snapshot.md) / [Manifest](../lakehouse/manifest.md)
- [ ] 读 [Schema Evolution](../lakehouse/schema-evolution.md)
- [ ] 做：用 Spark / DuckDB 在一份公开零售数据（如 TPC-DS 小样本）上建 ODS / DWD / DWS / ADS 四层，把一张宽事实表落成 Iceberg 表
- [ ] 自测：画出从 ODS 到 ADS 的血缘图；说清每一层的粒度与目标 SLO

### Week 2 —— 查询加速三板斧

- [ ] 读 [查询加速](../bi-workloads/query-acceleration.md)
- [ ] 读 [Compaction](../lakehouse/compaction.md)
- [ ] 读 [物化视图](../bi-workloads/materialized-view.md)
- [ ] 做：对 Week 1 的 ADS 表跑 10 条典型 BI 查询，记录 p95；然后分别加分区、加排序、加物化视图，每一步都量出差异
- [ ] 自测：能用一句话回答"这条查询为什么现在快了"——分区剪枝？Zone Maps？MV 改写？

### Week 3 —— 引擎选型与加速副本

- [ ] 读 [Trino](../query-engines/trino.md) / [Spark](../query-engines/spark.md) / [DuckDB](../query-engines/duckdb.md) / [StarRocks](../query-engines/starrocks.md)
- [ ] 读 [BI on Lake](../scenarios/bi-on-lake.md) 场景
- [ ] 做：在 Trino 和 StarRocks 上跑同一组 BI 查询，对比延迟 / 并发表现；尝试 StarRocks 直读 Iceberg + 物化为本地表两种模式
- [ ] 自测：给出一份 "在什么场景下用 Trino、什么时候加 StarRocks / ClickHouse 加速副本" 的决策文档

### Week 4 —— 运维、成本、治理

- [ ] 读 [可观测性](../ops/observability.md) / [性能调优](../ops/performance-tuning.md) / [成本优化](../ops/cost-optimization.md)
- [ ] 读 [统一 Catalog 策略](../unified/unified-catalog-strategy.md)
- [ ] 读 [Unity Catalog](../catalog/unity-catalog.md) 或 [Iceberg REST Catalog](../catalog/iceberg-rest-catalog.md)
- [ ] 做：为 Week 1 的表族建一套监控 dashboard（查询 p95 / 数据新鲜度 / 小文件数 / MV 命中率 / 月度存储 $）
- [ ] 做：写一份 ADR，题目 "在我们场景下选 X 作为 BI on Lake 加速层"，引用上面所有材料

## 自测清单

- [ ] 能独立设计 ODS → ADS 分层并给出分区 / 排序策略
- [ ] 能量化评估加速手段：MV / Z-order / StarRocks 各自 ROI
- [ ] 能搭一套最小可用的监控
- [ ] 能做成本预估：给出每月存储 + 计算 + MV 额外开销的预算表
- [ ] 能识别并处理小文件、MV stale、慢查询三类典型问题

## 进阶

- 深读一篇 TPC-DS / TPC-H benchmark 的论文或测评博客
- 贡献一个"BI on Lake 选型 ADR" 到本 Wiki
- 尝试把团队一张最慢的仪表盘全链路优化，把结果写成场景页 PR
