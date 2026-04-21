---
title: Guardrails · 输入输出安全防护
type: system
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: Llama Guard 3 · NeMo Guardrails 2026 · Guardrails AI · Lakera Guard · OpenAI Moderation · 2024-2026 生态
tags: [ai, safety, guardrails, prompt-injection, pii]
status: draft
---

# Guardrails · 输入输出安全防护

!!! warning "本页建设中 · S25-F 即将填充"
    本页是应用层 Guardrails 工程落地 · 与 [AI 治理（frontier）](../frontier/ai-governance.md) 分工清晰：**本页讲工程** · ai-governance 讲 **法规 / 组织流程**。

    覆盖范围：
    - **输入 Guardrails**：Prompt Injection 检测 · PII 脱敏 · Jailbreak 防御
    - **输出 Guardrails**：Toxicity / 事实一致 / 策略合规
    - **工具**：Llama Guard 3 · NeMo Guardrails 2026（IORails）· Guardrails AI · Lakera Guard · OpenAI Moderation API · Azure Content Safety
    - **集成模式**：Pre-LLM / Post-LLM / In-LLM（作为 tool）· Defense-in-depth
    - **生产**：延迟开销 / 误报率 / 多语言 / 成本
