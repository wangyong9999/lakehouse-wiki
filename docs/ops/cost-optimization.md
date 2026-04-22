---
title: 成本优化 · FinOps
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: FinOps Framework 2025 · Kubecost · CloudHealth · 2024-2026 云 + 商业产品定价
tags: [ops, cost, finops, gpu-cost, llm-token-cost]
aliases: [Cost Optimization, FinOps]
related: [performance-tuning, compaction, observability, tco-model, capacity-planning, gpu-scheduling, llm-gateway]
systems: [kubecost, cloudhealth, aws-cost-explorer]
status: stable
---

!!! warning "章节分工声明"
    - **本页**：湖仓 + AI 的**五线成本控制**（存储 / 计算 / API / 出口 / GPU+LLM） + **FinOps 框架**
    - **GPU 调度 / FinOps for ML 细节** → [ml-infra/gpu-scheduling](../ml-infra/gpu-scheduling.md) §FinOps canonical
    - **LLM token 成本 · Gateway 节省**（Prompt Cache / Semantic Cache）→ [ai-workloads/llm-gateway](../ai-workloads/llm-gateway.md) · [ai-workloads/semantic-cache](../ai-workloads/semantic-cache.md)
    - **战略 TCO 决策**（自建 vs 云 vs SaaS）→ [tco-model](tco-model.md)
    - 本页讲**工程层面的成本控制实操** · 指向各 canonical 深度

# 成本优化

!!! tip "一句话理解"
    湖仓总成本 = **对象存储 + 计算 + API 调用 + 数据出口**。四项都要管。最大的隐藏成本是"**没用到的副本 + 没 compaction 的小文件 + 没归档的历史数据**"。

!!! warning "数值适用前提 · 仅作粗估"
    本页出现的成本占比 / GPU $/hr / token 单价 / 节省率依赖：
    - **厂商 / 区域前提**：AWS us-east-1 vs 华东 · 价格相差数倍
    - **合同 / 折扣前提**：list price vs 大客户 commitment
    - **负载形状**：批 vs 在线 · 稳态 vs 突发 · 差异显著
    - **时效前提**：LLM token / GPU 价格 6 月变化显著
    
    所有数字 **仅作量级参考**（±2-5× 常见）· 决策 **必须以自家实际账单为准** · 不可直接套用。价格变化快 · 本页列出的 LLM / GPU 单价参考 [benchmarks](../benchmarks.md) 或以厂商官网为准。

## 成本结构 · 五线划分（2024-2026 AI 时代）

典型云上湖仓 + AI 一个月账单 · 占比 `[量级参考 · 依负载差异大]`：

| 类别 | 占比 | 主要消耗 |
| --- | --- | --- |
| **对象存储** | 15–30% | 冷/热/多副本 |
| **计算**（CPU）| 30–50% | Spark / Flink / Trino / 向量检索 |
| **GPU**（2024-2026 主要新增）| 5–30% | ML 训练 / LLM 推理 / embedding 生成 |
| **LLM Token / API 调用** | 0–25% | OpenAI / Anthropic / 自托管 LLM 推理 token |
| **API / 数据出口** | 5–15% | S3 `LIST/GET/PUT` · 跨区 / 跨云 traffic |

**AI 时代的三个关键变化**（对比 2020-2023 纯湖仓）：
- **GPU 成本单独一大类**（不能归到"计算"里忽略）
- **LLM Token 成本可能超 20%**（尤其 RAG / Agent 重度场景）
- **Embedding 生成 GPU-hour** 是隐性大头

## 八条实操建议

### 1. 分层存储

- 热数据：S3 Standard
- 近线：S3 Infrequent Access（30 天以上不常访问）
- 冷数据 / 归档：S3 Glacier（合规存档）
- 规则用 **生命周期策略** 自动迁移，不手动搬

### 2. Snapshot 过期 + 孤儿文件清理

```sql
CALL system.expire_snapshots('db.t', TIMESTAMP '2026-03-01');
CALL system.remove_orphan_files('db.t', older_than => TIMESTAMP '2026-03-01');
```

不做这件事，**表占用会线性膨胀**，1 年 10 倍不稀奇。

### 3. Compaction 认真做

小文件让**每 GB 扫描成本翻倍**。参考 [Compaction](../lakehouse/compaction.md)。

### 4. 物化视图 & 加速副本的 ROI

每个 MV / StarRocks 副本都有成本。**按命中率裁剪**：

- 命中率 < 5% 的删
- 高命中的反而可以更激进地预计算

### 5. Compression Codec

- Parquet 默认 Snappy（快但压缩比弱）→ **Zstd level 3** 压缩比提升 20–30%，CPU 代价可接受
- Delete file 也记得压缩

### 6. 跨区 / 跨云慎配

S3 跨 region 的数据出口费贵。如果团队跨多云，用 **S3 对等 / 专用连接** 替代公网出口。

### 7. 列出"最贵 Top 10"

- 最贵的表（存储）
- 最贵的查询（计算 + IO）
- 最贵的作业（GPU·h / CPU·h）

每月 review 一次，Top 10 大概率藏着一个"**被遗忘的批作业 / 失控的索引重建**"。

### 8. 向量索引成本单独建账

GPU·h（embedding 生成）+ 索引内存 / SSD（索引存储）在快速增长的 AI 负载里常常被低估：

- HNSW 索引 = 原向量 × 1.2–1.5 内存
- 百亿向量 embedding 批量回填一次可能是数千 GPU·h

### 9. GPU 成本优化（AI 时代新增 · 详见 [ml-infra/gpu-scheduling §FinOps](../ml-infra/gpu-scheduling.md)）

**GPU 是 AI 时代最贵成本之一**·核心优化：

- **多租户 GPU 共享**（MIG · MPS · time-slicing · fractional GPU）
- **Spot / Preemptible 实例**训练（配 Elastic Training + checkpoint）
- **AWS Capacity Blocks for ML · GCP DWS**（GPU 预留市场 · 2024+）
- **GPU 利用率**目标 > 60%（低于说明瓶颈在数据加载 / 代码）
- **Cost attribution**（per-team / per-model / per-job tag）· Kubecost / 厂商 billing API
- **推理 vs 训练分池**（独占推理 · spot 训练）

### 10. LLM Token 成本优化（2024-2026 新增）

LLM 应用成本结构 · 各家厂商定价 `[来源未验证 · 快速变化 · 以官方为准]`：
- OpenAI GPT-4 约 $30/1M input tokens · $60/1M output tokens
- Anthropic Claude Sonnet 约 $3/1M input · $15/1M output
- 自托管 Llama 3 70B · 主要 GPU 成本

**优化杠杆**（详见 [ai-workloads/llm-gateway](../ai-workloads/llm-gateway.md)）：

1. **Prompt Caching**（Anthropic GA 2024-08 · OpenAI 自动）
   - 缓存相同前缀 · 命中 -50% 到 -90% 输入 token 成本
   - 详见 [ai-workloads/semantic-cache §Prompt Caching](../ai-workloads/semantic-cache.md)

2. **Semantic Cache**（应用层 · 语义相近 query 跳过 LLM）
   - 高频重复 query 场景节省 30%+ `[来源未验证]`

3. **模型路由**（LLM Gateway 按 query 复杂度路由到不同 tier）
   - 简单 query 用 Mistral 7B / Haiku · 复杂 query 用 GPT-4 / Sonnet

4. **Batching + Streaming**
   - 批 LLM 调用 · 减少 per-call overhead
   - Streaming 输出 · 提升 UX 但 token 数不变

5. **Prompt 优化**
   - 更短 system prompt（节省每次 input）
   - Few-shot 只在必要时加
   - Structured output 减少冗长

## FinOps 框架 · 2024-2026 成熟模式

**FinOps**（Financial Operations）· 2024-2026 成为工业标准。[FinOps Foundation](https://www.finops.org/) 定义的 **6 能力**：

| 能力 | 工程实施 |
|---|---|
| **可见性**（Visibility）| Dashboard · 按业务 / 团队 / 产品归因 |
| **使用优化**（Rate Optimization）| Reserved / Savings Plan / Spot |
| **用量优化**（Usage Optimization）| Right-sizing · 关机 · compaction |
| **分摊**（Allocation）| Tag 体系 · chargeback / showback |
| **预算**（Budget）| 月预算 + 告警 + 超支熔断 |
| **文化**（Culture）| FinOps 团队 · 工程师成本意识 |

### FinOps 工具生态

| 工具 | 定位 | 适合 |
|---|---|---|
| **Kubecost**（OSS + 商业）| K8s 原生成本归因 | K8s 重用户 |
| **CloudHealth**（VMware）| 多云成本管理 | 大企业多云 |
| **AWS Cost Explorer + Anomaly Detection** | AWS 原生 | AWS 主 |
| **Databricks Cost Management** | Databricks 内置 | Databricks 客户 |
| **Snowflake Resource Monitor** | Snowflake 内置 | Snowflake 客户 |
| **自建**（Grafana + 厂商 billing API）| 灵活定制 | 有工程能力 |

## 定期 review 清单

每季度至少一次：

- [ ] 过期 Snapshot / 孤儿文件回收是否在跑
- [ ] Top 10 大表 / 贵查询变化
- [ ] MV / 加速副本命中率
- [ ] 存储分层策略是否仍合理
- [ ] Compaction 作业健康度
- [ ] GPU / 向量相关开销
- [ ] 是否有 "阴间副本"（某团队一年前建的 debug 表）

## 陷阱

- **"存储便宜，算力贵" 的误区**：小文件问题让存储和算力**同时贵**
- **盲目开 caching / 加速副本**：没数据支持就是猜
- **把 Snapshot 保留窗拉很长**：90 天审计窗 = 90 天的重复文件
- **不关注出口**：开发者无感地从 S3 往外导 TB 级数据

## 相关

- [Compaction](../lakehouse/compaction.md)
- [性能调优](performance-tuning.md)
- [可观测性](observability.md)

## 延伸阅读

- *FinOps for Data Teams* —— a16z / Gradient Flow 等博客
- Databricks / Snowflake 官方 Cost Optimization 文档
