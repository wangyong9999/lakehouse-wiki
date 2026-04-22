---
title: 容量规划 · 集群规模 + GPU + 向量库 + LLM
type: reference
depth: 资深
level: A
last_reviewed: 2026-04-21
applies_to: 2024-2026 云 + 自建集群容量规划 · 含 AI 负载
tags: [ops, capacity, sizing, resource, gpu-capacity, llm-capacity]
aliases: [Sizing, Resource Planning]
related: [cost-optimization, performance-tuning, tco-model, gpu-scheduling]
status: stable
---

!!! warning "章节分工声明"
    - **本页**：湖仓 + AI 生产的**容量估算方法**
    - **GPU 调度机制**（MIG / 多租户 / topology-aware）→ [ml-infra/gpu-scheduling](../ml-infra/gpu-scheduling.md)
    - **LLM 推理性能**（TTFT / Tokens/sec / 并发）→ [ai-workloads/llm-inference](../ai-workloads/llm-inference.md)
    - **成本优化**细节 → [cost-optimization](cost-optimization.md)

# 容量规划

!!! tip "一句话定位"
    **"要多少机器 / 磁盘 / 内存 / 网络"的工程估算方法**。核心原则：**按业务规模线性外推 + 预留 30-50% buffer + 持续观测调整**。不要靠拍脑袋。

!!! abstract "TL;DR"
    - **规划流程**：业务量 → 数据量 → 存储 → 计算 → 网络 → Buffer
    - **关键经验值**：Parquet 压缩率 10:1 · 每 core ~ 100MB/s Parquet scan · 单节点典型 Worker 32-64 core
    - **Buffer 公式**：预留 30% 日常 + 50% 峰值 + 年 50% 增长
    - **五个必估**：存储 · 计算 · 网络 · 元数据 DB · 备份

!!! warning "数值适用前提 · 仅作粗估"
    本页出现的经验数字（压缩率 / 吞吐 / QPS / 延迟 / 系数）依赖：
    - **Workload 前提**：批 ETL / 交互查询 / 流式 / AI 负载各不同
    - **硬件前提**：H100 / A100 / NVMe / 云 instance family · 不同代差显著
    - **规模前提**：GB 级到 PB 级 · 非线性段常见
    - **数据形状**：列式 vs 行式 · 字段宽度 · 压缩友好度
    
    所有数字**仅作量级参考**（±2-5× 常见）· **Sizing 决策必须自家压测校准** · 不可直接套用工程常量。数字来源参考 [benchmarks](../benchmarks.md)。

## 1. 规划流程（一张图）

```
业务指标
  事件 QPS · 用户数 · 查询 QPS · 数据保留
    ↓
数据量估算
  每日新增 · 总保留量 · 压缩率
    ↓
存储规划
  主数据 + 副本 + 历史 + 备份
    ↓
计算规划
  Peak Load · 吞吐 · Worker 数 · 并行度
    ↓
网络 / 元数据 / 备份
    ↓
加 Buffer（30-50%）
    ↓
成本估算 → 审批 → 监控迭代
```

## 2. 存储规划

### 数据量估算

```
日增 = 事件 QPS × 平均事件大小 × 86400 秒
年增 = 日增 × 365
总存储 = 年增 × 保留年数 × (1 + 副本系数)
压缩后 = 总存储 / 压缩率
```

### 经验系数

| 格式 / 场景 | 压缩率 |
|---|---|
| JSON → Parquet (ZSTD) | 8-15× |
| CSV → Parquet (ZSTD) | 5-10× |
| 日志 → Parquet | 10-20× |
| 图像（JPEG）→ 已压缩 | ~1×（二次压缩无效）|
| 向量 float32 → IVF-PQ | 4-8×（量化）|

### 示例 · 电商订单入湖

```
业务：100M DAU · 平均 10 events/day · 每 event 1KB
   ↓
日增 = 100M × 10 × 1KB = 1 TB/day
年增 = 365 TB
Parquet 压缩 (8×) = 45 TB
5 年保留 = 225 TB
副本（S3 本身 3 副本，对象存储透明） = 225 TB
+ 备份（cross-region） = +225 TB
→ 总 ~ 450 TB

对象存储成本（S3 Standard $0.023/GB/月）:
450 TB × $23/TB × 12 ≈ $124k/年
```

### 分层存储降本

| 热度 | S3 类 | 节省 |
|---|---|---|
| 热（近 30 天） | Standard | - |
| 温（30-180 天） | S3 IA | 45% |
| 冷（180 天+） | Glacier Deep | 95% |

典型配置：
```yaml
# S3 Lifecycle
transitions:
  - days: 30
    storage: STANDARD_IA
  - days: 180
    storage: GLACIER_DEEP
```

## 3. 计算规划

### 批 ETL（Spark）

```
ETL 工作负载 = 日数据量 / 可用窗口
             = 1 TB / 4 hours
             = 250 GB/hour
             ≈ 70 MB/s

Spark Executor 吞吐 ~ 100 MB/s
→ 需 ~ 2-5 Executor 保底（加 buffer 后 5-10）
```

### 交互查询（Trino）

```
业务指标：200 QPS 仪表盘 + 50 QPS 探索
平均查询扫 500 MB、p95 2s

Peak 吞吐 = 250 QPS × 500 MB × (1/2s) = 62 GB/s scan

单 Worker scan ~ 500 MB/s
→ Worker 数 ≈ 130 ... 这是 Peak，平均 30-50 Worker 够用
+ Buffer 50% = 50-75 Worker
```

### 流处理（Flink）

```
业务：10k events/s
平均 event 1KB + state / event 5KB

Flink TM 吞吐 ~ 30k events/s / slot
→ 1 TM × 4 slot 够用（简单 stateless）

有状态：
→ State 总量 = 1亿 key × 5KB = 500GB → RocksDB
→ 至少 3 TM（HA） × 64GB 内存
```

## 4. 向量库规划

### 内存估算

```
向量 × 维度 × 4 bytes (float32)
+ HNSW 图（M=32）× 8 bytes × 2
= 每向量 ~ dim × 4 + 500 bytes

1 亿向量 × 768 维 = 300 GB 向量 + 50 GB 图 = 350 GB
→ 需至少 400GB 内存节点 或 分布式或量化
```

### 量化后

- INT8：~ 1/4 → 80GB
- IVF-PQ：~ 1/16 → 25GB
- Binary：~ 1/32 → 12GB

## 5. 元数据 DB 规划

### Iceberg Catalog (Postgres)

```
每表平均 metadata 行数 ~ 几 KB
10k tables × few KB = 几十 MB
Audit log: 100 QPS × 1KB × 86400 = 8 GB/day

→ Postgres RDS db.r5.large + 500GB 存储起步
→ 100k+ tables 要上 HA + 读副本
```

### Hive Metastore（老系统）

- 百万分区 → HMS 性能崩
- 建议 < 10 万分区 / 实例
- **尽快迁 Iceberg REST Catalog**

## 6. 网络规划

### 跨 AZ / 跨 Region

- **单 AZ**：几乎零成本
- **跨 AZ**：$0.01-0.02/GB
- **跨 Region**：$0.02-0.09/GB
- **出云**：$0.05-0.09/GB（AWS）

### 典型事故

- 开发把 Trino 放 us-east-1，S3 数据在 us-west-2 → 跨 region 费用爆
- 正解：**Trino / Spark 和 S3 在同一 region**

### 网络带宽规划

```
Scan 吞吐 × 并行度 = 所需网络
1 GB/s 总 scan × 10 Worker → 100 MB/s / Worker（够用）
```

注意 **ENI / NIC 限制**：EC2 m5.4xlarge 有 10 Gbps，m5.16xlarge 有 25 Gbps。

## 7. Buffer 策略

### 三种 Buffer

| 类型 | 比例 | 理由 |
|---|---|---|
| **日常波动** | +30% | 日周末峰值 |
| **年度增长** | +50% | 业务增长预期 |
| **突发事件** | +50% (应急) | 大促 / 活动 / 故障 |

**总结**：按平均估算后 **至少 × 1.8** 做规划。

### 弹性 vs 预留

**弹性**：Spark on K8s / Flink 自动扩缩、按需拉起；优于预留资源 30-50%。

**预留**：Trino Coordinator / Flink JobManager / 向量库 / 数据库 必须固定。

## 8. 监控与调整

### 关键指标

| 指标 | 含义 | 阈值 |
|---|---|---|
| **CPU 利用率** | Worker / Executor | 平均 40-60%，峰值 80% |
| **内存利用** | - | < 80% |
| **磁盘利用** | 本地 SSD / state | < 75% |
| **S3 4xx / 5xx** | 限流 / 权限 | < 0.1% |
| **HMS / Catalog QPS** | 热点 | 看 p99 |
| **网络流量** | 跨 region | 看月账单 |

### 扩容触发

- 持续 7 天 CPU > 70% → 扩 20-30%
- 持续 p99 延迟上涨 20% → 查是数据增长还是扩容
- 大促前 → 预留 2× 资源

## 9. 实战 Sizing 例子

### 例 1 · 中型 Lakehouse（50 TB 数据，10 分析师）

| 组件 | 规格 |
|---|---|
| S3 存储 | 50 TB × 3（年保留 + 归档） = 150 TB |
| Trino | 3 Worker × r5.4xlarge (16c / 128GB) |
| Spark on K8s | 按 Job 弹性扩 |
| HMS | db.r5.large Postgres |
| Metadata | Glue / REST Catalog |
| **月成本** | ~$5k |

### 例 2 · 大型湖仓（5 PB，100+ 分析师）

| 组件 | 规格 |
|---|---|
| S3 存储 | 5 PB × 分层（Standard 10% + IA 30% + Deep 60%） |
| Trino | 50 Worker × c5.9xlarge (36c / 72GB) |
| Spark | 500-2000 Executor 弹性 |
| Flink | 10 TM × r5.2xlarge 维持流 |
| Iceberg REST Catalog | 3 副本 × c5.2xlarge |
| Postgres 元数据 | db.r5.4xlarge + Multi-AZ |
| **月成本** | ~$80k-150k + 团队 |

### 例 3 · 向量检索（10M 向量 × 768 维，100 QPS）

| 组件 | 规格 |
|---|---|
| Milvus / LanceDB | 3 node × r5.4xlarge (128GB) |
| 向量总内存 | 10M × 768 × 4 = 30GB + 图 50GB = 80GB × 3 副本 |
| QPS 目标 | 100 × 3 = 300 全局 |
| **月成本** | ~$3k |

## 9.5 GPU 容量规划（AI 时代必需）

### GPU 池分层

| 负载 | 卡型示例 | 容量特点 |
|---|---|---|
| **在线推理 P0** | H100 / H200 / B200 | 独占 · SLO 严 · 24/7 |
| **LLM Serving** | H100 80GB / H200 141GB | 显存决定 · 越大支持的模型和 context 越长 |
| **训练**（大模型）| B200 / GB200 NVL72 | 多卡 gang · 可抢占 + checkpoint |
| **微调 / RLHF** | A100 / H100 | 中等规模 · 可 spot |
| **探索 / Notebook** | A10 / L4 · MIG 切分 | 共享 · 弹性 |

### LLM 推理容量估算

```
单卡 LLM 吞吐（H100 · Llama-3.3-70B AWQ 量化）`[来源未验证 · 示意性]`:
- 短 prompt（<1k tokens）：~100 tokens/sec
- 长 context（8k+）：50-80 tokens/sec
- 并发 batch：10-50 requests 同时

容量估算示例:
业务 QPS = 10 req/s · avg tokens = 500
→ 需要 tokens/sec = 5000
→ 单卡 100 tokens/sec × N 卡 = 5000
→ N = 50 卡（高峰）
```

**工具**：vLLM · TGI · SGLang benchmark（详见 [ai-workloads/llm-inference](../ai-workloads/llm-inference.md) §6 性能数字）。

### 向量库容量估算

```
向量库存储 = N 向量 × 维度 × 4 bytes × (1 + 索引 overhead 0.3-0.5)

示例：
- 1 亿向量 × 1024 维 × 4B = 400GB 原始
- HNSW 索引 overhead × 1.4 = 560GB 总存储
- 单节点 SSD 4TB 够存 · 内存需要 400GB（索引 hot path）
- 多节点：3 节点 × 200GB 内存 = 够覆盖
```

**QPS 估算**：
- HNSW on NVMe：单机 1000-5000 QPS `[来源未验证]`
- 多节点分片：线性扩展

详见 [retrieval/hnsw](../retrieval/hnsw.md) · [retrieval/ivf-pq](../retrieval/ivf-pq.md) 机制 canonical。

### 典型 AI 推理 SLA 对应容量

| SLA | GPU / 向量库 |
|---|---|
| 单模型 · 1000 QPS · p99 < 100ms | 2-4 H100 + 3 节点向量库 |
| RAG · 100 QPS · p95 < 1.5s | 1-2 H100 LLM + 2 节点向量库 + 1 节点 rerank |
| 大规模推荐召回 · 10k QPS | 自研 ANN + 10-20 节点（Pinterest 级规模）|

## 10. 陷阱

- **只按当前估算、不考虑增长**：3 个月后再扩容 → 数据迁移痛苦
- **Buffer 太少**：大促 / 活动 / 故障期间扛不住
- **Spark 给太大 Executor**：32GB + 16 core 不如 8GB × 2 core × 多个（调度更好）
- **HMS 单机**：百万分区后炸；早期就上 HA
- **跨 region 不注意**：每月几万美元网络费偷走利润
- **元数据 DB 没备份**：Catalog 挂了等于所有表找不到
- **向量库单机扛全量**：1 个节点挂 = 全丢，至少 3 副本

## 11. 延伸阅读

- [TCO 模型](tco-model.md)
- [成本优化](cost-optimization.md) · [性能调优](performance-tuning.md)
- *Site Reliability Engineering*（Google SRE 书）
- AWS / GCP / Azure Well-Architected Framework

## 相关

- [成本优化](cost-optimization.md) · [TCO 模型](tco-model.md) · [灾难恢复](disaster-recovery.md)
- [多租户](multi-tenancy.md) · [性能调优](performance-tuning.md)
