---
title: 0009 frontier → main 下沉判据 · 成熟度门槛 + 周期审视
type: adr
status: accepted
date: 2026-04-21
deciders: [wangyong9999]
---

# 0009. frontier → main 下沉判据

## 背景

wiki 的 `frontier/` 章节原意是"前沿 / 实验性 / 快变" · 为避免主章污染。但 2024-2026 AI 基础设施演进极快 · 多个话题从"前沿"变为"生产标配"却仍留在 frontier · 造成**读者找不到 · 作者不知该迁** 的双输：

- `frontier/llm-inference-opt.md` · vLLM 已是生产标配 · SGLang 主流 · 不再是"前沿"
- `frontier/rag-advances-2025.md` · CRAG / Self-RAG / Contextual Retrieval 多已进入工程落地
- `frontier/vector-trends.md` · 部分内容（Matryoshka / BQ）已成主流 · 部分（RaBitQ）仍前沿

**治理缺失**：没有明确"什么时候该从 frontier 迁到主章"的判据 · 导致 frontier 变成"永久抽屉"。

## 决策

定义 **frontier → main 下沉的三道门槛**。满足任一即触发下沉讨论：

### 门槛 A · 生产成熟度（定性）

**满足 ≥ 3 个 signal 时 · 应下沉**：

1. 主流 AI 工程博客（Databricks / Snowflake / AWS / Google Cloud / Uber / Meta 等）**公开生产实践**（非 POC / demo）
2. 至少 **2 个** Top 开源项目 GA 发布且过 1.0（版本号 ≥ 1.0 或类似稳定标记）
3. **主流 LLM 厂商**（OpenAI / Anthropic / Google / Meta）**官方文档**推荐作为工程实践
4. ASF / LF AI / CNCF 等 **孵化或毕业**
5. 出现在至少 1 个 2025-2026 年**生产故障 postmortem** 公开复盘（说明在跑 · 在出问题也在解决）

### 门槛 B · 读者查询压力（定量）

- 该话题在 wiki 搜索日志中连续 3 个月 **Top 20 关键词**（如有搜索 analytics）
- 或**被学习路径 / 场景章 / 其他主章 link 次数 ≥ 5**（即已被作为"必读"被多处引用）

### 门槛 C · 内容规模（定性）

- 该 frontier 页**已超 300 行**（说明内容不再"前沿"· 是在积累生产经验）
- 或已出现**非"前沿"的章节**（如"陷阱"、"性能数字"、"工程细节"）· 内容性质已变

### 下沉流程

1. 任一门槛触发 · 在 PR / Issue 公开讨论迁移判断
2. 决定迁移后：
   - 主章写新页（可从 frontier 拷贝 / 重写 / 拆分）
   - frontier 原页**保留但标注 `status: superseded` + 顶部 admonition 指向主章**（**不删** · 保留历史链接）
   - mkdocs.yml nav 更新
   - 在该 commit 或随后 commit 写"迁移说明"（可作为子 ADR）
3. 下次对抗评审（按 ADR 0008）检查迁移是否完成

### 保留在 frontier 的判据

以下明确**不下沉**：

- **规范 / 法规层内容** · 如 `ai-governance.md`（EU AI Act / Red Teaming 流程）· 本质是治理不是工程
- **论文前沿** · 未进入任何产品实现的学术方向
- **benchmark 数据集** · `benchmark-numbers.md` 类参考表格
- **厂商动态** · `vendor-landscape.md` 快变行业情报

## 依据

### 为什么不直接删除 frontier 章

- `frontier/` 本身有价值 · 收纳"还不成熟但值得跟踪"的话题
- 一刀切下沉 = 主章膨胀 + 失去"跟踪入口"
- 保留 frontier + 明确迁移机制 · 是"活流"设计

### 为什么"保留 superseded 页"而不是删

- wiki 已有外部链接 / 社区引用可能指向 frontier URL
- 保留页 + admonition 转移 · 兼顾历史与现在
- frontier stub 成本很低（10 行 admonition）· 不值得为 URL 洁癖删除

### 为什么要三门槛而非单门槛

- **单成熟度门槛**：容易被"技术流行周期"误判 · 需要配合实际读者压力（B）
- **单规模门槛**：可能 frontier 页本身写得详细但未成熟
- **三门槛"任一即触发"**：既不错过 · 也不误杀

### 为什么保留 superseded 状态而非直接删

- wiki 已有外部链接 / 社区引用可能指向 frontier URL
- 保留 stub 10 行成本 · 换 URL 稳定 · 划算

## 后果

**正面**：

- frontier → main 有明确判据 · 不再永久抽屉
- 作者知道"我写的这页应该放哪"· 判断有据
- 读者不会在 frontier 找到已是 main 内容 · 也不会在 main 找到实验性

**负面**：

- 迁移本身有一次性成本（写主章新页 + frontier stub + nav 更新）
- 判断门槛有主观成分（"成熟度 signal"不是硬性定义）
- 每年至少一次 frontier 审视成本（季度对抗评审已含）

**后续**：

- **2026-Q2 首次应用**：S25 计划中 `frontier/llm-inference-opt.md` 下沉为 `ai-workloads/llm-inference.md`（满足门槛 A4 · LLM Gateway 标配后端 · vLLM / SGLang 均过 1.0）
- **2026-Q2 同时应用**：`frontier/ai-governance.md` 工程落地部分（Guardrails）迁移到 `ai-workloads/guardrails.md`（工程化部分已成熟 · 治理 / 法规部分保留 frontier）
- 未来新 frontier 页写时 · `status: frontier` + 定期 review
- 按 ADR 0008 季度对抗评审时检查 frontier 是否该下沉

## 相关

- ADR [0006](0006-chapter-structure-dimensions.md) 章节结构 · 下沉后放哪一章的判断依据
- ADR [0007](0007-version-refresh-sop.md) 版本刷新 · 下沉的触发信号之一
- ADR [0008](0008-adversarial-review-sop.md) 对抗评审 · frontier review 是其中一环
