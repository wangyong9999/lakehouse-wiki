---
title: 60 分钟 RAG on Iceberg
type: tutorial
level: A
depth: 进阶
applies_to: pyiceberg 0.9+ · LanceDB 0.8+ · BGE / FlagEmbedding 1.2+（2026-Q2）
last_reviewed: 2026-04-18
tags: [tutorial, rag, iceberg, lancedb, llm]
related: [rag, rag-on-lake, iceberg, embedding]
status: stable
---

# 60 分钟 RAG on Iceberg

!!! tip "你会做完"
    - 把一个**内部文档库**（若干 Markdown / PDF）**处理成 Iceberg chunks 表**
    - 用 CLIP / BGE 生成 embedding，落到 **LanceDB** 向量库
    - 跑一条完整 **RAG 问答链路**：检索 → rerank → 生成答案 + 引用
    - 全过程 **60 分钟**，纯本地，不需要集群 / GPU（CPU 可接受）
    - 最后跑得动之后，你知道**每一步做错会怎么样**

!!! abstract "TL;DR"
    - 数据：公开 Markdown 文档（本手册源码就行）
    - 事实源：`doc_chunks` Iceberg 表
    - 向量库：LanceDB
    - embedding：BGE-small（CPU 快）
    - LLM：OpenAI API 或本地 Ollama（二选一）
    - 全 Python，自己打得通

## 前置

- Python 3.10+
- 约 4GB 空闲内存
- 任一 LLM 访问：OpenAI API key **或** 本地 Ollama（装过 `llama3:8b` 或类似）

## Step 1 · 环境

```bash
mkdir rag-lab && cd rag-lab
python3 -m venv .venv && source .venv/bin/activate

pip install "pyiceberg[duckdb,sql-sqlite]" \
            "lancedb>=0.5" \
            "sentence-transformers" \
            "rank-bm25" \
            "openai" \
            "python-frontmatter" \
            "markdown"
```

## Step 2 · 准备文档语料

两条路线选一：

**路线 A（最快）**：本手册自己当语料。
```bash
git clone https://github.com/wangyong9999/lakehouse-wiki.git docs-source
```

**路线 B**：用你自己的任意 Markdown 目录（FAQ、onboarding docs 等）。

本教程假设 `./docs-source/docs/` 下有大量 `.md` 文件。

## Step 3 · 解析 + chunking

```python
# 1_chunk.py
import frontmatter, re, hashlib, pathlib
from typing import Iterator

DOCS_ROOT = pathlib.Path("docs-source/docs")

def chunk_markdown(text: str, max_chars: int = 1500, overlap: int = 150) -> Iterator[str]:
    """按 H2 分章，长章再按字符切，保留 overlap。"""
    sections = re.split(r'(?m)^## ', text)
    for sec in sections:
        if not sec.strip(): continue
        # 长 section 切块
        if len(sec) <= max_chars:
            yield sec.strip()
        else:
            for i in range(0, len(sec), max_chars - overlap):
                yield sec[i:i + max_chars].strip()

rows = []
for path in DOCS_ROOT.rglob("*.md"):
    if path.name.startswith('_') or path.name in ('404.md',): continue
    raw = path.read_text()
    post = frontmatter.loads(raw)
    body = post.content
    title = post.metadata.get('title', path.stem)
    for idx, chunk in enumerate(chunk_markdown(body)):
        rows.append({
            'chunk_id': hashlib.sha1(f"{path}:{idx}".encode()).hexdigest()[:16],
            'doc_path': str(path.relative_to(DOCS_ROOT)),
            'doc_title': title,
            'chunk_idx': idx,
            'content': chunk,
            'token_count': len(chunk.split()),
        })

import json
pathlib.Path('chunks.jsonl').write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows))
print(f"Produced {len(rows)} chunks from {DOCS_ROOT}")
```

```bash
python 1_chunk.py
```

**预期**：`Produced ~600 chunks from docs-source/docs`（视手册页数）。

## Step 4 · 写到 Iceberg 表

```python
# 2_write_iceberg.py
import json, datetime as dt
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, IntegerType, TimestampType
import pyarrow as pa

catalog = SqlCatalog("lab",
    uri="sqlite:///rag_catalog.db",
    warehouse="file:///tmp/rag_warehouse"
)
catalog.create_namespace_if_not_exists("rag")

schema = Schema(
    NestedField(1, "chunk_id",   StringType(),  required=True),
    NestedField(2, "doc_path",   StringType(),  required=True),
    NestedField(3, "doc_title",  StringType(),  required=True),
    NestedField(4, "chunk_idx",  IntegerType(), required=True),
    NestedField(5, "content",    StringType(),  required=True),
    NestedField(6, "token_count", IntegerType(), required=True),
    NestedField(7, "ingested_at", TimestampType(), required=False),
)

try:
    catalog.drop_table("rag.doc_chunks")
except Exception:
    pass

tbl = catalog.create_table("rag.doc_chunks", schema=schema)

rows = [json.loads(l) for l in open('chunks.jsonl')]
for r in rows:
    r['ingested_at'] = dt.datetime.now()

tbl.append(pa.Table.from_pylist(rows, schema=tbl.schema().as_arrow()))
print(f"Wrote {len(rows)} chunks to Iceberg table rag.doc_chunks")
print("Snapshots:", [s.snapshot_id for s in tbl.metadata.snapshots])
```

```bash
python 2_write_iceberg.py
```

**预期**：`Wrote 600 chunks to Iceberg table rag.doc_chunks`，有 1 个 snapshot。

**验证**（可选）：
```bash
python -c "
from pyiceberg.catalog.sql import SqlCatalog
c = SqlCatalog('lab', uri='sqlite:///rag_catalog.db', warehouse='file:///tmp/rag_warehouse')
tbl = c.load_table('rag.doc_chunks')
print(tbl.scan().to_pandas().head(3))
"
```

## Step 5 · Embed + 入 LanceDB

```python
# 3_embed.py
from pyiceberg.catalog.sql import SqlCatalog
from sentence_transformers import SentenceTransformer
import lancedb, numpy as np

# 读 Iceberg 表（snapshot 锁定 → 可复现）
catalog = SqlCatalog("lab", uri="sqlite:///rag_catalog.db", warehouse="file:///tmp/rag_warehouse")
tbl = catalog.load_table("rag.doc_chunks")
df = tbl.scan().to_pandas()
print(f"Loaded {len(df)} chunks from Iceberg (snapshot {tbl.current_snapshot().snapshot_id})")

# Embed（CPU 上约 1-3 分钟）
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
texts = df['content'].tolist()
vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=True, batch_size=32)

# 写 LanceDB
db = lancedb.connect("lancedb")
rag_tbl = db.create_table(
    "doc_embeddings",
    data=[{
        "chunk_id": r['chunk_id'],
        "doc_title": r['doc_title'],
        "doc_path": r['doc_path'],
        "content": r['content'],
        "vector": vec.tolist(),
        "snapshot_id": str(tbl.current_snapshot().snapshot_id),
    } for r, vec in zip(df.to_dict('records'), vecs)],
    mode="overwrite",
)
print(f"Indexed {len(df)} rows into LanceDB")
```

```bash
python 3_embed.py
```

**预期**：进度条显示 encoding 中，最后 `Indexed ~600 rows`。

## Step 6 · 简单 RAG（只用向量检索）

```python
# 4_rag_basic.py
import lancedb, os
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
db = lancedb.connect("lancedb")
tbl = db.open_table("doc_embeddings")

def retrieve(query: str, k: int = 5):
    q_vec = model.encode([query], normalize_embeddings=True)[0]
    results = tbl.search(q_vec.tolist()).limit(k).to_pandas()
    return results

def ask(query: str, k: int = 5) -> str:
    ctx = retrieve(query, k)
    context = "\n\n---\n\n".join(
        f"【来源：{r['doc_title']} ({r['doc_path']})】\n{r['content'][:800]}"
        for _, r in ctx.iterrows()
    )
    prompt = f"""你是一个基于内部文档库回答问题的助手。
**只根据材料回答**，回答末尾用 [doc_title] 格式列出引用来源。
材料如果不相关，回答"文档中没找到答案"。

材料：
{context}

问题：{query}

回答："""
    # 用 OpenAI 或本地 Ollama（选一）
    from openai import OpenAI
    client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    for q in ["什么是湖表？和 DB 存储引擎有什么不同？",
              "HNSW 和 IVF-PQ 怎么选？",
              "多模检索流水线关键步骤？"]:
        print(f"\nQ: {q}")
        print(f"A: {ask(q)}\n{'='*60}")
```

```bash
export OPENAI_API_KEY=sk-...          # 或本地 Ollama 用 OPENAI_BASE_URL=http://localhost:11434/v1
python 4_rag_basic.py
```

**预期**：三个问题都能回答并带引用。回答应该基于你的文档内容。

## Step 7 · 加 Hybrid + Rerank（质量跃升）

```python
# 5_rag_hybrid.py
import lancedb, os
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
reranker = CrossEncoder("BAAI/bge-reranker-base")
db = lancedb.connect("lancedb")
tbl = db.open_table("doc_embeddings")

# 离线构建 BM25 索引（只在启动时做一次）
all_rows = tbl.to_pandas()
tokenized = [list(text) for text in all_rows['content']]  # 字符级分词，中文够用
bm25 = BM25Okapi(tokenized)

def hybrid_retrieve(query: str, k_dense=30, k_sparse=30, k_final=10):
    # 1. Dense
    q_vec = model.encode([query], normalize_embeddings=True)[0]
    dense = tbl.search(q_vec.tolist()).limit(k_dense).to_pandas()
    dense['src'] = 'dense'
    dense['rrf_score'] = 1.0 / (60 + dense.index.values)

    # 2. Sparse (BM25)
    scores = bm25.get_scores(list(query))
    top_idx = scores.argsort()[-k_sparse:][::-1]
    sparse = all_rows.iloc[top_idx].copy()
    sparse['src'] = 'sparse'
    sparse['rrf_score'] = 1.0 / (60 + range(len(sparse)))

    # 3. RRF 融合
    merged = (dense[['chunk_id','doc_title','doc_path','content','rrf_score']]._append(
              sparse[['chunk_id','doc_title','doc_path','content','rrf_score']])
              .groupby('chunk_id', as_index=False)
              .agg({'doc_title':'first', 'doc_path':'first', 'content':'first',
                    'rrf_score':'sum'})
              .sort_values('rrf_score', ascending=False)
              .head(30))

    # 4. Cross-encoder rerank
    pairs = [[query, c] for c in merged['content']]
    scores = reranker.predict(pairs)
    merged['rerank_score'] = scores
    return merged.sort_values('rerank_score', ascending=False).head(k_final)

def ask_hybrid(query: str) -> str:
    ctx = hybrid_retrieve(query)
    context = "\n\n---\n\n".join(
        f"【{r['doc_title']} · {r['doc_path']}】\n{r['content'][:600]}"
        for _, r in ctx.iterrows()
    )
    prompt = f"""只基于以下材料回答，引用格式 [doc_title]。
材料无关就说"没找到答案"。

材料：
{context}

问题：{query}

回答："""
    from openai import OpenAI
    client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}], temperature=0.2)
    return resp.choices[0].message.content

if __name__ == "__main__":
    for q in ["什么是湖表？和 DB 存储引擎有什么不同？",
              "HNSW 和 IVF-PQ 怎么选？"]:
        print(f"\nQ: {q}")
        print(f"A: {ask_hybrid(q)}\n{'='*60}")
```

```bash
python 5_rag_hybrid.py
```

**预期**：相比 Step 6 纯向量版，这一版**命中更准**、更少幻觉、引用更贴切。

## Step 8 · 验证"可复现性"（Iceberg Snapshot 的价值）

```python
# 6_verify_reproducible.py
from pyiceberg.catalog.sql import SqlCatalog

catalog = SqlCatalog("lab", uri="sqlite:///rag_catalog.db", warehouse="file:///tmp/rag_warehouse")
tbl = catalog.load_table("rag.doc_chunks")

print("所有 snapshot:")
for s in tbl.metadata.snapshots:
    print(f"  id={s.snapshot_id}  ts={s.timestamp_ms}  summary={s.summary}")

# 模拟"未来这张表已经变了 10 次"，我还能读回今天这一版
current_snap = tbl.current_snapshot().snapshot_id
print(f"\n按 snapshot_id={current_snap} 精确复现当时的数据：")
scan = tbl.scan(snapshot_id=current_snap)
print(f"  行数：{sum(1 for _ in scan.to_arrow().to_pylist())}")
```

```bash
python 6_verify_reproducible.py
```

**这是 Iceberg 给 RAG 的最大额外价值**：**训练集 / 回归测试集永远可复现**。如果 3 个月后模型升级退化，你能精确回到"当时的文档版本"对比。

## 跑不通的自查

| 症状 | 可能原因 |
| --- | --- |
| `pyiceberg` 报 schema 错 | PyArrow 版本 < 14，升级 |
| SQLite `database is locked` | 并行多进程同时连；改成顺序执行 |
| BGE 模型下载慢 | 国内用 `HF_ENDPOINT=https://hf-mirror.com`；或用 `text2vec-base-chinese` 备选 |
| LanceDB 搜索返回 0 行 | 检查 embeddings 是否真存进去（`tbl.count_rows()`）|
| LLM 回答"没找到" | 检索结果没相关内容；检查 Step 3 chunk 质量 |
| Hybrid 不如纯 Dense 好 | BM25 tokenize 方式对中文不对；改分词器或调 RRF k |
| Rerank 太慢 | 本地 CPU 上 30 条 × Cross-encoder 要 5-20s；生产要用 GPU |

## 你现在明白了什么

- [RAG](../ai-workloads/rag.md) 的实际 pipeline：**chunk → embed → retrieve → rerank → LLM**
- [Iceberg](../lakehouse/iceberg.md) 作为**事实源 + 版本化**给 RAG 的可复现性加了保险
- [LanceDB](../retrieval/lancedb.md) 作为**嵌入式向量库**省了运维
- [Hybrid Search](../retrieval/hybrid-search.md) 比纯向量好一档，[Rerank](../retrieval/rerank.md) 再升一档
- 这套东西**本地 CPU 能跑完整链路** —— 上生产就换模型和硬件就行

## 下一步

- **加 RAG 评估**：golden set + Recall@K / Faithfulness，见 [RAG 评估](../ai-workloads/rag-evaluation.md)
- **换强模型**：GPT-4o / Claude / 本地 Qwen2.5 → 回答质量更上
- **加 Prompt 管理**：见 [Prompt 管理](../ai-workloads/prompt-management.md)
- **做成服务**：FastAPI + Gradio 包一层 UI，[Model Serving](../ml-infra/model-serving.md)
- **改用 Lance 表**：把 chunks 直接存 Lance format，训练/回填更顺畅

## 相关

- [RAG](../ai-workloads/rag.md) · [RAG 评估](../ai-workloads/rag-evaluation.md)
- [Hybrid Search](../retrieval/hybrid-search.md) · [Rerank](../retrieval/rerank.md)
- [你的第一张 Iceberg 表](first-iceberg-table.md)
- [30 分钟湖上多模检索 Demo](multimodal-search-demo.md)
- 场景：[RAG on Lake](../scenarios/rag-on-lake.md)
