---
title: Structured Output · JSON / Schema / Function Calling
type: concept
depth: 进阶
level: A
last_reviewed: 2026-04-21
applies_to: OpenAI Structured Outputs (2024-08+) · Anthropic Tool Use · Instructor · Outlines · Marvin · Gemini JSON mode · 2024-2026
tags: [ai, llm, json-mode, function-calling, structured-output, pydantic]
status: draft
---

# Structured Output · LLM 结构化输出

!!! warning "本页建设中 · S25-E 即将填充"
    本页讲 LLM **输出结构化**的工程化 · 是生产 AI app 的核心能力 · 从 Function Calling 到 Schema 约束的完整谱系。

    覆盖范围：
    - **原生 JSON mode**：OpenAI · Anthropic · Gemini · 各家 API 差异
    - **Schema 约束**：Structured Outputs (schema-guaranteed) vs Prompt-based JSON
    - **开源库**：Instructor (Pydantic-based) · Outlines (grammar-constrained) · Marvin · LangChain output parsers
    - **Function Calling**：Tool use 作为结构化输出的特例
    - **生产模式**：重试 · fallback · 部分 valid 处理 · 流式结构化
    - **陷阱**：JSON mode 非 schema 强约束 · 嵌套对象 token 爆 · 多模态结构化 · 和 Agent Tool 的关系
