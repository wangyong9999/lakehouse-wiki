---
title: Benchmark 参考
type: reference
tags: [frontier, benchmark]
status: stable
---

# Benchmark 参考

!!! tip "一句话理解"
    湖仓 / 向量 / LLM 领域常见 benchmark 汇总，帮你快速**定位选型参照系**。但请记住——**自家数据的 benchmark 比外部 benchmark 权威 10 倍**。

## 湖仓 / OLAP

| Benchmark | 测什么 | 主要规模 | 备注 |
| --- | --- | --- | --- |
| **TPC-DS** | 决策支持（多表 join） | 100GB / 1TB / 10TB | OLAP 长期主流 benchmark |
| **TPC-H** | 仓库查询 | 1GB - 10TB | 较早的标准 |
| **SSB**（Star Schema Benchmark） | 星型模式 | 灵活 | 小而美 |
| **ClickBench** | 单表查询 | 100M 行 Hits 数据 | ClickHouse 倡导，单表密集 |
| **tpch-tools** / **duckdb-benchmarks** | 引擎对比 | 多规模 | 常见用于公开对比 |

## 向量检索

| Benchmark | 测什么 | 规模 | 备注 |
| --- | --- | --- | --- |
| **ANN-Benchmarks** | 各 ANN 算法 | 1M - 1B 向量 | 最权威 |
| **Big-ANN-Benchmarks** | 十亿级 | 1B - 10B | 学界 + 工业 |
| **VectorDBBench** (Zilliz) | 向量 DB 端到端 | 千万 - 亿 | 跨系统 benchmark |
| **MTEB Retrieval** | 基于 embedding 的检索 | 多领域 | 评估 embedding 模型 |

## Embedding 模型

| Benchmark | 测什么 | 语种 |
| --- | --- | --- |
| **MTEB**（Massive Text Embedding Benchmark） | 56 个任务 | 多语，英语为主 |
| **C-MTEB** | MTEB 中文版 | 中文 |
| **MMTEB** | 多语言扩展 | 100+ |
| **BEIR** | 检索专项 | 英语 |

## LLM

| Benchmark | 测什么 | 备注 |
| --- | --- | --- |
| **MMLU** | 57 学科常识 | 英语通识 |
| **C-Eval** / **C-MMLU** | 中文通识 | 中文 |
| **GSM8K** | 数学推理 | 难 |
| **HumanEval** / **MBPP** | 代码 | Python |
| **HELM** | 综合框架 | 不是单一 benchmark |
| **LMSys Chatbot Arena** | 人工 ELO | 最贴近真实体验 |

## RAG 评估

| Benchmark / 工具 | 测什么 |
| --- | --- |
| **RAGAS** 内置指标 | Groundedness / Context Relevance / Answer Relevance |
| **BEIR / MTEB Retrieval** | 检索阶段 |
| **MS MARCO** | 问答语料 |
| **Natural Questions** | 问答 |
| **RGB** | RAG 鲁棒性专项 |

## 读 benchmark 的三条原则

1. **看绝对数字无意义** —— 硬件 / 配置 / 数据分布都影响。看**相对顺序**和**差距幅度**
2. **找"测评负载和你负载接近"的 benchmark** —— 你做点查就别看 TPC-DS 的大 shuffle 分数
3. **复现关键几个** —— 自己跑得通，才能排除 cherry-pick

## 自家 benchmark 建议

- **固化 Golden Set**（100-500 条真实 query）
- **每次选型 / 升级都跑一遍**
- 结果入表：
  ```
  benchmark_run_id | engine | config | metric | value | ts
  ```
- 定期 review，识别退化

## 相关

- [检索评估](../retrieval/evaluation.md)
- [RAG 评估](../ai-workloads/rag-evaluation.md)
- [向量数据库对比](../compare/vector-db-comparison.md)
- [Embedding 模型横比](../compare/embedding-models.md)
- [性能调优](../ops/performance-tuning.md)

## 延伸阅读

- <https://ann-benchmarks.com/>
- <https://huggingface.co/spaces/mteb/leaderboard>
- <https://lmarena.ai/>
- <https://benchmark.clickhouse.com/>
