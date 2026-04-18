---
title: 贡献指南
description: 如何为本手册新增页面、修订内容、参与评审、维护时效
---

# 贡献指南

欢迎贡献 —— 任何人都可以加一条概念、补一个系统、改一处错。

## 快速开始

1. 开 [Issue](https://github.com/wangyong9999/lakehouse-wiki/issues/new/choose) 认领（避免撞车）
2. 在 `docs/_templates/` 找到对应模板，复制到目标目录
3. 填写 frontmatter + 内容，`mkdocs build --strict` 本地通过
4. 开 PR，通过 CI + 至少 1 位 review → squash merge
5. Actions 自动发布，几分钟后线上可见

## 写什么、放哪里

| 类型 | 模板 | 放到 |
|---|---|---|
| 概念 | [`concept.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/concept.md) | 对应领域目录 |
| 系统 / OSS | [`system.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/system.md) | 对应领域目录 |
| 两个以上对象的对比 | [`comparison.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/comparison.md) | `compare/` |
| 端到端场景 | [`scenario.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/scenario.md) | `scenarios/` |
| 学习路径 | [`learning-path.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/learning-path.md) | `learning-paths/` |
| 团队决策 | [`adr.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/adr.md) | `adr/`（四位编号） |

---

## Frontmatter 规范（2026+ 新要求）

每页 frontmatter 建议字段：

```yaml
---
title: <页标题>
type: concept | system | comparison | scenario | reference | learning-path | adr
depth: 入门 | 进阶 | 资深            # 建议阅读门槛
level: S | A | B                    # S 核心资产 · A 重要主题 · B 维持水位
applies_to: <版本 / 时效范围>        # 如 "Iceberg 1.4+"、"2024-2026 主流"；当前参考版本见 frontier/benchmark-numbers.md §12
tags: [...]
owner: <team / person>              # 该页负责人（可选但推荐）
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

## 运营节奏（2026 起试行）

- **月度 Review**：第一周 pings 所有 S 级页 owner 检查是否需要更新
- **季度更新**：核心资产页更新 `last_reviewed` + 必要内容刷新
- **年度审视**：整体结构、废弃页识别、下一阶段重点
- **Feature-driven**：遇到生产事故 / 新技术 / 新产品 → 触发相关页更新

### 谁是 owner

- 每章节**建议**至少 1 位 owner（通过 frontmatter 标注）
- owner 责任：审核 PR、回应 Issue、季度 review
- 无 owner 的章节由**轮值编辑**兜底

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

## Issue 类型（使用模板）

- **Bug / Factual Error** —— 发现事实错误 / 坏链接
- **Outdated Content** —— 发现内容过时（需要刷新）
- **New Topic Request** —— 建议新增主题
- **Discussion** —— 开放讨论（某技术选型、范式）

---

## 常见疑问

**Q：概念和系统应该同目录还是分开？**
A：同目录，用 frontmatter `type:` 区分。

**Q：同词条已有页面，我想用不同切角补一版？**
A：优先在原页增加一节；新切角独立到 300+ 字且不重复时开新页。

**Q：能引用外部博客 / 论文吗？**
A：可以。CC BY 4.0 下，只引摘要或必要片段，"延伸阅读"注明来源。

**Q：一个页面可以有多个 owner 吗？**
A：可以，frontmatter 写数组或用 team 名。

**Q：`last_reviewed` 日期落后怎么办？**
A：超过 6 个月的页面在季度 review 时优先刷新；如果内容仍准确，只更新日期即可。

**Q：发现一页偏 hype / 过度乐观怎么办？**
A：开 Outdated Content Issue；或直接 PR 加"现实检视"段落（参考 frontier 页面范式）。

---

## 致谢

本手册由团队共同维护。所有贡献者见 `git log` 与 PR 历史。
