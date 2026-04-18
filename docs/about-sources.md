---
title: 关于本手册 · 数据来源与可信度声明
description: 如何阅读本手册的数据、引用和断言 —— 一份诚实的阅读指南
last_reviewed: 2026-04-18
---

# 关于本手册 · 数据来源与可信度声明

!!! warning "先读这一页"
    本手册是一份**系统性的技术参考**，但**不是权威数据源**。所有具体数字、版本号、性能基线**在用于方案评审、决策、对外引用前应核对官方文档或自家测试**。本页说明如何辩证地使用手册内的信息。

---

## 一、手册的定位

### 它是什么

- 数据湖 / 多模检索 / AI 基础设施领域的**系统性中文参考手册**
- 基于**公开文献 + 开源社区 + 作者经验**整理
- 提供**结构化的学习路径、概念地图、选型决策支持**
- 包含**辩证性描述**（优劣 + 现实检视）和权威来源指引

### 它不是什么

- ❌ **不是一手工业实证**：手册内的数字多为二手引用或经验估算
- ❌ **不是 benchmark 报告**：具体性能数字需以自家数据和最新公开测试为准
- ❌ **不是实时更新的厂商白皮书**：有 last_reviewed 标记，可能滞后于最新版本
- ❌ **不是代码质量保证**：示例代码为说明性，未经系统验证

---

## 二、数字与断言的可信度分级

阅读手册时，遇到具体数字请对照下表心里默认分级：

### 🔵 官方来源（最可信）

**特征**：引用官方 spec / 官方文档 / 原作者论文 / 官方 benchmark。

**例子**：
- "Iceberg REST Catalog spec"（引自 [Apache Iceberg 官方](https://iceberg.apache.org/spec/)）
- "Codd 1970 关系模型论文"
- "Flash Attention 3 论文"

**如何使用**：可以引用、可以作为决策依据。

### 🟢 公开可验证数据（较可信）

**特征**：引自 2022+ 权威博客、会议演讲、公开 benchmark；有年份标注。

**例子**：
- "Netflix 全司 Iceberg 表 10 万+（引自 Netflix Tech Blog 2022）"
- "Anthropic Contextual Retrieval +35% recall（2024.09 官方博客，BEIR 子集）"
- "BEIR 平均 NDCG@10 Hybrid ≈ 0.52-0.55（EMNLP 2021 论文）"

**如何使用**：了解量级 · 引用时附原始链接 · **注意年份**（2022 数据到 2026 可能已变）。

### 🟡 经验估算（参考量级）

**特征**：没有明确公开来源、由工程经验 / 综合信息推断的"量级参考"。

**例子**：
- "HNSW 1M × 768d 查询 p99 < 1ms"
- "某电商 500 特征 p99 20ms 端到端"
- "Feast + Redis 单 entity get 2-10ms"

**如何使用**：**只作为量级心智模型**。方案评审和对外引用前**必须**自家测试或查最新公开 benchmark。

### 🔴 历史数据（已过时风险）

**特征**：2022 年以前的数字；或已知有重大版本变化后未更新。

**例子**：
- "Uber Michelangelo 日训 5000+ 模型"（原文约 2019-2020 数据，2026 年实际未知）
- 某些 query-engines 页面的基线（2023 前做的测试）

**如何使用**：**仅供历史视角**，不作为当前决策依据。

---

## 三、本手册遵循的原则

### 1. 辩证性（反 hype）
- 避免 "最强 / 必选 / 事实标准" 等无条件断言
- 用 "在 X 场景下相对 Y" 等条件化表达
- 多页含 **"现实检视"** 段落区分工业验证 vs 仅论文

### 2. 时效标注
- 每个 S/A 级页 frontmatter 含 `applies_to`（版本范围）和 `last_reviewed`（最近复核日期）
- 超过 6 个月未 review 的页**可能信息滞后**
- 一年前的数字在 frontmatter 明确

### 3. 可追溯
- 重要数字尽量标注来源（逐步补齐中）
- 延伸阅读优先引用官方 spec / 权威论文

### 4. 鼓励 fact-check
- 发现数字错误或过时 → [Outdated Issue 模板](https://github.com/wangyong9999/lakehouse-wiki/issues/new/choose)
- 欢迎 PR 补强来源标注或更新数字

---

## 四、引用本手册的建议

### 可以这样引用

- **作为起点**：了解某个领域有哪些关键要素
- **作为选型参考**：结合决策矩阵判断方向
- **作为学习路径**：按"按角色"或"按主题"展开
- **作为术语索引**：快速定位概念

### 不建议这样引用

- ❌ 把具体数字写到**方案评审 / 对外文档 / 投资人材料**里，不核对原始来源
- ❌ 把 benchmark 数字作为 SLA 承诺依据
- ❌ 假设手册内容"最新 / 最权威"
- ❌ 未声明来源的复用（尤其商业用途，请遵守 [LICENSE](https://github.com/wangyong9999/lakehouse-wiki/blob/main/LICENSE)）

---

## 五、信息漂移的治理

手册采用 **Single Source of Truth (SSOT)** 原则：

- 每个核心概念有**一个主页面**深入讲解
- 其他页面**只简短引用 + 链接**到主页
- 减少"同一概念在多页独立演化"的风险

**典型主页**：
- PIT Join 定义 → [Feature Store](ai-workloads/feature-store.md)
- Hybrid Search → [Hybrid Search](retrieval/hybrid-search.md)
- Rerank → [Rerank](retrieval/rerank.md)
- Snapshot · MVCC → [Snapshot](lakehouse/snapshot.md)
- Train-Serve Skew → [Feature Store](ai-workloads/feature-store.md)
- 工业级 benchmark 数字 → [量级数字总汇](frontier/benchmark-numbers.md)

---

## 六、关键权威资源（优于本手册）

当本手册与以下来源冲突时，**以它们为准**：

### 底座协议
- **[Apache Iceberg Spec](https://iceberg.apache.org/spec/)**
- **[Delta Lake Protocol](https://github.com/delta-io/delta/blob/master/PROTOCOL.md)**
- **[Apache Paimon Docs](https://paimon.apache.org/)**
- **[Apache Hudi Docs](https://hudi.apache.org/)**

### 学术奠基
- **[Armbrust et al., *Lakehouse: A New Generation of Open Platforms* (CIDR 2021)](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)**
- **[Malkov & Yashunin, *HNSW* (2016)](https://arxiv.org/abs/1603.09320)**
- **[DiskANN (NeurIPS 2019)](https://www.microsoft.com/en-us/research/publication/diskann/)**
- **[*Designing Data-Intensive Applications* (Kleppmann)](https://dataintensive.net/)**
- **[*The Data Warehouse Toolkit* (Kimball & Ross)](https://www.kimballgroup.com/)**

### 工业实践
- **[Netflix Tech Blog](https://netflixtechblog.com/)**
- **[Uber Engineering Blog](https://www.uber.com/blog/engineering/)**
- **[LinkedIn Engineering Blog](https://engineering.linkedin.com/)**
- **[Databricks Blog](https://www.databricks.com/blog)** · **[Snowflake Blog](https://www.snowflake.com/en/blog/)**
- **[a16z Data Infrastructure](https://future.com/)**

### 社区观察
- **[Benn Stancil (Substack)](https://benn.substack.com/)** —— 数据栈经济学
- **[Simon Willison Blog](https://simonwillison.net/)** —— LLM / AI 独立观察
- **[Jay Kreps (Confluent blog)](https://www.confluent.io/blog/author/jay-kreps/)** —— 流处理原点
- **[Chip Huyen](https://huyenchip.com/)** —— MLOps / ML systems

---

## 七、如何帮助改进

### 发现问题
- 事实错误 / 坏链接 → [Erratum Issue](https://github.com/wangyong9999/lakehouse-wiki/issues/new/choose)
- 内容过时 → [Outdated Issue](https://github.com/wangyong9999/lakehouse-wiki/issues/new/choose)
- 建议新主题 → [New Topic Issue](https://github.com/wangyong9999/lakehouse-wiki/issues/new/choose)

### 补强引用
- 某页数字没标来源而你知道来源 → PR 补齐
- 发现更新的数据 → PR 更新 + 更新 `last_reviewed`

### 贡献内容
- 见 [贡献指南](contributing.md)

---

## 相关

- [贡献指南](contributing.md) —— 写作风格与规范
- [术语表](glossary.md) —— 字母序索引
- [量级数字总汇](frontier/benchmark-numbers.md) —— 常见量级参考（附来源）
