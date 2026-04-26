---
title: 参考资料 · AI 应用 / RAG / Agent
type: reference
status: stable
tags: [reference, references, ai-workloads]
description: RAG / Agent / LangChain / LlamaIndex / Anthropic 等权威
last_reviewed: 2026-04-25
---

# 参考资料 · AI 应用 / RAG / Agent

## RAG 论文

- **[Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)** _(2020, paper - Lewis et al. / Meta)_ —— RAG 概念奠基论文。
- **[Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://arxiv.org/abs/2310.11511)** _(2023, paper)_ —— LLM 自决策何时检索 + 自我评估。
- **[Corrective RAG (CRAG)](https://arxiv.org/abs/2401.15884)** _(2024, paper)_ —— 检索后纠正的范式。
- **[Anthropic - Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)** _(2024, blog)_ —— Contextual chunk pre-prompting，工业可复现 35% 提升。
- **[Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)** _(2023, paper - Stanford)_ —— LLM 长上下文中间内容易失，RAG chunk 顺序设计的依据。

## Agent 论文与协议

- **[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)** _(2022, paper)_ —— Agent 推理-行动循环奠基。
- **[Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761)** _(2023, paper)_ —— LLM 工具使用。
- **[Anthropic - Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)** _(2024, blog)_ —— 5 类 Agent 模式 + 何时用 workflow vs agent。**工业建议必读**。
- **[Model Context Protocol (MCP) Specification](https://modelcontextprotocol.io/)** _(2024+, official-doc - Anthropic)_ —— Anthropic 提出的 LLM-工具开放协议。
- **[Anthropic Claude Engineering Blog](https://www.anthropic.com/engineering)** _(blog)_ —— Constitutional AI / Claude API / Agent SDK 等深度内容。

## 框架文档

- **[LangChain Documentation](https://docs.langchain.com/)** _(official-doc)_ —— Models / Agents / Tools / LangGraph / Deep Agents 等模块。
- **[LlamaIndex Documentation](https://developers.llamaindex.ai/python/framework/)** _(official-doc)_ —— Component Guides 含 Indexing/Loading/Storing/Querying/Evaluating/Observability/MCP；5 workflow 模式 (Agents/Workflows/Structured Data/Query/Chat)。**与本 wiki ai-workloads/ 的"应用 / Runtime 桥 / 工程纪律"三层组织部分对齐**。
- **[OpenAI Cookbook](https://cookbook.openai.com/)** _(official-doc)_ —— 实践代码模式。

## 评估与 Observability

- **[RAGAS: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217)** _(2023, paper)_ —— RAG 评估指标 (faithfulness / answer relevancy / context precision / recall)。
- **[Evaluating LLM Applications with TruLens](https://www.trulens.org/)** _(official-doc)_ —— TruLens RAG triad evaluation。
- **[OpenAI Evals](https://github.com/openai/evals)** _(official-doc)_ —— 评估框架。

## 安全 / Guardrails

- **[OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)** _(official-doc)_ —— LLM 应用安全清单。
- **[Anthropic - Constitutional AI](https://www.anthropic.com/news/claudes-constitution)** _(blog)_ —— Constitutional 方法。
- **[NVIDIA NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)** _(official-doc)_ —— 输入输出 guardrails 框架。

## 综述

- **[A Survey on RAG Meeting LLMs: Towards Retrieval-Augmented Large Language Models](https://arxiv.org/abs/2405.06211)** _(2024, survey)_ —— 工业综述。
- **[The Rise and Potential of Large Language Model Based Agents](https://arxiv.org/abs/2309.07864)** _(2023, survey)_ —— Agent 系统综述。

---

**待补**：2025-2026 RAG / Agent 演进；vLLM Agent serving；Agent Memory / Long-term context 最新研究
