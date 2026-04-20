---
title: Weaviate · 自带 Module 生态的向量库
type: system
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: Weaviate 1.23+（2024-2026 主流）· OSS + Weaviate Cloud
tags: [retrieval, vector, modules, rag]
category: vector-db
repo: https://github.com/weaviate/weaviate
license: BSD-3-Clause
status: stable
---

# Weaviate · 自带 Module 生态的向量库

!!! tip "一句话定位"
    **自带向量化 / Reranker / 多模 Module 的向量数据库**。**开箱即用**——schema 偏 OOP（Class / Property）· 对"懒得自己搭完整 ML 流水线"的团队最友好。**RAG 原型 / 小型创业公司**的快速路径。

!!! abstract "TL;DR"
    - **甜区**：RAG 原型 · schema 清晰的业务对象数据 · 中等规模（< 亿级）
    - **差异化 Module 生态**：text2vec / multi2vec / reranker / generative / qna · 插件式集成 Embedding 服务
    - **外部依赖风险**：Module 调第三方 API（OpenAI / Cohere / HuggingFace）· 数据外流 + 成本
    - **企业级替代**：自建 module（local embedding）或社区 module 避免供应商锁定
    - **2024-2026 生态**：Vectorizer 加 `text2vec-transformers` 自托管 · Reranker 选项更多

## 1. 它解决什么

大多数向量库只管"**存 + 查**"· embedding 生成 · rerank · summarizer 都得自己搞。Weaviate 把这些做成**Module** 内置：

| Module 类别 | 代表 | 用途 |
|---|---|---|
| **text2vec-*** | text2vec-openai / text2vec-cohere / text2vec-huggingface / text2vec-transformers | **直接把文本丢进去自动向量化** |
| **multi2vec-*** | multi2vec-clip | 多模向量化（图 + 文） |
| **reranker-*** | reranker-cohere / reranker-voyage / reranker-transformers | 内置 rerank |
| **generative-*** | generative-openai / generative-cohere / generative-anthropic | 检索到的直接喂 LLM（RAG 一体）|
| **qna-*** | qna-openai / qna-transformers | 问答 module |

**对 RAG 原型和初创公司特别省事**。

## 2. 架构

- **部署**：单机 / 集群（sharded · replicated）
- **存储**：自研 LSM-tree 风格的 shard
- **索引**：HNSW（默认）· FLAT 备选
- **对外**：REST + GraphQL + gRPC
- **Auth**：OIDC / API Key · RBAC

## 3. Schema（偏 OOP）

```python
client.schema.create_class({
  "class": "Document",
  "properties": [
    {"name": "title", "dataType": ["text"]},
    {"name": "body",  "dataType": ["text"]},
    {"name": "tags",  "dataType": ["text[]"]},
    {"name": "pub_date", "dataType": ["date"]},
  ],
  "vectorizer": "text2vec-openai",
  "moduleConfig": {
    "text2vec-openai": {"model": "text-embedding-3-small"}
  }
})
```

创建完 class · 直接 insert 数据 · Weaviate **自动调 OpenAI** 算 embedding 并存下来。查询：

```python
# 语义检索
client.query.get("Document", ["title"]).with_near_text({
  "concepts": ["秋冬穿搭"]
}).with_limit(10).do()

# Hybrid Search
client.query.get("Document", ["title"]).with_hybrid(
  query="秋冬穿搭", alpha=0.5  # 0=pure BM25, 1=pure vector
).with_limit(10).do()
```

**复杂多模 schema** 示例：

```python
# 图 + 文混合 schema
client.schema.create_class({
  "class": "Product",
  "properties": [
    {"name": "title", "dataType": ["text"]},
    {"name": "image", "dataType": ["blob"]},
    {"name": "price", "dataType": ["number"]},
    {"name": "tags", "dataType": ["text[]"]},
  ],
  "vectorizer": "multi2vec-clip",  # 图+文同空间
})
```

## 4. 关键能力

### Module 系统 · 核心差异化

- 向量化 / rerank / generative 插件化
- **一条写入自动完成多阶段**（embedding + 存储）
- **一条查询自动完成 RAG**（检索 + rerank + LLM 生成）

### Hybrid Search 原生

- **BM25** + **vector** 双路召回
- `alpha` 参数控制融合比例
- 详见 [Hybrid Search](hybrid-search.md)

### Multi-Tenancy · 每租户独立 shard

- `multiTenancyConfig: { enabled: true }` 开启
- 每租户物理独立 shard · 数据隔离强

### GraphQL API · 复杂查询友好

```graphql
{
  Get {
    Document(
      nearText: { concepts: ["AI 治理"] }
      where: {
        operator: And
        operands: [
          { path: ["pub_date"], operator: GreaterThan, valueDate: "2024-01-01" }
          { path: ["tags"], operator: ContainsAny, valueText: ["policy"] }
        ]
      }
      limit: 10
    ) {
      title
      _additional { certainty }
    }
  }
}
```

**对比 SQL**：GraphQL 嵌套过滤更直观；但团队熟悉 SQL 的走 Qdrant / Milvus 的 filter expression 也 OK。

## 5. 生产实践要点

### Module 外部依赖 · 数据外流风险

**陷阱**：`text2vec-openai` 会把原始文本发 OpenAI API：

- **数据合规** · 敏感数据不能外流 → 自建 `text2vec-transformers` 用本地 GPU 模型
- **成本** · 大规模数据调 API 账单大 → 本地部署 OSS embedding 模型
- **延迟** · API 延迟 50-200ms → 本地部署延迟 10-50ms

**本地 Module 替代方案**：

| 外部依赖 Module | 本地替代 |
|---|---|
| text2vec-openai | **text2vec-transformers**（HF 模型本地部署）|
| reranker-cohere | **reranker-transformers**（BGE-reranker / Jina-reranker 本地）|
| generative-openai | 走自建 LLM Gateway · 不走 Weaviate module |

### 大规模扩展

- **单机上限**：亿级 · 但推理负载（通过 module）会打满 CPU/GPU
- **集群 sharding**：数据量大时按字段 hash 分片
- **副本策略**：读副本提升 QPS

### Auto Schema · 生产慎用

- **开发态** 友好（不用先建 schema · 自动推导）
- **生产态** 灾难——不受控的列会膨胀 · 类型不一致 · 查询慢

## 6. 什么时候选 / 不选

**选 Weaviate**：

- **快速搭 RAG 原型** · 不想自己搭 embedding + rerank 流水线
- **schema 清晰的业务对象**（非湖上宽事实表）
- **规模中等**（< 亿级）
- **GraphQL 查询表达**对团队有吸引力
- **愿意接受 Module 生态 + 外部 API 集成**

**不选 Weaviate**：

- 湖仓一体化 → [LanceDB](lancedb.md) / Iceberg + Puffin
- 超大规模 → [Milvus](milvus.md)
- 强过滤语义 → [Qdrant](qdrant.md)
- 数据合规严 + 本地模型部署成本高
- 已有独立 embedding pipeline · Module 用不上

## 7. 陷阱

- **Module 依赖外部 API** · 数据外流 + 账单失控 · **生产必做本地 Module 评估**
- **Auto Schema 开发态用 · 生产别用** · 列膨胀灾难
- **HNSW 内存** · 和其他 HNSW 向量库同样 · 规模大时要预算
- **供应商锁定风险** · 深度依赖 Weaviate module 生态 · 迁出成本高
- **GraphQL 学习曲线** · 团队不熟 GraphQL · SQL 栈可能更高效
- **集群多租户 shard 数过多** · 百万级 shard 元数据压力大

## 8. 相关

- [向量数据库](vector-database.md) · 通用定位
- [Hybrid Search](hybrid-search.md) · Weaviate 原生支持
- [Rerank](rerank.md) · Weaviate reranker module
- [向量数据库对比](../compare/vector-db-comparison.md) · 详细横比
- [ai-workloads/RAG](../ai-workloads/rag.md) · Weaviate 的典型应用

## 9. 延伸阅读

- **[Weaviate docs](https://weaviate.io/developers/weaviate)**
- **[Modules 文档](https://weaviate.io/developers/weaviate/configuration/modules)**
- **[Weaviate Cloud](https://weaviate.io/pricing)** · 商业托管
