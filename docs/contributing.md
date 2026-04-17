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
