---
title: 事件时间 · Watermark · 乱序
type: concept
depth: 进阶
level: A
last_reviewed: 2026-04-20
prerequisites: [oltp-vs-olap]
tags: [foundations, streaming, flink, watermark]
related: [flink, streaming-upsert-cdc, paimon, kafka-ingestion]
systems: [flink, kafka]
status: stable
---

# 事件时间 · Watermark · 乱序

!!! tip "一句话理解"
    流处理真正的时间维度是 **事件发生时**（event time），不是 **被处理时**（processing time）。**Watermark** 是"我相信到这条线之前的事件都到齐了"的承诺。没有它，窗口永远等不到关闭；设太松，结果不对；设太紧，正确数据被当迟到丢掉。

!!! abstract "TL;DR"
    - 三种时间：**事件时间 > 摄入时间 > 处理时间**
    - Watermark 是**逻辑时钟**：声明 "event_time ≤ T 的数据都已到达"
    - 乱序容忍 = **Watermark 相对最大 event_time 的滞后量**
    - 窗口在 Watermark 越过窗尾时**关闭并触发**；滞后数据要么丢、要么走 side output、要么重新 materialize
    - CDC / 日志入湖的"新鲜度"本质上是 Watermark 推进速度

## 三种时间

| 时间 | 定义 | 何时用 |
| --- | --- | --- |
| **事件时间** `event_time` | 事件**真实发生**的时刻（业务系统写的） | 业务分析、报表、审计——**唯一正确的时间** |
| **摄入时间** `ingestion_time` | 事件**进入流处理系统**的时刻 | 折中选择，系统自动记录 |
| **处理时间** `processing_time` | 事件**被算子处理**的时刻 | 只用于低延迟触发、健康监控；分析绝不能用 |

**反直觉的点**：一条业务事件可能 10:00 发生，10:15 到 Kafka，10:18 到 Flink，10:22 被算子处理。这三个时间都不同。**分析看的是 10:00**。

## 为什么需要 Watermark

想象一个按事件时间的 "1 分钟窗口" 聚合：

```
10:00-10:01 窗口：该关窗输出结果了吗？
  - 处理时间 10:01：还有事件在路上吗？
  - 谁知道？网络抖动、下游重试、跨区延迟……
  - 永远等一个"最迟"的事件 → 窗口永远不关 → 内存炸
  - 立刻关 → 迟到的事件直接丢 → 结果错
```

**Watermark 打破僵局**：给一个承诺——"W=T 之后，我保证之前的 event_time ≤ T 都已到达"。窗口结束时间 ≤ W 时触发输出。

```
时间轴 (event_time):
  ... 9:59:58  10:00:02  10:00:15  10:00:45  10:01:03 ...
                                          ↑
                                       W = 10:00:30
                                       （意思：10:00:30 前的都到了）
  窗口 10:00–10:01 在 W 越过 10:01:00 时关闭并触发。
```

## Watermark 生成策略

### 基于时间戳 + 固定乱序容忍

**最常用**。假设最大乱序 5 秒：

```
W(T_now) = max(event_time seen so far) - 5 seconds
```

- 新事件更新 Watermark
- 容忍 5 秒范围内乱序
- 超过 5 秒的是"迟到数据"

### 基于 punctuated（标记事件）

上游显式在消息里带 "checkpoint"，watermark 看到标记就推进。适合上游系统能发出明确进度信号的场景。

### 基于全局时钟（Kafka / Pulsar broker 时间）

上游 broker 写入时间作为 watermark。简化但容易乐观，乱序保障弱。

## 乱序容忍的权衡

| 容忍量 | 优点 | 代价 |
| --- | --- | --- |
| **0**（严格对齐） | 结果最及时 | 轻微乱序就丢数据 |
| **5–30s** | 大多数场景够用 | 窗口关闭延迟几十秒 |
| **1–5 min** | 容忍重传、网络抖动 | 结果新鲜度降到分钟级 |
| **≥ 1 hour** | 接近批式，能容忍大回放 | 流式优势丧失 |

**Flink 典型配置**：

```java
DataStream<Event> stream = env.fromSource(...,
    WatermarkStrategy
        .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(30))
        .withTimestampAssigner((e, ts) -> e.getEventTime()),
    "source");
```

## 迟到数据的 4 种处理

1. **丢弃**（默认）：算子收到 event_time < current watermark 的数据直接抛
2. **Side Output**：用独立流捕获迟到数据，走补偿链路
3. **Allowed Lateness**：窗口关闭后再保留 N 分钟；迟到数据触发**增量再输出**（覆盖之前的结果）
4. **Materialized 覆盖**：湖仓场景下，迟到数据作为 upsert 覆盖原聚合行

## Delivery Semantics · At-least-once vs Exactly-once

事件时间不能单独工作，**必须配合 delivery semantics**——一条消息从上游到下游最终"出现几次"。流处理三档：

| 语义 | 现象 | 如何做到 |
|---|---|---|
| **At-most-once** | 最多一次，可能丢 | 源不重放 · 下游不去重 · 崩了就丢 |
| **At-least-once** | 至少一次，可能重 | 源可重放（Kafka offset 持久化）· 下游接收重复 |
| **Exactly-once** | 恰好一次 | 源可重放 + 下游去重 / 幂等 / 事务性提交 |

**关键**："exactly-once" 在不同层面意思不同：

- **处理语义上的 exactly-once**（Flink checkpoint / Kafka transaction）：算子内部状态每条消息只算一次。**不等于**下游看到一次
- **端到端 exactly-once**：需要 **sink 可参与两阶段提交**（Kafka transactions · JDBC sink XA · 湖表 commit 原子性）

**湖仓的 exactly-once 机制**：

- **Iceberg / Paimon** 通过 Flink checkpoint + 原子 commit 实现端到端 exactly-once —— Flink 每个 checkpoint 完成时，Paimon 做一次 commit；如果 checkpoint 失败，数据不可见、回放重试
- **Kafka → Iceberg** 典型路径：Kafka source + Flink 2PC sink + Iceberg commit（需要连接器支持）
- **幂等写入**：给每条消息一个稳定 ID，下游 upsert on ID —— 这是 at-least-once 环境下做到"effectively-once"的常用方法，比真正的 2PC 简单

**选型口诀**：
- 指标准确性要求极高（金额 / 风控）→ 端到端 exactly-once
- 指标可容忍少量重复 / 缺失（日志 / 推荐）→ at-least-once + 业务层去重
- 实时监控 / 告警 → at-most-once 也可以（宁可丢也要快）

## 在湖仓 / 入湖里的具体意义

- **CDC 入湖的"新鲜度"** = Watermark 推进速度
  - Debezium / Flink CDC 给每条消息打 `source.ts_ms`
  - Flink 按这个 ts_ms 推进 Watermark
  - **commit 触发 ≠ watermark · 两者分开看**：
      - **commit 节奏**由 **Flink checkpoint 决定**——每次 checkpoint 成功 · Flink 的 `TwoPhaseCommitSinkFunction` 和 Paimon / Iceberg sink 完成原子 commit（详见 [管线韧性 · 端到端 Exactly-once](pipeline-resilience.md)）
      - **Watermark 决定**的是：下游**窗口触发**（`window end ≤ watermark` 才 emit）· **延迟数据处理**（超过 watermark 的 event 走 side output）· **SQL 事件时间聚合**的正确性
      - 两者**都依赖 checkpoint interval**（commit 周期 = checkpoint 周期 · 通常 30s-5min）· 但解决**不同问题** · 别混为一谈
- **Paimon Changelog Producer 的 `lookup` 模式** 对 watermark 对齐敏感（需要等同一 key 的 change 到齐后再 lookup 生成完整 changelog）
- **Iceberg 流式读（incremental_read）** 基于 **snapshot ID 范围**（`start-snapshot-id` / `end-snapshot-id`）定位增量，**不靠上游 watermark 保证完整性**。snapshot chain 本身就是增量读的真相源

## 常见坑

- **`env.setStreamTimeCharacteristic(EventTime)`**：旧 API，新版本默认 event-time
- **Kafka 多分区消费速率不均 · Watermark 不对齐**：单个 Flink task 从多个 Kafka 分区消费时，**某个分区数据少或空闲**（idle）· watermark 会被它卡住不推进（取最小值语义）
  - 解决：`withIdleness(Duration.ofMinutes(5))` 让空分区/慢分区不阻塞整体 watermark
- **批处理模式忘了关 Watermark**：Flink Batch mode 不产生 Watermark
- **时区混乱**：UTC vs 本地时间 → 窗口错位 1 天
- **Spark Structured Streaming 的等价物**：`withWatermark("event_time", "30 seconds")`

## 相关

- [Apache Flink](../query-engines/flink.md)
- [Streaming Upsert / CDC](../lakehouse/streaming-upsert-cdc.md)
- [Kafka 到湖](../pipelines/kafka-ingestion.md)
- [流式入湖场景](../scenarios/streaming-ingestion.md)

## 延伸阅读

- *Streaming Systems*（Akidau et al., O'Reilly）—— 事件时间 / Watermark 经典教材
- *Dataflow Model* 论文（Google, VLDB 2015）—— Watermark 理论起点
- Flink docs: Event Time
- [Martin Kleppmann - Stream Processing](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/)
