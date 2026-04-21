---
title: LLM 推理优化（已迁移）
type: concept
status: superseded
superseded_by: ai-workloads/llm-inference.md
last_reviewed: 2026-04-21
---

# LLM 推理优化 · 已迁移

!!! warning "本页已 superseded"
    按 [ADR 0009](../adr/0009-frontier-to-main-migration.md) frontier→main 下沉判据 · 本话题（vLLM / SGLang / TensorRT-LLM / 推理栈）已是**生产标配** · 不再是"前沿" · 内容迁移到：

    **→ [LLM Inference · 推理栈与服务引擎](../ai-workloads/llm-inference.md)**

    新页相比本页的增量：
    - 2026 最新版本（vLLM 0.10+ · SGLang 0.4+ · 含 async scheduling + zero-bubble overlap · Gemma 4 支持）
    - **NVIDIA Dynamo**（2025 下一代 Inference Server）
    - **Serverless LLM 托管对比**（Modal / Together / Replicate / Bedrock）
    - 工业真实瓶颈分布（多数团队问题是账单 · 不是 QPS）
    - 完整"已验证 vs 营销口号"矩阵
    - 和 [LLM Gateway](../ai-workloads/llm-gateway.md) / [Semantic Cache](../ai-workloads/semantic-cache.md) 的明确分工

    本 stub 保留用于维护 URL 稳定性。外部引用请更新到 `ai-workloads/llm-inference.md`。
