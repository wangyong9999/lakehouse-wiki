---
title: AI 应用
description: LLM 时代的应用层 · 从 RAG / Agent / MCP 到推理栈 / Guardrails / Structured Output
applies_to: 2024-2026 LLM 应用工程 · vLLM 0.10+ / SGLang 0.4+ / LangGraph 0.2+ / MCP 2025-11 spec
last_reviewed: 2026-04-21
---

# AI 应用

!!! tip "一句话定位"
    **湖仓 + 多模检索是底座 · AI 应用是负载**。本章讲 "LLM 应用层怎么被工程化" · 从 **应用模式**（RAG / Agent / Structured Output）到 **应用基础设施**（Gateway / Inference / Guardrails / Observability）。**不讲 ML 平台底层**（Model Serving / Feature Store / GPU 调度 → 看 ml-infra）· **不讲检索机制**（Embedding / ANN / Rerank → 看 retrieval）。

!!! abstract "TL;DR"
    - **核心命题**：LLM 不是模型 · 是一个生态 · 应用层有 20+ 个成熟话题
    - **应用模式**：RAG / Agent / Structured Output / Function Calling / Chat 是 5 个核心 pattern
    - **基础设施**：Gateway（代理）· Inference（推理）· Cache（语义 + 系统级）· Observability（追踪）· Guardrails（安全）
    - **关键协议**：MCP（Anthropic 2024）已成为 2025-2026 跨 host Tool 事实标准
    - **和 ml-infra 分工**：本章讲 LLM 应用 · ml-infra 讲 ML 平台底层（Feature Store / Model Registry / 训练 / 部署）
    - **和 retrieval 分工**：本章讲 **RAG 应用层**（chunking 策略 / prompt 构造 / 评估）· retrieval 讲**检索机制**（ANN / Hybrid / Rerank 算法）

!!! warning "边界声明 · 避免走错章"
    本章**不讲**以下话题 · 请去对应章：

    - **检索机制**（Embedding / ANN / Rerank / 向量库）→ [retrieval/](../retrieval/index.md)
    - **ML 平台**（Feature Store / Model Registry / Model Serving / 训练编排 / GPU 调度）→ [ml-infra/](../ml-infra/index.md)
    - **BI × LLM**（Text-to-SQL / 语义层 LLM 集成 / Auto-Viz）→ [bi-workloads/bi-plus-llm.md](../bi-workloads/bi-plus-llm.md)
    - **端到端业务场景**（RAG on Lake / Agentic Workflows / 推荐系统）→ [scenarios/](../scenarios/index.md)
    - **前沿 / 研究 / 治理规范**（EU AI Act / Red Teaming 组织流程）→ [frontier/](../frontier/index.md)

## 学习路径 · 4 阶段

**Step 1 · 了解应用模式**
- [RAG](rag.md) ⭐ —— 检索增强生成 · 工业 LLM 应用最普及 pattern
- [MCP](mcp.md) ⭐ —— 跨 host Tool 协议 · 2025 起 Agent 事实标准
- [Structured Output](structured-output.md) —— JSON mode / Function Calling / Schema 约束

**Step 2 · 构建 Agent 能力**
- [Agent Patterns](agent-patterns.md) ⭐ —— ReAct / Reflexion / 多 agent / Memory / HITL + 框架生态（LangGraph / AutoGen / Claude SDK / OpenAI Agents SDK / CrewAI）
- [Agents on Lakehouse](agents-on-lakehouse.md) —— 湖仓专属 Agent tool 设计

**Step 3 · 上生产**
- [LLM Gateway](llm-gateway.md) —— 统一代理 + 限流 + 重试 + 缓存 + 监控
- [LLM Inference](llm-inference.md) —— vLLM / SGLang / TRT-LLM / KV cache / 连续批次
- [Semantic Cache](semantic-cache.md) —— 语义缓存 + 系统级 Prompt Caching
- [Guardrails](guardrails.md) —— Llama Guard / NeMo / Lakera · 输入输出双向

**Step 4 · 工程纪律**
- [Prompt 管理](prompt-management.md) —— 版本化 + DSPy + Prompt Caching
- [RAG 评估](rag-evaluation.md) —— RAGAS / TruLens / Groundedness / Context Relevance

## 角色建议

| 角色 | 重点阅读 |
|---|---|
| **LLM 应用工程师（新手）** | rag → mcp → prompt-management → llm-gateway |
| **LLM 应用工程师（资深）** | 全部 + [agents on lakehouse 场景](../scenarios/agentic-workflows.md) + [RAG on Lake 场景](../scenarios/rag-on-lake.md) |
| **AI 平台工程师** | llm-inference → llm-gateway → guardrails → [ml-infra/](../ml-infra/index.md) |
| **数据 / BI 工程师接触 LLM** | rag + mcp → [BI × LLM](../bi-workloads/bi-plus-llm.md) + [Text-to-SQL 场景](../scenarios/text-to-sql-platform.md) |
| **SRE / Security** | guardrails + llm-gateway + [AI 治理](../frontier/ai-governance.md) |

## 横向对比（跳转 compare）

- [Feature Store 横比](../compare/feature-store-comparison.md)（ML 平台侧）
- [Embedding 模型横比](../compare/embedding-models.md) · [Rerank 模型横比](../compare/rerank-models.md)（检索侧）

## 前沿 · 跳转 frontier（话题仍在演进）

- [RAG 前沿](../frontier/rag-advances-2025.md) —— CRAG / Self-RAG / Agentic RAG 深度
- [向量检索前沿](../frontier/vector-trends.md) —— RaBitQ / BQ / Matryoshka 前沿部分
- [AI 治理](../frontier/ai-governance.md) —— EU AI Act / Red Teaming 组织流程

**注**：原 `frontier/llm-inference-opt.md` 已下沉为本章 [LLM Inference](llm-inference.md)（按 [ADR 0009](../adr/0009-frontier-to-main-migration.md) frontier→main 下沉判据）。

## 底层依赖

- [ML 基础设施](../ml-infra/index.md) —— Model Registry / Serving / Training / GPU / Feature Store
- [多模检索](../retrieval/index.md) —— 向量 / Hybrid / Rerank / 多模

## 场景

- [RAG on Lake](../scenarios/rag-on-lake.md) · [Agentic Workflows](../scenarios/agentic-workflows.md) · [Text-to-SQL](../scenarios/text-to-sql-platform.md) · [多模检索流水线](../scenarios/multimodal-search-pipeline.md)
- [推荐系统](../scenarios/recommender-systems.md) · [欺诈检测](../scenarios/fraud-detection.md) · [CDP](../scenarios/cdp-segmentation.md)
