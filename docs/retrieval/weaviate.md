---
title: Weaviate
type: system
tags: [retrieval, vector, modules]
category: vector-db
repo: https://github.com/weaviate/weaviate
license: BSD-3-Clause
status: stable
---

# Weaviate

!!! tip "一句话定位"
    **自带向量化 / Reranker / 多模 Module 的向量数据库**。开箱即用，schema 偏 OOP（Class / Property），对"懒得自己搭完整 ML 流水线"的团队最友好。

## 它解决什么

大多数向量库只管"存 + 查"；embedding 生成、rerank、summarizer 都得自己搞。Weaviate 把这些做成**Module** 内置：

- `text2vec-openai` / `text2vec-huggingface` / `text2vec-cohere` 等——**直接把文本丢进去自动向量化**
- `reranker-cohere` / `reranker-voyage` —— 内置 rerank
- `generative-openai` —— 检索到的直接喂 LLM
- `qna-*` —— 问答 module

对 RAG 原型和初创公司特别省事。

## 架构

- 单机 / 集群两种部署
- 存储：自研 LSM-tree 风格的 shard
- 索引：HNSW（默认），FLAT 备选
- 对外：REST + GraphQL + gRPC

## Schema

```python
client.schema.create_class({
  "class": "Document",
  "properties": [
    {"name": "title", "dataType": ["text"]},
    {"name": "body",  "dataType": ["text"]},
    {"name": "tags",  "dataType": ["text[]"]},
  ],
  "vectorizer": "text2vec-openai",      # 自动向量化 body
  "moduleConfig": {
    "text2vec-openai": {"model": "text-embedding-3-small"}
  }
})
```

创建完 class，直接 insert 数据，Weaviate 自动调 OpenAI 算 embedding 并存下来。查询：

```python
client.query.get("Document", ["title"]).with_near_text({
  "concepts": ["秋冬穿搭"]
}).with_limit(10).do()
```

## 关键能力

- **Module 系统** —— 向量化、rerank、generative 插件化
- **Hybrid Search** —— BM25 + vector 原生
- **Multi-Tenancy** —— 每个租户独立 shard
- **GraphQL API** —— 复杂嵌套过滤更易表达
- **Replication + Sharding** —— 分布式
- **Auto Schema**（开发态）—— 不用先建 schema

## 和同类对比

- **对比 Milvus** —— Milvus 更分布式、大规模；Weaviate 更开箱即用
- **对比 Qdrant** —— Qdrant filter 更强 + Rust 性能；Weaviate module 生态更全
- **对比 LanceDB** —— LanceDB 湖原生；Weaviate 独立服务生态

详见 [向量数据库对比](../compare/vector-db-comparison.md)。

## 什么时候选

- 想快速搭 RAG 原型，不想自己搭 embedding + rerank
- schema 清晰的业务对象数据（非湖上宽事实表）
- 规模中等（< 亿级）
- GraphQL 的查询表达方式对你有吸引力

## 什么时候不选

- 湖仓一体化（选 LanceDB / Iceberg + Puffin）
- 超大规模（选 Milvus）
- 强过滤语义（选 Qdrant）

## 陷阱

- **Module 依赖外部 API**：`text2vec-openai` 走 OpenAI → 数据外流 + 成本
- **Auto Schema**生产别用：不受控的列会膨胀
- **HNSW 内存**：和其他 HNSW 向量库同样要注意规模

## 相关

- [向量数据库](vector-database.md)
- [向量数据库对比](../compare/vector-db-comparison.md)
- [Hybrid Search](hybrid-search.md)
- [Rerank](rerank.md)

## 延伸阅读

- Weaviate docs: <https://weaviate.io/developers/weaviate>
- *Weaviate Modules* 文档章节
