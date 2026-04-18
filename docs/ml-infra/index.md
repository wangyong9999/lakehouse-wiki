---
title: ML 基础设施
description: Model Registry / Serving / Training / GPU 调度 / LLM Gateway
---

# ML 基础设施

!!! tip "它是什么"
    AI 负载（RAG、推荐、多模检索、Agent）背后的**工程底座**。和 "AI workloads" 的区别是：前者是"应用怎么跑"，后者是"应用下面的水电煤"。

## 模型生命周期

- [Model Registry](model-registry.md) —— 模型 + 版本 + 元数据一等公民
- [Model Serving](model-serving.md) —— vLLM / TGI / Ray Serve / KServe / Triton
- [训练编排](training-orchestration.md) —— Kubeflow / Flyte / Ray Train

## 资源与平台

- [GPU 调度](gpu-scheduling.md) —— 多租户、抢占、碎片整理
- [**LLM Gateway**](llm-gateway.md) ⭐ —— LiteLLM / Portkey / Helicone / OpenRouter 统一代理层

## 和其他节的关系

- **上游**：[Embedding 流水线](../ai-workloads/embedding-pipelines.md) / [RAG](../ai-workloads/rag.md) / [Agents](../ai-workloads/agents-on-lakehouse.md) 都依赖这层
- **下游**：[湖表](../lakehouse/lake-table.md) 是训练数据和产出模型引用数据的来源
- **姊妹**：[Feature Store](../ai-workloads/feature-store.md)
- **治理**：[Catalog](../catalog/index.md) 现代形态（Unity / Polaris）把**模型也当一类资产**管

## 前沿 / 对比跳转

- [LLM 推理优化](../frontier/llm-inference-opt.md) —— Model Serving 的性能优化
- [MLOps 生命周期](../ai-workloads/mlops-lifecycle.md) —— 闭环叙事
- [Feature Store 横比](../compare/feature-store-comparison.md)

