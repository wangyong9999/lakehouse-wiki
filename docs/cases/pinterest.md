---
title: 案例 · Pinterest 数据平台
type: reference
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: Iceberg · PinSage (GNN) · Pixie · Homefeed · Ads Ranking · PinLater · Dr.Elephant · Querybook · 2020-2026 公开资料
tags: [case-study, pinterest, multimodal-recommendation, pinsage, gnn, graphjet, iceberg]
aliases: [Pinterest Data Platform]
related: [studies, netflix, linkedin, uber, recommender-systems, multimodal-embedding]
systems: [iceberg, pinsage, graphjet, homefeed]
status: stable
---

# 案例 · Pinterest 数据平台

!!! info "本页性质 · reference · 非机制 canonical"
    基于 Pinterest Engineering Blog · 论文（PinSage SIGKDD 2018 · Pixie SIGMOD 2018）· 公开演讲整理。机制深挖见 [retrieval/multimodal-embedding](../retrieval/multimodal-embedding.md) · [scenarios/recommender-systems](../scenarios/recommender-systems.md)。

!!! success "对应场景 · 配对阅读"
    本案例 = **Pinterest 业务系统全栈**（推荐场景深度）。**场景切面**在 scenarios/：
    - [scenarios/recommender-systems](../scenarios/recommender-systems.md) §工业案例 · PinSage + Pixie 推荐切面
    - [scenarios/multimodal-search-pipeline](../scenarios/multimodal-search-pipeline.md) §工业案例 · Pinterest 多模检索切面

!!! abstract "TL;DR"
    - **身份**：**多模推荐系统工业代表** · "**图(Pin) + 文 + 用户行为**"融合推荐最成熟案例
    - **核心技术贡献**：**PinSage**（SIGKDD 2018 · 大规模 GNN 推荐）· **Pixie**（SIGMOD 2018 · 大规模实时 random walk 推荐）
    - **工业规模**：5 亿+ MAU · 万亿级 Pin · 每次 feed 调用涉及数十亿候选召回
    - **技术栈关键**：Iceberg（2020+ 迁移自 Hive）+ 自研 Serving + 自研 Embedding 产线 + PinLater（异步任务）+ Homefeed（主推荐系统）
    - **最有价值启示**：**"embedding 是推荐的一等语料"** · 多模推荐**需要图结构 + 内容 + 协同过滤三者结合** · 纯向量或纯 BM25 都不够
    - **最值得资深工程师看的**：§8 深度技术取舍（Pixie 实时 random walk vs PinSage 离线 GNN 的互补 · 为什么 Pinterest 保留两套系统）· §5 多模 embedding 实操

## 1. 为什么这个案例值得学

Pinterest 的独特性：
- **纯多模推荐业务**（和 Netflix / Uber 的数据平台业务不同 · Pinterest **本质是推荐公司**）
- **公开论文质量高**：PinSage（SIGKDD 2018）是最被引用的工业 GNN 推荐论文 · Pixie（SIGMOD 2018）是工业级实时 random walk 推荐的代表
- **技术代际演进公开**：从早期矩阵分解 → **Pixie random walk**（SIGMOD 2018）→ **PinSage GNN**（SIGKDD 2018）→ 后续 Transformer-based 是推荐系统 10 年演进的**活化石**

**资深读者关注点**：
- **多模 embedding 在推荐中的工业化路径**（§5）
- **图结构 vs 向量 vs 行为 · 三者如何工程组合**（§8.1 · 资深推荐读者核心兴趣）
- **PinSage 后的 10 年** · Pinterest 怎么做 Transformer + LLM 推荐（§6）

## 2. 历史背景

Pinterest 2010 成立 · 业务本质：**让用户发现图片 + 组织兴趣**（Pin + Board）。

**核心业务 = 推荐系统**：
- **Homefeed**（主 feed · 每次访问看几十个 Pin）
- **Related Pins**（Pin 详情页推荐）
- **Search**（搜索相关 Pin）
- **Ads Ranking**（广告排名）

所有这些都是**多模推荐问题**（图像 + 文本描述 + 用户行为 + 社交图）。

**技术演进**：
- 2012-2016 基于 Hadoop + Hive · 推荐用矩阵分解 + 协同过滤
- 2015-2018 **Pixie** · 工业级实时 random walk 推荐（SIGMOD 2018 论文）
- 2018 **PinSage** · 大规模 GNN 推荐（SIGKDD 2018 论文）
- 2020+ 迁 Iceberg · 现代化数据湖
- 2022+ Transformer-based 推荐 · 整合大语言模型
- 2024+ 多模 LLM 应用（visual search + 生成式推荐）

## 3. 核心架构（推荐链路 · 2026 形态）

```mermaid
flowchart BT
  subgraph "数据源"
    pin_events[Pin 创建 / 编辑 / save]
    user_events[用户浏览 / 点击 / 停留]
    img[图像内容]
  end

  subgraph "数据湖"
    kafka[Kafka]
    iceberg[(Iceberg 2020+<br/>历史 Hive 迁移中)]
  end

  subgraph "离线 embedding 产线"
    spark[Spark 批处理]
    cv[图像 embedding<br/>CLIP-like / 自研 VLM]
    text[文本 embedding<br/>BGE / 自研]
    user[用户 embedding]
    graph[图结构 embedding<br/>PinSage GNN]
  end

  subgraph "索引 + 召回"
    ann[ANN 索引<br/>自研 ScaNN-based]
    realtime[实时召回<br/>Pixie-like]
  end

  subgraph "精排 + 重排"
    ranker[LTR / DNN 精排]
    rerank[多样性 / 业务规则重排]
  end

  subgraph "服务"
    homefeed[Homefeed 服务]
    related[Related Pins]
    ads[Ads Ranking]
  end

  pin_events & user_events & img --> kafka --> iceberg
  iceberg --> spark --> cv & text & user & graph
  cv & text & user & graph --> ann
  iceberg --> realtime
  ann & realtime --> ranker --> rerank
  rerank --> homefeed & related & ads
```

## 4. 8 维坐标系

| 维度 | Pinterest |
|---|---|
| **主场景** | **多模推荐系统**（图 + 文 + 行为 + 图结构） |
| **表格式** | **Iceberg**（2020+ · 迁移自 Hive） |
| **Catalog** | 自研 + Iceberg REST |
| **存储** | S3 |
| **向量层** | **自研 ANN**（ScaNN 风格）· 深度定制化 · 非通用向量库 |
| **检索** | **Dense embedding + Graph 召回 + LTR 精排 + 多样性重排** 四段 |
| **主引擎** | Spark + 自研 serving（推荐场景特化） |
| **独特做法** | **embedding 作推荐主语料** · 图结构和向量融合（PinSage 思想） |

## 5. 关键技术组件 · 深度

### 5.1 PinSage · 大规模 GNN 推荐（SIGKDD 2018）

**Pinterest 2018 年公开的 GNN 推荐系统** · 是 GraphSAGE 在**工业级大规模**的第一个成功应用：

**核心思想**：
- Pin 之间通过 Board 形成图（同 Board 的 Pin 相关）
- **Random walk 采样邻居** + GraphSAGE 聚合
- 输出 Pin embedding · 用 ANN 召回

**工程亮点**：
- **30 亿 + Pin** 级别训练（2018 年已达这个规模）
- **MapReduce 并行化 GraphSAGE**
- 训练 72 GPU × 72 小时
- 论文：[*Graph Convolutional Neural Networks for Web-Scale Recommender Systems*](https://arxiv.org/abs/1806.01973)（SIGKDD 2018）

**意义**：PinSage 证明 **GNN 能在工业大规模场景下工作** · 后来被 Uber Eats / Alibaba 推荐等多家复刻。

### 5.2 Pixie · 实时 random walk 推荐（SIGMOD 2018 · Pinterest 自研）

**Pinterest 自研的实时推荐系统**（2015-2018 开发 · 2018 SIGMOD 发表）：
- **in-memory 图结构**（Pin × User × Board · 内存 10+ TB 规模）
- **实时 random walk**（每次请求 ms 级生成推荐）
- **非 GNN** · 纯算法 + 工程优化 · 单机处理 30 亿+ Pin

**论文**：[*Pixie: A System for Recommending 3+ Billion Items to 200+ Million Users in Real-Time*](https://dl.acm.org/doi/10.1145/3178876.3186183)（SIGMOD 2018 · Eksombatchai et al. · Pinterest）

!!! note "事实澄清 · Pixie vs GraphJet"
    Pixie 是 **Pinterest 自研**（SIGMOD 2018）· **Twitter 另有一个叫 GraphJet 的系统**（VLDB 2017 · 也是 random walk 推荐但在 Twitter）—— **两者不同** · 容易混淆。本页所讲的 Pinterest 实时推荐**指 Pixie**。

**和 PinSage 的区别**：
- Pixie · 实时 + 轻量 + 无模型训练
- PinSage · 离线 + 深度 + 需要大量训练

**Pinterest 保留两者**：Pixie 处理"**实时新鲜度**"需求 · PinSage 处理"**深度相关性**"需求。

### 5.3 Homefeed · 主推荐系统

Pinterest 的**主 feed 推荐系统**（用户首页）：
- 数十亿候选召回 → 百万精排 → 百级重排
- 多路召回：ANN + Graph + Text-based + 协同过滤
- LTR 精排：GBDT / DNN
- 业务重排：多样性 · 新鲜度 · 广告插入

**关键工程数字**（`[来源未验证]`）：
- **p95 端到端 < 300ms**
- 每请求处理 **数十亿候选**（通过多级剪枝）
- 数百个 online 模型

### 5.4 PinLater · 异步任务系统

Pinterest 自研 · 2020+ 公开：
- 推荐链路里的**异步任务**（embedding 计算 · 索引更新 · 批评分）
- 对标 Celery / Airflow · 但更低延迟
- 和数据湖深度集成

### 5.5 Multimodal Embedding 产线

Pinterest 的 embedding 产线**极度定制化**：
- **图像 embedding**：自研 VLM（CLIP 风格但专门 Pin 场景调）
- **文本 embedding**：Pin 标题 + 描述 + 评论
- **用户 embedding**：行为历史 + 社交关系
- **图结构 embedding**：PinSage

**关键工程实践**：
- 每一种 embedding **独立训练 + 独立迭代**
- **ANN 索引按 embedding 类型分**（图 index + 文 index + 用户 index 各自）
- 召回时**多 index 并行查询** · 融合 Top-K

### 5.6 Dr.Elephant · Hadoop 作业优化（历史遗产）

Pinterest 2016 年开源的 Hadoop / Spark 作业性能分析工具。**2020+ 已经维护降级**（随着 Iceberg + 新一代调度迁移）· 但仍是**工业作业分析工具的代表**。

### 5.7 Querybook · 协作 SQL IDE（2018 开源）

Pinterest 开源的**协作 SQL 查询工具** · 定位类似 Hue / Superset：
- 数据分析师友好
- 和内部 Catalog 集成
- 2020-2026 持续维护

## 6. 2024-2026 关键演进

| 时间 | 事件 | 意义 |
|---|---|---|
| 2020+ | Hive → Iceberg 迁移 | 数据湖现代化 |
| 2022+ | **Transformer-based 推荐**（替代部分 GBDT）| 推荐模型升级 |
| 2023+ | **视觉搜索 + 生成式推荐探索** | 多模 LLM 应用 |
| 2024 | LLM 增强的"Creative Studio"（广告主 AI 工具）| 商业化 AI 应用 |
| 2024+ | PinSage 后继版本（细节未公开）| GNN 推荐持续演进 |

!!! warning "以下为作者推测 · 非 Pinterest 官方"
    2025+ Pinterest 可能在 **visual search + 多模 RAG** 场景做生成式推荐 —— 但**具体产品和上线时间未官方确认**。以 Pinterest Engineering Blog 最新发布为准。

## 7. 规模数字

!!! warning "以下为量级参考 · `[来源未验证 · 示意性 · 来自 Pinterest Engineering Blog / 财报 / 论文]`"

| 维度 | 量级 |
|---|---|
| 月活用户 | 5 亿+ |
| Pin 总数 | 万亿级 |
| Board 总数 | 数百亿 |
| 每日推荐请求 | 数十亿 |
| Homefeed p95 端到端 | < 300ms |
| 单次 feed 候选池 | 数十亿 Pin |
| Embedding 维度典型 | 128-768 |
| ANN 索引节点 | 数十亿级 |

## 8. 深度技术取舍 · 资深读者核心价值

### 8.1 取舍 · 图 vs 向量 vs 行为 · 三者如何工程组合

推荐系统的**经典技术代际**：

1. **协同过滤**（2000+）· 用户行为矩阵分解
2. **内容 embedding**（2015+）· 物品内容向量（图像 / 文本）
3. **图结构**（2014+）· 社交 / Board / 关联图
4. **深度学习融合**（2018+ · PinSage）· GNN 统一三者

**Pinterest 2026 的实际架构**：**三者并存 · 不是单一方法**：
- 协同过滤：新用户冷启动差 · 只用不够
- 纯内容 embedding：**同质化严重** · 推不出多样性
- 纯图结构：新 Pin 信息不足
- **深度学习融合**（PinSage）：训练成本高 · 不是所有场景用

**资深启示**：**推荐系统 = 多路召回 + 精排 + 重排** · 不是"找到一个最好模型"。每路召回专门解决一类场景（冷启动 · 新鲜度 · 相关性 · 多样性）· 精排融合。

### 8.2 取舍 · 自研 ANN vs 通用向量库（Milvus / Qdrant）

Pinterest **不用通用向量库** · 用自研 ANN（ScaNN 风格）：

**自研的理由**：
- 推荐规模极大（数十亿级）· 通用库性能不够
- **过滤感知 ANN** 在推荐场景特别重要（按 user segment / 地理 / 年龄 过滤召回）
- 和内部数据系统（Iceberg / Kafka）深度集成
- 历史包袱（早于 Milvus / Qdrant 成熟）

**通用库的代价**：
- 不够定制
- 性能瓶颈在巨量候选下暴露

**资深启示**：**通用向量库在极大规模下往往不够** · 头部互联网推荐公司都自研 ANN（Facebook FAISS · Google ScaNN · Pinterest 自研 · 字节 / 阿里 / 美团都自研）。

### 8.3 取舍 · Pixie 和 PinSage 为什么并存

Pixie 和 PinSage **都是 Pinterest 2018 年公开的推荐系统** · 但两者**并存而不互相替代**。为什么？

**Pixie 的独特价值**：
- **实时性** · 新 Pin 立刻能被推出去（PinSage 需要批训练）
- **新鲜度** · 抓住短时热点
- **轻量** · 每次请求几毫秒

**PinSage 的独特价值**：
- **深度相关性** · 能捕捉复杂的图结构关系
- **规模** · 处理离线大图

**两者是互补 · 不是替代**：
- Homefeed 同时用两者
- 新鲜度高的推荐倾向 Pixie
- 深度相关性推荐倾向 PinSage

**资深启示**：**工业推荐系统很少"新技术替代旧技术"** · 而是"**新技术作新场景 · 旧技术继续服务老场景**"。这和纯学术"新方法 SOTA"不同。

### 8.4 取舍 · 多 embedding 独立 vs 统一 embedding

Pinterest 选择**每类 embedding 独立训练 + 独立 ANN 索引**：

**独立的好处**：
- 每类 embedding 可以**独立迭代**（图像模型升级不影响文本模型）
- ANN 索引**按类型优化**（图向量和文本向量用不同 HNSW 参数）
- 召回时**多路并行** · 结果融合

**统一 embedding 的好处**（不选）：
- 架构简单
- 训练一次覆盖所有
- 但**迭代速度慢**（一次训练就要全量重建所有索引）

**2024 的趋势**：多模 LLM（CLIP / SigLIP / ImageBind）提供"一个 embedding 空间覆盖多模"· 部分挑战 Pinterest 的"独立 embedding"哲学。但 Pinterest 实践中仍以**独立为主**（迭代速度 + 定制化的需求）。

## 9. 真实失败 / 踩坑

### 9.1 早期 Spark 作业性能问题

2016 年 Pinterest 开源 Dr.Elephant（Hadoop / Spark 作业性能分析）· 说明当时内部有**大量性能不优**的作业。

**教训**：大规模数据平台 · 作业性能问题**长期积累** · 需要专门工具链去持续优化（不是"写得好"就行）。

### 9.2 Hive → Iceberg 迁移慢

2020+ 启动 · 2024-2026 仍在进行。和 LinkedIn 类似的**大规模迁移低估**。

**教训**：表格式迁移是**组织工程** · 即使 Pinterest 这种技术实力强的公司也需要 5+ 年。

### 9.3 推荐模型的"A/B 疲劳"

推荐系统 A/B 实验极度依赖 · 但**长期会出现**：
- **实验重叠** · 多实验交互影响
- **Proxy metric 陷阱** · CTR 涨业务不涨
- **新奇效应** · 初期好看后续回落

Pinterest 和其他头部推荐公司都公开讨论过这些问题。

**教训**：**推荐系统 A/B 实验设计**是专门学科（见 [ml-infra/ml-evaluation](../ml-infra/ml-evaluation.md)）· 不是"流量分一分"就完事。

### 9.4 GNN 推理成本高

PinSage 训练成本高是公开的 · **推理成本也不低**（图结构计算非 trivial）。

**教训**：**GNN 在推荐中不是普适方案** · 计算成本和业务价值需要权衡。2024+ 很多公司回归**向量召回 + 轻量 rerank** 的简化路径。

## 10. 对团队的启示

!!! warning "以下为观点提炼 · 非客观事实 · 选 2-3 条记住即可"
    启示较多（5 条）· 不必全读全用。战略决策 canonical 在 [unified/index §5 团队路线主张](../unified/index.md) · [catalog/strategy](../catalog/strategy.md) · [compare/](../compare/index.md) · 本页启示是**可参考的观察** · 不是建议照搬。


### 启示 1 · "Embedding 是主语料"的彻底实施

Pinterest 把 embedding **作为数据平台的一等公民**：
- 每个 Pin 有多种 embedding
- Embedding 和数据表同一套治理
- 更新 embedding 有完整 pipeline（见 [ml-infra/embedding-pipelines](../ml-infra/embedding-pipelines.md)）

**对本团队**：**embedding 不是 RAG 的附属** · 是**检索 · 推荐 · 训练 · 缓存 · 去重**的通用基础设施。

### 启示 2 · 多路召回架构

推荐系统架构 = **多路召回 + 精排 + 重排**：
- 每路召回专门解决一类问题（相关性 / 新鲜度 / 多样性 / 冷启动）
- 精排融合
- 重排业务规则

**对中小推荐团队**：不要追求"一个模型解决所有" · 多路是必经之路（见 [scenarios/recommender-systems](../scenarios/recommender-systems.md)）。

### 启示 3 · 工业级推荐需要自研 ANN

规模到达几亿+ · 通用向量库性能和定制性不够。**自研 ANN 是头部公司的标准配置**（PinSage / ScaNN / 自研都是自研）。

**对本团队**：
- 小规模（千万级以下）· 通用向量库够
- 大规模（亿级+）· 需要深度定制 · 最终可能自研

### 启示 4 · 图 + 内容 + 行为的融合

推荐系统的**永恒问题**是图结构、内容、行为三者如何融合。Pinterest 的答案：**三者同时用 · 互相补位 · 不是二选一**。

### 启示 5 · 保留旧系统的智慧

Pixie 和 PinSage 并存（虽然都是 2018 公开 · 但解决不同问题）是**工业智慧**：两种技术路径可以**占据不同场景** · 不是"有新技术就必须替换旧技术"。**不要被"新技术就该替换"绑架**。

## 11. 技术博客 / 论文（权威来源）

- **[Pinterest Engineering Blog](https://medium.com/pinterest-engineering)** —— 推荐 / 数据相关文章高质量
- **[*Graph Convolutional Neural Networks for Web-Scale Recommender Systems*](https://arxiv.org/abs/1806.01973)**（SIGKDD 2018 · PinSage 原始论文）
- **[*Pixie: A System for Recommending 3+ Billion Items in Real-Time*](https://dl.acm.org/doi/10.1145/3178876.3186183)**（SIGMOD 2018 · Pinterest 自研）
- **[Homefeed 架构系列博客](https://medium.com/pinterest-engineering)**（搜索 homefeed）
- **[PinSage 扩展版博客](https://medium.com/pinterest-engineering/pinsage-a-new-graph-convolutional-neural-network-for-web-scale-recommender-systems-88795a107f48)**
- **[Dr.Elephant 开源](https://github.com/linkedin/dr-elephant)**（原 LinkedIn · Pinterest 实践过）
- **[Querybook 开源](https://github.com/pinterest/querybook)**

## 12. 相关章节

- [多模 Embedding](../retrieval/multimodal-embedding.md) —— 多模 embedding 机制
- [推荐系统 / 场景](../scenarios/recommender-systems.md) —— 推荐系统端到端
- [Embedding 流水线](../ml-infra/embedding-pipelines.md) —— embedding 产线机制
- [HNSW](../retrieval/hnsw.md) · [DiskANN](../retrieval/diskann.md) · [Filter-aware Search](../retrieval/filter-aware-search.md) —— ANN 机制
- [ML Evaluation](../ml-infra/ml-evaluation.md) —— A/B 实验显著性
- [案例 · Netflix · LinkedIn · Uber · Databricks · Snowflake · 阿里巴巴](studies.md) —— 同代案例
