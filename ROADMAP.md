# 手册深度提升计划 · Roadmap

> 本文档是手册的**内部提升计划**，不随站点发布。
> 跟踪"从知识导航升级到方案评审水位"的分阶段迭代。

---

## 背景 · 为什么需要这个计划

手册已覆盖 16 章节 / 158 页 / ~19,000 行，结构完整、业务场景闭环、横向对比齐备。

但资深工程师做**方案评审**时仍不够用——
- 核心底座页（`lakehouse/` / `retrieval/` / `query-engines/` / `catalog/`）平均只有 60-90 行
- 缺**原理深度 + 工程细节 + 性能数字 + 代码示例**
- 缺"没有这个技术世界会怎样"的反面论证（布道利器）
- 前沿主题（LLM / RAG / vector trends / AI 治理）覆盖浅
- 深度案例库薄弱，成了"总结性描述"而非"工业蓝图"

## 指导原则

1. **深度优先于广度**——先把核心页深度打到方案评审水位，再扩主题
2. **分级达标**而非一刀切——不是每页都要 250 行
3. **结构性改造先行**（模板 / benchmark 数字页 / 按技术栈索引）
4. **放弃完美覆盖**——明确"不做"清单防 scope creep
5. **每批 PR 可审、可回退、strict build 通过**

---

## 页面分级（达标线）

| 级别 | 定义 | 目标行数 | 交付结构 |
|---|---|---|---|
| **S 级（核心资产）** | 每次方案评审必查、新人必读 | 300-400 | 8 段完整骨架（见 S1） |
| **A 级（重要主题）** | 资深工程师常需深入 | 180-280 | 骨架 6 段 + 代码示例 |
| **B 级（维持水位）** | 参考型 / 介绍型 | 80-140 | 骨架 4 段即可 |
| **C 级（索引 / 导航）** | index / tags / glossary | 按需 | 结构清晰即可 |

---

## Round 1 · 核心深度拉齐（最高优先级）

### R1 · S1 结构模板升级（贯穿前置 · 先做）

在 `_templates/concept.md` 和 `_templates/system.md` 里定一个 **8 段骨架**：

1. 标题 · TL;DR · 一句话定位
2. **业务痛点**："没有这个技术世界会怎样"（反面论证）
3. **原理深度**（数学 / 协议 / 算法）
4. **工程细节**（参数 / 配置 / 实战经验）
5. **性能数字**（Benchmark 基线 / 量级曲线）
6. **代码 / SQL 示例**（可复制跑）
7. **陷阱与反模式**
8. **横向对比 + 延伸阅读**

S 级必须 8 段全；A 级可以压缩 3/4/5 为一段；B 级可以省 5/6。

### R1A · S 级核心资产深化（15 页）

**R1A.1 表格式底座（4 页 · S 级）**
- [ ] `lakehouse/lake-table.md` —— 湖表哲学总论（300+ 行）
- [ ] `lakehouse/iceberg.md` —— 含提交协议、CAS 实现、Puffin 细节（350+ 行）
- [ ] `lakehouse/paimon.md` —— LSM on S3 的合并代价模型（300+ 行）
- [ ] `lakehouse/snapshot.md` —— MVCC on Object Store（250+ 行）

**R1A.2 检索核心（4 页 · S 级）**
- [ ] `retrieval/hnsw.md` —— 算法数学推导 + filter-aware 三流派（300+ 行）
- [ ] `retrieval/vector-database.md` —— 工业定义 + 选型哲学（300+ 行）
- [ ] `retrieval/hybrid-search.md` —— RRF / LTR / 学习融合（250+ 行）
- [ ] `retrieval/rerank.md` —— Cross-Encoder 原理 + 模型对比（250+ 行）

**R1A.3 引擎核心（3 页 · S 级）**
- [ ] `query-engines/trino.md` —— 架构 / 执行 / 调优 / 坑（300+ 行）
- [ ] `query-engines/spark.md` —— AQE / Catalyst / 湖上写入（300+ 行）
- [ ] `query-engines/flink.md` —— 状态 / 检查点 / Paimon 集成（300+ 行）

**R1A.4 AI 核心能力（2 页 · S 级）**
- [ ] `ai-workloads/rag.md` —— 从论文到生产（300+ 行，对齐 scenarios 版）
- [ ] `ai-workloads/feature-store.md` —— PIT / 训推一致 / 架构（350+ 行）

**R1A.5 Catalog 核心（2 页 · S 级）**
- [ ] `catalog/iceberg-rest-catalog.md` —— REST 协议 + Commit 语义（250+ 行）
- [ ] `catalog/unity-catalog.md` —— 三层模型 + 开源化（250+ 行）

### R1B · A 级补强（15 页 · R1 后半段）

- [ ] `lakehouse/hudi.md` / `lakehouse/delta-lake.md` / `lakehouse/manifest.md` / `lakehouse/streaming-upsert-cdc.md`
- [ ] `retrieval/ivf-pq.md` / `retrieval/diskann.md` / `retrieval/embedding.md` / `retrieval/multimodal-embedding.md`
- [ ] `query-engines/duckdb.md` / `query-engines/starrocks.md` / `query-engines/clickhouse.md`
- [ ] `ai-workloads/embedding-pipelines.md` / `ai-workloads/agents-on-lakehouse.md`
- [ ] `catalog/nessie.md` / `catalog/polaris.md`

---

## Round 2 · 前沿扩主线

### R2.1 · 压轴总论（4 新页 · S 级）
- [ ] `frontier/data-systems-evolution.md` —— 三代数据系统演进史（数据库→数仓→湖仓）
- [ ] `frontier/modern-data-stack.md` —— MDS 全景（Airbyte/Fivetran/dbt/Airflow/Reverse ETL）
- [ ] `ai-workloads/mlops-lifecycle.md` —— 数据→训练→评估→上线→监控闭环
- [ ] `ai-workloads/mcp.md` —— Anthropic MCP 协议深度

### R2.2 · 新增横向对比（3 页）
- [ ] `compare/streaming-engines.md` —— Flink / Spark Streaming / Kafka Streams / RisingWave
- [ ] `compare/rerank-models.md` —— bge-reranker / Cohere Rerank / Jina
- [ ] `compare/orchestrators.md` —— Airflow / Dagster / Prefect / DolphinScheduler

### R2.3 · 前沿深度专题（4 页）
- [ ] `frontier/llm-inference-opt.md` —— vLLM / Flash Attn / Speculative / MoE
- [ ] `frontier/rag-advances-2025.md` —— CRAG / Self-RAG / Agentic RAG / Contextual Retrieval
- [ ] `frontier/vector-trends.md` —— Matryoshka / Binary Embedding / SPLADE-v3 / ColBERT-v2
- [ ] `frontier/ai-governance.md` —— EU AI Act / Guardrails / Red Teaming

### R2.4 · 合规 & 经济学（2 页）
- [ ] `ops/compliance.md` —— GDPR / HIPAA / PDPA / 个保法 / 跨境
- [ ] `ops/tco-model.md` —— TCO 模型 + 自建 vs 云 vs SaaS

### R2.5 · 场景补齐（3 页）
- [ ] `scenarios/text-to-sql-platform.md`
- [ ] `scenarios/ad-hoc-exploration.md`
- [ ] `scenarios/classical-ml.md`

---

## Round 3 · 案例 / 可视化 / 实操

### R3.1 · 深度案例（3 页 · 每 400-600 行）
- [ ] `cases/netflix-data-platform.md`
- [ ] `cases/linkedin-venice-pinot.md`
- [ ] `cases/uber-platform.md`

### R3.2 · 精工 SVG（10 张）
- [ ] Iceberg 提交流程 / Paimon LSM / HNSW 分层 / Hybrid 融合 / 双塔模型 / Feature Store 流 / MCP 架构 / RAG 五表 / Catalog 三层 / Lakehouse 演进时间轴

### R3.3 · 可运行教程（3 个优先）
- [ ] `tutorials/recommender-on-lake.md`
- [ ] `tutorials/feature-store-setup.md`
- [ ] `tutorials/mcp-agent-demo.md`

### R3.4 · 治理与反模式（2 页）
- [ ] `ops/anti-patterns.md` —— 湖仓建设 20 反模式整合
- [ ] `ops/capacity-planning.md`

### R3.5 · 索引与术语
- [ ] `glossary.md` 大幅扩充 + 中英对照
- [ ] `index-by-technology.md` 按技术栈导航
- [ ] `frontier/benchmark-numbers.md` 量级数字总汇（S2 贯穿）

---

## 贯穿性改造 S1-S5

- **S1 模板升级** —— R1 前置完成（见上）
- **S2 Benchmark 数字页** —— 与 R1 同步，累计页面 benchmark 时更新
- **S3 按技术栈 / 按业务产出 导航** —— R3 推
- **S4 版本 / 时效标注** —— R1A 新写时带上，旧页 R2 时批量补
- **S5 学术严谨度** —— R1 每页至少 1-2 篇权威引用 + R3 论文笔记系列

---

## 放弃做清单（防 scope creep）

- ❌ 英文版翻译（团队中文主力）
- ❌ 占位页 / 空目录（稀释信噪比）
- ❌ 详尽每家云厂商对比（保留横向对比即够）
- ❌ 把入门教程做成 OReilly 书（保持 60 分钟 tutorial 定位）
- ❌ 每页硬撑 300+ 行（分级达标，B 级页保持精简）
- ❌ 深度案例 5+ 家（3 家有代表性够）
- ❌ SVG 20+ 张（10 张核心够）

---

## 量级预估

| Round | 页面数 | 新增行数 | 周数 | 备注 |
|---|---|---|---|---|
| R1A · 核心资产 | 15 | ~4000 | 2 | 最高 ROI |
| R1B · A 级补强 | 15 | ~3000 | 1.5 | 可延期 |
| R2 · 前沿扩主线 | 16 | ~4500 | 2 | |
| R3 · 案例/SVG/实操 | 13 + 10 SVG | ~3500 | 1.5 | |
| **合计** | **~59 页** | **~15,000 行** | **7 周** | |

---

## 执行状态

- [x] R0 · 业务场景深化已完成（recommender / fraud / CDP / RAG / BI / FS / OLAP）
- [x] R1.S1 · 模板骨架升级
- [x] **R1A · 核心 S 级资产 15 页深化** (lake-table / iceberg / paimon / snapshot / hnsw / vector-database / hybrid-search / rerank / trino / spark / flink / rag / feature-store / iceberg-rest-catalog / unity-catalog)
- [x] **R1B 精选 · 6 页 A 级深化** （hudi / delta-lake / manifest / streaming-upsert-cdc / ivf-pq / diskann）
- [x] **R2.1 · 压轴总论 4 页** (data-systems-evolution / modern-data-stack / mlops-lifecycle / mcp)
- [x] **R2.2 · 新增横向对比 3 页** (streaming-engines / rerank-models / orchestrators)
- [x] **R2.3 · 前沿专题 4 页** (llm-inference-opt / rag-advances-2025 / vector-trends / ai-governance)
- [x] **R2.4 · 合规 + TCO 2 页** (compliance / tco-model)
- [x] **R2.5 · 场景补齐 3 页** (text-to-sql-platform / ad-hoc-exploration / classical-ml)
- [x] **S2 · Benchmark 数字总汇页**
- [x] **R3.1 · 深度案例 3 页** (case-netflix / case-linkedin / case-uber)
- [x] **R3.4 + R3.5 · 反模式 / 容量 / 索引** (anti-patterns / capacity-planning / glossary 扩充 / index-by-technology)
- [ ] R3.2 · 精工 SVG 10 张（**延后**，ROI 边际）
- [ ] R3.3 · 可运行教程 3 个（**延后**，改为 playbook 更合适）

### N 轮（辩证性优化 + 新价值）

- [x] **N1 · 5 章节 index.md 同步 + FAQ 补强**
- [x] **N2 · 辩证性强化** —— 给 MCP / RAG 前沿 / 向量前沿 / LLM 推理优化 加"现实检视"段落反 hype
- [x] **N3 · R1B 精选 6 页 A 级深化**（见上）
- [x] **N4 · 3 个新高价值页**：
  - `ops/sla-slo.md` —— 数据 SRE / DRE 体系
  - `frontier/vendor-landscape.md` —— 客观厂商格局
  - `compare/sparse-retrieval.md` —— BM25 / SPLADE / ColBERT / Elser
- [x] **N5 · 章节 index + nav 同步**

### F 轮（深度审视 → 精准修复）

- [x] **F1 · 首页改造** —— 18 个 ⭐ 精华分 4 组突出 + index-by-technology 入链
- [x] **F2 · FAQ 补 8 条** —— MCP / Semantic / Gateway / v3 / SLO / Data Contract / RAG 提效 / 厂商锁定
- [x] **F3 · 辩证性精准降温 8 处** —— LLM Gateway / Hybrid / Sparse / Streaming / OLAP / Rerank / Lake Table / Qdrant 的 hype 表达条件化
- [x] **F4 · last_reviewed 批量回填 41 页**
- [x] **F5a · 四表格式对比升 A 级** (84 → 230+ 行) · 含 2024-2026 重大事件（Databricks 收购 Tabular 等）+ 决策矩阵 + 现实检视
- [x] **F5b · 向量库对比升 A 级** (110 → 290+ 行) · 新增 Pinecone + 决策树 + 市场变化
- [x] **F5c · ANN 索引对比升 A 级** (108 → 340+ 行) · 新增 Binary Embedding + 分层检索策略
- [x] **命名去年份化**：全站"2025 前沿" → "前沿" · "2025 视角" → "2026 视角"（11 页）

### M 轮（最优方案精选补强 + 运营奠基）

- [x] **M1 · 真空补齐 5 页**：
  - `bi-workloads/olap-modeling.md` 118→500+ 行 A 级
  - `bi-workloads/semantic-layer.md` 新增 A 级
  - `ml-infra/llm-gateway.md` 新增 A 级
  - `catalog/nessie.md` 升 A 级
  - `catalog/polaris.md` 升 A 级
- [x] **M2 · AI 场景薄页升 A 级**：
  - `scenarios/feature-serving.md` 升 300+ 行
  - `scenarios/offline-training-pipeline.md` 升 400+ 行
- [x] **M3 · Iceberg v3 预览**：
  - `frontier/iceberg-v3-preview.md` 新增
- [x] **M4 · 运营机制奠基**：
  - `docs/contributing.md` 重写含 frontmatter 规范 + 运营节奏
  - `.github/ISSUE_TEMPLATE/outdated.yml` 新增
  - `.github/ISSUE_TEMPLATE/discussion.yml` 新增
  - `.github/CODEOWNERS` 完善分域 owner 结构
- [x] **M5 · nav + index 同步**

**交付累计**（四轮）：
- **核心深化 32 页**（15 S + 6 A + 8 A + 3 大对比，约 8400 行）
- **新增内容 29 页**（S/A 级，约 8800 行）
- **辩证性强化 + 现实检视** 贯穿 14 页（N2 · F3 · F5a/b/c 等）
- **运营机制奠基**（frontmatter 规范 · Issue 模板 · CODEOWNERS · **last_reviewed 回填 41 页**）
- **命名去年份化** 11 页（2025 前沿 → 2026 视角）
- **首页 + FAQ** 大改（18 个 ⭐ 精华 + 8 条新主题）
- **总计 61 页更新 / 新增 ~17,500 行**

已覆盖 ROADMAP 核心要素 **~98%**；内容已达 stable 水位。

**下阶段重点（转事件驱动）**：

- **事件驱动模式**：读到新论文 / 用了某工具 / 遇到生产事故 / 厂商重大变更时，触发对应页更新；不再做"S 编号大批量改造"
- **季度自检**：每季度花半天扫一遍 S 级页，必要时刷新 `last_reviewed` 日期
- **结构性重构按需而非按节奏**：出现"想再 reorganize 一遍"的冲动时，先在 changelog 写下原因，停一周再决定动不动 —— 避免陷入无限重构
- **新内容门槛**：只在用到 / 真实反馈触发时新增页；不再为"覆盖度"凑页

每批改动在 changelog 而非这里更新。本 ROADMAP 保留作历史轮次档案。
