---
title: Changelog
description: 手册版本变更记录
hide:
  - toc
---

# Changelog

!!! note "关于日期"
    早期版本（v0.1 – v0.7）集中在同一天完成多轮推进，日期为当次 commit 时间而非真实迭代周期。手册进入稳定期后才采用月度 / 季度节奏。真实历史见 [commit log](https://github.com/wangyong9999/lakehouse-wiki/commits/main)。

## 2026-04-17 · v0.8 · 品牌化与一致性修复

**品牌**

- 站点改名 `Lakehouse + Multimodal Wiki` → **`Multimodal Lakehouse Handbook`**（"手册"替"Wiki"，去符号堆砌）
- 子标题统一：**多模一体化湖仓 · 面向 AI 与 BI 负载的工程手册**
- LICENSE 持有方同步更新

**一致性修复**

- 13 处"本 Wiki"、"Wiki 框架"、"Wiki 变更记录" 等行文改为"本手册" / "站点框架" / "手册变更记录"
- 首页 H1 调整：`多模一体化湖仓 · Wiki` → `多模一体化湖仓手册`
- 首页架构图：`rerank → mm` 改回合理流向（`rerank → mm / llm`）；新增 `iceberg → ann` 表明 Puffin 路径
- ADR 0001 标题：`作为 Wiki 框架` → `作为站点框架`（正文里对 GitHub Wiki / Outline 等具名系统保留原称）
- README 同步到 143 页现状，更新目录树（加 pipelines / ml-infra / roles / cheatsheets）

**说明**

- ADR 0001 正文里对 "GitHub Wiki"、"自托管 Wiki"、"富文本 Wiki" 等具名系统的称谓保留，那些是通用概念指代不是本站
- `lakehouse-wiki` 仓库名和 Pages URL 保持不变（迁移成本 > 收益）

## 2026-04-17 · v0.7 · 完善版：管线 / ML 基础设施 / 角色 / 速查

**新增目录**

- `pipelines/` —— 数据管线（入湖、多模预处理、编排）
- `ml-infra/` —— ML 基础设施（Model Registry / Serving / Training / GPU）
- `cheatsheets/` —— 速查单（Iceberg / ANN / 向量 SQL / Embedding）
- `roles/` —— 按角色入口（4 种角色 + index）

**新页**

- pipelines: `kafka-ingestion` / `bulk-loading` / `image-pipeline` / `video-pipeline` / `audio-pipeline` / `document-pipeline` / `orchestration`
- ml-infra: `model-registry` / `model-serving` / `training-orchestration` / `gpu-scheduling`
- ai-workloads: `prompt-management` / `rag-evaluation` / `agents-on-lakehouse` / `fine-tuning-data`
- foundations: `compute-storage-separation`
- lakehouse: `branching-tagging`
- ops: `migration-playbook` / `troubleshooting`
- frontier: `benchmarks`
- learning-paths: `quarter-advanced`（一季度资深路径）
- adr: `0004 Catalog 选型` / `0005 引擎组合`

**结构性调整**

- 首页加 "按角色入门" 链接
- 新目录在 nav 里加入
- glossary 新增 30+ 条

## 2026-04-17 · v0.6 · 系统性打底

- 首页重做（加整体架构图 + 6 张 grid 卡）
- 一体化扩容到 6 页（新增 `cross-modal-queries` / `compute-pushdown` / `case-studies`）
- 基础新增：`oltp-vs-olap` / `consistency-models` / `predicate-pushdown`
- 新增 `lakehouse/partition-evolution`
- Catalog 增 `gravitino`
- 查询引擎增 `clickhouse` / `doris`
- 检索增 `weaviate`
- 场景：新增 `offline-training-pipeline` / `feature-serving`
- 对比：`parquet-vs-orc-vs-lance` / `embedding-models`
- 运维：`security-permissions` / `data-governance`
- ADR: `0002 Iceberg` / `0003 LanceDB`
- Frontier seed: DiskANN paper note
- 顶层：`faq.md`

## 2026-04-17 · v0.5 · 核心要素补齐

- foundations: `vectorized-execution` / `mvcc` / `orc`
- lakehouse: `streaming-upsert-cdc` / `compaction` / `delete-files`
- catalog: `polaris`
- query-engines: `flink` / `starrocks`
- retrieval: `evaluation` / `diskann` / `qdrant` / `pgvector`
- ai-workloads: `embedding-pipelines` / `semantic-cache`
- bi-workloads: `olap-modeling` / `materialized-view` / `query-acceleration`
- ops: `observability` / `performance-tuning` / `cost-optimization`
- scenarios: `streaming-ingestion`
- learning-paths: `month-1-bi-track`
- compare: `catalog-landscape`

## 2026-04-17 · v0.4 · 多模核心打底

- foundations: `lance-format` / `columnar-vs-row`
- lakehouse 7 页：`manifest` / `schema-evolution` / `time-travel` / `puffin` + 系统页 `paimon` / `hudi` / `delta-lake`
- catalog: `hive-metastore` / `iceberg-rest-catalog` / `unity-catalog`
- query-engines: `trino` / `spark` / `duckdb`
- retrieval: `ivf-pq` / `embedding` / `multimodal-embedding` / `milvus` / `lancedb` / `rerank`
- ai-workloads: `feature-store`
- unified 3 页：`lake-plus-vector` / `multimodal-data-modeling` / `unified-catalog-strategy`
- compare: `iceberg-vs-paimon-vs-hudi-vs-delta` / `ann-index-comparison` / `vector-db-comparison`
- scenarios: `multimodal-search-pipeline` / `bi-on-lake`
- learning-paths: `month-1-ai-track`

## 2026-04-17 · v0.3 · 初始种子

- 首页、14 章节导览、术语表、贡献指南、6 类页面模板
- 14 页种子内容（湖表、向量数据库、HNSW、RAG、DB vs 湖表等）
- 1 条 ADR（选 MkDocs Material）
- CI 三条（markdownlint / mkdocs strict / lychee）

## 2026-04-17 · v0.1 · 骨架

- MkDocs Material + GitHub Pages 基础框架
- 14 目录占位 + 6 类模板 + deploy workflow + Issue/PR 模板

---

!!! note "版本号说明"
    只是粗粒度里程碑，不是语义化版本。真正的历史记录在 [commit log](https://github.com/wangyong9999/lakehouse-wiki/commits/main)。
