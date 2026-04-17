---
title: 检索评估（Recall / MRR / nDCG）
type: concept
tags: [retrieval, evaluation, metrics]
aliases: [检索指标, Retrieval Metrics]
related: [vector-database, hybrid-search, rerank, rag]
systems: []
status: stable
---

# 检索评估

!!! tip "一句话理解"
    "检索准不准"不能靠感觉，必须有**度量**。三个基本指标：**Recall@K**（召回有没有覆盖到）、**MRR**（答案在多靠前）、**nDCG**（整体排序质量）。没有这三个，你无法做 A/B，也无法发现模型退化。

## 三个核心指标

### Recall@K

> **Top-K 结果里，有多少个相关文档被命中？**

$$\text{Recall@K} = \frac{|\text{relevant} \cap \text{top\_K}|}{|\text{relevant}|}$$

- 值域 [0, 1]，越大越好
- 对"覆盖率"最敏感——漏了重要文档会直接掉
- **RAG 场景下最关键**：没被召回的文档 LLM 无法使用

### MRR（Mean Reciprocal Rank）

> **正确答案出现在第几位？用 1/rank 加权。**

$$\text{MRR} = \frac{1}{Q} \sum_{q=1}^{Q} \frac{1}{\text{rank}_q}$$

- 值域 (0, 1]，越大越好
- 只看**第一个**相关结果的位置
- 适合"确切答案"型场景（QA、文档查找）

### nDCG（normalized Discounted Cumulative Gain）

> **综合多个相关结果的排序质量，相关度可分级。**

$$\text{DCG}@K = \sum_{i=1}^{K} \frac{2^{rel_i} - 1}{\log_2(i+1)}$$

nDCG = DCG / IDCG（理想 DCG）

- 值域 [0, 1]，越大越好
- 支持"很相关 / 有点相关 / 无关"三级标注
- 推荐 / 多答案场景的标准指标

## 其他常用

- **Precision@K**：Top-K 里有多少是相关的
- **F1@K**：Precision 和 Recall 的调和平均
- **Hit Rate@K**：Top-K 里是否**至少有一个**相关（二值）

## 怎么构造评测集

评测集质量决定指标可信度。三条路：

1. **专家标注** —— 业务专家标一批 query + 相关文档集合
2. **行为标签** —— 用户点击 / 消费作弱标签（有噪，但规模大）
3. **LLM 辅助标注** —— 让强 LLM 判相关性（要抽样人工校验）

**规模建议**：至少 100 条 query，分领域 / 难度分桶。golden set 应该**定期更新**，避免过拟合到老测试集。

## 在 RAG 流水线里的位置

```mermaid
flowchart LR
  golden[Golden Set<br/>query → relevant docs] --> run[Run Retrieval]
  run --> metrics[Recall@K / MRR / nDCG]
  metrics --> monitor[(监控看板)]
  metrics --> ci[CI Gate]
```

**把检索指标接进 CI / 上线流程**：模型升级前先跑 golden set，指标掉了不许上线。

## 常见陷阱

- **只看 Recall@10 忽视 Recall@100** —— 精排好不好的前提是召回足够
- **评测集老化** —— 上线一年后业务已经变了
- **单点指标** —— 一个 Recall 看不到"tail queries"崩坏；要分桶看
- **用训练数据做评测** —— 永远乐观；必须用独立 golden set
- **没对齐业务感受** —— 指标涨但用户说更烂了——说明 golden 没反映真实查询分布

## 相关

- [RAG](../ai-workloads/rag.md)
- [Rerank](rerank.md)
- [Hybrid Search](hybrid-search.md)

## 延伸阅读

- *Introduction to Information Retrieval* (Manning et al.) —— 第 8 章
- *Understanding the nDCG metric* —— 多篇技术博客
- *LLM-as-a-Judge: A Scalable Approach to Evaluating LLM Applications*
