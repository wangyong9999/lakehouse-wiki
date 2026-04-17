---
title: 贡献指南
description: 如何为本手册新增页面、修订内容、参与评审
---

# 贡献指南

欢迎贡献 —— 任何人都可以加一条概念、补一个系统、改一处错。

## 一句话流程

1. 开 [Issue](https://github.com/wangyong9999/lakehouse-wiki/issues/new/choose) 认领（避免撞车）
2. 在 `docs/_templates/` 找到对应模板，复制到目标目录
3. 填写内容，`mkdocs build --strict` 本地通过
4. 开 PR，通过 CI + 至少 1 位 review → squash merge
5. Actions 自动发布，几分钟后线上可见

## 写什么、放哪里

| 我想写的类型 | 模板 | 放到 |
| --- | --- | --- |
| 一个概念 | [`concept.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/concept.md) | 对应领域目录，如 `lakehouse/`、`retrieval/` |
| 一个系统 / OSS | [`system.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/system.md) | 对应领域目录（同上） |
| 两个以上对象的对比 | [`comparison.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/comparison.md) | `compare/` |
| 端到端场景（BI on Lake / RAG on Lake…） | [`scenario.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/scenario.md) | `scenarios/` |
| 新人学习路径 | [`learning-path.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/learning-path.md) | `learning-paths/` |
| 团队技术决策 | [`adr.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/adr.md) | `adr/`，按四位编号命名 |

## 写作风格

- **读者是一位同领域工程师**，无需解释"什么是 SQL"，但要解释"为什么湖表和 DB 存储引擎不同"
- **一页一事**：一个页面讲好一个概念 / 一个系统 / 一组对比；不要塞 3 个主题
- **一句话理解先行**：每个页面顶部必须有 `!!! tip "一句话理解"` admonition，让读者"就算不往下读也带走一个主要事实"
- **文献优先权威**：延伸阅读优先引用 spec / 论文 / 官方博客，次选高质量二手解读

## 画图规范

静态架构图（主打视觉的那 3–5 张）用 **Excalidraw** 作者源；流程 / 数据流图继续用 **Mermaid**（文本可 diff）。

### 色板（match 站点 Material Indigo 主题）

| 用途 | Hex | 用法 |
| --- | --- | --- |
| 主干强调 | `#3949ab` | 主要节点边框、箭头 |
| 主干填充 | `#5c6bc0` | 主要节点背景 |
| 次要节点 | `#c5cae9` | 辅助填充 |
| 层级背景 | `#e8eaf6` | 分层 band 淡底 |
| 强调焦点 | `#1a237e` | 关键层（如 Catalog） |
| 文本 | `#1a237e` / `#e8eaf6`（深/浅模式） |
| 箭头 | `#3949ab` / `#7986cb`（深/浅模式） |

### 排版约定

- **字体**：`"Noto Sans SC", system-ui, sans-serif`（和站点一致）
- **字号**：Layer 标题 18–20px / 700；Node 标签 14px / 500；副标 11px / 400
- **圆角**：统一 8px；节点描边 1.5px
- **箭头**：2px 实线，实心三角，**绝不交叉**（布局时手工避开）
- **层级分 band**：每个逻辑层单独一条横 band，背景色递进

### 文件与命名

每张图在 `docs/assets/diagrams/` 下交付 3 个文件：

```text
<slug>.svg           # 浅色，主展示
<slug>.dark.svg      # 深色变体
<slug>.excalidraw    # JSON 源（后续迭代起点）
```

Markdown 引用模式：

```markdown
![图标题](../assets/diagrams/<slug>.svg#only-light){ loading=lazy }
![图标题](../assets/diagrams/<slug>.dark.svg#only-dark){ loading=lazy }
```

`#only-light` / `#only-dark` 是 Material 的原生语法，自动跟随主题切换。

### 工作流（在 Excalidraw 里迭代）

1. 打开 <https://excalidraw.com> → 左上角菜单 → **Open** → 选 `.excalidraw` 文件
2. 编辑，右上角 **Export image** → **SVG** → 覆盖 `<slug>.svg`
3. 切暗色背景 → 再导一次 → 覆盖 `<slug>.dark.svg`
4. 左上角菜单 → **Save to...** → 覆盖 `.excalidraw` 源文件
5. 开 PR

### 什么时候用 Mermaid、什么时候用 SVG

| 场景 | 选 |
| --- | --- |
| 数据流 / 流程（任意节点数）| **Mermaid**（自动布局、可文本 diff）|
| 系统拓扑 / 架构分层 / ≥ 3 张并列的对比图 | **SVG（Excalidraw）**（需要精细控制）|
| 论文笔记 / ADR 里的小图 | **Mermaid**（简洁够用）|
| 主线页面的 hero 图 | **SVG**（读者第一眼就看到，值得精修）|

## 本地预览

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

打开 <http://127.0.0.1:8000/>，改动保存即热重载。

## CI 会跑什么

- `markdownlint` —— Markdown 风格与规范
- `mkdocs build --strict` —— 坏链接 / 坏引用直接失败
- `lychee` —— 外部链接探活（不阻断合并）

## 常见疑问

**Q：概念和系统应该同目录还是分开？**
A：同目录，用 frontmatter `type:` 区分；减少 IA 噪音。

**Q：同一个词条已有页面，但我想用不同切角补一版？**
A：优先在原页增加一节；只有当新切角独立到足以支撑 300+ 字且不与原页重复时，才开新页。

**Q：我要引用外部博客/论文，可以吗？**
A：可以。CC BY 4.0 下，请确保只引用摘要或必要片段，并在"延伸阅读"注明来源。
