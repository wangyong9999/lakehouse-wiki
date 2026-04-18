---
title: 量级数字总汇 · Benchmark Numbers at a Glance
type: reference
depth: 进阶
tags: [frontier, benchmark, reference]
aliases: [基准数字, Performance Cheat Sheet]
status: stable
---

# 量级数字总汇

!!! tip "一句话定位"
    **团队决策时"心里有数"的数字一览**。不是精确 benchmark，是**量级参考**——让你快速判断"这个目标合理吗 / 那个延迟能做到吗 / 这个规模选哪个方案"。所有数字都注明来源和规模前提。

!!! warning "使用方法"
    - 数字是**量级**（数量级 ~ ±2×），不是精确值
    - **自家业务数据 benchmark 永远最权威**
    - 版本升级、硬件迭代可能让数字 2-5× 变化
    - 每半年刷新一次此页

## 1. 湖仓 / 表格式

### Iceberg

| 指标 | 规模 | 典型值 | 来源 |
|---|---|---|---|
| 提交延迟（单 CAS） | - | 50-500ms | Iceberg 社区 |
| Planning（10M 数据文件） | - | 数百 ms - 几秒 | Netflix 博客 |
| Planning vs Hive LIST | 10k 分区 | Iceberg 快 50-100× | Netflix 迁移数据 |
| 最大单表规模 | - | PB 级 | Netflix / Apple |
| Snapshot 数（健康表） | - | 100-1000 | 社区建议 |
| metadata.json 大小（10k snapshot）| - | 几 MB | 估算 |

### Paimon

| 指标 | 规模 | 典型值 |
|---|---|---|
| CDC 主键表写吞吐 | 单 Flink 作业 | 10k-100k rows/s |
| 流读延迟（commit → 可见）| - | 30s-2min |
| 端到端延迟（CDC → 可查）| 生产 | 1-5 分钟 |
| Compaction 吞吐 | 后台 | 100+ MB/s |

### 对象存储

| 操作 | S3 典型延迟 |
|---|---|
| GET 单 object（小）| 20-50ms |
| PUT 单 object | 30-100ms |
| LIST 1000 objects | 50-200ms |
| Multi-part upload（100MB）| 1-3s |
| 跨 region 复制 | 秒-分钟 |

## 2. 查询引擎

### TPC-DS 100 参考时间（10 node × 64 core hardware）

| 引擎 | 总时间（99 queries） |
|---|---|
| Trino 450 | 15-20 分钟 |
| Spark 3.5 + AQE | 30-40 分钟 |
| StarRocks 3.3 | 8-12 分钟 |
| ClickHouse | 10-15 分钟（单表强）|
| Databricks Photon | 10-15 分钟 |
| DuckDB 单机 | 1 TB 数据 OK、10 TB 吃力 |

### Trino 典型交互查询

| 场景 | p50 | p95 |
|---|---|---|
| 仪表盘（聚合，走 MV） | 200ms | 1s |
| 即席查询（中等 join） | 1-5s | 15s |
| 大规模扫描（TB 级） | 10-60s | 3-5 min |

### Spark 典型 ETL

| 操作 | 吞吐 |
|---|---|
| Parquet 扫描 | 200-500 MB/s / executor |
| Shuffle 写 | 100-200 MB/s / executor |
| Iceberg 写入 | 50-150 MB/s / executor |
| Join（AQE + Broadcast）| 10 亿 × 1 亿: 10-30 分钟 |

### Flink

| 操作 | 规模 | 吞吐 / 延迟 |
|---|---|---|
| Map-only 流 | 单 TM 4 core | 100k+ events/s |
| Stateful KeyBy | 1M keys state | 10-50k events/s / slot |
| Window 聚合 | - | 50k-200k events/s / slot |
| Checkpoint | 10GB state | 30s-2min |
| 端到端延迟（实时大屏）| 秒级 commit | 1-5 秒 |

### DuckDB 单机

| 数据规模 | 性能 |
|---|---|
| < 100 GB | 亚秒-秒级 |
| 100 GB - 1 TB | 5-30s |
| 1 TB Iceberg 扫描 | 5-15 min |
| 分区裁剪后 | 快 10×+ |

## 3. OLAP 加速副本

### StarRocks / Doris

| 场景 | 延迟 |
|---|---|
| 仪表盘（走 MV） | < 500ms |
| 高并发聚合 | p99 < 1s |
| SSB Benchmark | 比 ClickHouse 快 1-2×（Join 场景） |

### ClickHouse

| 场景 | 延迟 |
|---|---|
| 单表聚合 10亿行 | 秒级 |
| 单表 TopN | 极快 |
| 复杂 Join | 明显慢于 StarRocks |
| ClickBench | 常年 top 1-3 |

### Druid / Pinot

| 场景 | 延迟 |
|---|---|
| 实时聚合大屏 | p99 < 200ms |
| Rollup 预聚合查询 | < 100ms |
| 支持的 Schema 变化 | 弱 |

## 4. 向量检索

### HNSW 延迟（典型）

| 数据集 | 规模 | M=16, ef=40 | Recall@10 |
|---|---|---|---|
| SIFT-1M | 1M × 128d | 0.2 ms | 99% |
| DEEP-10M | 10M × 96d | 0.8 ms | 99% |
| DEEP-100M | 100M × 96d | 3-8 ms | 98% |
| 1B 向量 | - | ⚠️ 需 DiskANN | - |

### 内存估算

| 规模 × 维度 | 内存（HNSW M=32）|
|---|---|
| 1M × 768 float32 | 3 GB |
| 10M × 768 | 30 GB |
| 100M × 768 | 300 GB（需分布式或量化） |

### 向量库典型 QPS（单节点）

| 系统 | QPS |
|---|---|
| Milvus HNSW | 5k-20k |
| LanceDB 嵌入式 | 10k+ |
| pgvector | 1k-5k |
| Qdrant | 5k-15k |

## 5. Embedding / RAG

### Embedding 模型吞吐（A100）

| 模型 | 参数 | 吞吐 |
|---|---|---|
| BGE-small | 33M | 20k tokens/s |
| BGE-base | 110M | 10k tokens/s |
| BGE-large | 335M | 3k tokens/s |
| OpenAI text-embedding-3（API）| - | 延迟 100-300ms / request |

### Rerank 延迟（A100）

| 模型 | 10 候选 | 50 候选 | 100 候选 |
|---|---|---|---|
| bge-reranker-base | 10ms | 40ms | 80ms |
| bge-reranker-large | 30ms | 80ms | 150ms |
| Cohere Rerank 3 (API) | 100ms | 200ms | 300ms |

### LLM 推理（H100 单卡）

| 模型 | 吞吐（tokens/s）|
|---|---|
| Llama-3-8B | 5000-8000 |
| Llama-3-70B (fp16) | 200-300 |
| Llama-3-70B (AWQ int4) | 500-800 |
| Llama-3-70B (fp8) | 700-1000 |
| Mixtral-8x7B (MoE) | 800-1500（激活少） |

### RAG 延迟分解（典型）

```
Query embed:       50ms
Hybrid retrieve:  150ms
Rerank:           100ms
Prompt + first token: 400ms
Stream to finish: 1000ms
──────
Total p95:        1.5-2s
```

## 6. 检索评估指标（BEIR）

| 管线 | Recall@10 | NDCG@10 |
|---|---|---|
| BM25 | 0.50 | 0.43 |
| Dense (BGE-large) | 0.55 | 0.47 |
| Hybrid (RRF) | 0.62 | 0.53 |
| Hybrid + bge-reranker | 0.70 | 0.60 |
| Hybrid + Contextual + Rerank | 0.75+ | 0.67+ |

## 7. MLOps / 训练

### XGBoost 训练基线

| 样本数 × 特征 | 硬件 | 时间 |
|---|---|---|
| 100k × 100 | CPU | < 1 min |
| 1M × 100 | CPU | 3-10 min |
| 10M × 100 | GPU | 30-60 min |
| 100M × 1000 | 多 GPU | 2-4 hr |

### LLM 微调（LoRA）

| 模型 | 数据规模 | GPU × 时间 |
|---|---|---|
| Llama-8B | 10k samples | 1 × A100 × 2hr |
| Llama-70B | 10k samples | 8 × A100 × 12hr |
| Qwen-72B | 100k samples | 16 × H100 × 48hr |

### 训练数据吞吐

| 操作 | 典型 |
|---|---|
| Parquet → DataLoader | 100-500 MB/s |
| PIT Join（Spark）| 100M 样本 × 20 FV ≈ 30 分钟 |
| Feast Materialization | 10k-100k rows/s |

## 8. Feature Store

| 操作 | 基线 |
|---|---|
| 单 entity get_online | 2-10ms |
| 100 entity batch get | 20-50ms |
| PIT Join（Spark 100M）| 30 分钟 |
| Materialize 吞吐 | 10k-100k rows/s |
| Online KV QPS | 10k+ 起步 |

## 9. Kafka / 消息

| 操作 | 典型 |
|---|---|
| 单 broker 吞吐 | 100 MB/s（写）· 150 MB/s（读）|
| 生产者 latency | 2-10ms |
| 消费 lag（健康）| < 秒 |
| 单主题 partition 数 | 几百 OK · 上万需谨慎 |

## 10. 成本参考（月）

| 规模 | 典型月成本 |
|---|---|
| Snowflake 50 TB | $10k-30k |
| BigQuery 50 TB | $5k-20k |
| 自建 Trino + Iceberg 50 TB | $3k + 1 工程师 |
| Databricks 500 TB | $50k-200k |
| 自建 PB 级 Lakehouse | $150k-500k + 10 人团队 |

## 11. 注意与免责

- 数字**量级参考**不等于精确基准
- 环境因素：云 vs 本地、SSD vs HDD、网络、压缩率
- **版本差异**：Trino / Spark / Milvus 每半年性能进化
- **硬件换代**：H100 比 A100 2-3×；B200 又 2×

**最终建议**：自家**复现关键 benchmark**是唯一可靠的办法。

---

## 相关

- [Benchmark 参考](benchmarks.md) —— Benchmark 体系介绍
- [LLM 推理优化](llm-inference-opt.md)
- [向量检索前沿](vector-trends.md)
- [TCO 模型](../ops/tco-model.md)
- [业务场景全景](../scenarios/business-scenarios.md)

## 延伸阅读

- [ClickBench](https://benchmark.clickhouse.com/) 单表聚合 live
- [ANN-Benchmarks](https://ann-benchmarks.com/) 向量检索 live
- [VectorDBBench](https://github.com/zilliztech/VectorDBBench) 向量库
- [MLPerf](https://mlcommons.org/benchmarks/) LLM / ML
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) Embedding
