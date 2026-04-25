---
title: 0010 废除 frontier 章节 · 前沿内容按主题归属
tags: [adr, decision, governance]
type: adr
status: accepted
date: 2026-04-22
deciders: [wangyong9999]
supersedes_partial: 0009-frontier-to-main-migration
---

# 0010. 废除 frontier/ 章节 · 前沿内容按主题归属

## 背景

ADR 0009（2026-04-21）建立了 `frontier/ → main` 的下沉判据 · 前提是 **保留 `frontier/` 作为 incubator**。

运行 1 轮（S25 · llm-inference-opt 下沉）后辩证审视发现 · **保留 frontier 的前提本身值得质疑**：

1. **12 页现状不健康**：4 页已应下沉但滞留（rag-advances / vector-trends / iceberg-v3-preview / ai-governance 工程部分）· 3 页本质不是"前沿"是生态 / 历史 / 参考（vendor-landscape / data-systems-evolution / modern-data-stack / benchmark-numbers）· 1 页是 stub（llm-inference-opt）· **仅 1 页**（diskann-paper）是合理论文前沿
2. **读者路径分裂**：主章读者（如读 `ai-workloads/rag`）想看"RAG 前沿"· 跳到 `frontier/rag-advances-2025` 是人为切割 · canonical source 原则（ADR 0006）要求一个主题一处权威
3. **治理失效**：多页 `last_reviewed` 未更新 · 证明"双地维护"没人做
4. **前沿心智 ≠ 章节归属**：时效标签由 frontmatter 的 `last_reviewed` + `applies_to` + `status: preview` 承担即可 · 不需章节本身做这件事
5. **"incubator 给新话题存放"理由弱**：新话题出现频率低 · 出现时等明确归属后再落到机制章（或先放 ADR）· 不需要常设 incubator

## 决策

**废除 `frontier/` 章节** · 12 页按以下三类重分布：

### 类 A · 归属明确的"前沿技术" → 机制章吸收

| 原 frontier 页 | 新归属 | 形式 |
|---|---|---|
| `rag-advances-2025` | `ai-workloads/rag §4` 补齐 | 整节内化 + 删 frontier |
| `vector-trends` | `retrieval/embedding` / `quantization` / `sparse-retrieval` 分散 | 核查三页覆盖 + 补缺 + 删 frontier |
| `iceberg-v3-preview` | `lakehouse/iceberg-v3.md` 独立新页 | 去 preview 字样 · frontmatter `status: stable` · 274 行规模独立合理 |
| `diskann-paper` | `retrieval/diskann §论文深度` 新节 | 选择性合并论文独有 60-70 行 · 删 frontier |
| `llm-inference-opt` | `ai-workloads/llm-inference`（已下沉）| 直接删 stub · 不保留 |
| `ai-governance` | 工程部分 → `ai-workloads/guardrails`（已覆盖） · 治理 / 法规 → `ops/compliance §4`（已覆盖） · Red Teaming 补充到 `ai-workloads/guardrails` | 删 frontier |

### 类 B · "生态 / 历史 / 参考" → 附录

| 原 frontier 页 | 新归属 | 理由 |
|---|---|---|
| `vendor-landscape` | `/docs/vendor-landscape.md`（根目录 · 附录组）| 商业观察 · 非前沿技术 |
| `data-systems-evolution` | `/docs/data-systems-evolution.md`（根目录 · 附录组）| 历史 · 非前沿 |
| `modern-data-stack` | `/docs/modern-data-stack.md`（根目录 · 附录组）| 生态全景 · 非前沿 |
| `benchmark-numbers` + `benchmarks` | `/docs/benchmarks.md`（根目录 · 附录组 · 两页合并）| 参考表格 · 非前沿 |

### 类 C · 章节本身删除

- `frontier/index.md` 删除
- `frontier/` 目录 `rmdir`
- `mkdocs.yml` nav 删除"研究前沿"组

## 替代机制 · 前沿内容的新治理

- **每机制章可有"§ 2024-2026 新方向 / § 前沿进展"节**（如 `ai-workloads/rag §4`）· 作为该主题的前沿收口
- **规模超 200 行时独立子页**（如 `lakehouse/iceberg-v3.md`）
- **跨章节 / 无明确归属的新话题**：先放 ADR 作为"讨论中"记录 · 成熟到独立成页时再决定归属
- **厂商格局 / 生态 / 历史 / Benchmark 数字**：永久归附录 · 加 `last_reviewed` 季度刷

## ADR 0009 的状态

ADR 0009 的**下沉判据（门槛 A / B / C）仍有效** · 仅作为"章内内容是否升级为独立页"或"新内容是否成熟到写入主章"的判断框架。其"保留 frontier 作为 incubator"的前提由本 ADR 废除 · 相关段落（`## 为什么不直接删除 frontier 章`、`## 为什么"保留 superseded 页"而不是删`）视为**历史讨论 · 不再适用**。

ADR 0009 不删除 · 保留作为决策演进记录。未来引用 frontier 下沉判据时 · 配合本 ADR 读。

## 依据

### 为什么一次性彻底废除 · 而不是渐进下沉

- ADR 0009 走渐进路线 1 个月 · 只下沉 1 页 · **证明渐进模式执行力不足**（心智负担大 / 判据门槛主观 / 每次迁移都要讨论）
- 一次性重构 · 边界清晰 · 未来"要不要迁"的判断消失 · 只剩"新内容归哪章"
- 读者心智简化：**没有"前沿章节"这个概念** · 读 `ai-workloads/rag` 就能看到 RAG 所有深度

### 为什么附录放根目录而非新建 `references/` 目录

- 现有 `faq.md` / `glossary.md` / `about-sources.md` / `index-by-technology.md` 已在根目录 · 统一风格
- 4 个附录新增不足以开独立子目录
- mkdocs nav 的"附录"分组已存在 · 直接加入即可

### 为什么 URL 不保留 redirect

- wiki 内部使用为主 · 外部深链风险低
- 之前决策（2026-04-20）已选"不启用 mkdocs-redirects" · 本次延续
- 跨 30 文件的 wiki 内引用本次批修 · 内部一致性由此保证

## 后果

**正面**：
- 读者单一路径：读某主题 → 该主题一处权威（canonical source 完全落实）
- 作者单一归属：写新内容不用判断"这算前沿还是主章" · 永远是主章
- 维护成本降低：不再有"双地同步"压力
- 章节心智清晰：基础 / 表格式 / Catalog / 引擎 / 管线 / 检索 / BI / AI / ML / 一体化 / 运维 / 场景 / 案例 / 附录 · 每个有明确职责

**负面**：
- 一次性重构工作量大（~30-40 文件变更 · 2-3 小时）
- 历史 URL 破坏（接受 · 内部 wiki）
- 独立的 lakehouse/iceberg-v3.md 是本 ADR 新增的页粒度决策 · 需后续 review 是否过细

**后续**：
- 2026-Q2 对抗评审（ADR 0008）：核查本次重构的遗留引用 / 内容覆盖 / nav 正确性
- 未来新前沿话题出现：先看是否归现有机制章的 "§ 前沿" 节 · 规模大再独立

## 相关

- ADR [0006](0006-chapter-structure-dimensions.md) 章节结构 · canonical source 原则的彻底落实
- ADR [0007](0007-version-refresh-sop.md) 版本刷新 · 附录类页的时效治理
- ADR [0008](0008-adversarial-review-sop.md) 对抗评审 · 检查重构效果
- ADR [0009](0009-frontier-to-main-migration.md) 下沉判据 · 被本 ADR 部分 supersede
