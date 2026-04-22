---
title: AI 应用
description: LLM 时代的应用层 · 三层分组 · 应用模式 / 应用-Runtime 桥 / 工程纪律
applies_to: 2024-2026 LLM 应用工程 · vLLM 0.10+ / SGLang 0.4+ / LangGraph 0.2+ / MCP 2025-11 spec
last_reviewed: 2026-04-21
---

# AI 应用

!!! tip "一句话定位"
    **湖仓 + 多模检索是底座 · AI 应用是负载**。本章讲 "LLM 应用层怎么被工程化" · 按**三层分组**组织页面（**应用模式 / 应用-Runtime 桥 / 工程纪律**）· 让读者知道不同层该什么时间进入。**不讲 ML 平台底层**（Model Serving / Feature Store / GPU 调度 → 看 ml-infra）· **不讲检索机制**（Embedding / ANN / Rerank → 看 retrieval）。

!!! abstract "TL;DR"
    - **分层结构**：
        - **层 1 · 应用模式**（RAG · MCP · Agent Patterns · Structured Output · Agents on Lakehouse）—— 写什么样的 AI 应用
        - **层 2 · 应用-Runtime 桥**（LLM Inference · LLM Gateway · Semantic Cache）—— LLM 怎么被服务到应用
        - **层 3 · 工程纪律**（Prompt 管理 · Evaluation · Observability · Guardrails · Authorization · Conversation Lifecycle）—— 生产 AI 必过的质量 / 安全 / 运维
    - **和 ml-infra 分工**：本章讲 **LLM 应用层** · ml-infra 讲 **ML 平台底层**（Feature Store / Model Registry / 训练 / 通用部署）· llm-inference 例外在本章是因为它是 LLM-specific runtime
    - **和 retrieval 分工**：本章讲 **RAG 应用层**（chunking / prompt / 评估）· retrieval 讲 **检索机制**（ANN / Hybrid / Rerank 算法）
    - **关键协议**：MCP（Anthropic 2024）已是 2025-2026 跨 host Tool 事实标准

!!! warning "边界声明 · 避免走错章"
    本章**不讲**以下话题 · 请去对应章：

    - **检索机制**（Embedding / ANN / Rerank / 向量库）→ [retrieval/](../retrieval/index.md)
    - **ML 平台**（Feature Store / Model Registry / Model Serving / 训练编排 / GPU 调度）→ [ml-infra/](../ml-infra/index.md)
    - **BI × LLM**（Text-to-SQL / 语义层 LLM 集成 / Auto-Viz）→ [bi-workloads/bi-plus-llm.md](../bi-workloads/bi-plus-llm.md)
    - **端到端业务场景**（RAG on Lake / Agentic Workflows / 推荐系统）→ [scenarios/](../scenarios/index.md)
    - **法规 / 治理规范**（EU AI Act / NIST AI RMF / 中国生成式 AI 管理办法）→ [ops/compliance §4](../ops/compliance.md)

## 三层分组

### 层 1 · 应用模式（你要写什么样的 AI 应用）

- [**RAG**](rag.md) ⭐ —— 检索增强生成 · 工业 LLM 应用最普及 pattern · 含 GraphRAG
- [**MCP**](mcp.md) ⭐ —— 跨 host Tool 协议 · 2025 起 Agent 事实标准
- [**Agent Patterns**](agent-patterns.md) ⭐ —— ReAct / Reflexion / Multi-agent / Memory / HITL / **执行契约** + 框架生态（LangGraph / Microsoft Agent Framework / OpenAI Agents SDK / Claude Agent SDK / Google ADK / CrewAI）
- [**Structured Output**](structured-output.md) —— JSON mode / Function Calling / Schema 约束 / Instructor / Outlines / SGLang CFSM
- [**Agents on Lakehouse**](agents-on-lakehouse.md) —— 湖仓专属 Agent tool 设计 + MCP × 湖仓架构

### 层 2 · 应用-Runtime 桥（LLM 怎么被服务到应用）

这一层是 **LLM-specific runtime** · 和 ml-infra 的通用 model serving 分工（本章讲 LLM specific · ml-infra 讲通用 ML）。

- [**LLM Inference**](llm-inference.md) ⭐ —— vLLM / SGLang / TensorRT-LLM / Dynamo · KV cache / 连续批次 / PagedAttention · Serverless 托管对比
- [**LLM Gateway**](llm-gateway.md) —— 统一代理 · 限流 / 重试 / 缓存 / 成本监控 / 路由 / 灰度
- [**Semantic Cache**](semantic-cache.md) —— 语义缓存 + **系统级 Prompt Caching**（Anthropic / OpenAI / Gemini）机制对比

### 层 3 · 工程纪律（生产 AI 必过的质量 / 安全 / 运维）

- [**Prompt 管理**](prompt-management.md) —— 版本化 · DSPy · Prompt Caching · System Prompt 工程
- [**LLM / RAG / Agent 评估**](rag-evaluation.md) ⭐ —— RAGAS · TruLens · DeepEval · SWE-bench · τ-bench · Agent 评估生产 5 维 · Eval vs Obs 分工
- [**LLM Observability**](llm-observability.md) ⭐ —— Trace / Cost / Latency / Version 四维契约 · OTel GenAI · Langfuse / LangSmith / Phoenix / Helicone · 事故归因模板
- [**Guardrails**](guardrails.md) ⭐ —— Llama Guard 3 · NeMo Guardrails 2026 IORails · Guardrails AI · Lakera · 输入输出双向 · Defense-in-Depth
- [**AI App Authorization**](authorization.md) ⭐ —— Tool ACL / Data ACL / Cache 隔离 / Log 隔离 / Identity 流转 / Multi-tenant
- [**Conversation Lifecycle**](conversation-lifecycle.md) ⭐ —— 会话状态 6 组件 · 3 种 history 裁剪 · Letta / ReMe / Mem0 · 多轮工程

## 学习路径 · 按角色顺序

**新手**（任一角色起步）：
- 层 1 先选 `rag → mcp → structured-output` 一对
- 搭一个最小可用应用（Gateway + 简单 RAG + 基础 prompt）
- 上 evaluation（RAG 最简 · 层 3 的 rag-evaluation）
- 再补 observability · guardrails · authorization（层 3 全家桶）

**资深 LLM 应用工程师**：
- 全章通读 · 重点 layered Prompt Caching × Semantic Cache 组合优化
- Agent 侧从 agent-patterns 模式 → 执行契约（§8）→ agents-on-lakehouse 湖仓专属
- 场景端到端：[agentic-workflows](../scenarios/agentic-workflows.md) · [rag-on-lake](../scenarios/rag-on-lake.md) · [text-to-sql-platform](../scenarios/text-to-sql-platform.md)

**AI 平台工程师**：
- 层 2 · llm-inference → llm-gateway → semantic-cache 全
- 层 3 · llm-observability → guardrails → authorization · 三大生产支柱
- 底层 [ml-infra/](../ml-infra/index.md)

**数据 / BI 工程师接触 LLM**：
- 层 1 rag + mcp + structured-output
- 相邻 [BI × LLM](../bi-workloads/bi-plus-llm.md) + [Text-to-SQL](../scenarios/text-to-sql-platform.md)

**SRE / Security**：
- 层 3 · guardrails + authorization + llm-observability · 三件都读
- llm-gateway（运维视角）
- 相邻 [AI 治理](../ops/compliance.md)（法规层）

## 角色建议速查

| 角色 | 首读路径 |
|---|---|
| **LLM 应用工程师（新手）** | rag → mcp → prompt-management → llm-gateway |
| **LLM 应用工程师（资深）** | 全层 1 + agent 执行契约（agent-patterns §8）+ conversation-lifecycle · 加 evaluation + observability |
| **AI 平台工程师** | llm-inference → llm-gateway → semantic-cache → llm-observability → guardrails → authorization |
| **数据 / BI 工程师** | rag + mcp + structured-output → [BI × LLM](../bi-workloads/bi-plus-llm.md) |
| **SRE / Security** | guardrails + authorization + llm-observability · llm-gateway |

## 横向对比（跳转 compare）

- [Feature Store 横比](../compare/feature-store-comparison.md)（ML 平台侧）
- [Embedding 模型横比](../compare/embedding-models.md) · [Rerank 模型横比](../compare/rerank-models.md)（检索侧）

## 2024-2026 新方向

- [RAG §4 高级范式](rag.md) —— Contextual Retrieval / CRAG / Self-RAG / Agentic RAG / GraphRAG / Multi-Query / HyDE / ColBERT v2 / LLMLingua
- [Embedding](../retrieval/embedding.md) · [Quantization](../retrieval/quantization.md) · [Sparse Retrieval](../retrieval/sparse-retrieval.md) —— Matryoshka / Binary / SPLADE / BM42 / ColBERT
- [AI 合规](../ops/compliance.md)（法规层）· [Guardrails §7 Red Teaming](guardrails.md)（工程层 + 对抗测试）

**注**：参见 [ADR 0010](../adr/0010-abolish-frontier-chapter.md) · 原 frontier/ 章节已按主题归属到机制章。

## 底层依赖

- [ML 基础设施](../ml-infra/index.md) —— Model Registry / Serving / Training / GPU / Feature Store
- [多模检索](../retrieval/index.md) —— 向量 / Hybrid / Rerank / 多模

## 场景（端到端）

- [RAG on Lake](../scenarios/rag-on-lake.md) · [Agentic Workflows](../scenarios/agentic-workflows.md) · [Text-to-SQL](../scenarios/text-to-sql-platform.md) · [多模检索流水线](../scenarios/multimodal-search-pipeline.md)
- [推荐系统](../scenarios/recommender-systems.md) · [欺诈检测](../scenarios/fraud-detection.md) · [CDP](../scenarios/cdp-segmentation.md)
