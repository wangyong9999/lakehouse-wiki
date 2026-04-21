---
title: 一月 AI 方向路径
type: learning-path
tags: [learning-path, ai, retrieval]
audience: 完成"一周新人路径"后、想深入 AI / 检索方向的工程师
duration: 1 月
status: stable
---

# 一月 AI 方向路径

!!! tip "目标"
    一个月后能独立**设计一条 RAG / 多模检索流水线**：从湖上原始数据切到 embedding、切到向量索引、切到在线检索 + rerank + LLM；清楚每一步的选型依据与坑位。

## 前置

- 已完成 [一周新人路径](week-1-newcomer.md)
- 能读懂 Iceberg 的元数据结构和一次 commit 的流程
- 会用至少一种向量库跑一次简单的 ANN 检索

## 节奏表

### Week 1 —— Embedding 与向量空间

- [ ] 读 [Embedding](../retrieval/embedding.md)
- [ ] 读 [多模 Embedding](../retrieval/multimodal-embedding.md)
- [ ] 做：用 `sentence-transformers` + CLIP 各跑一组 embedding，比较文 / 图向量的分布与相似度
- [ ] 做：把一组公开 PDF 用 BGE 生成向量，导入 LanceDB / Faiss 做检索
- [ ] 自测：能解释 Matryoshka embedding、L2 归一化、pre-filter vs post-filter

### Week 2 —— ANN 索引与向量库

- [ ] 深度对照 [HNSW](../retrieval/hnsw.md) / [IVF-PQ](../retrieval/ivf-pq.md) / [DiskANN]（ANN 索引对比）
- [ ] 读 [Milvus](../retrieval/milvus.md) 和 [LanceDB](../retrieval/lancedb.md)
- [ ] 读 [向量数据库对比](../compare/vector-db-comparison.md)
- [ ] 做：在同一份数据上跑 Milvus + LanceDB，对比召回率、延迟、存储占用
- [ ] 自测：能在 "10M 向量 + 4GB 内存预算 + 200 QPS" 场景下给出选型与调参方案

### Week 3 —— Hybrid Search + Rerank + RAG

- [ ] 读 [Hybrid Search](../retrieval/hybrid-search.md) 和 [Rerank](../retrieval/rerank.md)
- [ ] 读 [RAG](../ai-workloads/rag.md)
- [ ] 读 [RAG on Lake](../scenarios/rag-on-lake.md)
- [ ] 做：把 Week 1 的语料扩成一个完整 RAG demo —— BM25 + dense 召回 + cross-encoder rerank + LLM 拼 prompt
- [ ] 做：人工标注 50 条 query，度量 Recall@5 / MRR，用两种不同 embedding / rerank 模型对比
- [ ] 自测：能画出 RAG 三阶段（召回 / 精排 / 生成）并说出每一级的瓶颈度量

### Week 4 —— 一体化、Feature Store、多模流水线

- [ ] 读 [Lake + Vector 融合架构](../unified/lake-plus-vector.md)
- [ ] 读 [多模数据建模](../unified/multimodal-data-modeling.md)
- [ ] 读 [统一 Catalog 策略](../catalog/strategy.md)
- [ ] 读 [多模检索流水线](../scenarios/multimodal-search-pipeline.md) 场景
- [ ] 读 [Feature Store](../ml-infra/feature-store.md)
- [ ] 做：设计一张 `multimodal_assets` 表，含三种模态和两种向量列；在 Iceberg / Lance 二选一落地
- [ ] 做：画出一条端到端流水线（入湖 → enrichment → embedding → 索引 → 检索 → rerank → LLM），标注每一步的选型和监控指标
- [ ] 自测：能向团队讲 20 分钟 "我们为什么要把 BI 和 AI 跑在同一个湖上"

## 自测清单

- [ ] 能独立选型：不同规模 / 预算下选哪个 ANN 索引、哪个向量库
- [ ] 能独立设计一张多模湖表 schema
- [ ] 能规划一条完整 RAG 流水线并说出每步的失败兜底
- [ ] 能评估检索质量：知道怎么构造评测集、用什么指标
- [ ] 知道目前社区几个关键争议点：Iceberg Puffin 进展、Lance vs Parquet、Milvus vs LanceDB 适用面

## 进阶

- 读一篇 SIGMOD / VLDB 上的最新向量 / 湖仓论文写 paper note（贡献到 `frontier/`）
- 为团队 wiki 补一页你最有把握的概念 / 系统页
- 向 `adr/` 写一个"在 X 场景下我们选择 Y"的决策记录
