---
title: 数据来源与引用说明
description: 手册内数字 / 引用 / 断言的来源分级 —— 给工程师的阅读参考
last_reviewed: 2026-04-18
---

# 数据来源与引用说明

面向内部技术工程师的阅读参考：手册内的数字 / 断言**来自哪里、能不能直接用**。

## 数字的来源分级

遇到具体数字时，按来源分级判断可信度：

| 级别 | 特征 | 例子 | 怎么用 |
|---|---|---|---|
| 🔵 **官方来源** | 官方 spec / 原作者论文 / 官方 benchmark | Iceberg spec · Anthropic Contextual Retrieval 2024 | 可引用 |
| 🟢 **公开博客 / 会议** | 2022+ 权威博客或会议演讲，有年份 | "Netflix 全司 Iceberg 表 10 万+（Netflix Tech Blog 2022）" | 了解量级 · 注意年份 |
| 🟡 **经验估算** | 未标明来源的量级参考 | "HNSW 1M × 768d 查询 p99 < 1ms" | 心智模型 · 方案评审要自测 |
| 🔴 **历史数据** | 2022 年前，已有版本变化未更新 | "Uber Michelangelo 日训 5000+（2019-2020）" | 仅历史视角 |

**实务**：手册多数具体数字是 🟢🟡 级。**方案评审里引用前，核对原文或自家测试**。

## 手册遵循的原则

- **辩证性**：避免"最强 / 必选 / 事实标准"无条件断言；多页有"现实检视"段落区分工业验证 vs 仅论文
- **时效**：S/A 级页含 `applies_to` + `last_reviewed`；超过 6 个月建议复核
- **可追溯**：重要数字尽量标来源（逐步补齐中）；延伸阅读优先官方 spec / 原论文
- **SSOT（单一事实源）**：核心概念有**一个主页面**，其他页精简引用 + 链接，避免独立演化

## 典型概念主页

| 概念 | 主页 |
|---|---|
| PIT Join · Train-Serve Skew | [Feature Store](ml-infra/feature-store.md) |
| Hybrid Search | [Hybrid Search](retrieval/hybrid-search.md) |
| Rerank | [Rerank](retrieval/rerank.md) |
| Snapshot · MVCC on Object Store | [Snapshot](lakehouse/snapshot.md) |
| Manifest · 元数据索引 | [Manifest](lakehouse/manifest.md) |
| 量级数字汇总 | [量级数字总汇](benchmarks.md) |

## 权威资源（优于本手册）

冲突时以下列为准。

### 协议 / spec
- [Apache Iceberg Spec](https://iceberg.apache.org/spec/)
- [Delta Lake Protocol](https://github.com/delta-io/delta/blob/master/PROTOCOL.md)
- [Apache Paimon](https://paimon.apache.org/) · [Apache Hudi](https://hudi.apache.org/)

### 学术奠基
- [Armbrust et al., *Lakehouse* (CIDR 2021)](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)
- [Malkov & Yashunin, *HNSW* (2016)](https://arxiv.org/abs/1603.09320)
- [DiskANN (NeurIPS 2019)](https://www.microsoft.com/en-us/research/publication/diskann/)
- *Designing Data-Intensive Applications* (Kleppmann)
- *The Data Warehouse Toolkit* (Kimball)

### 工业博客
- [Netflix Tech Blog](https://netflixtechblog.com/) · [Uber Engineering](https://www.uber.com/blog/engineering/) · [LinkedIn Engineering](https://engineering.linkedin.com/)
- [Databricks Blog](https://www.databricks.com/blog) · [Snowflake Blog](https://www.snowflake.com/en/blog/)

### 独立观察
- [Benn Stancil](https://benn.substack.com/) —— 数据栈经济学
- [Simon Willison](https://simonwillison.net/) —— LLM / AI 独立观察
- [Chip Huyen](https://huyenchip.com/) —— MLOps 系统

## 如何帮助改进

- 事实错误 / 坏链接 → [Erratum Issue](https://github.com/wangyong9999/lakehouse-wiki/issues/new/choose)
- 内容过时 → [Outdated Issue](https://github.com/wangyong9999/lakehouse-wiki/issues/new/choose)
- 补来源标注 / 更新数字 → PR 直接提

## 相关

- [贡献指南](contributing.md) · [术语表](glossary.md) · [量级数字总汇](benchmarks.md)
