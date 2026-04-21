---
title: 场景指南
description: 端到端的典型场景 —— 业务视角 + 架构视角，都能对着看
---

# 场景指南

!!! info "本章是场景视角 · 不复述机制"
    `scenarios/` 讲**业务场景的端到端编排**——多个机制如何拼成一个业务方案 · 含真实数字 / 选型陷阱 / 跨团队协同。**机制原理（湖表 / 检索 / 引擎 / BI 负载 / AI 负载 / Catalog）不在本章** · 请移步对应技术栈章：[lakehouse/](../lakehouse/index.md) · [retrieval/](../retrieval/index.md) · [query-engines/](../query-engines/index.md) · [bi-workloads/](../bi-workloads/index.md) · [ai-workloads/](../ai-workloads/index.md) · [catalog/](../catalog/index.md) · [pipelines/](../pipelines/index.md)。参见 [ADR 0006 canonical source 原则](../adr/0006-chapter-structure-dimensions.md)。

!!! tip "怎么用"
    - **带着业务问题进来** → 从 [E2E 业务场景全景](business-scenarios.md) 开始
    - **想深挖某个业务** → 直接看下面"业务深挖"
    - **要搭架构 / 流水线** → 看"架构视角的端到端场景"

## 从业务找入口 · 强烈推荐先读

- ⭐ [**E2E 业务场景全景**](business-scenarios.md) —— 业务视角的分类框架 + Top 10 主流场景 + 前沿方向 + 决策矩阵 + Benchmark 索引。**新同事带着业务问题进来，这里是第一站**。

## 业务视角深挖

**从业务问题出发的完整解决方案**——每个深挖都带业务图景、组件链路、Benchmark、陷阱。

- [**推荐系统 · 搜索 · 发现**](recommender-systems.md) —— 四阶段流水线（召回 → 粗排 → 精排 → 重排）+ Feature Store + 冷启动 + 近实时
- [**欺诈检测 · 风险控制**](fraud-detection.md) —— 四层拦截（黑白名单 / 规则 / ML / GNN）+ 样本不平衡 + 标签延迟 + 图分析
- [**CDP · 用户分群**](cdp-segmentation.md) —— OneID + 画像宽表 + 标签体系 + 触达回流闭环
- [**RAG on Lake · 企业知识库问答**](rag-on-lake.md) —— 五张表架构 + Chunk 策略 + Hybrid + Rerank + Evaluation
- [**BI on Lake · 湖上分析与仪表盘**](bi-on-lake.md) —— Medallion 分层 + 查询加速三板斧 + 语义层 + SLO 打法
- [**Agentic 工作流 · 自动化**](agentic-workflows.md) —— L1/L2/L3 成熟度 + Tool 设计 + 评估 + 成本 + 安全
- [**Text-to-SQL 平台**](text-to-sql-platform.md) —— 自然语言查询数据仓库 · Schema RAG · 权限穿透 · 准确性策略
- [**多模检索流水线**](multimodal-search-pipeline.md) —— 图 / 文 / 音 / 视混合检索

## 架构视角的端到端场景

**从架构组件出发的流水线模板**——适合要搭建某条链路时参考。

- [流式入湖](streaming-ingestion.md) —— CDC + 事件流持续入湖
- [Real-time Lakehouse](real-time-lakehouse.md) —— 端到端分钟级一体化（BI + AI + DS 都读准实时）
- [离线训练数据流水线](offline-training-pipeline.md) —— 可复现 + PIT 的训练集生成
- [Feature Serving](feature-serving.md) —— 在线推理的毫秒级特征拉取

