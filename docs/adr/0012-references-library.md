---
title: 0012 外部参考资料库 · 按章节归档 + 长期维护
type: adr
status: accepted
tags: [adr, decision, governance]
date: 2026-04-25
deciders: [wangyong9999]
---

# 0012. 外部参考资料库结构

## 背景

本手册的内容组织、选型判断、取舍论证大量基于外部权威（论文 / 官方文档 / 经典博客 / 行业综述）。但到 T1 治理为止：

- 这些外部权威**散落在各页"延伸阅读"段**，没有跨章可比的索引
- 写新页 / 改老页时**无单一入口快速看权威**，容易凭印象
- "本章如何组织"的论证若**没有外部出处背书**，容易被读者质疑（"这是 wiki 作者的主观分类还是工业惯例？"）
- 季度刷新时**没有抓手**判断"权威更新了吗"

## 决策

**建立 `docs/references/<chapter>/index.md` 长期维护参考资料库**，与内容章节一一对应。

### 结构

```
docs/references/
  index.md                      # 主入口 + 设计原则
  lakehouse/index.md            # 表格式协议 / Iceberg / Delta / Paimon / Hudi 权威
  retrieval/index.md            # ANN / Embedding / Hybrid / 多模检索权威
  ai-workloads/index.md         # RAG / Agent / LLM 应用权威
  ml-infra/index.md             # MLOps / Feature Store / Model Serving 权威
  catalog/index.md              # Catalog 协议与产品文档
  ops/index.md                  # SRE / DataOps / FinOps 经典
  ...                           # 其余章节占位 + 起步条目
```

### 内容约定

每条按以下格式：

```markdown
- **[标题](URL)** _(年份, 类型)_ —— 价值描述。补充信号：工业验证 / 仅论文 / 厂商主张
```

类型分 4 类：
- **paper** —— 学术论文（CIDR / SIGMOD / VLDB / NeurIPS 等）
- **official-doc** —— 官方文档 / spec
- **blog** —— 高质量工业博客
- **survey** —— 综述 / 教科书章节

辩证信号：
- **工业验证** —— 大厂生产部署证明
- **仅论文** —— 学术结论，工业上未广泛验证
- **厂商主张** —— 商业方有动机的内容（保留但读时打折）

### 不做什么

- **不复制原文**（版权 + 鲜度问题）：以链接 + 摘要为主
- **不强求量**：每章节起步 5-10 条够用，自然增长
- **不把"延伸阅读"段全搬过来**：references/ 是**精选 + 跨章索引**，不是穷举
- **不重复 vendor-landscape.md / benchmarks.md**：这两页讲选型 / 量级，references 讲学习路径

## 依据

### 为什么独立 references 章节而非每章 subfolder

- **单一入口**：读者一处看到全部权威路径
- **跨章对比**：MLOps 论文也对 catalog 治理有启发，独立后容易交叉
- **不污染内容章节结构**：内容章节按机制 / 概念组织，refs 是 meta，归档分离更清晰

替代方案 `docs/<chapter>/references/` 的考虑：
- 优势：locality
- 劣势：12 个章节都加 subfolder，结构噪声大；跨章查阅麻烦

### 为什么不只用每页"延伸阅读"段

每页延伸阅读是**该页相关**的延伸，references/ 是**该领域整体**的权威路径，定位不同。两者并存，不重复。

### 为什么不索引 PDF / 视频内容

- 法律灰色区
- 鲜度风险（链接腐烂时无法找回原内容）
- 工程上：让读者自己去原站点

## 后果

**正面**：
- 给"本章组织"声明（[ADR-0011](0011-chapter-internal-organization.md)）提供外部背书
- 季度刷新有抓手
- 新加页前有快速权威 check 入口

**负面**：
- 12 章 references 长期维护工作量（~小时/季度）
- 容易膨胀成"链接坟场"——靠"精选+辩证标注"约束

**后续**：
- 6 章 bootstrap 起步内容，6 章占位
- 季度自检顺手扫"权威是否有新出版"
- 当某章 references 超过 30 条时，拆分为子页（papers.md / official-docs.md / surveys.md）

## 相关

- [ADR-0006 章节结构与维度划分](0006-chapter-structure-dimensions.md) —— references 结构对齐内容章节
- [ADR-0007 版本刷新 SOP](0007-version-refresh-sop.md) —— 季度自检入口
- [ADR-0011 章节内部组织模式](0011-chapter-internal-organization.md) —— "本章组织"声明引用 references 作背书
- [contributing.md](../contributing.md) —— 贡献规范
