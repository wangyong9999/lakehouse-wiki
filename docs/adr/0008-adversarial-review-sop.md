---
title: 0008 对抗评审 SOP · 季度 Agent 驱动 + 人工复核
type: adr
status: accepted
date: 2026-04-21
deciders: [wangyong9999]
---

# 0008. 对抗性评审 SOP

## 背景

wiki 由单人维护 · 从未经过独立审阅。2026-Q2 首次**对抗性 Agent 评审**覆盖 7 章（~60% 内容）· 产出 **~70 条 issue · 14 P0 事实错**：

- Apache Polaris 2026-02 已毕业 TLP · wiki 称"仍孵化"
- OpenAI ChatGPT 2025-09 已全支持 MCP · wiki 称"未采纳"
- Matryoshka 论文 NeurIPS 2022 · wiki 写"2023-2024 新范式"
- Iceberg V3 spec 时间线与引擎版本矛盾
- Delta DV 的 "v3+" 与 Iceberg V3 spec 混淆
- 等等

这些错误**无法靠作者自审发现** · 因为作者本来就信任自己写下的内容（尤其 LLM 辅助写作输出）。

同时 · 对抗 agent 自己也会 hallucinate（观察到 2 例：A4 虚构行号 · A5 虚构 BGE-M3 标签错误）——agent 不是真理。

## 决策

把**对抗评审常态化**为季度制度 · 三层防线：

### 第一层 · 季度 Agent 评审（主力）

- **频率**：每季度一次 · 与 [ADR 0007](0007-version-refresh-sop.md) 版本刷新同期
- **范围**：5-7 个章节 / 轮 · 优先级 = 事实密度 × 最近改动 × 快变领域
- **Agent 类型**：Explore subagent · thoroughness = very thorough
- **输入模板**：
    - 评审者身份（adversarial · 不配合）
    - 当前日期
    - 单人维护 · 无独立审阅 · 可能有事实错 / 逻辑断 / 关键缺失
    - 快变点（该章对应的 2025-2026 变化事件）
    - 输出格式（P0/P1/P2 + 证据 + 建议）
- **并行启动**：单个 message 发送多 Agent tool_use · 一次性拉满并行

### 第二层 · 人工复核 Agent 输出（强制）

Agent 报告每条 P0 · 应用前必须：

1. WebSearch 验证（日期 / GA 状态 / 版本号 / paper 年份）
2. Grep 验证（文件 / 行号 / 引用的措辞）
3. 或直接访问上游 source（产品 release page · paper abstract）

观察到的 hallucinate 模式：
- 虚构行号（声称 line 459 · 文件只 280 行）
- 虚构措辞（声称文件说"2025 年内"· 实际无此表达）
- 范畴错配（声称 BGE-M3 被标"多模态"· 实际未标）

**不复核直接应用 = 把 agent 错误引入 wiki**。

### 第三层 · Commit 公开 trace

每轮对抗评审独立 commit series（本次为 S22-1 到 S22-5）· commit message 明确：

- agent 报告的真错 vs hallucinate
- WebSearch 验证过的关键事实
- Agent 原建议 vs 实际修正的差异（例：MCP 时间 agent 报 2025-10 · 实际 2025-03/09）

Trace 对未来维护者是教训：**agent 报告不是真理 · 是 signal**。

## 依据

### 为什么不完全人工审

- 单人自审有盲点 · 尤其"自己的 LLM 辅助产出"· 难自查
- Agent 跨页 / 跨领域扫描比人快 10x
- Agent 抓到的 14 P0 · 人工读一年都未必全捞

### 为什么不完全信 Agent

- 观察到的 20% hallucinate 率是 2026 LLM 客观水平
- 修 wiki 的成本是"错一次全世界看得到"· 容不得 20% 错
- 复核成本（WebSearch / Grep）低 · 跳过是劣化

### 为什么不直接人工 + Agent 混合

其实就是混合 · 但必须**明确分工**：
- Agent 负责**广度**（哪些地方可能错）
- Human 负责**深度**（每条真假）
- 记录**两者差异** · 保留治理线索

## 后果

**正面**：

- 季度一次对抗评审 · 60% 事实错在发生后 90 天内被发现
- 作者对"自己写的内容"失去盲目信任 · 写作更谨慎
- 对抗评审 trace 是组织记忆 · 后续作者能学到"LLM 典型错法"

**负面**：

- 每季度 60-90min 额外时间（启动 + 人工复核 + commit）
- 需要 Agent 工具 · 不适合完全无外部工具的团队
- 人工复核疲劳 · 可能选择性跳过 → **需要结构化复核清单**

**后续**：

- 季度对抗评审的结果沉淀为 memory · 帮下次评审找盲区
- 对**新发布的章节** · 发布后 30 天内触发第一轮评审（不等季度）
- 一年内观察 agent hallucinate 率变化 · 评估是否要加"第二 agent cross-check"

## 相关

- ADR [0006](0006-chapter-structure-dimensions.md) 章节结构 · 对抗评审的组织单元
- ADR [0007](0007-version-refresh-sop.md) 版本刷新 · 与对抗评审同期
- 2026-Q2 评审的 commit trace：S22-1 (042a21b) · S22-2 (aa657fa) · S22-3 (332c44f) · S22-4 (7906585) · S22-5 (134f4c6)
