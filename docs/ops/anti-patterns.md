---
title: 湖仓 + AI 28 反模式 · 别这样做
type: reference
depth: 进阶
level: A
last_reviewed: 2026-04-21
applies_to: 2024-2026 湖仓 + AI 生产运维实践
tags: [ops, anti-patterns, best-practices, ai-anti-patterns]
aliases: [反模式清单, Anti-Patterns]
related: [performance-tuning, cost-optimization, troubleshooting, production-checklist]
status: stable
---

# 湖仓 + AI 28 反模式

!!! tip "一句话定位"
    **新手最常踩的坑总汇**。涵盖**表格式设计 · 入湖 · 查询 · 检索 · AI · 运维 · 治理**七个维度的 20 个反模式。每条带**症状 / 根因 / 正确做法**。**上线前自查一遍，能避 80% 的生产事故**。

!!! abstract "TL;DR"
    - **表格式**：分区过度 · 小文件爆炸 · 从不 expire
    - **入湖**：多引擎并发写 · CDC 无保序 · 流批交叉污染
    - **查询**：SELECT * · 无 WHERE · 长查询不隔离
    - **检索**：纯向量无 Rerank · 权限写 Prompt · chunk 一刀切
    - **AI / ML**：Train-Serve Skew · 无 PIT · 无漂移监控
    - **运维**：Catalog 混用 · 无备份 · 无审计
    - **治理**：数据沼泽 · 标签不治理 · 口径不统一

---

## 表格式 / 建表

### 反模式 1 · 按高基数列分区

**症状**：`PARTITIONED BY (user_id)` 或 `PARTITIONED BY (ts)`（毫秒级）→ 百万分区、HMS 崩、Iceberg 元数据爆。

**根因**：分区列基数过高。每分区只有几行。

**正确做法**：
```sql
-- ❌ 错
PARTITIONED BY (user_id)

-- ✅ 对（按时间粗粒度）
PARTITIONED BY (days(ts), bucket(16, user_id))
```

### 反模式 2 · 小文件灾难

**症状**：流入湖每分钟写几十个 5 MB 文件 → 一个月百万文件 → 查询光打开文件就几秒。

**根因**：checkpoint 频率高 + 无后台 compaction。

**正确做法**：
- `target-file-size-bytes = 256MB` 左右
- **定时跑** `CALL system.rewrite_data_files(...)`
- Paimon 配 dedicated compaction job

### 反模式 3 · 从不 expire snapshot

**症状**：metadata.json 几十 MB，打开表慢；对象存储成本失控。

**根因**：没跑 `expire_snapshots` + `remove_orphan_files`。

**正确做法**：每日 Airflow DAG：`rewrite_data_files → expire_snapshots → remove_orphan_files`

### 反模式 4 · Iceberg v1 还在用

**症状**：无行级删除、无 MoR、无 branch/tag → 2024 功能全错过。

**正确做法**：新建表一律 `format-version = 2`；老表走 v1→v2 migration。

---

## 入湖 / 流处理

### 反模式 5 · 多引擎 / 多脚本同时写同一张表

**症状**：Spark + Flink + 手工 Python 都写同一张 Iceberg 表 → CAS 冲突频繁、脏提交。

**正确做法**：
- **分区隔离**（每个写入方写自己的分区）
- 或 **集中 writer 服务**
- 若必须并发，用 Paimon changelog（为流设计）

### 反模式 6 · CDC 无保序

**症状**：Flink CDC 把 MySQL 写到湖后，`update → delete → insert` 到 Kafka 的顺序错乱 → Paimon 主键表结果错。

**正确做法**：
- CDC **单 partition per key**
- Paimon `changelog-producer = input` 要求上游有 proper changelog

### 反模式 7 · 流写入不配 checkpoint 策略

**症状**：Flink 作业重启后重放 5 小时数据；或 checkpoint 失败率高。

**正确做法**：
- `execution.checkpointing.interval = 1-5 min`
- **RocksDB state backend + incremental**
- 独立 savepoint 管理用于升级

### 反模式 8 · 流批交叉污染

**症状**：同一张表白天流写、晚上批重写同分区 → 数据错乱。

**正确做法**：
- 流批**分不同表**或**不同分区**
- 用 Paimon + Iceberg 分工（Paimon 流热 · Iceberg 批历史）

---

## 查询

### 反模式 9 · `SELECT *` 大表

**症状**：扫全列、全行，耗时 + 成本爆。

**正确做法**：
- 永远列出需要的列（列式存储的核心优势）
- 永远加 WHERE + 分区过滤

### 反模式 10 · 没有 Resource Groups

**症状**：一个大查询拖垮所有仪表盘。

**正确做法**：Trino **Resource Groups** 硬隔离（仪表盘 / 探索 / ETL）。

### 反模式 11 · CBO 无 stats

**症状**：Trino / Spark 选烂 Join Order，查询慢 10×。

**正确做法**：**定期 `ANALYZE TABLE ...`** 更新列统计。

---

## 检索 / RAG

### 反模式 12 · 只有向量检索，无 Hybrid

**症状**：产品错误码 / 人名 / 代码片段检索漏。

**正确做法**：**Hybrid (BM25 / SPLADE + Dense) + RRF 融合**。

### 反模式 13 · 没加 Rerank

**症状**：RAG 效果一直不如预期、LLM 引用混乱。

**正确做法**：必须加 Cross-Encoder Rerank（bge-reranker / Cohere）。

### 反模式 14 · 权限写在 Prompt 里

**症状**：`"你只能回答 public 内容"` → 必然被 prompt injection 绕过 → 数据泄露。

**正确做法**：
- **metadata filter 在向量库侧强制**
- 向量库的 `visibility` 字段过滤，不靠 LLM

### 反模式 15 · Chunk 一刀切 512 tokens

**症状**：代码被切断函数、表格被切碎、PDF 图表位置丢。

**正确做法**：**结构感知 chunk**（按 Markdown 标题 / 代码 AST / 段落）+ 200-800 变长。

---

## AI / ML

### 反模式 16 · Train-Serve Skew

**症状**：离线 AUC 0.92、线上 0.74。

**正确做法**：**Feature Store 一处定义**，离线在线同算。

### 反模式 17 · PIT 泄露

**症状**：离线训练用了"未来"的特征值 → 离线 AUC 飙 → 上线崩。

**正确做法**：**Point-in-Time Join**，特征取事件发生时刻的值。详见 [Feature Store](../ml-infra/feature-store.md)。

### 反模式 18 · 无 Drift 监控

**症状**：模型悄悄退化两个月，业务才发现。

**正确做法**：PSI / KS / 业务指标每日监控 + 告警。

---

## 运维 / 治理

### 反模式 19 · Catalog 混用

**症状**：部分引擎用 HMS、部分用 Glue、部分用 REST → 脏提交、元数据不一致。

**正确做法**：**团队内一套 Catalog**（推荐 REST 系：Polaris / Nessie / Unity）。

### 反模式 20 · 无审计日志 / 无血缘

**症状**：数据泄露查不到谁、合规审计做不出来。

**正确做法**：
- 所有 query 写入 **Iceberg audit 表**
- 上 **Unity / DataHub / OpenMetadata** 做血缘

---

## AI 应用 / LLM

### 反模式 21 · Prompt 硬编码在应用代码里

**症状**：Prompt 改一字要发版 · 不同环境 prompt 版本不同 · 事故时不知道用的哪版。

**根因**：Prompt 没作版本化资产管理。

**正确做法**：
- Prompt 存 Registry（MLflow / 自建 · 详见 [ai-workloads/prompt-management](../ai-workloads/prompt-management.md)）
- 每次调用记录 prompt_version
- Prompt 评估集 + 上线前回归

### 反模式 22 · 无 Guardrails 的 LLM 输出直连业务

**症状**：LLM 输出**未经过滤**直接进业务（Agent 执行 / 用户可见）· 注入攻击 / 越狱 / PII 泄漏。

**根因**：把 LLM 当"API"用 · 忽略它是**不可信输入源**。

**正确做法**：
- 入口 + 出口双向 Guardrails（见 [ai-workloads/guardrails](../ai-workloads/guardrails.md)）
- 输入：prompt injection 检测 · 敏感内容过滤
- 输出：PII mask · 幻觉验证 · Tool call 白名单

### 反模式 23 · Agent 无 sandbox 执行任意 Tool

**症状**：LLM Agent 被给**全权限**（读写库 / 调 shell / 外部 API）· 一次坏决策毁库。

**根因**：Tool 设计没有 authorization · Agent 当管理员。

**正确做法**：
- Tool ACL（见 [ai-workloads/authorization](../ai-workloads/authorization.md)）
- Agent 的身份 ≠ 当前用户（identity 流转）
- 高风险 Tool 必须 HITL（human-in-the-loop）

### 反模式 24 · 向量库无权限模型

**症状**：RAG 检索跨用户 / 跨租户 · 用户 A 问问题检索到用户 B 的私密文档。

**根因**：向量库没有 row-level filter · 权限只在 Prompt 里说"别返回别人文档"（LLM 靠不住）。

**正确做法**：
- 向量库原生**元数据过滤**（LanceDB / Milvus / Qdrant 都支持）
- 强制 `WHERE tenant_id = current_user_tenant()` 在向量库侧
- 详见 [retrieval/cross-modal-queries](../retrieval/cross-modal-queries.md) §多租户权限

### 反模式 25 · 模型 artifact 无 License 管理

**症状**：用了 Llama 3 微调模型商业化 · 没看过**Llama Community License**（7 亿 MAU 限制 / 不得训练竞品 LLM）· 法律风险。

**根因**：Model Registry 没有 license 字段 · 使用合规不成体系。

**正确做法**：
- Model Registry 强制 license 元数据（见 [ml-infra/model-registry](../ml-infra/model-registry.md) §合规）
- 派生模型（fine-tuned）继承 license 限制
- 合规扫描（某 adapter 基于 Llama · 自动告警 MAU 接近限制）

## 运维 / 生产（AI 扩展）

### 反模式 26 · LLM 输出没 SLO

**症状**：LLM 服务上线半年 · 质量悄悄退化（模型换版 / prompt 改了 / 上游数据变了）· 业务投诉才发现。

**根因**：只监控技术指标（延迟 / 错误率）· 没监控业务指标（幻觉率 / groundedness / user thumbs）。

**正确做法**：
- LLM SLO 体系（见 [sla-slo](sla-slo.md) §AI SLO）
- 定期 LLM-as-judge 评估 + 人工抽检
- 详见 [ai-workloads/llm-observability](../ai-workloads/llm-observability.md)

### 反模式 27 · GPU 不归因成本

**症状**：月底 GPU 账单爆 · 不知道哪个业务 / 模型用了多少 · 优化无从下手。

**根因**：无 per-team / per-model tag · 成本看板只看总账。

**正确做法**：
- K8s namespace 或 pod label tag cost-center
- Kubecost 或厂商 billing API 按 tag 聚合
- 详见 [ml-infra/gpu-scheduling](../ml-infra/gpu-scheduling.md) §FinOps

### 反模式 28 · AI 应用无 DR 规划

**症状**：向量库 / Prompt 仓库 / RAG 索引挂了 · 业务 AI 功能全停 · 没有备份。

**根因**：把向量库 / Prompt 当"应用状态"· 没作**数据资产**做 DR。

**正确做法**：
- 向量库定期快照（见 [disaster-recovery](disaster-recovery.md) §AI DR）
- Prompt 仓库版本化（Git / Registry）
- RAG 索引能从湖表重建（记录 `source_snapshot_id`）

---

## 补充（超 28 条的"还见过的"）

- **副本当真相源**：StarRocks / ClickHouse 挂了就丢数据
- **数据沼泽**：数据不分类、不 owner，一堆表没人管
- **口径不统一**：10 个报表 10 种 GMV 定义 → 上语义层（dbt semantic / Cube）
- **加速副本全量同步**：100TB 冷数据都复制 → 成本爆；只同步热 30 天
- **DuckDB 在生产多用户**：单机适合 Notebook 不适合并发
- **SQL 用函数阻止分区裁剪**：`WHERE YEAR(ts) = 2024` 慢；应 `WHERE ts >= '2024-01-01' AND ts < '2025-01-01'`

---

## 快速自查清单（上线前）

### 表格式
- [ ] 分区列基数合理（每分区 > 100 MB）
- [ ] 配置了定时 compaction
- [ ] 配置了 snapshot expire
- [ ] Iceberg `format-version = 2`

### 入湖
- [ ] 单 writer 或分区隔离
- [ ] Checkpoint / exactly-once 正确
- [ ] 流批表分开

### 查询
- [ ] Resource Groups 隔离
- [ ] ANALYZE 跑过
- [ ] MV / 加速副本按热查询配
- [ ] 慢查询监控 + 告警

### RAG / 向量
- [ ] Hybrid + Rerank 在位
- [ ] 权限在向量库侧
- [ ] Chunk 结构感知
- [ ] Evaluation 管线（RAGAS / 业务指标）

### ML
- [ ] Feature Store 统一定义
- [ ] PIT Join 正确
- [ ] Drift 监控
- [ ] Model Registry + 回滚流程

### 治理
- [ ] Catalog 统一
- [ ] Audit log 到位
- [ ] 血缘 / 标签治理
- [ ] 合规分类 + 权限矩阵

---

## 相关

- [性能调优](performance-tuning.md) · [成本优化](cost-optimization.md) · [故障排查](troubleshooting.md)
- [数据治理](data-governance.md) · [多租户](multi-tenancy.md) · [合规](compliance.md)
- 场景 / 业务：[业务场景全景](../scenarios/business-scenarios.md)

## 延伸阅读

- *Designing Data-Intensive Applications*（Kleppmann）
- *Fundamentals of Data Engineering*（Reis & Housley）
- Netflix / Uber / Airbnb 失败案例博客
