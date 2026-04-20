---
title: Embedding 流水线
type: concept
tags: [ai, embedding, pipeline]
aliases: [Embedding Pipeline, 向量化流水线]
related: [embedding, multimodal-embedding, rag, feature-store]
systems: [spark, flink, ray]
status: stable
---

# Embedding 流水线

!!! tip "一句话理解"
    持续把湖上新增 / 变更的语料转成向量、写回湖表 + 向量库 / 索引的工程链路。**批与流并行、模型可升级、故障可恢复**是三件最难的事。

## 流水线两种形态

### 批式（最常见）

```mermaid
flowchart LR
  src[(Iceberg/Paimon: 原始语料)] --> chunk[Chunk & Clean]
  chunk --> embed[批 Embedding<br/>Spark + GPU]
  embed --> vec[(Iceberg/Lance: 向量表)]
  vec --> idx[索引构建]
  idx --> online[(向量库 / Puffin)]
```

- 周期（小时/日）触发
- Spark + Ray on Spark / GPU Executor 批量 embedding
- 产出写回湖（带 `embedding_model_version`）

### 流式（CDC 场景）

```mermaid
flowchart LR
  paimon[(Paimon: Primary Key 表)] -->|Changelog| flink[Flink CDC 流]
  flink --> embed_service[Embedding Service<br/>gRPC]
  embed_service --> sink[向量库 / Paimon 向量表]
```

- 逐条或小批（秒–分钟粒度）embedding
- 用现成 Embedding Service（避免在 Flink 内部加载大模型）

## 四个必答工程问题

### 1. 增量 vs 全量

每次 run 的输入是什么？

- **全量重跑**：简单但贵
- **snapshot diff**（推荐）：用 Iceberg `snapshot-id` 对比或 Paimon changelog，只跑新增 / 变更的行
- **基于 watermark**：按 `updated_ts` 范围拉

### 2. 模型版本管理

换模型 = 必须重新 embedding 所有历史。流程：

1. 新版模型上线，先在表里**加一列** `embedding_v2`
2. 批作业回填历史行（可能数天）
3. 双索引期，双读比对
4. 切流量到新向量列，旧列保留 N 天后删除

**永远不要覆盖旧向量列**。

### 3. 失败恢复

百万级 embedding 跑一半挂了怎么办？

- **checkpoint 每批 offset**：Spark 用 `partition + batch_id`；Flink 用 source offset
- **写入幂等**：按 `(asset_id, embedding_model_version)` upsert，重跑不重复
- **至少一次 + 去重** > **恰好一次**：大多数场景可接受

### 4. GPU 资源调度

Embedding 是 GPU-bound。两条路：

- **Executor 内嵌 GPU**（Spark RAPIDS / Ray）—— 调度简单，资源绑死
- **远程 Embedding Service**（Ray Serve / TorchServe / Triton）—— Worker 只做分发，GPU 池化

百万级以下前者简单，亿级以上后者更灵活。

## 典型日吞吐参考

| 模型 | 硬件 | 吞吐（近似） |
| --- | --- | --- |
| BGE-base（文本 768 维） | A10 GPU | 50k–100k docs/min |
| CLIP-ViT-B/32（图） | A10 GPU | 5k–10k images/min |
| OpenAI text-embed-3（API） | — | 受 TPM / RPM 限制，≈ 30k/min |

批 size + 序列长度差异大，实际以 benchmark 为准。

## 一张生产级表长什么样

```sql
CREATE TABLE doc_embeddings (
  asset_id           BIGINT,
  chunk_id           INT,
  content            STRING,
  embedding_bge      VECTOR<FLOAT, 1024>,
  embedding_clip     VECTOR<FLOAT, 512>,
  embedding_version_bge  STRING,              -- 'bge-v2-m3-2026-02'
  embedding_version_clip STRING,              -- 'siglip-so400m-2026-01'
  source_snapshot_id BIGINT,                   -- 来自原始 Iceberg 快照
  embedded_at        TIMESTAMP,
  lang               STRING,
  tenant_id          STRING
) USING iceberg
PARTITIONED BY (tenant_id, bucket(32, asset_id));
```

字段设计到位，后面的回填、迁移、监控都从这张表读出答案。

## 监控指标

- **新鲜度**：`max(source_snapshot_id)` vs 原始表 `current-snapshot-id` 的差距
- **吞吐**：docs/min
- **失败率**：模型调用失败 / 超时
- **成本**：GPU·h / 1M docs
- **分布健康度**：定期抽样看向量 L2 norm / 均值，异常漂移告警

## 相关

- [Embedding](../retrieval/embedding.md)
- [多模 Embedding](../retrieval/multimodal-embedding.md)
- [Feature Store](feature-store.md) —— 思想相近
- 场景：[多模检索流水线](../scenarios/multimodal-search-pipeline.md)

## 延伸阅读

- *Embedding Pipelines at Scale* —— LanceDB / Databricks 系列博客
- Ray Data + embedding 官方教程
