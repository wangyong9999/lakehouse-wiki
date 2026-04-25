---
title: BI 负载
type: reference
status: stable
tags: [index, bi-workloads]
description: 湖仓上 OLAP / 仪表盘 / 指标中台 / BI × LLM 的工程机制
last_reviewed: 2026-04-20
---

# BI 负载

!!! tip "一句话定位"
    **"湖仓就是数仓"时代**——BI 负载从独立数仓迁到 Iceberg/Paimon 之上。本章讲**机制和原理**（建模 · 物化视图 · 查询加速 · 语义层 · 仪表盘 SLO · BI × LLM）· 不讲端到端场景编排（看 [BI on Lake 场景页](../scenarios/bi-on-lake.md)）。

!!! info "章节边界"
    - **本章（bi-workloads/）** · 单点机制：建模范式 · MV 算法 · 加速手段 · 语义层抽象 · SLO 设计 · BI 与 LLM 的结合
    - **[scenarios/bi-on-lake.md](../scenarios/bi-on-lake.md)** · 端到端场景：完整数据流 · 组件选型 · 运维闭环 · SLO 打法
    - **[scenarios/text-to-sql-platform.md](../scenarios/text-to-sql-platform.md)** · Text-to-SQL 作为独立平台场景 · 本章 `bi-plus-llm` 讲 Text-to-SQL 在 BI 里的位置
    - **[ai-workloads/](../ai-workloads/index.md)** · LLM/Agent 应用通用 · 本章只涉及"LLM 辅助 BI"这一特化
    - **[query-engines/](../query-engines/index.md)** · 引擎本身（Trino/Spark/StarRocks）· 本章引用而非重复
    - **[compare/olap-accelerator-comparison.md](../compare/olap-accelerator-comparison.md)** · 加速副本产品横比 · 本章讲"为什么要副本"机制 · 不讲 StarRocks vs Doris 细节

!!! abstract "TL;DR · BI 负载的六个核心机制"
    - **[OLAP 建模](olap-modeling.md)** · 星型/雪花/宽表/Data Vault · 湖仓时代宽表 + 星型混合主导 · SCD + Time Travel 融合
    - **[语义层](semantic-layer.md)** · 2023+ dbt SL/Cube 主流化 · **2026 成为 LLM × BI 的核心抓手**
    - **[物化视图](materialized-view.md)** · IVM 算法家族 · Iceberg MV spec 2025-2026 成熟中 · 查询改写机制
    - **[查询加速](query-acceleration.md)** · Clustering/Sort/Z-order · 二级索引（Puffin/Lance）· 加速副本作为机制
    - **[仪表盘 SLO](dashboard-slo.md)** · 并发 × QPS × p95 × 新鲜度的目标→手段映射 · Resource Group · Admission Control
    - **[BI × LLM](bi-plus-llm.md)** · 2026 最大变革 · Semantic Layer 作为 LLM Schema 抓手 · Auto-Narrative · Databricks Genie/Snowflake Cortex/Tableau GPT

## 本章学习路径

**Step 1 · 建模打底**（必读）
→ [OLAP 建模](olap-modeling.md) · 理解事实/维度/粒度/SCD · **之后一切的地基**

**Step 2 · 性能工程**
→ [查询加速](query-acceleration.md) → [物化视图](materialized-view.md) · 机制栈
→ [仪表盘 SLO](dashboard-slo.md) · 把机制映射到业务目标

**Step 3 · 治理与可扩展**
→ [语义层](semantic-layer.md) · 指标口径一致性 · 多 BI 消费

**Step 4 · 2026 AI 变革**
→ [BI × LLM](bi-plus-llm.md) · 语义层 × Text-to-SQL × Auto-Insight

**Step 5 · 端到端落地**
→ [BI on Lake 场景](../scenarios/bi-on-lake.md) · 把 Step 1-4 的机制组合成一套完整 BI 栈

## 建模 / 治理

- [**OLAP 建模**](olap-modeling.md) ⭐ · 星型/雪花/宽表/Data Vault 2.0 · 湖仓视角
- [**语义层 · Semantic Layer**](semantic-layer.md) ⭐ · dbt / Cube / LookML · 指标中台 · LLM × SL

## 加速 / 优化

- [**物化视图**](materialized-view.md) · IVM 算法家族 · Iceberg MV · StarRocks/Databricks 增量 MV
- [**查询加速**](query-acceleration.md) · Zone Maps · Clustering · Z-order · 二级索引 · 加速副本作为机制

## 工程实践

- [**仪表盘 SLO**](dashboard-slo.md) ⭐ · 并发/延迟/新鲜度目标 → 手段映射
- [**BI × LLM**](bi-plus-llm.md) ⭐ · 2026 变革 · Text-to-SQL/Auto-Narrative/AI Chart · Databricks Genie · Snowflake Cortex

## 相关

- **场景** · [BI on Lake](../scenarios/bi-on-lake.md) · [即席探索](../scenarios/ad-hoc-exploration.md) · [Text-to-SQL 平台](../scenarios/text-to-sql-platform.md) · [实时湖仓](../scenarios/real-time-lakehouse.md)
- **引擎** · [Trino](../query-engines/trino.md) · [Spark](../query-engines/spark.md) · [StarRocks](../query-engines/starrocks.md) · [DuckDB](../query-engines/duckdb.md) · [ClickHouse](../query-engines/clickhouse.md)
- **对比** · [OLAP 加速副本横比](../compare/olap-accelerator-comparison.md) · [计算引擎对比](../compare/compute-engines.md)
- **运维** · [性能调优](../ops/performance-tuning.md) · [多租户](../ops/multi-tenancy.md)
- **学习路径** · [一月 BI 方向](../learning-paths/month-1-bi-track.md)
