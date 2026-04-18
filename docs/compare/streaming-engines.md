---
title: 流处理引擎横比 · Flink / Spark Streaming / Kafka Streams / RisingWave
type: comparison
depth: 进阶
tags: [comparison, streaming, flink, spark, kafka, risingwave]
related: [flink, spark, real-time-lakehouse, paimon]
status: stable
---

# 流处理引擎横比

!!! tip "一句话回答"
    **Flink** 在**有状态流 + Exactly-Once + 事件时间**三件事上综合最强，湖仓场景配 Paimon 天作之合。**Spark Streaming** 是 batch 思维的流，适合已有 Spark 栈。**Kafka Streams** 是**库**不是引擎，适合嵌入 Kafka 生态的微服务。**RisingWave** 是"流 + SQL 一体" 2024+ 新星，PostgreSQL 协议。

!!! abstract "TL;DR"
    - **四家本质差异**：Flink（纯流）· Spark Structured Streaming（批微分流）· Kafka Streams（库）· RisingWave（PG-compatible 流 DB）
    - **选型关键**：**延迟 SLO · 状态规模 · 已有栈 · 运维能力**
    - **湖上主流**：**Flink + Paimon** 不二之选
    - **Kafka Streams 的位置**：轻量 / 微服务侧，不做分布式 ETL
    - **RisingWave 新在哪**：PG 协议 + 流物化视图 + 实时聚合

## 1. 场景画像

### 什么是"流处理"

不是"低延迟批"——是**持续处理无界数据流**，**有状态**，**输出也是流**。

典型诉求：
- 实时特征（推荐 / 风控）
- CDC 入湖
- 实时监控 / 告警
- 流式 ETL

### 四家总览

| 引擎 | 类型 | 语言 | 主要定位 |
|---|---|---|---|
| **Apache Flink** | 纯流 + 批 | Java/Scala + SQL + Python | 工业标准、大规模 |
| **Spark Structured Streaming** | Micro-batch | Scala + Python + SQL | Spark 栈延伸 |
| **Kafka Streams** | 库 | Java | 嵌入式微服务 |
| **RisingWave** | 流 SQL DB | SQL（Postgres compat）| 流物化视图 |

---

## 2. 逐一深度

### Flink

**定位**：**有状态流处理的事实标准**。

**优势**：
- **真正逐条流处理**（非 micro-batch），ms 级延迟
- **事件时间 + Watermark** 一等公民
- **Checkpoint + Exactly-Once** 语义最成熟
- **State** 可达 TB 级（RocksDB backend）
- **Flink CDC** 成熟的 MySQL / Postgres / Mongo 同步
- **Flink + Paimon** 湖仓流一体最佳组合

**劣势**：
- 学习曲线陡（概念多：checkpoint / barrier / watermark / keyBy / window）
- 运维相对复杂
- 部分 DataStream API 较底层

**适合**：大规模流处理、有复杂有状态业务、湖仓场景。

### Spark Structured Streaming

**定位**：**Spark 用户的流处理选项**。

**核心**：**micro-batch**——每几秒一批处理。也有 **Continuous Mode**（实验性），延迟 ms 级。

**优势**：
- 和 Spark 批 API 统一
- 湖表连接器成熟（Delta / Iceberg）
- 生态复用（Spark ML / SQL）
- 队伍已用 Spark 的话零学习

**劣势**：
- Micro-batch 最低延迟 100ms-秒
- 状态管理**不如 Flink 精细**
- 复杂事件时间处理弱

**适合**：已有 Spark 栈、延迟不极致、流批统一优先。

### Kafka Streams

**定位**：**Kafka 生态内的流处理库**（不是集群引擎）。

**优势**：
- 纯 Java 库，打包进应用
- **无独立集群**，运维简单
- 和 Kafka 深度集成（Exactly-Once via transactions）
- **微服务友好**

**劣势**：
- **不是分布式计算**——规模受限于单应用实例
- 仅 JVM（Python / Go 用户请看 Faust / goka）
- 大规模 ETL 不合适

**适合**：微服务内嵌流处理、小规模聚合、Kafka 重度用户。

### RisingWave

**定位**：**PostgreSQL 兼容的流数据库**（2022+ 新秀）。

**特色**：
- **Postgres wire protocol**：客户端像用 PG
- **流物化视图**：创建 MV 自动持续增量更新
- **SQL-first**，写 SQL 就是写流处理
- 内置存储（S3-backed）
- 对接 Kafka / Pulsar / CDC

**优势**：
- 运维比 Flink 简单
- SQL 语义强
- 增量 MV 是杀手级特性

**劣势**：
- 社区小（相对 Flink）
- 复杂流处理（自定义状态机 / CEP）仍不如 Flink
- 早期产品，有成熟度提升空间

**适合**：实时 OLAP 加速副本、物化视图驱动分析。

---

## 3. 能力矩阵

| 能力 | Flink | Spark Streaming | Kafka Streams | RisingWave |
|---|---|---|---|---|
| 真正流处理 | ✅ 逐条 | ⚠️ micro-batch | ✅ 逐条 | ✅ 逐条 |
| 延迟 | ms | 100ms+ | ms | 秒 |
| Exactly-Once | ✅ 原生 | ✅ 原生 | ✅ 原生 | ✅ |
| 事件时间 + Watermark | ✅ 最强 | ✅ | ⚠️ 基本 | ✅ |
| 状态规模 | TB | 百 GB | GB | TB (S3-backed) |
| SQL 友好 | ✅ FlinkSQL | ✅ | ❌ | ✅✅ PG compat |
| Python 支持 | PyFlink | PySpark | Faust | ✅ PG client |
| CDC 能力 | ✅ Flink CDC | 通过 Debezium | 通过 Kafka Connect | 原生 |
| 湖表 sink | Paimon / Iceberg / Hudi / Delta | Iceberg / Delta | 无直接 | 通过 sink |
| 运维复杂度 | 高 | 中 | 低 | 中 |
| 社区规模 | 最大 | 大 | 中 | 小但快涨 |

---

## 4. 场景 → 推荐

| 场景 | 推荐 |
|---|---|
| **CDC 入湖（Paimon / Iceberg）** | **Flink** |
| **实时风控 / 复杂有状态** | **Flink** |
| **实时大屏 / 物化视图** | **RisingWave** 或 **Flink + Paimon + StarRocks** |
| **轻量聚合、嵌入应用** | **Kafka Streams** |
| **已有 Spark 栈 / 流批一体** | **Spark Structured Streaming** |
| **Exactly-Once 对 Kafka** | Flink 或 Kafka Streams |
| **PostgreSQL 熟练团队做流** | **RisingWave** |

---

## 5. 选型决策矩阵

```
需要真正流处理（<100ms 延迟）？
    ├── 是 ──┐
    │       ├── 已有 Spark 栈？──是──> Spark Continuous Mode (早期慎用)
    │       ├── 小规模嵌入？──是──> Kafka Streams
    │       ├── 希望 SQL-first？──是──> RisingWave (OLAP 场景) 或 FlinkSQL
    │       └── 复杂有状态 / 大规模？──> Flink
    └── 否（延迟可接受秒级）──> Spark Streaming 或 Flink
```

---

## 6. 成本对比（粗略，100MB/s 入流）

| 方案 | 集群规模 | 月成本（EC2 参考）|
|---|---|---|
| Flink on K8s | 3 TM × 4c16g | $500 |
| Spark Streaming | 10 Executor × 4c16g | $1500 |
| Kafka Streams（嵌入应用）| 3 instance × 2c8g | $200 |
| RisingWave | 3 compute × 4c16g + S3 | $600 |

（不含 Kafka 本身成本）

---

## 7. 代码片段对比（相同任务：Kafka 订单流 → 5 分钟聚合）

### Flink SQL

```sql
CREATE TABLE orders (
  order_id BIGINT, region STRING, amount DECIMAL(18,2), ts TIMESTAMP(3),
  WATERMARK FOR ts AS ts - INTERVAL '10' SECOND
) WITH ('connector'='kafka', ...);

INSERT INTO region_gmv_5min
SELECT
  region,
  TUMBLE_END(ts, INTERVAL '5' MINUTE) AS window_end,
  SUM(amount)
FROM orders
GROUP BY region, TUMBLE(ts, INTERVAL '5' MINUTE);
```

### Spark Structured Streaming

```python
orders = (spark.readStream.format("kafka")
          .option("subscribe", "orders").load())

result = (orders
    .withWatermark("ts", "10 seconds")
    .groupBy(window("ts", "5 minutes"), "region")
    .agg(sum("amount")))

result.writeStream.outputMode("update").format("console").start()
```

### Kafka Streams

```java
KStream<String, Order> orders = builder.stream("orders");
orders.groupBy((k, v) -> v.region)
      .windowedBy(TimeWindows.of(Duration.ofMinutes(5)))
      .aggregate(() -> 0.0, (k, v, agg) -> agg + v.amount)
      .toStream().to("region-gmv-5min");
```

### RisingWave

```sql
CREATE SOURCE orders_src WITH (connector='kafka', topic='orders', ...) ROW FORMAT JSON;

CREATE MATERIALIZED VIEW region_gmv_5min AS
SELECT
  region,
  window_end,
  SUM(amount)
FROM TUMBLE(orders_src, ts, INTERVAL '5 MINUTES')
GROUP BY region, window_end;

-- 查询时像查普通表
SELECT * FROM region_gmv_5min;
```

---

## 8. 陷阱 · 通用

- **以为流处理 = 低延迟批**：必须理解 watermark / exactly-once 等概念
- **State 膨胀不管**：所有引擎都会 OOM；**必须 TTL**
- **Checkpoint 策略错**：太频繁 → 压 performance；太少 → 重放 lag 大
- **Mix 处理时间 vs 事件时间**：bug 源头
- **低估运维成本**：Flink 集群运维是专职工作

---

## 9. 延伸阅读

- [Flink](../query-engines/flink.md) · [Spark](../query-engines/spark.md) · [Paimon](../lakehouse/paimon.md)
- **[*Streaming Systems* (Tyler Akidau, O'Reilly 2018)](https://www.oreilly.com/library/view/streaming-systems/9781491983867/)** —— 流处理经典
- **[Flink 官方文档](https://flink.apache.org/)** · **[Spark Streaming 官方](https://spark.apache.org/streaming/)**
- **[Kafka Streams Docs](https://kafka.apache.org/documentation/streams/)** · **[RisingWave 官方](https://risingwave.com/)**
- **[Real-time Lakehouse 场景](../scenarios/real-time-lakehouse.md)**

## 相关

- [计算引擎对比](compute-engines.md) —— 包含批引擎
- [Real-time Lakehouse](../scenarios/real-time-lakehouse.md)
- [流式入湖场景](../scenarios/streaming-ingestion.md)
