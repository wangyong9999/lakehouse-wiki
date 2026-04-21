---
title: 多模数据建模 · 表 Schema 设计
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: Iceberg 1.10+ · Paimon 1.4+ · Lance 0.20+ · 2024-2026 实践
tags: [unified, multimodal, modeling, schema, cross-chapter]
aliases: [多模建表, 多模 Schema 设计, Multimodal Data Modeling]
related: [multimodal-embedding, lake-plus-vector, lake-table, schema-evolution, multi-modal-lake]
systems: [iceberg, lance, paimon]
status: stable
---

!!! info "本页是跨章组合视角 · schema 设计焦点"
    本页讲"**一张湖表同时承载 BI 和 AI 数据**的 schema 设计"· 涉及机制深挖去：
    
    - **湖表底层机制** → [lakehouse/lake-table](../lakehouse/lake-table.md) · [lakehouse/multi-modal-lake](../lakehouse/multi-modal-lake.md)
    - **Schema Evolution** → [lakehouse/schema-evolution](../lakehouse/schema-evolution.md)
    - **Embedding 模型选型** → [retrieval/embedding](../retrieval/embedding.md) · [retrieval/multimodal-embedding](../retrieval/multimodal-embedding.md)
    - **Embedding 生成流水线** → [ml-infra/embedding-pipelines](../ml-infra/embedding-pipelines.md)
    
    **本页专做**：多模表 schema 的**跨 BI + AI 设计**。

# 多模数据建模

!!! tip "一句话理解"
    一张湖表，同时承载**结构化字段 + 非结构化资产（或其指针）+ 多种向量列 + 元数据**。三条原则：**二进制不直接进表、向量列按用途分列、元数据是一等公民**。

## 为什么单独讨论

"把一张图存进表里"听起来简单，实际坑非常多：

- 大二进制放行里 → 列剪裁失效 / 扫描爆内存
- 一张表只存一种向量 → 换模型就得复制全表
- 没有统一元数据 schema → 过滤语义没法跨表复用

一个好的多模表设计决定了未来检索、训练、治理全部的顺畅度。

## 推荐表结构模板

![multimodal_assets 表的 7 类字段分组](../assets/diagrams/multimodal-schema.svg#only-light){ loading=lazy }
![multimodal_assets 表的 7 类字段分组](../assets/diagrams/multimodal-schema.dark.svg#only-dark){ loading=lazy }

```sql
CREATE TABLE multimodal_assets (
  -- 标识
  asset_id        BIGINT   NOT NULL,
  asset_version   INT      NOT NULL DEFAULT 1,

  -- 模态标签
  kind            STRING   NOT NULL,            -- image / video / audio / text / doc
  modality_tags   ARRAY<STRING>,                -- 'ocr-able', 'face-present', ...

  -- 资产指针（二进制不进表）
  raw_uri         STRING   NOT NULL,            -- s3://.../xxx.jpg
  raw_size_bytes  BIGINT,
  raw_sha256      STRING,
  thumb_uri       STRING,                       -- 缩略图 / 代表帧

  -- 可检索的文字侧
  caption         STRING,                       -- 人写 / 模型生成
  ocr_text        STRING,
  transcript      STRING,                       -- 语音转写

  -- 向量列（按用途 / 模型拆）
  clip_vec        VECTOR<FLOAT, 512>,           -- 多模通用检索
  text_vec        VECTOR<FLOAT, 1024>,          -- 长文精细检索
  audio_vec       VECTOR<FLOAT, 512>,           -- 音频检索（仅音频 / 视频有）

  -- 业务 & 治理
  owner           STRING,
  visibility      STRING,                       -- public / internal / restricted
  source          STRING,                       -- 来源系统 / 采集 pipeline
  tags            ARRAY<STRING>,
  ts              TIMESTAMP,
  partition_date  DATE

) USING iceberg
PARTITIONED BY (kind, partition_date, bucket(16, asset_id))
TBLPROPERTIES (
  'write.parquet.compression-codec' = 'zstd',
  'write.distribution-mode'         = 'hash',
  'history.expire.max-snapshot-age-ms' = '2592000000'  -- 30 天
);
```

## 三条原则，拆开来看

### 1. 二进制不直接进表

原始图 / 视频 / 音频放**对象存储**，表里只保留 `raw_uri + sha256 + size`。理由：

- Parquet 列剪裁只对标量列最高效
- 大二进制让 Row Group 扫描极不可控
- 统一对象存储更适合分层存储、CDN、权限系统

### 2. 向量列按用途 / 模型分列

不要"一列存所有向量"。常见分法：

- **多模通用**（CLIP / SigLIP）—— 跨模态检索
- **文本精细**（BGE / E5 / Jina）—— 长文场景、高召回
- **稀疏向量**（SPLADE）—— [Hybrid Search](../retrieval/hybrid-search.md)
- **领域专用**（人脸 embedding / 指纹 embedding 等）

好处：换模型只重建一列；不同列可独立建索引、独立 rerank。

### 3. 元数据是一等公民

`visibility`、`owner`、`source`、`modality_tags` 等都是**下游过滤 + 权限的锚点**。多模检索几乎都要带 `WHERE visibility = 'internal' AND kind = 'doc'` 这种条件，这些字段必须可索引（min/max + bloom filter）。

## 分区策略

多模表通常**按 `kind` + 时间**分区；在 Iceberg 里配合 `bucket(N, asset_id)` 做 hash 子分区来稳定并行度。

为什么按 `kind`？

- 不同模态的写入频率差异大（日志级文本 vs 每日上传图片）
- 向量索引按模态构建，物理隔离更利于后续 compaction / reindex
- 绝大多数查询都**只查一种模态**

## 演化场景

### 新增一种模态

加列：`modality_tags` 里加一个 tag，新增资产写入即可。历史数据不需要动。

### 换 embedding 模型

增加一列新向量，老列保留一段时间做 A/B。**不要覆盖老列**，以免新模型效果不如旧模型时回不去。

### 新增一个治理字段

加列 + 批作业回填 + 重建索引（通常只影响 bloom filter）。Schema Evolution 原生支持。

## 相关

- [Lake + Vector 融合架构](lake-plus-vector.md)
- [多模 Embedding](../retrieval/multimodal-embedding.md)
- [Schema Evolution](../lakehouse/schema-evolution.md)

## 延伸阅读

- *Designing Data-Intensive Applications* (Kleppmann) —— 建模基础
- LanceDB 的多模表 tutorial
- Databricks MosaicML 公开的多模数据 blueprint
