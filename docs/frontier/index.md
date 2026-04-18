---
title: 研究前沿
description: 论文速读、趋势观察、Benchmark、AI 治理
---

# 研究前沿

团队外的最新论文、早期 OSS、工业界趋势沉淀。**本章内容**偏向"正在发生"的技术，读的时候请注意**时效性 + 辩证性** —— 每页都标注了适用版本范围，并在可能的地方注明"争议/未验证"。

## 量级数字与 Benchmark

- [**量级数字总汇**](benchmark-numbers.md) ⭐ —— 湖仓 / 检索 / LLM 各场景的典型量级数字，决策时心里有数
- [Benchmark 参考](benchmarks.md) —— 主流 Benchmark 汇总与使用指引

## LLM / AI 前沿专题

- [**LLM 推理优化**](llm-inference-opt.md) —— vLLM / SGLang / Flash Attention / Speculative / MoE / 量化
- [**RAG 前沿 2025**](rag-advances-2025.md) —— Contextual Retrieval / CRAG / Self-RAG / Agentic RAG 及其边界
- [**向量检索前沿**](vector-trends.md) —— Matryoshka / Binary / SPLADE v3 / ColBERT v2 的实务选择
- [**AI 治理**](ai-governance.md) —— EU AI Act / Guardrails / Red Teaming，合规视角

## 论文笔记

- [DiskANN 论文笔记](diskann-paper.md) —— NeurIPS 2019 · 单机 SSD 十亿级 ANN

## 待补（下一轮）

- 月更 Digest（向量 / 湖仓 / AI 方向）
- Lakehouse 论文综述（CIDR 2021 原始 Lakehouse paper）
- 更多论文笔记（Contextual Retrieval / ColBERT v2 / vLLM 等 S 级）
- 季度趋势 report

## 贡献方式

每篇论文一个独立页面，推荐结构：

```
一句话收获 · 论文解决什么 · 核心创新 · 实验结论 · 工程启示 · 对团队的价值 · 现实检视
```

"现实检视"段落说明：论文的哪些结论在工业界已被复现、哪些只在特定数据集上成立、有什么已知的限制。**强烈建议前沿页面都保留这一段**。
