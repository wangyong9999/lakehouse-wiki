---
title: 场景指南
description: 端到端的典型场景 —— 输入、流水线、关键选型
---

# 场景指南

## 从业务找入口 · 强烈推荐先读

- [**E2E 业务场景全景**](business-scenarios.md) —— 业务视角的分类框架 + Top 10 主流场景 + 前沿方向 + 决策矩阵 + Benchmark 索引。**新同事带着业务问题进来，这里是第一站**。

## 架构视角的端到端场景

- [RAG on Lake](rag-on-lake.md) —— 把湖作为 RAG 的单一事实源
- [BI on Lake](bi-on-lake.md) —— 把传统 BI 负载搬到湖仓之上
- [多模检索流水线](multimodal-search-pipeline.md) —— 图 / 文 / 音 / 视混合检索
- [流式入湖](streaming-ingestion.md) —— CDC + 事件流持续入湖
- [Real-time Lakehouse](real-time-lakehouse.md) —— 端到端分钟级一体化（BI + AI + DS 都读准实时）
- [离线训练数据流水线](offline-training-pipeline.md) —— 可复现 + PIT 的训练集生成
- [Feature Serving](feature-serving.md) —— 在线推理的毫秒级特征拉取

## 业务深挖

- [推荐系统 · 搜索 · 发现](recommender-systems.md) —— 四阶段流水线（召回 → 粗排 → 精排 → 重排）+ 冷启动 + 近实时
- [Agentic 工作流 · 自动化](agentic-workflows.md) —— LLM + 工具 + 控制循环；Tool 设计 + 评估 + 成本 + 安全

## 待补

- Cross-cloud / 多区域
- 数据迁移手册（Hive → Iceberg 等）
- 欺诈检测深挖（现在在 business-scenarios.md 里有综述）
- Text-to-SQL / AI-native Analytics 独立深挖
