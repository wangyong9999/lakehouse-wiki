---
title: LLM / RAG / Agent Evaluation · 质量评估全景
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: RAGAS · TruLens · Langfuse · Promptfoo · Braintrust · DeepEval · SWE-bench · τ-bench · WebArena · 2024-2026 eval 生态
prerequisites: [rag, agent-patterns]
tags: [ai, rag, agent, evaluation, ragas, trulens]
aliases: [RAG Evaluation, Agent Evaluation, LLM Evaluation]
related: [rag, agent-patterns, prompt-management, llm-observability]
systems: [ragas, trulens, langfuse, promptfoo, deepeval, braintrust]
status: stable
---

# LLM / RAG / Agent Evaluation · 质量评估全景

!!! tip "一句话理解"
    **LLM 应用没有评估就是盲飞 · 有评估才能迭代**。本页覆盖**三类评估**：**RAG 质量**（Groundedness / Context / Answer）· **通用 LLM 任务**（分类 / 摘要 / 代码 / 翻译）· **Agent**（Task Success / Tool Accuracy / Step Efficiency）。和 [LLM Observability](llm-observability.md) 分工：Obs 讲"**发生了什么**"· Eval 讲"**质量怎么样**"。

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

## 通用 LLM 任务评估 · 非 RAG 场景

**除了 RAG · 大量 LLM 应用是"通用任务"**（分类 / 摘要 / 翻译 / 代码 / Chat）· 评估框架不同：

### 任务类型 × 评估维度

| 任务 | 主指标 | 典型工具 / Benchmark |
|---|---|---|
| **分类** | Accuracy · F1 · 混淆矩阵 | 自建 golden set · scikit-learn metrics |
| **摘要** | ROUGE · BLEU · BERTScore · LLM-as-Judge | ROUGE · Anthropic 摘要质量评分 |
| **翻译** | BLEU · COMET · METEOR · 人工 | sacreBLEU · COMET |
| **代码生成** | Pass@k · HumanEval · MBPP | EvalPlus · LiveCodeBench |
| **Chat / 通用对话** | LLM-as-Judge · Arena ELO · 用户满意度 | Chatbot Arena · MT-Bench |
| **Long-context** | Needle-in-Haystack · RULER | RULER · Needle Test |
| **推理** | GSM8K · MATH · MMLU-Pro · Math-Verify | 公开 benchmark |
| **Safety** | ToxiGen · BOLD · 自建红队集 | Llama Guard 分类 |
| **Instruction following** | IFEval · LLM-as-Judge | IFEval |

### 关键原则

1. **离线 benchmark + 在线 A/B 双轨**：离线挡回归 · 在线看真实
2. **LLM-as-Judge 广泛适用但非万能**：主观类任务效果好 · 客观类任务用硬指标
3. **评估模型最好不是被评估模型**：自己评自己有偏（详见 §陷阱）
4. **任务不同指标不同** · 不要一刀切"answer relevance"

### 主流通用 Eval 工具

| 工具 | 定位 | 开源 |
|---|---|---|
| **OpenAI Evals** | OpenAI 官方 eval harness · 可扩展 | ✅ |
| **DeepEval**（Confident AI）| Pytest 风格 LLM eval · CI 友好 | ✅ |
| **Promptfoo** | Config 驱动 · CI 最顺 | ✅ |
| **Braintrust** | 商业 · Eval + Obs 一体 | ❌ |
| **Langfuse Evaluations** | 商业 / 自托管 · 内置 eval runner | ✅ MIT |
| **lm-evaluation-harness**（EleutherAI）| 学术 benchmark 统一 runner | ✅ |

## Agent 评估 · 比 RAG 更难

详见 [Agent Patterns § 7 Agent 评估](agent-patterns.md) 的 benchmark 部分。本节**扩展生产维度**：

### 生产 Agent 评估 5 维

| 维度 | 测法 | 数据源 |
|---|---|---|
| **Task Success Rate** | 最终结果是否正确 · LLM judge 或人工 | 生产抽样 + golden set |
| **Tool Call Accuracy** | 每步调用 tool 是否合理 · 参数是否对 | trace 数据（见 [LLM Observability](llm-observability.md)）|
| **Step Efficiency** | 平均完成步数 · 比理想多几步 | trace |
| **Cost per Task** | Token + tool 执行总成本 | 计费 / obs |
| **Replan Rate** | 中途 replan 比例高 = planner 差 | trace |

### Agent Benchmark（再引用 · 加生产视角）

| Benchmark | 生产使用价值 | 注意 |
|---|---|---|
| **SWE-bench**（代码修复）| 高 · 接真实 GitHub issue | 自建变种更准 |
| **τ-bench**（客服）| 高 · 对齐真实业务流 | 适合客服 agent |
| **WebArena**（网页操作）| 中 · 测通用网页能力 | 具体业务仍需自建 |
| **AgentBench** | 中 · 通用 sanity check | 不代表自家任务 |
| **GAIA** | 低（SOTA < 40%）· 主要用于研究对标 | 生产用过高估模型 |

### Agent 离线 Eval 模板

```python
# pytest-style · DeepEval
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import TaskCompletionMetric, ToolCorrectnessMetric

test_cases = [
    LLMTestCase(
        input="帮我分析过去一周销售异常",
        expected_tools=["query_sales", "identify_anomaly", "vector_search"],
        expected_output_contains=["异常商品", "原因分析"],
    ),
    # ...
]

evaluate(
    test_cases,
    metrics=[TaskCompletionMetric(threshold=0.8), ToolCorrectnessMetric()],
)
```

### 生产 Agent 在线 Eval

- 用户反馈（👍/👎）作为 ground truth
- **采样人工复核** · 5-10% trace
- **灰度 eval**：新 agent 版本小流量 · 对比旧版 metrics
- 关键任务**每次运行后 LLM judge 一下** · 立即发现退化

## Eval 和 Observability 的分工（重要）

**Agent 评审 #2 点出过**，两事混起来是常见误区：

| | **Observability**（[llm-observability](llm-observability.md)）| **Evaluation**（本页）|
|---|---|---|
| 回答什么 | **发生了什么** · 请求怎么走的 · 哪步慢 · 哪步贵 | **质量怎么样** · 答对没 · 有没有幻觉 |
| 数据 | Trace / Metrics / Logs · 实时生成 | Test cases / Golden set · 预先标注 |
| 用法 | 事故排查 · 监控告警 | 回归测试 · 质量闭环 · A/B |
| 频率 | 持续（每个请求）| 定期（PR / 版本 / 季度）|
| 工具 | Langfuse / Phoenix / OTel | RAGAS / DeepEval / Promptfoo / 自建 |
| 告警 | 技术指标（latency / error / cost）| 质量指标（groundedness / task success）|
| 联动 | **Trace 数据可作为 Eval 输入** · Eval 可反哺 Obs 告警 | |

**组合才是完整**：
- Obs 发现 "latency 涨了" → 查 trace 定位
- Eval 发现 "groundedness 退化了" → 找到哪个 prompt 版本 + 回滚
- Obs trace → 抽样 → 人工标注 → 加入 Golden set → 下次 Eval 覆盖

## 相关

- [RAG](rag.md) · [Agent Patterns](agent-patterns.md) · [Prompt 管理](prompt-management.md) · [LLM Observability](llm-observability.md) · [Guardrails](guardrails.md)
- [检索评估](../retrieval/evaluation.md)（更基础，偏检索层）
- [Rerank](../retrieval/rerank.md)

## 延伸阅读

- **[RAGAS](https://docs.ragas.io/)** · **[TruLens](https://www.trulens.org/)** · **[Promptfoo](https://www.promptfoo.dev/)** · **[DeepEval](https://docs.confident-ai.com/)**
- **[OpenAI Evals](https://github.com/openai/evals)** · **[lm-evaluation-harness (EleutherAI)](https://github.com/EleutherAI/lm-evaluation-harness)**
- **[SWE-bench](https://www.swebench.com/)** · **[τ-bench](https://github.com/sierra-research/tau-bench)** · **[WebArena](https://webarena.dev/)** · **[GAIA](https://huggingface.co/papers/2311.12983)** · **[IFEval](https://github.com/google-research/google-research/tree/master/instruction_following_eval)**
- **[Chatbot Arena / MT-Bench](https://lmsys.org/blog/2023-05-03-arena/)**
- **[RULER · Long-context benchmark](https://github.com/NVIDIA/RULER)** · **[Needle-in-a-Haystack](https://github.com/gkamradt/LLMTest_NeedleInAHaystack)**
- *Evaluating RAG: A Practitioner's Guide*（Pinecone / LlamaIndex 博客系列）
