---
title: E2E 业务场景全景 · Business Scenarios Atlas
type: scenario
depth: 进阶
prerequisites: [lake-table, vector-database]
tags: [scenarios, business, atlas]
related: [bi-on-lake, rag-on-lake, multimodal-search-pipeline, real-time-lakehouse]
status: stable
---

# E2E 业务场景全景

!!! tip "一句话理解"
    `scenarios/` 里其他页是**架构视角**（这种结构怎么搭）；这一页是**业务视角**——给你一个分类框架 + Top 10 主流业务场景 + 前沿方向，每个都映射到**核心组件**和**可部署的参考**。新同学带着业务问题进来，这页是第一站。

!!! abstract "TL;DR"
    - **分类框架 = 工作负载访问模式 × 业务产出**（两个正交轴）
    - **Top 10 主流场景**：BI 报表 / 即席探索 / 实时运营 / 企业 RAG / 多模检索 / 推荐 / 欺诈风控 / CDP 分群 / 经典 ML / Agentic 工作流
    - **前沿**：Text-to-SQL · AI-native Analytics · 近实时个性化 · 持续学习 · 多模内容生成 · 科研数据平台
    - **决策矩阵**：场景 × 存储 × 计算 × 检索 × 观测
    - **Benchmark 索引**：TPC-DS · BEIR · MS MARCO · Criteo · Taobao · LAION 等

## 为什么要这一页

团队新同学过来常问的不是"湖表怎么做 ACID"，而是：

- "我们要做客服 AI 问答，该怎么组合？"
- "我要搭一个电商推荐系统，选哪些组件？"
- "风控团队的反欺诈怎么落湖？"

**架构视角不直接回答这些**。这页**按业务→技术**倒推，把手册的组件拼成场景方案。

---

## 分类框架

### 两个正交轴

**Axis 1 · 工作负载访问模式**（workload shape）—— 决定了技术栈的核心诉求

| 访问模式 | 特征 | 延迟目标 | 规模特征 |
|---|---|---|---|
| **Batch OLAP** | 批量大扫描 + 聚合 | 分钟-小时 | GB/s 扫描吞吐 |
| **交互探索** | 分析师 ad-hoc SQL | 秒级 | 并发低但要快 |
| **实时分析** | 事件驱动 / 看板 / 告警 | 秒-分钟 | 持续流入 |
| **经典 ML** | 批训练 + 在线推理 | 训练：分钟-小时；推理：毫秒 | 训练重；推理高并发 |
| **检索 / 搜索** | ANN + hybrid + 过滤 | p99 < 50ms | 数百-千 QPS |
| **LLM / 生成** | 长上下文生成 | 秒-十秒 | TPM/RPM |
| **多模 / 跨模态** | 图 ↔ 文 ↔ 音 联合检索 | < 400ms | 中等 QPS |

**Axis 2 · 业务产出**（what it delivers）—— 决定了数据模型和消费路径

| 产出 | 读者 | 典型形态 |
|---|---|---|
| **决策支持** | 管理层 / 分析师 | 仪表盘 · 报表 · 临时分析 |
| **预测 / 评分** | 业务系统 | 分值 API · 批产出表 |
| **推荐 / 发现** | 终端用户 | Top-K 列表 · 排序结果 |
| **生成 / 回答** | 终端用户 / 内部工具 | 文本 · 代码 · 图片 |
| **检测 / 识别** | 风控 / 审核 / 运维 | 告警 · 打分 · 自动决策 |
| **自动化** | 内部工作流 | Agent 执行完整任务链 |

### 交叉矩阵

每个业务场景 = 落在一组"(访问模式, 产出)"格子里。

---

## Top 10 主流业务场景

每个场景 **统一 6 段结构**：业务定义 → 存储 → 计算 → 组件链路 → Benchmark → 可部署参考。

---

### 1. BI · 报表 · 仪表盘

**业务**：月/周/日报、KPI 大屏、部门分析、财务审计。面向**管理决策**。

**存储诉求**：
- 宽事实表 + 维度表（详见 [OLAP 建模](../bi-workloads/olap-modeling.md)）
- 数据新鲜度 T+1 或小时级
- 历史可追溯（Time Travel 可选）

**计算诉求**：
- 大 shuffle + 聚合（Spark 批 ETL）
- 高并发仪表盘查询（Trino 或 StarRocks 加速副本）
- p95 ≤ 3s（仪表盘）

**组件链路**：
```
OLTP / 日志 → Flink CDC / Spark → Iceberg (ODS / DWD / DWS / ADS 四层)
                                      → Trino 交互 + StarRocks 物化视图
                                      → Superset / Tableau / 自研
```

**Benchmark**：**TPC-DS** / **TPC-H** / **SSB**（Star Schema Benchmark）

**可部署参考**：
- Superset + Trino + Iceberg（docker-compose 社区方案很多）
- 我们的 [BI on Lake 场景](bi-on-lake.md)

---

### 2. 即席探索 / 数据科学 Notebook

**业务**：数据分析师、科学家打开 Jupyter 随手查；验证假设；出一张图。

**存储诉求**：
- 直接读湖表（无需 export）
- Snapshot 锁定以保证复现

**计算诉求**：
- 单机或小集群即可
- 延迟敏感（< 10s 出结果）

**组件链路**：
```
Iceberg / Paimon → DuckDB / Polars / pyiceberg + PyArrow → Jupyter
```

**Benchmark**：没有标准；用自家 Top 20 真实查询

**可部署参考**：
- DuckDB + Iceberg extension，零配置起步
- [Your first Iceberg table tutorial](../tutorials/first-iceberg-table.md)

---

### 3. 实时运营看板 / 监控告警

**业务**：实时 GMV、实时流量、订单异常告警、服务健康大屏。

**存储诉求**：
- 分钟级新鲜度（流式入湖）
- 短期热数据 + 长期归档分层

**计算诉求**：
- Flink / Spark Streaming 聚合
- StarRocks / ClickHouse 加速副本供仪表盘
- 流式聚合 + 窗口（见 [Watermark](../pipelines/event-time-watermark.md)）

**组件链路**：
```
Kafka / CDC → Flink → Paimon (主键表 + changelog)
                         ↓
                    StarRocks 加速 → Dashboard (秒级刷新)
                         ↓
                    Flink CEP → 告警 / 通知
```

**Benchmark**：业内无统一；可用 NYC Taxi 流式数据集做测试

**可部署参考**：
- [Real-time Lakehouse 场景](real-time-lakehouse.md)
- Flink CDC + Paimon 社区 demo

---

### 4. 企业 RAG · 知识库问答 · 客服

**业务**：员工问"休假流程怎么走"；客户问"我的订单状态"；开发者问"代码库里的 API 怎么用"。基于企业内部文档 / 代码 / 对话库。

**存储诉求**：
- `doc_chunks` Iceberg / Paimon 表（元数据可追溯）
- 向量列多套（CLIP / BGE / 语种特化）

**计算诉求**：
- 离线：Embedding 批量 + 索引构建
- 在线：检索 < 150ms + rerank < 100ms + LLM < 1s
- 更新频率：分钟到小时

**组件链路**：
```
源文档 (wiki/代码/JIRA) → 解析 + chunk → Iceberg doc_chunks
                                            ↓
                             Embedding (BGE / multilingual) → LanceDB / Puffin
                                            ↓
Query → Hybrid (dense + BM25) → Rerank (Cross-encoder) → Prompt → LLM (vLLM/TGI) → 答案 + 引用
```

**Benchmark**：**BEIR** · **MS MARCO** · **Natural Questions** · **RAGAS** 评估框架

**可部署参考**：
- 我们的 [60 分钟 RAG on Iceberg tutorial](../tutorials/rag-on-iceberg.md)
- [RAG on Lake 场景](rag-on-lake.md)
- LangChain + LlamaIndex 社区 RAG demo

---

### 5. 多模检索 · 以图搜图 · 跨模态

**业务**：设计师"用一张图找相似款"；电商"以图搜货"；视频平台"找到同款"；法务"翻 PDF 找证据图"。

**存储诉求**：
- 多模 asset 表（URI + 元数据 + CLIP 向量 + 文本 OCR/caption）
- 原文件留对象存储，表里只存指针

**计算诉求**：
- 离线：VLM caption / OCR / 音频 ASR + 多模 embedding
- 在线：跨模态向量检索 + metadata 过滤

**组件链路**：
```
上传 / 采集 → 对象存储 → 元数据入 Iceberg / Lance
                          ↓
        图像管线 / 视频管线 / 音频管线 / 文档管线
                          ↓
              CLIP / SigLIP embedding
                          ↓
                    LanceDB 向量列
                          ↓
         Query (文 / 图 / 混) → Hybrid → Rerank → 返回
```

**Benchmark**：**COCO** (caption) · **Flickr30k** · **LAION 子集** · **MS-COCO image-text retrieval**

**可部署参考**：
- [30 分钟多模检索 demo](../tutorials/multimodal-search-demo.md)
- [多模检索流水线场景](multimodal-search-pipeline.md)

---

### 6. 推荐系统 · 搜索 · 发现

**业务**：电商首页推荐、视频 feed 排序、音乐推荐、搜索结果个性化。面向**终端用户**，追求转化 / 停留。

**存储诉求**：
- 用户行为明细表（曝光 / 点击 / 消费，百亿级）
- 用户 / Item embedding
- 在线 Feature Store（低延迟 KV）

**计算诉求**：
- 离线：召回 / 排序模型训练
- 在线：**毫秒级**召回 + 排序 + rerank
- 近实时：用户行为反馈分钟级更新特征

**组件链路**：
```
行为日志 (Kafka) → Flink → Iceberg 事实表
                              ↓
                    Feature Store (离线训练 + 在线 KV)
                              ↓
            双塔 embedding 模型 (用户 × item)
                              ↓
            LanceDB / Milvus 向量召回
                              ↓
      Learning-to-Rank 精排 (XGBoost / DNN)
                              ↓
                   业务规则过滤 → 结果
```

详见 **[推荐系统场景深挖](recommender-systems.md)**。

**Benchmark**：**Criteo** (点击率) · **MovieLens** (电影推荐) · **Taobao** 公开数据集

**可部署参考**：
- RecBole (Python 推荐系统库，集成多个 baseline)
- 阿里 EasyRec (开源推荐框架)
- Merlin (NVIDIA GPU 推荐)

---

### 7. 欺诈检测 · 风险控制

**业务**：支付欺诈、账号盗用、洗钱识别、信贷风控。

**存储诉求**：
- 交易明细表 + 用户画像 + 设备指纹
- 图数据（账户/设备/交易关系网络）
- 规则引擎配置表

**计算诉求**：
- 实时：单笔交易**百毫秒**完成打分
- 近实时：滚动特征（近 1h / 24h）
- 离线：模型重训

**组件链路**：
```
支付流水 (Kafka) → Flink → Iceberg / Paimon
                              ↓
                 实时特征 (Flink state + Redis)
                              ↓
             特征 → 模型 (XGBoost / DNN / GNN)
                              ↓
                    规则引擎 (Drools / 自研)
                              ↓
                   判决: pass / review / reject
```

**图侧**（高级）：
- Neo4j / Nebula Graph 建账户关系
- GNN 训练识别欺诈团伙

详见 **[欺诈检测深挖](fraud-detection.md)**。

**Benchmark**：**IEEE-CIS Fraud Detection** · **PaySim** (模拟金融交易) · **Elliptic Bitcoin** (图) · **DGraphFin**

**可部署参考**：
- Feast + Spark + XGBoost 最小闭环
- PyG / DGL + DGraphFin 做 GNN baseline

---

### 8. 用户分群 · CDP · 精细化运营

**业务**：RFM 分群、流失预警、促销定向、个性化触达（短信 / Push）。

**存储诉求**：
- 行为事件表（海量）
- 画像宽表（数百列）
- 标签表（业务定义的群组）

**计算诉求**：
- 离线：Spark 跑 RFM / 聚类 / LTV
- 准实时：事件触发规则（用户 7 天无下单 → 加入流失风险群）

**组件链路**：
```
事件 → Iceberg 明细表
         ↓
      Spark 计算宽表 / 标签 / 分群
         ↓
        Trino / BI (分群可视化)
         ↓
  标签表 → 营销系统 (SMS / Push / 广告投放)
```

详见 **[CDP / 用户分群深挖](cdp-segmentation.md)**。

**Benchmark**：**[Olist 巴西电商](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)** · **[Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)** · **[Retailrocket](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset)**

**可部署参考**：
- GrowingIO / 神策 / Segment 公开 demo
- 自研：Iceberg + dbt + Superset 的最小 CDP
- Apache Unomi（开源 CDP 标准实现）

---

### 9. 经典 ML 预测 / 评分

**业务**：用户流失预测、信贷额度、商品销量预测、需求预测。

**存储诉求**：
- 训练集可复现（Iceberg Snapshot 锁定）
- Point-in-Time Correct Join（见 [离线训练数据流水线](offline-training-pipeline.md)）
- 在线特征 KV（Redis / DynamoDB）

**计算诉求**：
- 批训练：Spark MLlib / XGBoost / PyTorch
- 在线推理：REST API 毫秒级

**组件链路**：
```
事实表 + 特征表 (Iceberg) → PIT Join → 训练集
                                          ↓
                             训练 (Ray Train / Spark ML)
                                          ↓
                                   Model Registry
                                          ↓
                 部署 (Ray Serve / KServe / MLflow serving)
                                          ↓
                          业务系统调 API 拿评分
```

**Benchmark**：取决任务
- 分类：**Higgs** · **Criteo**
- 时序预测：**M5** · **M6**
- 推荐评分：见推荐系统 benchmark

**可部署参考**：
- [离线训练数据流水线](offline-training-pipeline.md) + [Feature Serving](feature-serving.md)
- MLflow + DVC 的标准 MLOps 闭环

---

### 10. Agentic 工作流 · 自动化

**业务**：客服自动处理工单；研发 "自动写测试"；运维 "自动 debug 慢查询"；数据分析师的 "chat-to-insight"。

**存储诉求**：
- 任务 / 对话历史表
- Tool 注册表
- 知识库（RAG 侧同享）
- Audit log

**计算诉求**：
- LLM 多轮调用
- Tool 调用（SQL / API / 代码执行）
- 长上下文（10K+ tokens 常见）

**组件链路**：
```
用户请求 → Agent (LLM + Controller)
                 ↓
            决策循环：
                ├── Tool: Text-to-SQL → Trino → 结果
                ├── Tool: Vector 检索 → LanceDB
                ├── Tool: 执行代码 → 沙箱
                └── Tool: 外部 API
                 ↓
              最终回答 + 引用 + 可复现轨迹
```

详见 **[Agentic 工作流深挖](agentic-workflows.md)**。

**Benchmark**：**SWE-bench** (软件工程)· **τ-bench** (工具使用) · **WebArena** · **AgentBench**

**可部署参考**：
- LangGraph / AutoGen 上的 demo
- Anthropic Computer Use / OpenAI Function Calling 示例

---

## 前沿场景（2024–2026）

### Text-to-SQL / Semantic SQL

**业务**：业务人员"给我看过去 30 天华北区 iPhone 销量"，系统自动生成 SQL。

**关键挑战**：
- 表 schema / 列语义自动对齐
- 多表 join 的启发式
- 权限穿透（用户能查的表不能越权）

**推荐栈**：Vanna / LlamaIndex SQL / Spider 数据集训练的自定义模型 + RAG over schema

**Benchmark**：**Spider** · **BIRD** · **WikiSQL**

### AI-native Analytics

**业务**：**分析师和 LLM 协同工作**——不是替代分析师，而是让分析师 10× 效率。LLM 写查询草稿、解释结果、提建议。

**推荐栈**：LLM co-pilot 嵌入 Superset / Metabase / Jupyter；RAG 辅助 schema 理解

### 近实时个性化

**业务**：用户行为**分钟级**反馈到推荐排序，而不是 T+1。

**推荐栈**：Flink 实时特征 + Paimon changelog → 在线 FS → 模型在线更新

### 持续学习 / Online Learning

**业务**：模型不是"训一次部署"，而是**持续用新数据增量更新**。

**推荐栈**：River (Python)  · Vowpal Wabbit · 自研 embedding drift 检测

### 多模内容生成

**业务**：电商自动生成商品描述 + 封面图；营销文案 + 配图；短视频脚本。

**推荐栈**：LLM 文本 + Stable Diffusion / Imagen 图片 + MCP 编排

### 科研数据平台

**业务**：药物发现（AlphaFold）· 材料（ChEMBL）· 基因（UK Biobank）· 气候模拟。

**特点**：
- 数据量极大（PB 级）
- 多模：结构 + 文献 + 实验
- 强复现性要求

**推荐栈**：湖仓 + Notebook + 专用工具（RDKit / Biopython）

---

## 决策矩阵：场景 × 核心组件

| 场景 | 表格式 | 计算 | 检索 / 向量 | 加速 | 观测关键 |
|---|---|---|---|---|---|
| BI 仪表盘 | Iceberg | Trino · Spark | — | StarRocks MV | 查询 p95 · 仪表盘刷新 |
| 即席探索 | Iceberg | DuckDB · Trino | — | — | 查询 p50 |
| 实时运营 | **Paimon** | Flink · Trino | — | StarRocks | 端到端 lag · 告警延迟 |
| 企业 RAG | Iceberg | Spark 批 · Flink CDC | **LanceDB** | — | 召回 @ K · Groundedness |
| 多模检索 | Iceberg / Lance | Spark · Flink | **LanceDB / Milvus** | — | 跨模态 recall |
| 推荐 | Iceberg · Feature Store | Spark · Ray Train | LanceDB (召回) | Online KV | 线上效果 AB |
| 欺诈检测 | Paimon · 图 DB | Flink · Spark | 图嵌入 | Redis | 实时打分延迟 |
| CDP | Iceberg 明细 | Spark · dbt | — | — | 分群跑批 SLA |
| 经典 ML | Iceberg + FS | Spark · Ray | — | Online KV | train/serve skew |
| Agentic | Iceberg | LLM serving | LanceDB | — | Task success · cost |

---

## Benchmark · Dataset · Demo 索引

| 领域 | Benchmark / Dataset | 对应 |
|---|---|---|
| OLAP | TPC-DS 10/100/1000, TPC-H, SSB, ClickBench | [Benchmark 参考](../frontier/benchmarks.md) |
| 检索 | BEIR, MS MARCO, Natural Questions, HotpotQA | RAG / 搜索 |
| 多模检索 | MS COCO, Flickr30k, LAION 子集, MS-COCO image-text | 多模检索 |
| 推荐 | Criteo, MovieLens, Taobao User Behavior | 推荐系统 |
| 欺诈 | IEEE-CIS Fraud, PaySim | 风控 |
| ML 经典 | Higgs, Kaggle 各比赛 | ML 预测 |
| 时序 | M5, M6, ETT | 预测 |
| LLM | MMLU, HumanEval, Chatbot Arena | LLM 选型 |
| Agent | SWE-bench, τ-bench, WebArena | Agentic |
| 向量检索 | ANN-Benchmarks, VectorDBBench | ANN 选型 |
| Embedding | MTEB, C-MTEB | Embedding 选型 |

---

## 建议的读法

1. **按业务找**：左边 Top 10 找到你最接近的业务
2. **按访问模式反查**：如果你业务不像任何一个典型，用分类框架 Axis 1 判断该走哪种栈
3. **组件映射**：从决策矩阵看你要哪些页深读
4. **跑起来**：Benchmark / Demo 索引里挑一个动手

---

## 相关

- [BI on Lake](bi-on-lake.md) · [RAG on Lake](rag-on-lake.md) · [Real-time Lakehouse](real-time-lakehouse.md) · [多模检索流水线](multimodal-search-pipeline.md)
- [推荐系统场景](recommender-systems.md) · [Agentic 工作流](agentic-workflows.md)
- [按角色入门](../roles/index.md) — 不同角色的优先阅读清单

## 延伸阅读

- *Data Mesh* (Zhamak Dehghani) — 按业务域组织数据的观点
- *The AI Engineering Handbook* (Chip Huyen) — 现代 AI 业务场景综述
- Databricks / Snowflake 的业务场景 "Solution Accelerator" 系列博客
- Netflix / Uber / Pinterest 各自的 Engineering Blog
