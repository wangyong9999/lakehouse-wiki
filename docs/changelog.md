---
title: Changelog
type: reference
status: stable
tags: [reference, changelog]
description: 手册版本变更记录
hide:
  - toc
---

# Changelog

!!! note "关于日期"
    早期版本（v0.1 – v0.7）集中在同一天完成多轮推进，日期为当次 commit 时间而非真实迭代周期。手册进入稳定期后才采用月度 / 季度节奏。真实历史见 [commit log](https://github.com/wangyong9999/lakehouse-wiki/commits/main)。

## 2026-04-25 · T2 治理收尾 · 长期参考库 + 章节组织声明 + 元数据深化

**P1 · ADR-0011 同步**：补 ADR/index.md 已有列表（漏加修正）

**P2 · related slug 修复**：8 处失效 slug 修正（含我 P6 自身的 lance vs lance-format bug）；YAML field 解析改用精确分隔符避免贪婪 bug

**P3 · 长期参考库 + 章节组织声明（最大头）**：
- 新增 `docs/references/<chapter>/` 目录结构 + 13 章 references 索引
  - 6 章 bootstrap 含完整起步内容（lakehouse / retrieval / ai-workloads / ml-infra / catalog / ops）
  - 7 章占位含基础起步条目（foundations / query-engines / bi-workloads / pipelines / scenarios / cases / unified）
- 新 ADR-0012 治理 references 长期维护规范（每条带类型 + 价值描述 + 辩证标注：工业验证 / 仅论文 / 厂商主张）
- 修订 ADR-0011：从"X 轴"抽象标签 → "子组 + 一句话定位"实用格式
  - **辩证发现**：原"主题+产品双层轴"等抽象标签反而增加认知负担，读者要的是直接看子组
- 13 章 index.md 统一加"本章组织"admonition · 列子组 + 关键页 + 指向对应 references/
- nav 加"参考资料库"子菜单（在"速查与索引"组下）

**P4 · depth 字段补 13 页**：foundations 入门/进阶 / scenarios 资深 / compare/query-engines 进阶 · 启发式

**外部权威验证**（按本轮新增方法论）：
- LangChain / LlamaIndex 官方文档结构与 ai-workloads/ 三层组织 cross-check
- Google MLOps 成熟度模型与 ml-infra/ 三组分布对齐
- Apache Iceberg 官方 docs 结构与 lakehouse/ 五组接近
- 直接用 WebFetch 拉取，避免凭模型记忆写

**辩证修正记录**：
- T2-P4 (level 审视) 取消：hooks/page_badges 验证发现 level 是纯元数据无 UI 消费，原计划价值低 → 替换为 depth 补齐（depth 才是真 UI 字段）
- prerequisites 缺 172 页跳过：必须逐页判断真前置，不能批补
- aliases / systems / level 字段：跳过（纯元数据，无 UI 消费，价值低）
- tag 长尾砍：T1 已辩证否决（产品名合法）
- 自身 bug 揭露：P2 第一次正则贪婪导致 27 文件误改 → 立即回退 + 用精确分隔符重做

**总计**：5 commits · 影响 ~50 文件改动 · 14 个新文件（ADR-0012 + 13 references 索引）· 全程 mkdocs build --strict 通过

## 2026-04-25 · T1 治理大改造 · 元数据 + 边界 + 导航 + 章节规范

**P1 · 信息架构 / 导航**

- 主菜单提升「速查与索引」组：FAQ / 术语表 / 横向对比索引 / 按技术栈索引 / 按 Tag 浏览（原埋附录第 50+ 位 → 第 3 大菜单组）
- 4 个入口 index.md（roles / learning-paths / scenarios / cases）顶部统一加 5 维交叉链 admonition
- 一体化架构 nav 标题改为「一体化架构 · 跨章决策中心」，明示作用

**P2 · 模块边界清理**

- materialized-view 双份对称 admonition（lakehouse 协议视角 / bi-workloads BI 视角，各为 canonical）
- RAG canonical 标定 = `ai-workloads/rag.md` 范式总论；satellites（`scenarios/rag-on-lake.md` 工程实践、cases/* 公司切面）加 admonition 指回
- ADR-0006 加条款锚定 unified/ 极窄设计是 feature 不是塌陷
- contributing.md 加「新内容归属决策 5 问」+ scenarios/cases 边界规则

**P3 · Frontmatter 机械补**

- 84 页按类别批补 type/status/tags/applies_to
  - ADR / META / index 页 → reference 类型 + chapter tag
  - foundations → applies_to「通用基础概念 · 长期稳定」
  - scenarios → applies_to「2024-2026 工业实践」
  - 其余技术页 → applies_to「2024-2026 主流」

**P4 · level 字段补 44 页**

- 启发式：行数 + 章节角色（cases/scenarios 偏 S · foundations/compare 偏 B · 其余按行数）
- 覆盖率 63% → 80%

**P5 · tag 治理（保守归并）**

- 13 处同义词归并（vector-database → vector · mlops → ml-infra · multi-modal → multimodal 等）
- **辩证发现**：原以为「386 tag 失控」，深入看发现 87% 长尾是合法产品名（vllm / ragas / langfuse / mcp 等）· 不该删 · 只做同义归并 · 405 → 395

**P6 · related 字段补 44 页**

- 章节启发式：compare 解析 filename 提取对比对象 · system 页用同章兄弟 + canonical 概念 · ai-workloads 用同章相邻
- slug 修正：catalog-strategy → strategy 等

**P7 · glossary 扩充 18 个高频缺词**

- 新增：AQE / Backfill / Bin-packing / Bloom Filter / CBO / Data Contract / Data Lineage / Dedupe / Iceberg v3 / Incident Management / Lakehouse / OpenLineage / PII / RBAC / SCD / Schema Drift / Semantic Layer / SLA·SLO·SLI / Snapshot Isolation / Star Schema
- 160 → 180 条目；保持「指向型反查索引」性质（非定义型）

**P8 · 章节组织规范**

- 新 ADR-0011：章节内部组织模式 · 显式声明轴 + 不强求统一
- 不同章节按其领域内在结构组织（抽象层轴 / 生命周期轴 / 关注点轴 / 主题+产品轴 等）· 但 index.md 必须显式声明本章组织轴
- contributing.md 加「季度自检 5 问」（过时 / canonical 漂移 / 章节组织 / 元数据 / 死链）

**辩证修正记录**

- B2 unified/ 章节原计划「彻底废除」· 深读后发现是 [ADR-0006](adr/0006-chapter-structure-dimensions.md) 极严格归属验证的设计成果（跨章 orchestrator + 6 维地图 + 团队路线主张）· 改为「保留 + 防误解声明」
- D1 tag 失控原以为要大幅删长尾 · 深查发现长尾多是合法产品名 · 改为保守同义归并

**总计**：9 commits · 影响 ~250 文件改动 · 不破坏内容 · 全程 mkdocs build --strict 通过

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
- `cheatsheets/` —— 速查单（2026-04 S39 按主题归属合并到对应机制页 · 废除此目录）
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
