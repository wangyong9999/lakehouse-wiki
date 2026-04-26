---
title: 参考资料库 · 外部权威与原始来源
type: reference
status: stable
tags: [reference, references, external-sources]
description: 按章节归档外部权威参考（论文 · 官方文档 · 经典博客 · 行业综述） · 长期维护 · 持续补充
last_reviewed: 2026-04-25
---

# 参考资料库

按章节归档外部权威参考。**目的**：让本手册的内容组织 / 选型判断 / 取舍论证有可追溯的外部来源；读者可以从一页快速看到该领域的权威阅读路径。

## 设计原则（按 [ADR-0012](../adr/0012-references-library.md)）

1. **结构对齐内容章节**：`docs/references/<chapter>/index.md` 与 `docs/<chapter>/` 一一对应
2. **只索引不复制**：以链接 + 1-2 句价值说明为主，不复制原文（版权 + 鲜度）
3. **每条带最低元数据**：标题 / 链接 / 年份 / 类型（paper · 官方 doc · 博客 · 综述）/ 价值描述
4. **辩证标注**：标"工业验证"vs"仅论文"vs"厂商主张"，与本 wiki 内的 "现实检视" 段落呼应
5. **长期维护**：每季度自检（见 [contributing.md §季度自检](../contributing.md)）顺手补 1-2 条新出版

## 章节索引

### 已 bootstrap（含起步内容）

- [`lakehouse/`](lakehouse/index.md) —— 表格式协议 / Iceberg / Delta / Paimon / Hudi 论文与 spec
- [`retrieval/`](retrieval/index.md) —— ANN 算法 / Embedding / Hybrid Search / 多模检索综述
- [`ai-workloads/`](ai-workloads/index.md) —— RAG / Agent / LangChain / LlamaIndex / Anthropic 权威
- [`ml-infra/`](ml-infra/index.md) —— MLOps / Feature Store / Model Serving / Google MLOps 模型
- [`catalog/`](catalog/index.md) —— Iceberg REST / Unity Catalog / Polaris / Nessie 文档
- [`ops/`](ops/index.md) —— SRE Book / DataOps / FinOps / Postmortem 经典

### 起步占位（后续补充）

- [`foundations/`](foundations/index.md) · [`query-engines/`](query-engines/index.md) · [`bi-workloads/`](bi-workloads/index.md) · [`pipelines/`](pipelines/index.md) · [`scenarios/`](scenarios/index.md) · [`cases/`](cases/index.md) · [`unified/`](unified/index.md)

## 怎么用

- **写新页 / 改老页**：先到对应 references/<chapter>/ 看权威，避免凭印象
- **决策评审**：从 references 反查权威背书，verify "这观点是否有出处"
- **季度刷新**：扫一遍是否有新论文 / 新版本 / 新综述

## 怎么贡献

PR 加新条目时按现有格式：
```markdown
- **[标题](URL)** _(年份, 类型)_ —— 价值描述。补充信号：工业验证 / 仅论文 / 厂商主张
```
