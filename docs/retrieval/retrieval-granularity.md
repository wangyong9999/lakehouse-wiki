---
title: 检索单元粒度 · Retrieval Unit / Chunking Granularity
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: 文本 RAG · 图像 · 视频 · 音频 · 文档检索 通用
tags: [retrieval, granularity, chunking, shot, frame, asset]
aliases: [检索粒度, chunking 粒度, retrieval unit]
related: [multimodal-retrieval-patterns, multimodal-embedding, hybrid-search, evaluation, rag]
systems: []
status: stable
---

# 检索单元粒度 · Retrieval Unit / Chunking Granularity

!!! tip "一句话定位"
    **"检索什么单位"** 是多模检索的一等问题——直接决定**召回质量 / 索引规模 / rerank 成本**。文本 RAG 里的 "chunk 大小"只是这个问题的一个表现。在图像 / 视频 / 音频场景下有**更多独立粒度决策**：整文档 vs 段落 · 整视频 vs shot vs frame · 整音频 vs 说话人段 vs 句级。

!!! info "和其他页的边界"
    - 本页 · **"一个对象在索引里是几条记录 / 什么粒度"** 的设计原则
    - [多模检索架构模式](multimodal-retrieval-patterns.md) · 端到端架构 · 本页粒度决策是其中一环
    - [Hybrid Search](hybrid-search.md) · 稀疏+稠密融合 · 粒度已定后的下一层
    - [pipelines/document-pipeline · chunking](../pipelines/document-pipeline.md) · 文档管线里的 chunking 具体实现

!!! abstract "TL;DR"
    - **粒度是硬设计** · 建完索引后改粒度 = 重新索引 + 重写数据
    - **粒度 × 模态** 矩阵：文本（文档/章节/段落/句）· 图像（整图/patch/ROI）· 视频（整视/shot/frame/key-frame）· 音频（整音/说话人段/句）· 文档（文件/页/块/图文对）
    - **召回质量 vs 索引规模 vs rerank 成本** 三角权衡
    - **粗粒度 + rerank 精细化** vs **细粒度 + 高质量召回** · 两条生产范式
    - **业务对齐的粒度**最优——用户问的是"哪句"就以句为单位 · "哪页"就以页为单位

## 1. 为什么粒度是一等问题

### 文本 RAG 的粗糙直觉

大多数 RAG 教程直接说"把文档切成 512 token 的 chunk"——**这只是文本世界的一个选择**，而且往往是错的。

**真相**：粒度选择影响**整个检索栈**：

- **太粗**（整文档当一个向量）· 检索无法定位相关段落 · LLM 收到超大上下文 · 有效信息稀释
- **太细**（每句一个向量）· 索引暴涨 · 上下文片段不完整 · 跨句语义丢
- **不对齐业务问题**（用户问"哪页" · 但你以"段落"为粒度）· 最终答案对不齐

### 多模场景更复杂

| 模态 | 可选粒度 |
|---|---|
| **文本** | 文档 / 章节 / 段落 / 句 / token |
| **图像** | 整图 / patch grid（如 14×14）/ ROI（object detection 后）|
| **视频** | 整视频 / shot（镜头）/ key-frame / 帧 / 时间段（如 10 秒）|
| **音频** | 整音频 / 说话人段（diarization）/ 句（ASR）/ 时间段 |
| **文档**（PDF/PPT）| 文件 / 页 / 块（layout）/ 图文对 / 表格 |
| **图文对资产** | 整资产 / 图像独立 + 文本独立 / 图+文融合为一个 |

**"检索什么单位"比"选 HNSW 还是 IVF"更重要**——错了的粒度 · 再好的 ANN 救不回来。

## 2. 粒度决策三角

```
      召回质量
        ▲
        │
        │
 粗 ────┼──── 细
        │
        │
        ▼
  索引规模 · rerank 成本
```

**权衡**：

| 维度 | 粗粒度 | 细粒度 |
|---|---|---|
| **召回质量** | 难定位具体位置 | 精准到具体段 |
| **索引规模** | 小 · 1 对象 1 条 | 大 · 1 对象 N 条（N=10-1000）|
| **rerank 成本** | 低 · 候选少 | 高 · 候选多 |
| **LLM 上下文** | 上下文完整但稀释 | 精炼但可能丢上下文 |
| **业务对齐** | 对齐"查哪个文档" | 对齐"查哪段 / 哪句 / 哪帧" |

## 3. 两种生产范式

### 范式 A · 粗粒度 + Rerank 精细化

```
Index: 整文档 / 整视频 级别
  ↓
Stage 1: 粗粒度召回 Top-100 文档
  ↓
Stage 2: Rerank 或 LLM 二次检索 · 定位文档内具体段 / 帧
  ↓
返回精准位置 + 上下文
```

**适用**：
- 索引预算紧 · 不想几倍膨胀
- 二阶段成本可接受
- 文档级召回能解决 80% 问题

**典型**：商品搜索（整商品召回 + LLM 摘要）· 视频推荐（整视频召回 + 客户端定位高光）。

### 范式 B · 细粒度 + 高质量召回

```
Index: 段落 / shot / 帧 级别
  ↓
Stage 1: 直接召回精准单位 Top-10
  ↓
返回具体段 + 原对象 ID
```

**适用**：
- 质量要求极高 · 索引规模预算足
- RAG 需要精准上下文片段
- 视频搜索要跳转具体时间点

**典型**：高质量 RAG（段落级）· 视频检索（shot 级）· 法律条款查询（句级）。

## 4. 各模态的粒度选择

### 文本 / RAG · 块级是默认

**chunk 策略**：

- **固定长度**（如 512 token）+ overlap（50-128 token）—— 简单兼容性好
- **语义分块**（llama-index / unstructured 的 semantic splitter）—— 按句/段边界切 · 质量高
- **结构分块**（按 Markdown heading / PDF page block）—— 保留结构信息
- **Parent-child 策略**：子 chunk（小 · 精准召回）→ 父 chunk（大 · 丢给 LLM）—— 2024+ 流行

**推荐默认**：**semantic splitter + 父子策略 + overlap**。chunk 大小按 LLM 上下文预算反推（Top-5 chunk × 大小 < LLM 上下文 / 2）。

### 图像 · Patch vs 整图

- **整图 embedding**（CLIP / SigLIP）· 粗粒度 · 适合语义搜索（"找夏天海边的图"）
- **Patch-level**（ViT 14×14 grid · 每 patch 一个 token）· 细粒度 · 支持"图的某个区域"检索
- **ROI-level**（先跑 object detection · 每 box 一个 embedding）· 精准定位物体 · 成本高

**推荐**：整图 + CLIP 作默认——除非明确需要"区域级"检索。

### 视频 · Shot / Key-frame / Frame

```
整视频(一个向量)        shot 级(10-100 个向量)       key-frame(30-500 个)        frame(数千到万)
     ↓                      ↓                             ↓                          ↓
  语义搜索               内容摘要                      跳转具体时点                视频理解
   (粗)                   (中)                           (细)                       (极细)
```

**生产默认**：**shot 切分 + 每 shot 一个 key-frame embedding**。

- shot 切分用 ffmpeg scene detection（见 [video-pipeline](../pipelines/video-pipeline.md)）
- key-frame 通常取 shot 中间帧 / 关键帧
- 每 shot 一个向量索引 · 查询时返回 shot 级 Top-K + 时间戳
- 细粒度需求走 ColBERT 多向量（见 [multimodal-retrieval-patterns Pattern E](multimodal-retrieval-patterns.md)）

### 音频 · 说话人段 / 句级

- **整音频**（CLAP embedding）· 音乐 / 环境音搜索
- **说话人段**（diarization 切分后每段一个 embedding）· 播客 / 会议检索
- **ASR 句级** + 文本检索 · 语音转写后走文本检索路径（**常常比音频 embedding 更好**）

**推荐**：**ASR 转文本 + 句级文本检索** 作为主路径 · 音频 embedding 作为补充。

### 文档（PDF / PPT）· 页 / 块 / 图文对

- **文件级** · 太粗 · 查不到具体位置
- **页级** · 中粒度 · 对齐用户"查哪页"心智
- **块级**（layout-aware · 段 / 表 / 图 独立 chunk）· 细粒度 · 高质量 RAG 首选
- **图文对**（页中的图 + 对应 caption 作为一个 asset）· 特殊场景

**推荐**：**块级 + 图文对** 双索引。详见 [document-pipeline](../pipelines/document-pipeline.md) 的 chunking 段。

## 5. 粒度与业务对齐

**最重要原则**：**粒度应该对齐用户的问题形态**。

| 用户问的 | 对应粒度 |
|---|---|
| "哪个文档讨论 X？" | 文档级 / 章节级 |
| "哪段话说 X？" | 段落级 |
| "哪一帧显示 X？" | 视频帧级 |
| "谁说了 X？" | 音频说话人段 |
| "哪一页是发票？" | 文档页级 |

**典型错误**：用户问"哪一页" · 你索引以"段落"为单位 · 结果召回多条段落但跨多页 · UI 展示混乱。

## 6. 粒度迁移成本

**粒度是硬设计**——一旦建完索引就**很难改**：

- 改粒度 = **重新切分 + 重新计算 embedding + 重建索引**
- 亿级 embedding 重算可能 GPU 月级
- 如果走 embedding 模型 API 按量计费 · 重算成本巨大

**所以 · 上线前一定要试不同粒度 · Golden Set 对比** · 不要上线了才发现粒度错。

## 7. 陷阱

- **用 512 token chunk 不看业务** · 合法默认但可能和用户问题形态不对齐
- **细粒度不做 parent 映射** · 返回的片段脱离上下文 · LLM 看不懂
- **视频按 frame 建索引** · 存储 100× · 95% 冗余（连续帧差异很小）
- **文档直接按页索引** · 页里的表格 / 图丢失结构信息
- **chunk 之间没 overlap** · 跨边界语义丢
- **忘记 embedding 模型的上下文窗口** · chunk 大于窗口被截断 · embedding 质量暴跌
- **粒度选择没跑 golden set 评估** · 凭直觉选 · 上线后 Recall@K 崩

## 8. 相关

- [多模检索架构模式](multimodal-retrieval-patterns.md) · 端到端架构 · 粒度是其中一环
- [多模 Embedding](multimodal-embedding.md) · embedding 模型上下文窗口决定粒度上限
- [Hybrid Search](hybrid-search.md) · 粒度确定后的融合策略
- [检索评估](evaluation.md) · 粒度选型必配 Golden set 评估
- [pipelines/document-pipeline](../pipelines/document-pipeline.md) · 文档 chunking 具体实现
- [pipelines/video-pipeline](../pipelines/video-pipeline.md) · 视频 shot 切分具体实现
- [ai-workloads/RAG](../ai-workloads/rag.md) · RAG 场景的粒度典型选择

## 9. 延伸阅读

- **[LlamaIndex · Chunking Strategies](https://docs.llamaindex.ai/)** · 文本 chunking 实战
- **[Unstructured · semantic chunking](https://unstructured.io/)** · 语义分块工具
- **[LangChain · Parent Document Retriever](https://python.langchain.com/docs/modules/data_connection/retrievers/parent_document_retriever)** · 父子策略
- **[ColBERT · late interaction](https://arxiv.org/abs/2004.12832)** · 细粒度多向量
