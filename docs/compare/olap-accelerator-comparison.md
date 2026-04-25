---
title: OLAP 加速副本横比 · StarRocks / ClickHouse / Doris / Druid / Pinot
applies_to: "2024-2026 主流"
type: comparison
level: B
depth: 进阶
prerequisites: [lake-table]
tags: [comparison, olap, starrocks, clickhouse, doris, druid, pinot, accelerator]
related: [bi-on-lake, real-time-lakehouse, compute-engines, lake-table]
status: stable
last_reviewed: 2026-04-18
---

# OLAP 加速副本横比

!!! tip "一句话回答"
    仪表盘 **p95 < 1s**、高并发场景，Iceberg + Trino 往往不够；需要**列存 OLAP 加速副本**。**StarRocks** 在"湖上加速"维度生态最成熟，**ClickHouse** 单表极速聚合无敌，**Druid / Pinot** 做实时大屏专业，**Doris** 是国产替代，**Trino** 本身在不用副本时就够用则更简单。

!!! abstract "TL;DR"
    - **用不用副本先判断**：Trino 能打 p95 < 3s、并发 < 50 QPS 就别自找麻烦
    - **StarRocks** = 湖联邦 + 物化视图在四家里最成熟 · BI 场景常见加速副本选项（与 Doris 生态接近、互有侧重）
    - **ClickHouse** = 单表极致 · 日志 / 时序 / 大宽表 · Join 弱
    - **Apache Doris** = StarRocks 的国产开源伙伴 · 兼容 MySQL 协议
    - **Apache Druid** = 实时大屏专业 · Segment 模型 · 运维重
    - **Apache Pinot** = LinkedIn 系 · 实时 OLAP · 多租户强
    - 副本**永远不是真相源**——挂了要能从湖重建

## 场景画像：什么时候需要 OLAP 加速副本

### Trino + Iceberg 已经够用的场景

- 分析师即席查询（并发低，单次延迟 3-10s 可接受）
- 数据工程 / ETL 监控
- T+1 报表刷新

### 明显需要副本的场景

- **BI 大屏，p95 < 1s**，并发 > 100
- **OLAP 实时聚合**（秒级从 Kafka 刷新）
- **高并发 TopN / 精确去重**（COUNT DISTINCT）
- **用户面 Dashboard**（给外部客户看，对延迟敏感）

**经验法则**：如果业务方每天投诉"仪表盘太慢"，就是信号。

---

## 五大选型一览

| 方案 | 出身 | 开源 | 集群模式 | 湖表原生 | MySQL 协议 |
|---|---|---|---|---|---|
| **StarRocks** | 鼎石 → Linux Fdn | ✅ Apache 2.0 | 存算分离 | ✅ Iceberg/Hudi/Delta | ✅ |
| **Apache Doris** | 百度 → Apache | ✅ Apache 2.0 | 传统分布式 | ✅（通过 Multi-Catalog）| ✅ |
| **ClickHouse** | Yandex → ClickHouse Inc | ✅ Apache 2.0 | Shared-Nothing | ⚠️ 通过外表 | ❌（HTTP/native） |
| **Apache Druid** | Metamarkets → Apache | ✅ Apache 2.0 | Coord+Broker+Historical | ⚠️ 需要 ingest | ❌（HTTP） |
| **Apache Pinot** | LinkedIn → Apache | ✅ Apache 2.0 | Controller+Broker+Server | ⚠️ 需要 ingest | ❌（HTTP） |

---

## 1. StarRocks · 湖上加速首选

!!! example "适合"
    已经在湖（Iceberg / Hudi / Delta / Paimon），想做高性能 BI / 用户面 Dashboard。

### 核心特点

- **存算分离版 (v3.0+)**：弹性伸缩 + 成本友好
- **Multi-Catalog**：**直接读 Iceberg / Hudi / Delta 外表**，无需搬数据
- **物化视图**：
  - 同步 MV（写入即更新）
  - **异步增量 MV**（行业领先）
  - 自动查询改写（用户写原表 SQL 自动路由到 MV）
- **MySQL 协议**：BI 工具无缝接
- **向量化 + CBO + Runtime Filter**：性能成熟
- **Pipeline 执行引擎**：高并发不崩

### 两种使用模式

**模式 A · 纯加速层**（推荐）：
```
Iceberg (真相源)
  │ (增量 MV 自动同步)
  ↓
StarRocks 本地列存
  ↓
BI Dashboard
```

**模式 B · 联邦查询**（无副本）：
```
StarRocks 直接查 Iceberg 外表
适合: 灵活性优先、延迟可接受 1-3s
```

### 优劣

| 优 | 劣 |
|---|---|
| 湖联邦 + MV 组合最完整 | 欧美社区略弱于 ClickHouse |
| Join 比 ClickHouse 强很多 | 大规模部署学习曲线 |
| 异步增量 MV 自动路由 | Bitmap 精确去重内存开销大 |
| MySQL 协议、BI 友好 | 不适合单机 / 小数据 |

### Benchmark

- **SSB**（Star Schema Benchmark）大多数维度领先 ClickHouse
- **TPC-H 100**：与 Trino 接近，高并发下优势明显
- 参考：[StarRocks 官方 Benchmark](https://www.starrocks.io/blog/benchmarks)

---

## 2. ClickHouse · 单表极致聚合

!!! example "适合"
    日志分析、时序数据、大宽表聚合、少 Join 场景。

### 核心特点

- **MergeTree** 列存引擎，单机性能王者
- **向量化 + SIMD** 深度优化
- **Replication + Sharding** 分布式但 Join 弱
- **ReplacingMergeTree / AggregatingMergeTree** 为特定场景定制
- **原生 S3 支持**（不是真正的"湖表"，但可以读 Parquet）
- **LowCardinality** 列优化

### 典型部署

- 日志分析：OpenTelemetry / Vector → ClickHouse
- 用户行为分析：Snowplow 事件流
- 实时大屏：Kafka → ClickHouse 直接
- 时序数据：TSDB 替代（相比 Prometheus）

### 优劣

| 优 | 劣 |
|---|---|
| **单表聚合极速**（业界标杆）| Join 性能差（尤其 distributed join） |
| 简单部署、单机也强 | 分布式扩展复杂 |
| 丰富的聚合函数 | 没有原生湖表支持（靠外表） |
| HTTP / Native 协议 | **不支持 MySQL 协议**（BI 要 JDBC driver） |
| 社区全球最活跃 | 事务 / 更新能力弱 |

### 不适合

- 复杂多表 Join（星型 Schema 场景）
- 高频更新（UPSERT）
- 严格 ACID 的分析

---

## 3. Apache Doris · 国产 OLAP

!!! example "适合"
    希望国产化、纯开源、兼容 MySQL；已经熟悉 Doris 生态。

### 核心特点

- 与 StarRocks **同源**（原 Palo → 百度开源 → Apache 孵化毕业）
- **SQL 92 兼容**、MySQL 协议
- **Multi-Catalog**（Iceberg / Hudi / Hive）类似 StarRocks
- **物化视图** 支持，但异步 MV 成熟度略低于 StarRocks
- **社区活跃**（国内），海外相对弱

### 和 StarRocks 的区别

| 维度 | StarRocks | Doris |
|---|---|---|
| 异步增量 MV | 更成熟 | 追赶中 |
| 存算分离 | v3.0+ | v2.1+ |
| 向量化 | Pipeline 执行 | 相对成熟 |
| 社区 | 海外更活跃 | 国内更活跃 |
| 商业化 | StarRocks Inc. | SelectDB |

**实务**：两家在互相追赶。选型看**公司内部偏好**和**商业支持需求**。

---

## 4. Apache Druid · 实时大屏专业户

!!! example "适合"
    **秒级数据新鲜度 + 高并发大屏 + 时间序列**为主的场景。

### 核心特点

- **Segment 模型**：按时间分段不可变
- **实时 Ingestion + 批 Ingestion 双路**
- **预聚合**（Rollup）在写入时完成
- **Approx 查询**（HLL / ThetaSketch）非常快
- **多组件架构**：Coordinator / Broker / Historical / MiddleManager
- **没有 Update / Delete**（新 Segment 覆盖）

### 优劣

| 优 | 劣 |
|---|---|
| 实时 + 批统一 | **运维复杂**（4 类节点 + Zookeeper） |
| 时序查询极快 | 无 Join（1.0+ 有但弱） |
| 高并发低延迟 | Schema Evolution 痛苦 |
| HLL / 近似查询丰富 | 学习曲线陡 |

### 典型用户

- Airbnb · Netflix · 腾讯 · 小米
- 场景：广告监控、用户行为大屏、网络监控

---

## 5. Apache Pinot · LinkedIn 出品

!!! example "适合"
    用户面 Dashboard（给外部客户看）、高并发 < 100ms 延迟。

### 核心特点

- LinkedIn 2014 开源，StarTree 商业化
- **StarTree Index**（多维预聚合索引）
- **Real-Time Upsert**（Paimon 类似能力）
- **多租户强**（Isolation 到 Segment 级）
- **Segment 模型**类似 Druid

### 和 Druid 对比

| 维度 | Druid | Pinot |
|---|---|---|
| 上手难度 | 陡 | 陡 |
| 索引能力 | Bitmap / BloomFilter | StarTree / Inverted / Sorted |
| Upsert | 弱 | 强（v0.8+） |
| 社区（中文） | 有 | 较少 |
| 用户案例 | 广 | LinkedIn · Uber · Stripe |

---

## 场景 → 方案决策

| 场景 | 首选 | 为什么 |
|---|---|---|
| **BI 仪表盘 on 湖** | StarRocks | 湖联邦 + MV + MySQL |
| **日志分析 / OpenTelemetry** | ClickHouse | 单表聚合极速、生态丰富 |
| **实时大屏（秒级）** | Druid / Pinot / StarRocks | 实时 ingestion 成熟 |
| **用户面 Dashboard 给外部** | Pinot / StarRocks | 多租户 + 高并发 |
| **国产化要求** | Doris / StarRocks（国内团队） | 两家都行，偏好决定 |
| **时序指标** | ClickHouse / Druid | 专业索引 |
| **OLAP + 联邦查询（无副本）** | Trino | 不需要这里的加速 |
| **大量 Join + 复杂 SQL** | StarRocks / Doris | ClickHouse 放弃 |
| **PB 级数据** | ClickHouse / StarRocks 存算分离 | 成本敏感 |

---

## 常见误区

- **把加速副本当真相源**：副本挂了 = 数据找不回；**真相**永远是 Iceberg / Paimon
- **全量同步到 ClickHouse**：冷数据也在本地盘 → 成本爆；**只同步热 30-90 天**
- **不监控副本 lag**：业务看着数据过时，没人知道
- **StarRocks / Doris 上物化视图无限加**：MV 维护成本随数量指数增长
- **ClickHouse 用来做 Join-heavy**：走错路 → 立刻慢
- **Druid 不预聚合**：等于放弃 Druid 最大的优势
- **Pinot 没做好 Schema 设计**：后期改表痛苦
- **Trino + Iceberg 够用却上副本**：多一套系统维护、监控、同步 → 技术债增加

---

## 性能 Benchmark 参考

!!! note "注意"
    Benchmark 结果依赖数据、配置、查询；以下是行业普遍观察，**不绝对**。

- **ClickBench**（单表聚合）：ClickHouse 通常第一，StarRocks 接近
- **SSB**（星型 BI）：StarRocks / Doris 领先，ClickHouse 由于 Join 慢落后
- **TPC-H**：StarRocks / Doris 通常领先 ClickHouse 2-5×
- **实时 p99 延迟**：Druid / Pinot / StarRocks 都能做 < 200ms

详见各家官方 Benchmark；一定自己跑一次真实业务数据。

---

## 成本粗估（100TB 数据规模）

| 方案 | 硬件 | 特点 |
|---|---|---|
| **Trino + Iceberg（无副本）** | 50 核 + 100GB 内存 | 最便宜、延迟 3-10s |
| **StarRocks 存算分离** | 50 核 + 200GB + 对象存储 | 热数据 SSD 5-10TB |
| **StarRocks 本地盘** | 100 核 + 500GB + 50TB SSD | 性能最稳 |
| **ClickHouse 分布式** | 80 核 + 400GB + 50TB SSD | 单表爆炸快 |
| **Druid / Pinot** | 100 核 + 400GB + 50TB SSD | 运维要人手 |

---

## 相关

- 场景：[BI on Lake](../scenarios/bi-on-lake.md) · [Real-time Lakehouse](../scenarios/real-time-lakehouse.md) · [CDP / 用户分群](../scenarios/cdp-segmentation.md)
- 对比：[计算引擎对比](compute-engines.md)（Trino vs Spark vs Flink vs DuckDB）
- 底座：[湖表](../lakehouse/lake-table.md) · [Iceberg](../lakehouse/iceberg.md) · [Paimon](../lakehouse/paimon.md)
- 业务：[业务场景全景](../scenarios/business-scenarios.md)

## 延伸阅读

- [StarRocks 官方博客](https://www.starrocks.io/blog) · [Apache Doris 社区](https://doris.apache.org/)
- [ClickBench 在线对比](https://benchmark.clickhouse.com/) · [ClickHouse 文档](https://clickhouse.com/docs)
- [Druid in Action](https://druid.apache.org/docs/latest/) · [Pinot 官方](https://pinot.apache.org/)
- *Designing Data-Intensive Applications*（Kleppmann）— OLAP 底层原理
- Uber / Airbnb / Netflix / LinkedIn 各自的 OLAP 工程博客
