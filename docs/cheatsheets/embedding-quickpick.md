---
title: Embedding 模型速查
description: 按语种 / 维度 / 许可 1 分钟选型
type: reference
tags: [cheatsheet, embedding]
---

# Embedding 模型速查

## 一分钟选型

```
私有数据 + 中英为主 + 自托管:    BGE-v2-m3 (1024维)
多语言 + 长文 + 自托管:          Jina v3 (1024维，Matryoshka 可裁)
数据可出网 + 预算充足:           OpenAI text-embedding-3-large
企业级 API + RAG 全家桶:         Cohere embed v3
有 PG + 小规模:                  随便哪个 → pgvector 存
```

## 模型对比表

| 模型 | 开源 | 语种 | 维度 | Max tokens | MTEB 位次 | 许可 |
| --- | --- | --- | --- | --- | --- | --- |
| **BGE-v2-m3** | ✅ | 中英强 多语好 | 1024 | 8192 | 顶级 | MIT |
| **BGE-M3** | ✅ | 多语 | 1024 | 8192 | 顶级 | MIT |
| **E5-large-v2** | ✅ | 多语 | 1024 | 512 | 较强 | MIT |
| **Jina v3** | ✅ | 100+ 语 | 1024（可裁） | 8192 | 顶级 | Apache 2.0 |
| **Nomic v1.5** | ✅ | 英 | 768 | 8192 | 较强 | Apache 2.0 |
| **OpenAI ada-002** | API | 多语 | 1536 | 8191 | 中上 | 商用 |
| **OpenAI text-3-small** | API | 多语 | 1536 可截 | 8191 | 顶级 | 商用 |
| **OpenAI text-3-large** | API | 多语 | 3072 可截 | 8191 | 顶级 | 商用 |
| **Cohere embed v3** | API | 100+ | 1024 | 512 | 顶级 | 商用 |
| **Voyage v2** | API | 多语 | 1024 | 16000 | 顶级 | 商用 |

## 多模（跨模态）

| 模型 | 开源 | 模态 | 维度 | 备注 |
| --- | --- | --- | --- | --- |
| **CLIP ViT-B/32** | ✅ | 图 + 文 | 512 | 经典基线 |
| **SigLIP SO400M** | ✅ | 图 + 文 | 1152 | 比 CLIP 强，Google 开源 |
| **Jina CLIP v1** | ✅ | 图 + 文 | 768 | 含中文支持 |
| **BLIP-2** | ✅ | 图 + 文 | 多种 | 有生成能力 |
| **CLAP** | ✅ | 音 + 文 | 512 | 音频检索 |

## 按场景选

### 场景 1：中文客服 RAG，自托管

→ **BGE-v2-m3** 或 **BGE-reranker-v2-m3** 组合，甜区最稳

### 场景 2：多语言文档搜索

→ **Jina v3** 或 **BGE-M3**

### 场景 3：图文混合检索

→ **SigLIP SO400M**（跨模态）+ **BGE-v2-m3**（纯文本精细）两列

### 场景 4：规模大成本敏感

→ **BGE-small** 或 **Nomic** + Matryoshka 维度裁到 256

### 场景 5：POC / 原型

→ **OpenAI text-3-small**（1 行代码上线，上生产再换）

## 调用模板

### HuggingFace

```python
from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-large-zh-v1.5")
model = AutoModel.from_pretrained("BAAI/bge-large-zh-v1.5")

def encode(texts, batch_size=32):
    all_vecs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        inputs = tokenizer(batch, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outs = model(**inputs)
        vecs = outs.last_hidden_state[:, 0]           # CLS
        vecs = torch.nn.functional.normalize(vecs, p=2, dim=-1)
        all_vecs.extend(vecs.cpu().numpy())
    return all_vecs
```

### Sentence-Transformers

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-large-zh-v1.5")
vecs = model.encode(texts, normalize_embeddings=True)
```

### OpenAI

```python
from openai import OpenAI
client = OpenAI()
response = client.embeddings.create(
    input=texts,
    model="text-embedding-3-small",
    dimensions=768,      # 可截
)
vecs = [d.embedding for d in response.data]
```

## 版本治理清单

- [ ] 每张表都有 `embedding_version` 列
- [ ] CI 禁止直接修改 embedding 模型的 prod pin
- [ ] 换模型 = 新列 + 回填 + 双索引 + AB
- [ ] 评估集跟模型版本走
- [ ] `instruction prefix`（BGE 指令前缀）要一致

## 陷阱

- **忘加 BGE 的 `query:` 前缀** → 召回掉
- **L2 未归一化** → cosine 行为错乱
- **截维度到任意值** → 只有 Matryoshka 模型支持
- **中英混排用纯英文 embedding** → 中文段被忽略
- **超长文本不切块** → 截断 = 信息丢失

## 相关

- [Embedding](../retrieval/embedding.md)
- [多模 Embedding](../retrieval/multimodal-embedding.md)
- [Embedding 模型横比](../compare/embedding-models.md)
- [Embedding 流水线](../ml-infra/embedding-pipelines.md)
