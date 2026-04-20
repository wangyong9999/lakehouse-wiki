---
title: 检索评估 · Recall / MRR / nDCG / BEIR / MTEB
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: Retrieval · RAG · 推荐 · 搜索 通用评估
tags: [retrieval, evaluation, metrics, beir, mteb]
aliases: [检索指标, Retrieval Metrics]
related: [vector-database, hybrid-search, rerank, embedding, rag, rag-evaluation]
systems: []
status: stable
---

# 检索评估

!!! tip "一句话理解"
    "检索准不准"不能靠感觉——必须有**度量 + Benchmark + 业务映射**。本页覆盖：三核心指标（Recall/MRR/nDCG）· 业界 Benchmark（BEIR/MTEB）· 业务→检索指标映射 · Golden set 工程 · 生产监控契约。

!!! info "和其他页的边界"
    - 本页 · **检索层**（Top-K 召回 + 排序质量）的评估
    - [RAG 评估](../ai-workloads/rag-evaluation.md) · **RAG 端到端**评估（生成质量 + 忠实度 + 答案对齐）· 包含检索层但视角更上
    - 两层评估**互补不重复**——检索层指标是 RAG 指标的前置条件

!!! abstract "TL;DR"
    - **核心 3 指标**：Recall@K（召回覆盖）· MRR（首正确位置）· nDCG（排序质量）
    - **业界 Benchmark**：**MTEB**（通用 embedding · 8 任务类）· **BEIR**（检索专项 · 18 数据集 · 2021+）· **C-MTEB**（中文）· **MIRACL**（多语）
    - **业务 → 检索指标映射**：RAG 看 Recall@K（K=5-10）· 搜索看 MRR/nDCG · 推荐看 Recall@100+
    - **Golden set 工程** · 分桶 · 代表性 · 定期更新 · 成本
    - **生产监控契约** · 不只是开发时跑 · 要上线后持续监控

## 1. 三个核心指标

### Recall@K · 召回覆盖

> **Top-K 结果里，有多少个相关文档被命中？**

$$\text{Recall@K} = \frac{|\text{relevant} \cap \text{top\_K}|}{|\text{relevant}|}$$

- 值域 [0, 1] · 越大越好
- 对"**覆盖率**"最敏感——漏了重要文档会直接掉
- **RAG 场景下最关键**：没被召回的文档 LLM 无法使用

### MRR（Mean Reciprocal Rank）

> **正确答案出现在第几位？用 1/rank 加权。**

$$\text{MRR} = \frac{1}{Q} \sum_{q=1}^{Q} \frac{1}{\text{rank}_q}$$

- 值域 (0, 1] · 越大越好
- 只看**第一个**相关结果的位置
- 适合"**确切答案**"型场景（QA · 文档查找）

### nDCG（normalized Discounted Cumulative Gain）

> **综合多个相关结果的排序质量 · 相关度可分级。**

$$\text{DCG}@K = \sum_{i=1}^{K} \frac{2^{rel_i} - 1}{\log_2(i+1)}$$

nDCG = DCG / IDCG（理想 DCG）

- 值域 [0, 1] · 越大越好
- 支持"**很相关 / 有点相关 / 无关**"多级标注
- **推荐 / 多答案场景的标准指标**

### 其他常用

| 指标 | 含义 |
|---|---|
| **Precision@K** | Top-K 里有多少是相关的 |
| **F1@K** | Precision 和 Recall 的调和平均 |
| **Hit Rate@K** | Top-K 里是否**至少有一个**相关（二值）|
| **MAP (Mean Average Precision)** | 召回质量的综合——Precision@1, @2, ... 的平均 |

## 2. 业务 → 检索指标映射

**不同业务的 "检索质量" 定义不同**：

| 业务 | 首要指标 | 原因 |
|---|---|---|
| **RAG / QA** | **Recall@K (K=5-10)** | LLM 只看 Top-K · 必须覆盖相关文档 · 排序靠 rerank + LLM 后处理 |
| **搜索（web / 站内）** | **MRR + nDCG@10** | 用户主要看首屏 · 前几位质量决定体验 |
| **推荐** | **Recall@100-500 + nDCG@10** | 先召回大池 · 排序 + 业务规则筛选后展示前 10-20 |
| **去重 / 聚类** | **Precision@K + 阈值** | 宁可漏不误合 · 高准确率优先 |
| **异常检测** | **Recall@1** + 低延迟 | 第一结果就要是异常 · 误报可接受 |
| **代码搜索** | **Hit Rate@5 + nDCG** | 用户查找具体代码片段 · 前几个能找到就好 |

**配合 rerank 的分层策略**：

- 一阶段 · 召回：看 **Recall@100-1000**（大池）
- 二阶段 · rerank：看 **nDCG@10** 或 **MRR**（Top-K 排序质量）
- 端到端：看首要业务指标 + 业务 A/B 数字

## 3. 业界 Benchmark

### MTEB · 通用 Embedding Benchmark

**[MTEB (Massive Text Embedding Benchmark)](https://huggingface.co/spaces/mteb/leaderboard)** · Muennighoff et al. 2023 · 业界事实**embedding 模型榜单**。

覆盖 **8 类任务**：

| 任务类别 | 说明 | 主指标 |
|---|---|---|
| **Retrieval** | 检索 | nDCG@10 |
| **Reranking** | 重排 | MAP / MRR |
| **Classification** | 分类 | Accuracy |
| **Clustering** | 聚类 | V-measure |
| **Pair Classification** | 句对分类 | AP |
| **Semantic Similarity (STS)** | 语义对齐 | Spearman |
| **Summarization** | 摘要评估 | Spearman |
| **Bitext Mining** | 双语对齐 | F1 |

**选模型只看 "综合分" 是典型错误**——**各任务子榜差异巨大**。RAG 看 Retrieval 子榜 · 分类看 Classification 子榜。

### BEIR · 零样本检索 Benchmark

**[BEIR (Benchmarking IR)](https://github.com/beir-cellar/beir)** · Thakur et al. 2021 · **专门评估检索**——18 个数据集覆盖多领域：

- **开放域 QA**：MS MARCO · NaturalQuestions · HotpotQA
- **事实验证**：FEVER · Climate-FEVER
- **金融 / 法律 / 生物医学**：FiQA · SCIDOCS · NFCorpus
- **论坛 / 社区**：CQADupStack · Quora
- **新闻 / 百科**：Touche-2020 · ArguAna · DBPedia

**核心价值**：**零样本（zero-shot）评估**——模型不见过这些数据集的训练数据 · 测 generalization。

**主指标**：nDCG@10

### C-MTEB / MIRACL · 中文 + 多语

- **[C-MTEB](https://huggingface.co/spaces/mteb/leaderboard)** · MTEB 的中文子榜
- **[MIRACL](https://github.com/project-miracl/miracl)** · 多语言 retrieval benchmark（17 语言）

### 自家数据 benchmark · 生产必须

**MTEB / BEIR 告诉你模型的"**通用能力**"**——**但你的自家数据和业务 query 分布可能与 benchmark 完全不同**。

**上线前必须**：
- 在**自家 Golden Set** 上评 · 见下 §4
- 特别关注**业务长尾 query**（稀有词 / 专业术语 / 多意歧义）· 这是模型最容易翻车的地方

### 多模评估 · 不要把文本 benchmark 结论外推

!!! warning "MTEB / BEIR 主要评的是文本检索"
    以上 benchmark 都是**文本为主**——**把文本结论直接外推到多模检索是典型错误**。多模评估有独立的挑战：

- **跨模态 benchmark 不多 · 且偏差大**：
  - **COCO Caption / Flickr30k** · 最常用的图文检索 benchmark · 但 caption 风格很工具化 · 和业务 query 分布差很远
  - **MSCOCO Image-to-Text / Text-to-Image** · 对齐 benchmark · 但 1 图 × 5 caption 的设定和生产"1 图 × N 种业务描述"不同
  - **MSR-VTT / MSVD** · 视频检索 benchmark · 2016-2019 构造 · 规模小 · 领域窄
  - **AudioSet / Clotho** · 音频检索 benchmark · 但 caption 覆盖有限

- **各模态组合的评估成熟度不均衡**：
    - 图 ↔ 文 · 有 benchmark 但有偏差
    - 视频 ↔ 文 · benchmark 数量少 · 多为实验室级别
    - 音频 ↔ 文 · benchmark 规模小
    - 图 ↔ 音 / 音 ↔ 视 等 · 几乎无 benchmark

### 多模检索评估 · 业务驱动方法论

**对"多模检索"章节**来说 · 评估应该按业务场景定义：

| 多模场景 | 评估思路 | 典型指标 |
|---|---|---|
| **文搜图**（产品 / 素材） | 自家图文对 + 业务分类分桶 · 图像 recall 人工抽样 | Recall@10 + 点击率 |
| **图搜图**（视觉相似） | 同类图对 + 专家标注 · "同款 / 相似 / 无关" 三级 | nDCG@10 |
| **视频语义搜索** | 业务 query + 视频 shot 级相关性 · 视频标注**粒度和业务对齐**（见 [retrieval-granularity](retrieval-granularity.md)）| Hit Rate + 视频跳转位置准确率 |
| **音频内容搜索**（播客 / 会议）| 关键词 + 音频段 · **优先评估 ASR 后的文本检索路径** | 句级 Recall + 说话人段定位准确 |
| **多模 RAG**（检索 + LLM 回答）| 参见 [RAG 评估](../ai-workloads/rag-evaluation.md) · 检索层 + 生成层分开评 | 检索 Recall@K + RAG 端到端 faithfulness |

### 多模评估的关键差异点

**和文本检索评估的 5 个不同**：

1. **相关性分级更难**——文本"相关/不相关"清晰 · 图"同款/相似/稍相似/无关"四级判断要视觉专家
2. **多模态召回分布要监控**——纯看综合 Recall 看不到"文本路 100% 文本 · 图像路 0% 图像"的不平衡（见 [multimodal-retrieval-patterns §4 失败 3](multimodal-retrieval-patterns.md)）
3. **粒度和评估绑定**——以 shot 还是 frame 为单位评估视频 · 决定了召回定义
4. **对齐度 ≠ 检索质量**——benchmark 显示 CLIP 对齐 85% 不代表业务 Recall@10 是 85%（见 [multimodal-embedding 失败 5](multimodal-embedding.md)）
5. **跨语言 / 跨文化**——英文 benchmark 的图文结论在中文业务里可能不成立

### 多模 Golden Set 的特殊工程

- **相关性需要视觉 / 听觉专家**——不是文本标注员能做的 · 标注成本更高
- **分桶维度多**——除了 query 长度 / 类型 · 还要按**模态 · 视觉复杂度 · 场景**分
- **业务 A/B 是最终裁判**——多模评估指标远未成熟 · 最好**指标 + 业务 A/B 双验证**

## 4. Golden Set 工程

**Golden Set** = (query, relevant_doc_ids, relevance_level) 三元组集合 · 是所有评估的**真相源**。

### 构造 · 三条路 + 工程细节

| 路径 | 工具推荐 | 成本 | 质量 |
|---|---|---|---|
| **专家标注** | Label Studio / Prodigy / Argilla / 自建 UI | 高（$1-10/query）| 最高 |
| **行为标签** | 用户点击 / 停留 / 购买作弱标签 | 低（数据已有）| 有噪 · 规模大 |
| **LLM 辅助标注** | GPT-4 / Claude / Qwen 判相关性 | 中（$0.01-0.10/query）| 待人工抽样校验 |

**规模建议**：

- **最小可用**：100 条 query · 每 query 5-10 个相关 doc
- **生产可用**：500-1000 条 query · 覆盖主要业务场景
- **工业级**：5000+ query · 持续扩充 + 版本化

### 分桶 · 必须做

**golden set 不分桶 = 指标平均掩盖问题**。关键分桶维度：

- **query 长度** · 短 query（< 5 词）/ 长 query（> 20 词）· 长尾效应不同
- **query 类型** · 查询型 / 探索型 / 导航型 / 交易型
- **领域 / 类别** · 按业务分类分桶
- **query 难度** · 根据历史指标 · 简单 / 中 / 难三档
- **模态（多模场景）** · 纯文 / 文+图 / 纯图

### 定期更新

- **业务周期** · 每季度 / 每月更新 · 防老化
- **新词 / 新类别** · 业务扩张后及时补
- **定期重新标注** · 相关性理解会随业务变化

## 5. 生产监控契约 · 不只是开发评

### 上线前 · CI Gate

```mermaid
flowchart LR
  golden[Golden Set] --> run[Run Retrieval]
  run --> metrics[Recall@K / MRR / nDCG]
  metrics --> gate{< 阈值?}
  gate -->|是| block[阻止上线]
  gate -->|否| pass[通过]
```

**把检索指标接进 CI / 上线流程**：模型升级前先跑 golden set · 指标掉了 fail。

### 上线后 · 持续监控

| SLI | 含义 | 告警阈值示例 |
|---|---|---|
| **线上 MRR（行为标签估计）** | 从用户点击推断 · 相对数 · 看趋势 | 跌 10% 告警 |
| **Top-K 真实点击率 (CTR)** | 业务侧兜底指标 | 跌 5% 告警 |
| **长尾 query 覆盖** | 小众 query 是否仍有返回 | 覆盖率 < 95% 告警 |
| **Golden Set 周扫** | 定期跑 golden | 任意指标跌 5% 告警 |
| **embedding 分布漂移** | 新数据向量分布 vs 老数据 | KL 散度 > 阈值告警 |

### 分桶分析 · 诊断指标掉落

**指标掉了之后怎么诊断**？

1. 分桶看 · 哪个桶掉得最狠
2. query 模式分析 · 长 query / 短 query / 特定领域
3. 对比新旧模型在差异 query 上的 Top-K 结果 · 人工 review
4. Rerank 侧 vs 召回侧 · 分别看指标

## 6. 陷阱

- **只看 Recall@10 忽视 Recall@100** · 精排好不好的前提是召回足够
- **评测集老化** · 上线一年业务已经变 · golden set 没更新
- **单点指标** · Recall 看不到"tail queries"崩坏 · 要分桶看
- **用训练数据做评测** · 永远乐观 · 必须用**独立** golden set
- **没对齐业务感受** · 指标涨但用户说更烂 · 说明 golden 没反映真实查询分布
- **只看综合分不看子榜** · MTEB 综合 top 的模型在你的任务上可能一般
- **LLM 辅助标注不做人工校验** · 一致性问题会污染 golden set
- **忽视 rerank 和召回的指标分层** · 混在一起看不清瓶颈在哪

## 相关

- [RAG 评估](../ai-workloads/rag-evaluation.md) · 端到端 RAG 层
- [Rerank](rerank.md) · 二阶段评估
- [Hybrid Search](hybrid-search.md) · 融合策略对指标的影响
- [Embedding](embedding.md) · 模型选型看 MTEB 子榜
- [RAG](../ai-workloads/rag.md) · 业务映射到 Recall@K

## 延伸阅读

- **[MTEB · 原始论文](https://arxiv.org/abs/2210.07316)** · Muennighoff et al. 2023
- **[BEIR · 原始论文](https://arxiv.org/abs/2104.08663)** · Thakur et al. 2021
- **[MIRACL](https://arxiv.org/abs/2210.09984)** · Zhang et al. 2022 · 多语言 retrieval
- **[*Introduction to Information Retrieval*](https://nlp.stanford.edu/IR-book/)** · Manning et al. · 第 8 章 Evaluation
- **[LLM-as-a-Judge · Scaling Evaluating LLM Applications](https://arxiv.org/abs/2306.05685)** · Zheng et al. 2023
