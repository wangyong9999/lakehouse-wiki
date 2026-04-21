---
title: TCO 模型 · 自建 vs 云 vs SaaS · 含 AI 场景
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: 2024-2026 云 + 商业产品定价 · 含 AI / LLM 场景
tags: [ops, cost, tco, economics, ai-tco]
aliases: [TCO, Total Cost of Ownership]
related: [cost-optimization, capacity-planning, data-systems-evolution]
status: stable
---

# TCO 模型 · 总体成本分析

!!! tip "一句话理解"
    **"便宜 vs 贵"往往是伪命题**——任何方案的真实成本 = **存储 + 计算 + 人力 + 工具 + 风险 + 机会**。Snowflake 账单 $100k 可能比自建湖仓 + 3 工程师更便宜；某些规模下正相反。**看 TCO，不看 sticker price**。

!!! abstract "TL;DR"
    - **三类方案**：自建 OSS · 商业 SaaS · 云厂商托管
    - **六项成本**：**存储 · 计算 · 软件许可 · 人力 · 工具链 · 机会成本**
    - **拐点规律**：数据规模 < 10 TB SaaS 便宜 · 100 TB+ 自建划算 · 1 PB+ 必自建
    - **最大隐形成本**：**人力**（1 个高级工程师/年 $200k+）
    - **最大隐形收益**：**开放性**（数据可出、引擎可换）

## 1. TCO 的六项构成

### 1 · 存储成本

| 存储 | 单价（$/GB/月）| 备注 |
|---|---|---|
| S3 Standard | 0.023 | 基础 |
| S3 IA | 0.0125 | 少访问 |
| S3 Glacier Deep | 0.00099 | 归档 |
| Snowflake 存储 | 0.040 | 含管理 |
| BigQuery 主动 | 0.020 | 超 90d 降 0.010 |
| Databricks Delta | 存 S3 + 管理费 | |
| 自建 HDFS | 硬件 + 机房 | 规模越大越便宜 |

**经验**：PB 级数据在 S3 Standard 的存储费 $23k/月，一年 $276k。自建 HDFS 可能 $150k/年（含硬件折旧）。

### 2 · 计算成本

这是最大变量，因工作负载而异。

**Snowflake**：按 Warehouse × 运行秒计费。
- X-Small: $2/小时 · XL: $32/小时 · 6XL: $512/小时
- 典型公司月 $10k-1M+

**BigQuery**：按扫描字节或 slots。
- On-demand: $6.25/TB 扫描
- Edition: slots 包月

**Databricks**：DBU × compute 时长。

**Trino / Spark 自建**：EC2 / K8s 成本。
- m5.xlarge: $0.192/小时 × 100 台 × 24h × 30 = ~$14k/月

### 3 · 软件许可

| 产品 | 定价 | 规模对应 |
|---|---|---|
| **Snowflake** | 合并到计算 | |
| **Databricks** | DBU + 订阅 | 企业常见 $100k-5M/年 |
| **Tecton** | $50k-500k+/年 | 随规模 |
| **Starburst** | $10k-500k+/年 | |
| **Monte Carlo** | $50k-300k+/年 | 数据质量监控 |
| **Unity Catalog OSS** | 免费 | 但治理能力弱于商业版 |
| **Apache OSS (Iceberg / Paimon / Trino)** | 免费 | 但要自运维 |

### 4 · 人力成本（最容易低估）

- **高级数据工程师**：北京 $150k-300k/年 · 硅谷 $250k-500k+/年
- **SRE**：$150k-300k/年
- **MLE / 平台工程师**：$200k-500k+/年

**自建 Lakehouse 平台**通常需要：
- 2-5 个平台工程师
- 1-2 个 SRE
- 1 个治理 / 合规

**年成本 $800k-2M**——超过很多中型公司 Snowflake 账单。

### 5 · 工具链成本

- Airflow / Dagster：自建成本 1-2 工程师 · SaaS 产品 $50k/年
- DataHub / Atlan / Collibra：商业 $50k-500k+/年
- MLflow：自建成本低 · Weights & Biases $50k+
- Fivetran：$60k-500k/年
- Monitoring (Datadog / Grafana) $30k-500k/年

### 6 · 机会成本

- 数据锁定：切换 Snowflake → 其他栈可能 $500k+ 项目成本
- 创新速度：自建慢 3-6 个月上线新能力
- 人才招聘：OSS 人才好招 · 商业栈专家难招

## 2. 三类方案 · 成本曲线

```
月成本 ($)
  │
2M├─────────────────────── 商业 SaaS (Snowflake)
  │                 ╱
1M├─────────────╱
  │         ╱      ╱────── 云厂商托管 (BigQuery)
  │     ╱      ╱
500k├─╱────╱
  │╱     ──────────── 开源自建 (Iceberg + 自运维)
  │───────
  └──────────────────────────── 数据量
     10TB  100TB  1PB  10PB
```

### 粗略拐点

| 数据量 | 最优方案 |
|---|---|
| < 1 TB | 单机 DuckDB + Postgres |
| 1-10 TB | **Snowflake / BigQuery**（省心）|
| 10-100 TB | 混合（湖 + 小数仓加速）|
| 100 TB-1 PB | **湖仓自建**（Iceberg + Trino） |
| > 1 PB | 必自建 |

**边界不是硬**——依团队成熟度 / 业务复杂度。

## 3. 真实案例对比

### 案例 A · 中型 SaaS 公司（数据 50 TB，5 分析师）

| 方案 | 月成本 |
|---|---|
| Snowflake + Fivetran + dbt Cloud + Hex | ~$25k |
| 自建 Iceberg + Trino + dbt CLI + Superset | ~$8k 基础 + 1 工程师 ($20k/月) = **$28k** |
| Databricks 一体 | ~$30k |

**结论**：50 TB 级自建**没有明显优势**，SaaS 省心得多。

### 案例 B · 大型互联网（数据 5 PB，50+ 数据工程师）

| 方案 | 年成本 |
|---|---|
| Snowflake 5 PB | > $10M/年（不现实） |
| Databricks + AWS | $5-8M/年 |
| 自建 Iceberg + Spark + Trino + Flink + ... | $3-5M/年（含 15-20 人团队） |

**结论**：大规模下**自建显著省**，但**前提是团队能力**。

### 案例 C · 初创（数据 500 GB，2 人）

| 方案 | 月成本 |
|---|---|
| Snowflake | $2k |
| BigQuery | $1.5k |
| DuckDB + Postgres + dbt Cloud | $500 |
| 自建 Iceberg | 不推荐（2 人搞不动） |

**结论**：小团队**别自建**。

## 4. 降本实战手段

### 存储层

- **分层**：热 / 温 / 冷分开（S3 Standard / IA / Glacier）
- **压缩**：ZSTD vs gzip vs snappy，ZSTD 压缩率好 + 速度 OK
- **Compaction**：小文件 → 大文件，管理元数据开销降
- **Expire Snapshot**：删旧 snapshot + orphan
- **Cross-region 减少**：数据留在单 region

### 计算层

- **Spot / Preemptible**：AWS Spot 省 70%
- **按查询 quota**：防吵闹邻居
- **查询缓存 / MV**：热查询走 MV
- **Auto-suspend**：Snowflake 的 warehouse 自动挂起
- **右合适规格**：Warehouse 别用 2XL 跑 X-Small 活

### 许可层

- **开源 + 商业混合**：核心开源、监控 / 治理买 SaaS
- **合并工具**：能用 dbt 不要再买 Matillion

### 人力层

- **自建只在 PB+ 规模**：否则买 SaaS
- **托管 + 开源混合**：Databricks + OSS 生态，既省心又可扩
- **统一平台工具**：别每个业务线搞一套

## 5. 典型 ROI 计算

### 从 Snowflake 迁到湖仓（1 PB 规模）

**现状**：
- Snowflake $1M/年
- 1 个平台工程师 + Fivetran 1 个 ETL 工程师

**迁移后**：
- S3 存储：$276k/年
- EC2 Trino + Spark：$300k/年
- 团队扩充到 4 人平台 + 2 SRE：$1M/年
- Monitoring + Catalog：$100k/年
- **总计 $1.676M/年**

**结论**：1 PB 迁了**不省钱**，除非：
- 数据能涨到 5+ PB（Snowflake 会线性涨而自建不）
- 引擎需要多样性（Snowflake 不够用时）
- 数据锁定风险变大

**"迁移"本身成本** $500k-2M（一次性）也要算。

### 从 BigQuery 迁到湖仓（100 TB 规模）

典型**省不了多少**，但获得：
- Iceberg 开放（未来可换引擎）
- 可运行 OSS 工具（Trino / DuckDB / Spark）
- AI 能力（向量库 + ML）不受限

## 6. 决策流程

```
1. 数据规模评估（< 10TB / 10-100TB / 100TB-1PB / 1PB+）
   ↓
2. 团队能力评估（< 3 工程师 / 3-10 / 10+）
   ↓
3. 业务复杂度（纯 BI / BI+AI / 多模 / 合规严）
   ↓
4. 预算范围（月 / 季度）
   ↓
5. 锁定容忍度（长期想不被锁）
   ↓
计算 3 年 TCO：
  方案 A: sticker + infra + 人力 + 工具 + 风险 = TCO_A
  方案 B: 同上 = TCO_B
比较 + 决策
```

### 决策矩阵速查

| 现状 | 推荐 |
|---|---|
| 小团队 < 10TB 快启动 | **Snowflake / BigQuery / DuckDB** |
| 中团队 TB 级 + 想控锁定 | **湖仓 + Trino + 少量 SaaS** |
| 大团队 PB 级 | **自建湖仓** |
| 合规严（金融 / 医疗）| **混合（自建 + 商业治理）** |
| AI 重型 | **Databricks 或自建湖 + 向量库** |
| 特定云厂绑定（AWS 深度用户）| **EMR / Glue / Redshift Spectrum 混合** |

## 6.5 AI 场景 TCO（2024-2026 关键决策）

### LLM API vs 自托管 GPU · Break-even 分析

这是 2024-2026 最常问的成本决策。

**参数设定** `[来源未验证 · 价格快速变化 · 以官方为准]`：
- OpenAI GPT-4o：$5/1M input · $15/1M output
- Anthropic Claude Sonnet：$3/1M input · $15/1M output  
- Mistral Large：$2/1M input · $6/1M output
- 自托管 Llama-3.3-70B on H100：~$4/hour × 多卡

**Break-even 公式**：

```
月 tokens × (API 价 - 自托管 token 成本) vs 自托管 GPU 固定月成本

示例:
月 output tokens = 1B
GPT-4o 成本 = 1B × $15/1M = $15,000/月
自托管 Llama-3.3-70B · 4 × H100 · 月 $4 × 720 × 4 = $11,520/月（纯硬件）
+ 工程师 + 运维 ≈ $25,000/月总成本

→ 1B token/月场景 · GPT-4o API 反而便宜（$15k vs $25k）
→ 10B token/月场景 · 自托管胜（$150k vs $25k）
```

**决策矩阵**：

| 月 Output Tokens | 推荐方案 |
|---|---|
| < 500M | **API 为主**（工程成本 > 硬件成本节省）|
| 500M - 5B | **混合**（简单 query 自托管 Mistral / Llama · 复杂 query 用 API）|
| > 5B | **自托管为主**（但保留 API 兜底大峰值）|
| 合规要求"数据不出栈" | **自托管必然**（不看成本）|

### Vector DB 商业 vs 自建 TCO

| 方案 | 月成本估算 `[示例 · 以官方报价为准]` | 适合 |
|---|---|---|
| **Pinecone**（商业托管）| $0.096/hour × pod × N · 中等规模月 $1k-10k | 快速启动 · 不想运维 |
| **Zilliz Cloud**（Milvus 托管）| 类似 Pinecone 定价 | 已用 Milvus 想托管 |
| **自建 Milvus on K8s** | 3 节点 · 64GB · $500/月硬件 + 工程师 | 有 K8s 能力 · 中等规模 |
| **LanceDB 嵌入式** | 对象存储费 · 无独立服务成本 | 嵌入应用 / Lakehouse |
| **湖上向量**（Iceberg Puffin / Lance）| 复用湖仓基础设施 · 几乎零增量 | 已有湖仓栈 |

**AI 原生向量场景 TCO**：
- 小规模（< 1000 万向量）· **LanceDB 嵌入式**或 Pinecone Starter
- 中等规模（亿级）· **自建 Milvus** 或 Zilliz Cloud
- 超大规模（十亿+）· **自建 + 深度优化**（见 Pinterest / 阿里案例）

### ML 平台 TCO

| 方案 | 月成本典型 | 适合 |
|---|---|---|
| **Databricks Mosaic AI** | $50k-500k+（含计算）| BI + AI 一体化 · 高端客户 |
| **Sagemaker / Vertex AI** | 用量付费 · 变数大 | 云原生 · 中等规模 |
| **MLflow + 自建 K8s + Ray** | 工程师 2-5 人 + $10k-50k 硬件 | 开源自主 |
| **Weights & Biases + 外部计算** | $500-5k · SaaS | 小团队 experiment tracking |

## 7. 陷阱

- **只看 sticker price**：人力和机会成本才是大头
- **低估人力**：自建 PB 级湖仓**少于 5 人搞不定**
- **低估迁移成本**："换个栈半年就好"→ 通常 1-2 年
- **为了省 20% 换栈**：风险 + 人力成本远超收益
- **Snowflake Credit 透支**：不 Auto-suspend → 账单爆
- **Spot 实例用在关键**：Spot 中断导致 ETL 失败
- **过度优化**：小团队纠结 1% 成本，忘了业务价值
- **不算**：凭感觉决定，半年后后悔

## 8. 延伸阅读

- **[Uber: Cost-Efficient Big Data Platform](https://www.uber.com/blog/cost-efficiency-big-data/)**
- **[Pinterest Data Platform cost study](https://medium.com/pinterest-engineering)**
- **[Andreessen Horowitz: "The Emerging Data & AI Infrastructure Stack"](https://a16z.com/)**
- **[Benn Stancil: Substack](https://benn.substack.com/)** —— 数据栈经济学
- **[Cost of Snowflake vs BigQuery vs Redshift (2024)](https://fivetran.com/resources/warehouse-benchmark)**
- *Principles of Data Lake Economics*（社区白皮书集合）

## 相关

- [成本优化](cost-optimization.md) —— 具体技术手段
- [合规](compliance.md) · [数据治理](data-governance.md)
- [三代数据系统演进史](../frontier/data-systems-evolution.md)
