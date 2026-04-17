---
title: 首页
description: 多模一体化湖仓 · 支撑 AI+BI 负载 · 团队知识库
hide:
  - toc
---

# 多模一体化湖仓 · Wiki

面向数据湖上**多模检索 + 多模分析**（BI + AI 一体化）的团队知识库。
目标是让任一工程师在 30 秒内，找到一个概念、一个系统、一种对比，或一条学习路径。

---

## 三种心智入口

<div class="grid cards" markdown>

- :material-book-open-variant: **我想查一个概念**
  去 [术语表](glossary.md) 或直接进对应领域目录：
  [基础](foundations/index.md) · [湖仓](lakehouse/index.md) · [检索](retrieval/index.md) · [AI 负载](ai-workloads/index.md) · [BI 负载](bi-workloads/index.md)

- :material-compare-horizontal: **我想比较两样东西**
  去 [横向对比](compare/index.md)，例如
  [DB 存储引擎 vs 湖表](compare/db-engine-vs-lake-table.md)。

- :material-map-marker-path: **我是新人，给我一条路**
  去 [学习路径](learning-paths/index.md)，先跑
  [一周新人路径](learning-paths/week-1-newcomer.md)。

</div>

---

## 领域地图

| 方向 | 说明 | 入口 |
| --- | --- | --- |
| 基础 | 对象存储、文件格式、向量化执行、MVCC… | [foundations](foundations/index.md) |
| 湖仓表格式 | 湖表 / Snapshot / Manifest / Schema Evolution | [lakehouse](lakehouse/index.md) |
| 元数据与 Catalog | Hive / REST / Nessie / Unity / Polaris | [catalog](catalog/index.md) |
| 查询引擎 | Trino / Spark / Flink / DuckDB / StarRocks | [query-engines](query-engines/index.md) |
| 多模检索 | 向量数据库、ANN、Hybrid Search | [retrieval](retrieval/index.md) |
| AI 负载 | RAG / Feature Store / Embedding Pipeline | [ai-workloads](ai-workloads/index.md) |
| BI 负载 | OLAP 建模 / 物化视图 / 查询加速 | [bi-workloads](bi-workloads/index.md) |
| 一体化架构 | 湖 + 向量融合、统一 Catalog、多模建模 | [unified](unified/index.md) |
| 运维与生产 | 可观测性 / 成本 / 治理 | [ops](ops/index.md) |
| 研究前沿 | 论文笔记、趋势 | [frontier](frontier/index.md) |

---

## 跨向视图

- **[横向对比 `compare/`](compare/index.md)** —— 同层对象的硬比
- **[场景指南 `scenarios/`](scenarios/index.md)** —— 端到端叙事（BI on Lake、RAG on Lake…）
- **[学习路径 `learning-paths/`](learning-paths/index.md)** —— 时间维度的认知脚手架
- **[ADR `adr/`](adr/index.md)** —— 团队技术决策记录
- **[术语表 `glossary.md`](glossary.md)** —— 字母序兜底索引

---

## 参与贡献

见 [贡献指南](contributing.md)。一句话流程：**开 Issue 认领 → 按模板写页 → PR → CI 绿 + review 合格 → 自动发布**。
