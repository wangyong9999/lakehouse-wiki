---
title: 30 分钟湖上多模检索 Demo
type: tutorial
level: A
depth: 进阶
applies_to: LanceDB 0.8+ · open_clip_torch 2.x（2025-04）
last_reviewed: 2026-04-18
tags: [tutorial, lancedb, clip, multimodal]
status: stable
---

# 30 分钟湖上多模检索 Demo

!!! tip "你会做完"
    - 在**本地对象存储风格的目录**里建一张 LanceDB 表
    - 装一个公开图像数据集（小样本，200 张）
    - 用 CLIP 生成 embedding，入库
    - 用**文本查图 + 图查图**两种检索模式
    - 一个最小 Gradio UI 把它跑成网页
    - 全程 **30 分钟**，纯本地，CPU 即可

## 前置

- Python 3.10+
- 8GB 可用内存（CLIP-ViT-B/32 模型大约 600MB）
- 没了

## Step 1 · 环境

```bash
pip install lancedb pillow torch transformers datasets gradio pyarrow
```

说明：

- `lancedb` —— 湖原生向量库
- `transformers` —— 加载 CLIP
- `datasets` —— 抓公开样本图
- `gradio` —— 给出交互 UI

## Step 2 · 拉 200 张样本图

```python
# 1_fetch.py
from datasets import load_dataset
from pathlib import Path

out_dir = Path("data/images")
out_dir.mkdir(parents=True, exist_ok=True)

# Oxford Flowers 102，合法商用，图小，语义清晰
ds = load_dataset("nelorth/oxford-flowers", split="train[:200]")
for i, ex in enumerate(ds):
    ex["image"].save(out_dir / f"{i:03d}.jpg")

print("Saved 200 images to", out_dir)
```

```bash
python 1_fetch.py
```

**预期**：`Saved 200 images to data/images`

## Step 3 · CLIP encode + 入 LanceDB

```python
# 2_index.py
from pathlib import Path
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
import lancedb
import pyarrow as pa

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device).eval()
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def embed_images(paths, batch_size=16):
    vecs = []
    for i in range(0, len(paths), batch_size):
        batch = [Image.open(p).convert("RGB") for p in paths[i:i+batch_size]]
        inputs = processor(images=batch, return_tensors="pt").to(device)
        with torch.no_grad():
            v = model.get_image_features(**inputs)
        v = torch.nn.functional.normalize(v, p=2, dim=-1)
        vecs.extend(v.cpu().numpy())
    return vecs

# 索引所有图
image_paths = sorted(Path("data/images").glob("*.jpg"))
print(f"Encoding {len(image_paths)} images...")
vecs = embed_images(image_paths)

# 写到 LanceDB
db = lancedb.connect("data/lancedb")
rows = [
    {
        "asset_id": i,
        "uri": str(p),
        "vector": vec.tolist(),
    }
    for i, (p, vec) in enumerate(zip(image_paths, vecs))
]
tbl = db.create_table("flowers", data=rows, mode="overwrite")
print(f"Indexed {len(rows)} rows into LanceDB")
```

```bash
python 2_index.py
```

**预期**：`Indexed 200 rows into LanceDB`，耗时 1-3 分钟（CPU 上）。

## Step 4 · 用文本查图

```python
# 3_search_text.py
import lancedb, torch
from transformers import CLIPModel, CLIPProcessor

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device).eval()
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def text_embed(text):
    inputs = processor(text=[text], return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        v = model.get_text_features(**inputs)
    v = torch.nn.functional.normalize(v, p=2, dim=-1)
    return v[0].cpu().numpy().tolist()

tbl = lancedb.connect("data/lancedb").open_table("flowers")

for query in ["purple flower", "red rose", "yellow sunflower"]:
    results = tbl.search(text_embed(query)).limit(3).to_pandas()
    print(f"\n[{query}] → {list(results['uri'])}")
```

```bash
python 3_search_text.py
```

**预期输出**（具体文件名会变）：

```
[purple flower] → ['data/images/012.jpg', 'data/images/067.jpg', 'data/images/089.jpg']
[red rose]      → ['data/images/003.jpg', 'data/images/145.jpg', 'data/images/031.jpg']
[yellow sunflower] → ['data/images/152.jpg', 'data/images/098.jpg', 'data/images/184.jpg']
```

**打开这几张图核对**，是不是对的？这就是 CLIP 多模空间的魔法：**文本和图在同一个向量空间**里可以直接比相似度。

## Step 5 · 用图查图

```python
# 4_search_image.py
import lancedb, torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device).eval()
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def image_embed(path):
    img = Image.open(path).convert("RGB")
    inputs = processor(images=[img], return_tensors="pt").to(device)
    with torch.no_grad():
        v = model.get_image_features(**inputs)
    v = torch.nn.functional.normalize(v, p=2, dim=-1)
    return v[0].cpu().numpy().tolist()

tbl = lancedb.connect("data/lancedb").open_table("flowers")

# 拿第 0 张作为 query
q_vec = image_embed("data/images/000.jpg")
results = tbl.search(q_vec).limit(5).to_pandas()
print("相似图:", list(results['uri']))
```

跑完打开原图和结果图——**同品种的花应该排在前面**。

## Step 6 · 用 Gradio 套个 UI（5 分钟）

```python
# 5_ui.py
import lancedb, torch, gradio as gr
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device).eval()
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
tbl = lancedb.connect("data/lancedb").open_table("flowers")

def text_search(query):
    inputs = processor(text=[query], return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        v = torch.nn.functional.normalize(model.get_text_features(**inputs), p=2, dim=-1)
    results = tbl.search(v[0].cpu().numpy().tolist()).limit(6).to_pandas()
    return [r['uri'] for _, r in results.iterrows()]

demo = gr.Interface(
    fn=text_search,
    inputs=gr.Textbox(label="用文字描述你想找的花"),
    outputs=gr.Gallery(label="结果", columns=3, height=400),
    title="湖上多模检索 Demo",
    examples=["a purple flower", "red rose", "small white flower"],
)
demo.launch()
```

```bash
python 5_ui.py
```

浏览器打开 `http://127.0.0.1:7860`，直接输入英文描述找图。

## 跑不通的自查

| 症状 | 可能原因 |
| --- | --- |
| `OOM` | CPU 上 batch 太大，改 `batch_size=4` |
| 下载 CLIP 卡住 | 网络问题，用镜像或手动 `huggingface-cli download` |
| 结果离谱（牛头不对马嘴） | 没做 L2 归一化；检查 `F.normalize` |
| Gradio `Error` 在前端看到 | 看终端 traceback，通常 vector 长度不一致 |
| `datasets` 下载慢 | 换成本地图片目录，改 `1_fetch.py` |

## 你现在明白了什么

- [LanceDB](../retrieval/lancedb.md) 直接读写本地对象存储风格的目录，**不需要独立服务**
- [CLIP / 多模 Embedding](../retrieval/multimodal-embedding.md) 让文 / 图共享一个向量空间
- [HNSW / ANN 索引](../retrieval/hnsw.md) 在 200 张小数据上看不到效果，但换成 100 万张马上就是救命稻草

## 下一步

- 想加过滤？表里加 `category` 字段 + `tbl.search(vec).where("category='flower'")`
- 想做 RAG？把 CLIP 换成文本模型 BGE，表里存文档 chunk
- 系统读：[多模数据建模](../unified/multimodal-data-modeling.md) · [多模检索流水线](../scenarios/multimodal-search-pipeline.md) · [图像管线](../pipelines/image-pipeline.md)
- 速查：[向量数据库 §7 多引擎 SQL](../retrieval/vector-database.md) · [ANN 索引对比](../compare/ann-index-comparison.md)
