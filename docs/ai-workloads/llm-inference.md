---
title: LLM Inference · 推理栈与服务引擎
type: system
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: vLLM 0.10+ · SGLang 0.4+ · TensorRT-LLM / Triton · 2024-2026 生态
tags: [ai, llm, inference, serving, vllm, sglang]
status: draft
---

# LLM Inference · 推理栈与服务引擎

!!! warning "本页建设中 · S25-B 即将填充"
    本页从 `frontier/llm-inference-opt.md` 下沉而来（按 [ADR 0009](../adr/0009-frontier-to-main-migration.md)）· 内容将在 S25-B commit 填充。

    覆盖范围：
    - **核心机制**：KV cache / PagedAttention / 连续批次 / 前缀缓存 / Speculative decoding
    - **主流引擎**：vLLM / SGLang / TensorRT-LLM / Dynamo / Triton
    - **2026 生态**：vLLM 0.10+ 生产标配 · SGLang 0.4+ Structured Output 优化 · TRT-LLM 商业深度
    - **生产模式**：批次 / 队列 / Tensor 并行 / Pipeline 并行 / 托管方案（Modal / Together / Anyscale）
    - **成本 / 吞吐分析**
