---
title: RAG 评估
type: concept
depth: 进阶
prerequisites: [rag, evaluation]
tags: [ai, rag, evaluation]
related: [rag, evaluation, prompt-management]
systems: [ragas, trulens, langfuse, promptfoo]
status: stable
---

# RAG 评估

!!! tip "一句话理解"
    检索评估只看"能不能召回到"；RAG 评估还要看"回答对不对、引用正不正、有没有幻觉"。没有这套框架，**RAG 调参就是猜**。

!!! abstract "TL;DR"
    - RAG 质量 = **Retrieval 质量 + Generation 质量** 两层相乘
    - 三个必测指标：**Groundedness（有无幻觉）/ Context Relevance（召回准度）/ Answer Relevance（是否答到点）**
    - **RAGAS / TruLens / Promptfoo** 是主流开源评估框架
    - 评估集要**覆盖真实 query 分布**，不是凭感觉选
    - **LLM-as-Judge** 靠谱度可接受（85%+），值得作为自动化基线

## RAG 质量的五维度

| 维度 | 含义 | 如何衡量 |
| --- | --- | --- |
| **Groundedness（扎实性）** | 回答是否基于召回的材料，有没有幻觉 | LLM-as-Judge 逐句比对 |
| **Context Relevance（上下文相关性）** | 召回的材料对这个 query 是否相关 | 检索指标 + LLM 判 |
| **Answer Relevance（答案相关性）** | 回答是否真的回答了问题 | LLM 判 |
| **Completeness（完整性）** | 答案是否覆盖所有相关要点 | 人工或 LLM 判 |
| **Citation Accuracy（引用准确性）** | 引用的出处是否真的支持该主张 | 规则 + LLM 判 |

五个维度至少**前三个必测**。

## 主流工具

### RAGAS

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

dataset = Dataset.from_pandas(df)   # 含 question/contexts/answer/ground_truth
result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision],
)
print(result)
```

开源、Python 原生、主流。内置 LLM-as-Judge 实现。

### TruLens

类似 RAGAS 但更强的 trace / 观测能力。每次 RAG 调用都有完整 span（检索 / rerank / generation），可以事后分析。

### Langfuse

偏 LLM 可观测性产品，评估是其中一块。和 Prompt 管理一起用。

### Promptfoo

配置文件驱动的评估，适合 CI 跑：

```yaml
prompts: [file://prompts/rag.yaml]
providers: [openai:gpt-4]
tests:
  - vars:
      query: "如何取消订单？"
    assert:
      - type: llm-rubric
        value: "answer should mention 订单管理中心"
      - type: contains
        value: "[source]"
```

## 评估集（Golden Set）设计

**最关键**。没有好评估集，工具再多也是玩具。

### 分布对齐真实流量

- 抓线上 200-500 条真实 query
- 标注**正确答案 + 应被引用的 chunk**
- 保证覆盖：问题类型（事实 / 比较 / 总结）× 难度（简单 / 中等 / 困难）× 语种

### 难度分层

```
Tier 1: 直接事实查询（"产品 A 的价格"）
Tier 2: 需要多 chunk 合成（"对比 A 和 B"）
Tier 3: 需要推理 / 多轮（"根据历史数据推测…"）
Tier 4: 反例 / 越界（"怎么黑进系统？" → 应拒答）
```

Tier 1 你得 > 95%；Tier 3 > 70% 就很好；Tier 4 则应 100% 安全拒答。

### 维护

- 每季度抽样新 query 加入
- 发现生产 bad case → 加入评估集
- 旧 sample 退役要记录

## LLM-as-Judge

用强 LLM（GPT-4 / Claude）当裁判打分：

```python
judge_prompt = """
判断下面答案是否忠实于材料（Groundedness）。
材料：{contexts}
答案：{answer}
规则：
- 所有主张必须能在材料中找到支持 → 5 分
- 大部分能找到，小部分无法验证 → 3-4 分
- 关键主张找不到支持 → 1-2 分

只输出数字 1-5。
"""
```

**一致性**：LLM judge 和人工标注在多数任务上有 85%+ 一致率。足够自动化。

**成本控制**：
- 小评估集跑 GPT-4 judge
- 大规模跑 mini 模型 judge

## CI 集成

```yaml
# GitHub Actions
on: [pull_request]
jobs:
  rag-eval:
    steps:
      - uses: actions/checkout@v4
      - run: pip install ragas
      - run: python evals/rag_eval.py --dataset golden.jsonl
      - run: python evals/check_regression.py --threshold 0.85
```

CI 卡"任何一个指标掉 5% 以上" → 阻断合并。

## 常见陷阱

- **只看 metrics 不看 bad case** —— 指标没动但新类别 query 崩了
- **评估集太小**（< 30） —— 统计不显著
- **评估集和训练数据重合** —— 乐观高估
- **忽略成本维度** —— 质量涨 2% 但延迟 / 价格涨 5 倍
- **LLM judge 用和 generator 同一个模型** —— 自己打自己有偏

## 评估报表示例

上线候选 vs 生产：

```
Metric                        Prod (baseline)    Candidate      Δ
Groundedness                  0.89               0.92          +0.03 ✅
Context Relevance             0.76               0.82          +0.06 ✅
Answer Relevance              0.88               0.87          -0.01 ≈
Citation Accuracy             0.91               0.94          +0.03 ✅
Latency p95 (ms)              1200               1350          +12% ⚠️
Cost per query ($)            0.012              0.015         +25% ⚠️
```

必须把**所有维度摆一起**，而不是只看单一 metric。

## 相关

- [RAG](rag.md)
- [检索评估](../retrieval/evaluation.md)（更基础，偏检索层）
- [Prompt 管理](prompt-management.md)
- [Rerank](../retrieval/rerank.md)

## 延伸阅读

- RAGAS: <https://docs.ragas.io/>
- TruLens: <https://www.trulens.org/>
- *Evaluating RAG: A Practitioner's Guide*（Pinecone / LlamaIndex 博客系列）
- *Automatic Evaluation of Retrieval-Augmented Generation*（各种 2024 论文）
