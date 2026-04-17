---
title: 向量 SQL 语法对照
description: 各引擎向量查询语法 + 距离函数
tags: [cheatsheet, vector, sql]
---

# 向量 SQL 语法对照

## 距离函数对照

| 引擎 | Cosine | L2 | Inner Product |
| --- | --- | --- | --- |
| **pgvector** | `<=>` | `<->` | `<#>`（取反） |
| **LanceDB** | `cosine_distance(a, b)` | `l2_distance(a, b)` | `dot(a, b)` |
| **Milvus** | `COSINE` | `L2` | `IP` |
| **Qdrant** | `Cosine` | `Euclidean` | `Dot` |
| **Weaviate** | `nearVector` + distance | `distance` | — |
| **DuckDB VSS** | `array_cosine_similarity` | `array_distance` | `array_inner_product` |
| **ClickHouse** | `cosineDistance` | `L2Distance` | `dotProduct` |

## pgvector

```sql
CREATE TABLE docs (id BIGINT, embedding VECTOR(1024));
CREATE INDEX ON docs USING hnsw (embedding vector_cosine_ops);

-- 查询
SELECT id, title
FROM docs
WHERE tenant_id = 42
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

## LanceDB（Python）

```python
import lancedb
db = lancedb.connect("s3://warehouse/")
tbl = db.open_table("docs")

results = (
  tbl.search([0.1, 0.2, ...])
     .where("tenant_id = 42 AND kind = 'policy'")
     .limit(10)
     .select(["id", "title"])
     .to_pandas()
)
```

LanceDB SQL（预览）：

```sql
SELECT id, title
FROM docs
WHERE tenant_id = 42
ORDER BY cosine_distance(embedding, ?)
LIMIT 10;
```

## Milvus

```python
from pymilvus import MilvusClient

client.search(
  collection_name="docs",
  data=[[0.1, 0.2, ...]],
  filter='tenant_id == 42 and kind == "policy"',
  output_fields=["id", "title"],
  limit=10,
  anns_field="embedding",
  search_params={"metric_type": "COSINE", "params": {"ef": 128}},
)
```

Milvus Hybrid Search：

```python
from pymilvus import AnnSearchRequest, WeightedRanker

dense_req = AnnSearchRequest(
  data=[dense_vec], anns_field="dense_vec",
  param={"metric_type": "COSINE"}, limit=100,
)
sparse_req = AnnSearchRequest(
  data=[sparse_vec], anns_field="sparse_vec",
  param={"metric_type": "IP"}, limit=100,
)

client.hybrid_search(
  collection_name="docs",
  reqs=[dense_req, sparse_req],
  rerank=WeightedRanker(0.7, 0.3),
  limit=10,
)
```

## Qdrant

```python
client.search(
  collection_name="docs",
  query_vector=[0.1, 0.2, ...],
  query_filter=Filter(must=[
    FieldCondition(key="tenant_id", match=MatchValue(value=42)),
  ]),
  limit=10,
)
```

## Weaviate

```graphql
{
  Get {
    Doc(
      nearVector: {vector: [0.1, 0.2, ...]}
      where: {path: ["tenant_id"], operator: Equal, valueInt: 42}
      limit: 10
    ) { id title _additional { distance } }
  }
}
```

## DuckDB VSS

```sql
INSTALL vss;
LOAD vss;

CREATE TABLE docs (id BIGINT, embedding FLOAT[1024]);
CREATE INDEX idx ON docs USING HNSW (embedding) WITH (metric = 'cosine');

SELECT id, array_cosine_similarity(embedding, ?::FLOAT[1024]) AS sim
FROM docs
WHERE tenant_id = 42
ORDER BY sim DESC
LIMIT 10;
```

## ClickHouse

```sql
CREATE TABLE docs (
  id UInt64,
  embedding Array(Float32),
  INDEX v embedding TYPE annoy('cosineDistance') GRANULARITY 1
) ENGINE = MergeTree ORDER BY id;

SELECT id, cosineDistance(embedding, [0.1, 0.2, ...]) AS d
FROM docs
WHERE tenant_id = 42
ORDER BY d
LIMIT 10;
```

## 通用模式：Hybrid（Dense + Sparse + Rerank）

```
1. 并行两路召回: dense_topN + sparse_topN
2. RRF 或 weighted 融合 → 候选 topK*
3. Cross-encoder rerank → final topK
```

各引擎实现细节不同，但模式一致。

## 归一化惯例

- **入库前**做 L2 归一化（`v / ||v||`）
- 入库后用 **cosine** 距离
- 这样所有引擎的 Inner Product / Cosine 都等价
- 存储 / 内存更一致

## 陷阱

- **维度类型不匹配**（FLOAT[1024] vs DECIMAL[1024]）
- **ORDER BY DESC 忘了改**（cosine 是 distance 越小越近，similarity 越大越近）
- **跨语言客户端 tensor dtype 不一致**（numpy float64 vs float32）
- **索引未建就全扫**（慢得想杀程序）

## 相关

- [向量数据库](../retrieval/vector-database.md)
- [向量数据库对比](../compare/vector-db-comparison.md)
- [Hybrid Search](../retrieval/hybrid-search.md)
- [跨模态查询](../unified/cross-modal-queries.md)
