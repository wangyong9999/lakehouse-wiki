---
title: 贡献指南
type: reference
status: stable
tags: [reference, contributing]
description: 本手册的写作规范、frontmatter 字段、画图与数字引用约定
---

# 贡献指南

> 写作规范、流程与 frontmatter 约定。勘误 PR 直接走流程；新增页 / 大改动建议先开 Issue 对齐。

## 快速开始

1. 在 `docs/_templates/` 找到对应模板，复制到目标目录
2. 填写 frontmatter + 内容，`mkdocs build --strict` 本地通过
3. 开 PR，CI 绿后由维护者 review 合并 → Actions 自动发布

## 写什么、放哪里

| 类型 | 模板 | 放到 |
|---|---|---|
| 概念 | [`concept.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/concept.md) | 对应领域目录 |
| 系统 / OSS | [`system.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/system.md) | 对应领域目录 |
| 两个以上对象的对比 | [`comparison.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/comparison.md) | `compare/` |
| 端到端场景 | [`scenario.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/scenario.md) | `scenarios/` |
| 学习路径 | [`learning-path.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/learning-path.md) | `learning-paths/` |
| 团队决策 | [`adr.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/adr.md) | `adr/`（四位编号） |

### 新内容归属决策 · 5 问

按 [ADR-0006](adr/0006-chapter-structure-dimensions.md) canonical source 原则，新加页前问自己：

1. **是机制原理 / 算法 / spec 吗** → 放对应**技术栈章**（`lakehouse/` `retrieval/` `query-engines/` `catalog/` `ai-workloads/` `bi-workloads/` `ml-infra/` `pipelines/`），这是 canonical
2. **是 ≥2 个对象的对比 / 选型决策吗** → 放 `compare/`
3. **是端到端业务方案吗**（推荐系统 / 欺诈检测 / RAG 等）→ 放 `scenarios/`，**必须 link 到机制 canonical · 不复述机制**
4. **是单家公司全栈深拆吗**（Netflix / Databricks / 阿里 等）→ 放 `cases/`，reference 性质 · **只讲"别人怎么做"· 不讲机制**
5. **是通用工程治理吗**（备份 / SLO / 成本 / 安全 / 性能调优）→ 放 `ops/`

**scenarios vs cases 边界**（高频混淆）：
- 写"X 业务怎么做" + "业界 2-4 家怎么做的切面" → `scenarios/`
- 写"某家公司的全栈历史 / 取舍 / 演进 / 失败" → `cases/`
- 同一家公司可同时出现：cases 讲全栈，scenarios 引"切面"，两者交叉链接

**canonical 已有冲突时**（同概念已在多章有页）：
- 优先级：**技术栈章 > 对比章 > 场景章**
- 非 canonical 页头部加 `!!! info "本页是 X 视角 · canonical 见 ..."` admonition
- 例：`bi-workloads/materialized-view.md` 是 BI 视角 canonical · `lakehouse/materialized-view.md` 是协议层视角，互指

---

## Frontmatter 规范（2026+ 新要求）

每页 frontmatter 建议字段：

```yaml
---
title: <页标题>
type: concept | system | comparison | scenario | reference | learning-path | adr
depth: 入门 | 进阶 | 资深            # 建议阅读门槛
level: S | A | B                    # S 核心资产 · A 重要主题 · B 维持水位
applies_to: <版本 / 时效范围>        # 如 "Iceberg 1.4+"、"2024-2026 主流"；当前参考版本见 benchmarks.md §12
tags: [...]
last_reviewed: YYYY-MM-DD            # 最近一次人工 review 日期（建议季度刷新）
aliases: [...]                      # 异名（SEO + 术语）
related: [...]                      # 相关页 slug（不含 .md）
systems: [...]                      # 涉及 OSS / 产品
status: draft | stable | preview | deprecated
---
```

### 页面分级

| 级别 | 定义 | 目标行数 |
|---|---|---|
| **S 级** | 方案评审必查、新人必读核心 | 300-400 |
| **A 级** | 资深工程师常需深入 | 180-280 |
| **B 级** | 参考 / 介绍型 | 80-140 |

**S 级必须** 8 段骨架（见模板）：TL;DR · 业务痛点 · 原理深度 · 工程细节 · 性能数字 · 代码示例 · 陷阱 · 延伸阅读。

### last_reviewed 用法

- 新建页自动取建稿日
- 大幅更新时手动改
- 每季度 review，即使内容无变更也更新日期（证明"已复核"）
- 超过 6 个月未 review 的页在 CI 会标 **stale**（未来 feature）

---

## 写作风格

- **读者是同领域工程师**：无需解释"什么是 SQL"，但要解释"为什么湖表和 DB 存储引擎不同"
- **一页一事**：一个页面讲好一个主题；不要塞 3 个
- **一句话理解先行**：每页顶部必有 `!!! tip "一句话理解"`
- **辩证性 + 反 hype**：
  - 避免"最强"、"必选"、"事实标准"这类无条件断言
  - 给量化（"BEIR NDCG +5-8"）而非形容词
  - 明确"何时不要用"
  - 前沿页建议加**"现实检视"段落**区分工业验证 vs 仅论文
- **文献优先权威**：延伸阅读先引用 spec / 论文 / 官方博客，次选二手解读

### 数字引用规约（2026-Q2 新增）

**每个实证数字必须可溯源**。实证数字指：百分比、benchmark 分数、延迟 / QPS / 吞吐、用户 / 采用规模、日期事件、模型准确率等。

**规约**：

1. **首选 · 引用**：数字后括号注明来源 · 如 `(BEIR 2022 报告)` · `(Anthropic Contextual Retrieval 博客 2024)` · `(Databricks 官方 GA 公告)`
2. **次选 · 链接**：在同一句或同段落插入 markdown link · 指向 paper / 博客 / 产品首页
3. **兜底 · 标注未验证**：无法溯源但仍要写的数字 · 加 `[来源未验证]` 标签 · 将自身从信任域排除
4. **禁止 · 凭印象**：LLM 生成内容尤其注意 · "+35% recall" 这类数字容易幻觉 · 不能只因"听起来合理"就写

**典型反例**：

```markdown
<!-- ❌ 数字无来源 · 读者无法验证 -->
Contextual Retrieval 可把 recall 提升 35%。

<!-- ✅ 数字带来源 · 且解读准确 -->
Contextual Retrieval 把**检索失败率**相对降低 35%（5.7% → 3.7%）· 配合 reranker 降 67%（Anthropic 2024 博客原数据）。
```

**自动检查**：`scripts/unsourced_numbers_scan.py`（非阻断 · 季度扫描）报告可疑无源数字。

---

## 画图规范

静态架构图（主打视觉的 3–5 张）用 **Excalidraw**；流程 / 数据流图用 **Mermaid**（文本可 diff）。

### 色板（match 站点 Material Indigo 主题）

| 用途 | Hex |
|---|---|
| 主干强调 | `#3949ab` |
| 主干填充 | `#5c6bc0` |
| 次要节点 | `#c5cae9` |
| 层级背景 | `#e8eaf6` |
| 强调焦点 | `#1a237e` |

### 文件命名

```
docs/assets/diagrams/
  <slug>.svg           # 浅色
  <slug>.dark.svg      # 深色
  <slug>.excalidraw    # 源文件
```

### 什么时候用 Mermaid、什么时候用 SVG

| 场景 | 选 |
|---|---|
| 数据流 / 流程 | Mermaid |
| 架构分层 / 精修对比 | SVG（Excalidraw） |
| 主线 hero 图 | SVG |
| 论文笔记小图 | Mermaid |

---

## 更新节奏

- **事件驱动为主**：读到新论文 / 用了某工具 / 遇到生产事故 / 厂商重大变更 → 触发对应页更新
- **季度自检**：每季度花半天扫一遍 S 级页，必要时刷新 `last_reviewed` 日期
- **年度审视**：识别废弃页、整体结构是否需要调整
- **避免"为更新而更新"**：内容仍准确就保留旧 `last_reviewed`，不为刷日期而无意义改动

---

## 本地预览

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

打开 <http://127.0.0.1:8000/>，改动保存即热重载。

---

## CI 会跑什么

- `markdownlint` —— Markdown 风格规范
- `mkdocs build --strict` —— 坏链接 / 坏引用直接失败
- `lychee` —— 外部链接探活（不阻断合并）

---

## Issue 模板

- **Bug / Factual Error** —— 事实错误 / 坏链接
- **Outdated Content** —— 内容过时（需要刷新）
- **New Topic Request** —— 建议新增主题（不承诺时间）

---

## 常见疑问

**Q：概念和系统应该同目录还是分开？**
A：同目录，用 frontmatter `type:` 区分。

**Q：同词条已有页面，我想用不同切角补一版？**
A：优先在原页增加一节；新切角独立到 300+ 字且不重复时开新页。

**Q：能引用外部博客 / 论文吗？**
A：可以。CC BY 4.0 下，只引摘要或必要片段，"延伸阅读"注明来源。

**Q：`last_reviewed` 日期落后怎么办？**
A：超过 6 个月的页面在季度自检时优先扫；如果内容仍准确，只更新日期即可。

**Q：发现一页偏 hype / 过度乐观怎么办？**
A：直接 PR 加"现实检视"段落（范式：已验证 vs 论文声称 vs 坏信号识别）。

---

## 维护与历史

完整改动史见 `git log` 与 [changelog](changelog.md)。
