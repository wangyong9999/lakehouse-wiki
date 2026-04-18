---
title: 场景指南
description: 端到端的典型场景 —— 业务视角 + 架构视角，都能对着看
---

# 场景指南

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
- [**多模检索流水线**](multimodal-search-pipeline.md) —— 图 / 文 / 音 / 视混合检索

## 架构视角的端到端场景

**从架构组件出发的流水线模板**——适合要搭建某条链路时参考。

- [流式入湖](streaming-ingestion.md) —— CDC + 事件流持续入湖
- [Real-time Lakehouse](real-time-lakehouse.md) —— 端到端分钟级一体化（BI + AI + DS 都读准实时）
- [离线训练数据流水线](offline-training-pipeline.md) —— 可复现 + PIT 的训练集生成
- [Feature Serving](feature-serving.md) —— 在线推理的毫秒级特征拉取

## 待补（下一批）

- 即席探索 / Notebook 深挖（目前仅 business-scenarios 里综述）
- 经典 ML 预测深挖（从 offline-training-pipeline 拆分独立）
- Text-to-SQL / AI-native Analytics 独立深挖（目前在 agentic-workflows 里）
- Cross-cloud / 多区域
- 数据迁移手册（Hive → Iceberg）
