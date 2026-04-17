---
title: 平台 / 基础设施工程师
description: Catalog、权限、可观测性、成本、迁移 —— 平台视角的优先阅读
hide:
  - toc
---

# 平台 / 基础设施工程师 · 优先阅读清单

**你的主战场**：Catalog、治理、权限、K8s、成本、迁移、多租户。整个湖仓平台是否"长治久安"在你手里。

## 必读：平台骨架

- [存算分离](../foundations/compute-storage-separation.md)
- [对象存储](../foundations/object-storage.md)
- [一致性模型](../foundations/consistency-models.md)
- [统一 Catalog 策略](../unified/unified-catalog-strategy.md)
- [Catalog 全景对比](../compare/catalog-landscape.md)

## Catalog 系统

- [Hive Metastore](../catalog/hive-metastore.md)
- [Iceberg REST Catalog](../catalog/iceberg-rest-catalog.md)
- [Nessie](../catalog/nessie.md)
- [Unity Catalog](../catalog/unity-catalog.md)
- [Apache Polaris](../catalog/polaris.md)
- [Apache Gravitino](../catalog/gravitino.md)

## 运维核心

- [可观测性](../ops/observability.md)
- [性能调优](../ops/performance-tuning.md)
- [成本优化](../ops/cost-optimization.md)
- [安全与权限](../ops/security-permissions.md)
- [数据治理](../ops/data-governance.md)
- [故障排查手册](../ops/troubleshooting.md)
- [迁移手册](../ops/migration-playbook.md)

## 一体化架构

- [Lake + Vector 融合架构](../unified/lake-plus-vector.md)
- [Compute Pushdown](../unified/compute-pushdown.md)
- [案例拆解](../unified/case-studies.md)

## 引擎平面（知道每个的定位）

- [Trino](../query-engines/trino.md)
- [Apache Spark](../query-engines/spark.md)
- [Apache Flink](../query-engines/flink.md)
- [StarRocks](../query-engines/starrocks.md)
- [ClickHouse](../query-engines/clickhouse.md)

## ML 基础设施（支撑 AI 工作负载）

- [Model Registry](../ml-infra/model-registry.md)
- [Model Serving](../ml-infra/model-serving.md)
- [GPU 调度](../ml-infra/gpu-scheduling.md)

## 团队决策（ADR）

- [全部 ADR 列表](../adr/index.md)

## 对应场景

- [BI on Lake](../scenarios/bi-on-lake.md)
- [流式入湖](../scenarios/streaming-ingestion.md)

## 随时回头看

- [FAQ](../faq.md) · [术语表](../glossary.md)

## 你应该产出

- 新 ADR（决策留痕）
- 权限模型
- 成本月报
- 容量规划文档
- SLA 定义
