---
title: 场景指南
type: reference
status: stable
tags: [index, scenarios]
description: 端到端业务场景 · 内嵌工业案例切面分析 · 场景+案例配对阅读
applies_to: 2024-2026 工业实践 · 具体技术栈版本见各场景页 applies_to
last_reviewed: 2026-04-21
---

# 场景指南

!!! info "其他入口方式"
    本页是「按业务场景」入口。也可以从其他维度进入：
    
    - **按角色读** → [按角色入门](../roles/index.md)
    - **按时间顺序学** → [学习路径](../learning-paths/index.md)
    - **按工业案例学** → [工业案例](../cases/index.md)（与本章配对阅读，下面 §三角关系详）
    - **按技术栈反查** → [按技术栈索引](../index-by-technology.md)

!!! info "本章是场景视角 · 不复述机制"
    讲**业务场景的端到端编排** + **工业案例切面**。机制原理在对应技术栈章（[lakehouse/](../lakehouse/index.md) · [retrieval/](../retrieval/index.md) · [query-engines/](../query-engines/index.md) · [bi-workloads/](../bi-workloads/index.md) · [ai-workloads/](../ai-workloads/index.md) · [ml-infra/](../ml-infra/index.md) · [catalog/](../catalog/index.md) · [pipelines/](../pipelines/index.md)）· 本章不复述。
    
    和 [cases/](../cases/index.md) 配对：scenarios/X = "怎么做 X + 业界怎么做 X" · cases/X = 单家公司全栈历史与取舍。

!!! tip "怎么用"
    - **带着业务问题进来** → 从 [E2E 业务场景全景](business-scenarios.md) 开始
    - **想深挖某个业务** → 直接看下面"业务深挖"
    - **要搭架构 / 流水线** → 看"架构视角的端到端场景"
    - **要学工业案例** → 从业务页 §工业案例节切入 + 回 [cases/](../cases/index.md) 看全栈

## 三角关系 · 场景 / 案例 / 机制

```mermaid
flowchart LR
  scenarios[scenarios/<br/>业务场景端到端<br/>+ 内嵌案例切面]
  cases[cases/<br/>全栈企业参考<br/>Netflix/LinkedIn/Uber/...]
  mech[机制章 canonical<br/>lakehouse/retrieval/...<br/>ai-workloads/ml-infra/catalog]
  
  user[读者] -->|带业务问题| scenarios
  user -->|研究业界全栈| cases
  user -->|学机制原理| mech
  
  scenarios -.切面指向.-> cases
  scenarios -.机制指向.-> mech
  cases -.对应场景指向.-> scenarios
```

## 从业务找入口 · 强烈推荐先读

- ⭐ [**E2E 业务场景全景**](business-scenarios.md) —— 业务视角的分类框架 + Top 10 主流场景 + 前沿方向 + 决策矩阵 + Benchmark 索引。**新同事带着业务问题进来，这里是第一站**。

## 业务视角深挖

**从业务问题出发的完整解决方案** · 每页含：业务图景 + 组件链路 + Benchmark + **工业案例深度切面**（2-4 家）+ 陷阱。

| 场景页 | 主要内嵌案例 |
|---|---|
| [**推荐系统 · 搜索 · 发现**](recommender-systems.md) ⭐ | Pinterest · 阿里 · LinkedIn |
| [**RAG on Lake · 企业知识库问答**](rag-on-lake.md) ⭐ | Databricks · Snowflake · Netflix |
| [**BI on Lake · 湖上分析与仪表盘**](bi-on-lake.md) ⭐ | Databricks · Snowflake · Netflix |
| [**欺诈检测 · 风险控制**](fraud-detection.md) | Uber · LinkedIn |
| [**CDP · 用户分群**](cdp-segmentation.md) | 阿里 · LinkedIn |
| [**Agentic 工作流 · 自动化**](agentic-workflows.md) | Databricks Genie · Snowflake Cortex · Anthropic |
| [**Text-to-SQL 平台**](text-to-sql-platform.md) | Databricks Genie · Snowflake Cortex Analyst · 阿里 |
| [**多模检索流水线**](multimodal-search-pipeline.md) | Pinterest · 阿里 · Databricks |

## 架构视角的端到端场景

**从架构组件出发的流水线模板** —— 适合要搭建某条链路时参考。每页含"相关工业案例"短节 · 深度去 cases/ 全栈页。

- [**流式入湖**](streaming-ingestion.md) —— CDC + 事件流持续入湖 · 案例：LinkedIn Kafka · 阿里 Flink CDC
- [**Real-time Lakehouse**](real-time-lakehouse.md) —— 端到端分钟级一体化 · 案例：阿里 Paimon · Uber Hudi
- [**离线训练数据流水线**](offline-training-pipeline.md) —— 可复现 + PIT 的训练集生成 · 案例：Uber Michelangelo · Netflix Metaflow
- [**Feature Serving**](feature-serving.md) —— 在线推理的毫秒级特征拉取 · 案例：LinkedIn Venice · Uber Palette/Genoa

## 按问题找场景 · 反向索引

**"我要做 X · 先看哪页"**：

| 我的问题 | 优先读 | 配对案例 |
|---|---|---|
| 做电商 / 内容推荐 | [recommender-systems](recommender-systems.md) | Pinterest · 阿里 · LinkedIn |
| 做企业知识库 / 客服 RAG | [rag-on-lake](rag-on-lake.md) | Databricks · Snowflake |
| 做 BI 分析仪表盘 | [bi-on-lake](bi-on-lake.md) | Databricks · Snowflake · Netflix |
| 做风控 / 反欺诈 | [fraud-detection](fraud-detection.md) | Uber |
| 做用户分群 / 画像 | [cdp-segmentation](cdp-segmentation.md) | 阿里 |
| 做 Agent / 自动化 | [agentic-workflows](agentic-workflows.md) | Databricks Genie · Snowflake Cortex Agents |
| 做自然语言 BI | [text-to-sql-platform](text-to-sql-platform.md) | Databricks Genie · Snowflake Cortex Analyst |
| 做图文 / 视频检索 | [multimodal-search-pipeline](multimodal-search-pipeline.md) | Pinterest · 阿里 |
| 做 Feature Store 选型 | [feature-serving](feature-serving.md) + [ml-infra/feature-store](../ml-infra/feature-store.md) | LinkedIn Venice · Uber Palette |
| 做训练数据 PIT Join | [offline-training-pipeline](offline-training-pipeline.md) | Uber Michelangelo |
| 做流式湖仓 | [real-time-lakehouse](real-time-lakehouse.md) | 阿里 Paimon · Uber Hudi |
| 做 Kafka 入湖 | [streaming-ingestion](streaming-ingestion.md) | LinkedIn Kafka |

## 不同读者的阅读建议

### 新同事 · 带业务问题进来

1. 先读 [business-scenarios](business-scenarios.md) 建立业务全景
2. 按上面"反向索引"挑一页业务深挖
3. 读业务页前半（业务 + 架构 + 组件）
4. 读 §工业案例节（业界怎么做）
5. 想深度看某家公司 → 跳 [cases/](../cases/index.md)

### 资深架构师 · 做选型决策

1. 先读对应业务场景深挖页 §工业案例节（多家对比）
2. 看 [cases/studies.md](../cases/studies.md) 7 家横比矩阵
3. 读 [unified/index §5 团队路线主张](../unified/index.md)
4. 综合做决策

### 平台工程师 · 要搭架构

1. 读"架构视角"4 页（streaming / real-time / offline-training / feature-serving）
2. 配对对应机制章 canonical（ml-infra · ai-workloads · lakehouse · retrieval）
3. 参考 cases/ 工业规模和取舍

### 中国团队特别建议

- **推荐 / 电商场景**：重点读阿里切面 · 配对 [cases/alibaba](../cases/alibaba.md)
- **流式湖仓**：[real-time-lakehouse](real-time-lakehouse.md) + Paimon · 中国团队最可复制
- **国内工业实践**：目前 cases/ 只有阿里 · 后续补字节 / 腾讯 / 美团

## 和其他资源

- [ADR](../adr/index.md) · 团队技术决策
- [FAQ](../faq.md) · 常见问题速答
- [Learning Paths](../learning-paths/week-1-newcomer.md) · 角色学习路径
