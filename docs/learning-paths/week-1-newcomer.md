---
title: 一周新人路径
type: learning-path
tags: [learning-path, onboarding]
audience: 刚入组的工程师
duration: 1 周
status: stable
---

# 一周新人路径

!!! tip "目标"
    一周后能回答：**"湖表和数据库存储引擎的根本差异是什么？向量数据库解决什么问题？我们团队为什么把 BI 和 AI 跑在同一个湖上？"**，并能在本地跑通一张 Iceberg 表 + 一次向量检索。

## 目标读者 & 前置

- **目标读者**：刚入组的软件工程师，熟悉 SQL 与一门系统级语言（Go/Rust/Java/C++ 任一）
- **前置**：懂基本的分布式概念（副本、一致性）、看过 Parquet 字样但不必精通

## 节奏表

### Day 1 —— 基础地基

- [ ] 读 [对象存储](../foundations/object-storage.md)
- [ ] 读 [Parquet](../foundations/parquet.md)
- [ ] 做：用 DuckDB 打开任意 Parquet 文件，`SELECT * FROM read_parquet('f.parquet') LIMIT 10;`
- [ ] 自测：能说出对象存储的三条关键约束，以及它们如何影响湖表设计

### Day 2 —— 湖表是什么

- [ ] 读 [湖表](../lakehouse/lake-table.md)
- [ ] 读 [Snapshot](../lakehouse/snapshot.md)
- [ ] 读 [DB 存储引擎 vs 湖表](../compare/db-engine-vs-lake-table.md)
- [ ] 做：用 pyiceberg（或 Spark）本地建一张 Iceberg 表，写入 100 行，看 `metadata/` 下生成了什么
- [ ] 自测：能画出"metadata.json → manifest list → manifest → data files"四层结构

### Day 3 —— 一个真实系统

- [ ] 读 [Apache Iceberg](../lakehouse/iceberg.md)
- [ ] 读 [Nessie](../catalog/nessie.md)
- [ ] 做：在本地用 docker 起一个 Nessie，用 Spark 连上建表、提交一次 commit、回退一次
- [ ] 自测：能说出为什么 Iceberg 需要一个 Catalog、Catalog 做什么

### Day 4 —— 向量侧入门

- [ ] 读 [向量数据库](../retrieval/vector-database.md)
- [ ] 读 [HNSW](../retrieval/hnsw.md)
- [ ] 做：用 Faiss 或 LanceDB 在本地跑一次 ANN 检索（任意 10 万向量）
- [ ] 自测：能说出 HNSW 的 `M` / `ef` 参数分别控制什么，以及它们的内存 / 延迟 / 召回 trade-off

### Day 5 —— Hybrid 与 AI 负载

- [ ] 读 [Hybrid Search](../retrieval/hybrid-search.md)
- [ ] 读 [RAG](../ai-workloads/rag.md)
- [ ] 读 [RAG on Lake](../scenarios/rag-on-lake.md)
- [ ] 做：把 Day 4 的向量检索拼成一个简易 RAG（检索 → 塞 prompt → 调任意 LLM）
- [ ] 自测：能解释我们团队为什么把语料、embedding、索引都放在湖上，而不是各自独立系统

## 自测清单（读完后）

- [ ] 能向同事解释 DB 存储引擎和湖表的根本差异
- [ ] 能画出 Iceberg 的元数据结构
- [ ] 能说出至少三种 ANN 索引及其取舍
- [ ] 能列出 RAG 流水线的主要环节和常见陷阱
- [ ] 知道出问题时去查哪几处资料（上游 spec、官方博客、本手册）

## 进阶

- 想做 AI 方向 → 一月 AI 路径（待补）
- 想做 BI 方向 → 一月 BI 路径（待补）
- 想做引擎 → 读 Iceberg / Paimon 源码，从 `core/io` 层看起
