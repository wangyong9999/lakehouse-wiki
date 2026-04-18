---
title: Streaming Upsert / CDC · 流式入湖机制
type: concept
depth: 资深
level: A
applies_to: Paimon 0.9+, Hudi 0.14+, Iceberg v2, Flink CDC 3.0+
tags: [lakehouse, streaming, cdc]
aliases: [流式 upsert, Change Data Capture]
related: [lake-table, paimon, hudi, snapshot]
systems: [paimon, hudi, iceberg, flink, debezium]
status: stable
---

# Streaming Upsert / CDC · 流式入湖机制

!!! tip "一句话理解"
    把上游（OLTP / 业务系统）的**每一行变更（insert / update / delete）**持续、按序地落到湖表上——并且能**原样流式输出**给下游。**湖仓支持准实时的核心机制**。

!!! abstract "TL;DR"
    - **三个问题**：高频 upsert 写入 · 读最新状态 · Changelog 输出给下游
    - **两种落法**：**MoR**（写快读慢） · **CoW**（写慢读快）
    - **Changelog Producer 四策略**：input / lookup / full-compaction / none
    - **Paimon 是当前最成熟的流式 upsert 湖表**；Iceberg 也在跟进
    - **Flink CDC 3.0+** 是主流入口（MySQL / Postgres / MongoDB / Oracle 全覆盖）
    - **主键设计 + Bucket 策略**决定规模上限

## 它要解决的三个问题

1. **写入侧**：高频 upsert（主键更新）不能每次全量重写，否则吞吐崩
2. **读取侧**：查询时能看到"最新状态"（即：每个 key 最新一条 insert/update 生效，已 delete 的不可见）
3. **下游流侧**：把"这批 commit 新增/改动了哪些行"以 Changelog 形式喂给 Flink / 其他消费者

## 组件链路

```mermaid
flowchart LR
  oltp[(MySQL / PG / MongoDB)] --> debezium[Debezium / Flink CDC]
  debezium --> kafka[(Kafka, 可选)]
  kafka --> writer[Paimon / Hudi Writer]
  debezium --> writer
  writer --> lake[(Paimon / Hudi / Iceberg 表)]
  lake --> stream[Flink 流读 Changelog]
  lake --> batch[Spark / Trino 批读当前状态]
```

**Debezium / Flink CDC** 负责从 binlog / WAL 提取变更，**写入器**落盘成湖表。

## 两种表类型落法

### Merge-on-Read（MoR）

- 写时**只追加 delta 文件（Avro / Parquet delete file）**，不合并
- 读时合并 base + delta，拿到最新值
- **写快 / 读慢**；适合写多读少或有 compaction 资源

代表：Hudi MoR 表、Iceberg 的 row-level delete 文件、Paimon 的 L0

### Copy-on-Write（CoW）

- 写时把受影响的 key 所在文件**整文件重写**
- 读时直接读 base 文件
- **写慢 / 读快**；适合读多写少

代表：Hudi CoW 表、Iceberg 的 CoW 模式

## Changelog 输出

上游产生变更，下游想以流的形式消费——需要湖表能输出 **Changelog**（至少包含 `+I / -U / +U / -D` 四种事件）。主要有三种产生策略：

| 策略 | 说明 | 成本 | 精度 |
| --- | --- | --- | --- |
| `input` | 直接把上游 CDC 流当 changelog | 最低 | 假设上游已去重 |
| `lookup` | 写时查历史对比生成 changelog | 高 | 最精准 |
| `full-compaction` | Compaction 时产出 | 中 | 延迟到 compaction |

Paimon 把三种策略作为一等选项；Iceberg 目前偏向 `input` 路线；Hudi 走 Incremental Query + CDC 字段混合。

## 主键设计的影响

- **主键选得好** —— upsert 自然幂等，落地简单
- **主键错了** —— 要么重复（漏去重），要么"更新"实际在写新行
- **复合主键 + hash 分桶**（如 Paimon `bucket(N, pk)`）是大规模 upsert 稳定的常见配方

## 性能数字 · 规模基线

| 指标 | 典型值 |
|---|---|
| Flink CDC 单作业吞吐 | 10k - 100k rows/s |
| 端到端延迟（CDC → 可查）| 1 - 5 分钟（Paimon snapshot 频率决定）|
| Paimon Primary Key 表最大规模 | 单表 TB - 几十 TB |
| Bucket 典型数 | 16 - 256 |
| Compaction 频率 | L0 超 5-10 文件触发 |
| 延迟与成本权衡 | 秒级延迟 = 高频 commit = compaction 压力大 |

## 现实检视 · 2026 视角

### 这个领域的成熟度

- **Paimon** 是当前流式 upsert 最原生的选择——Flink 社区持续投入
- **Iceberg v3 (2025+)** 正在补齐流式能力，但**和 Paimon 仍有差距**
- **Hudi** 老而稳，在 Uber 等生产环境规模最大，但新项目不太选
- **Delta** 虽然有 Change Data Feed，但**不是为 CDC 高频 upsert 优化**

### 工业实务的坑

- **大部分团队用 `input` changelog producer**——因为上游 CDC 已经是 changelog 格式。但如果上游去重不够干净，会传播错误
- **`lookup` 策略成本高**：每次 compaction 都要查老值对比；千万级主键规模才会考虑
- **复合主键 + 多字段更新** 场景在 Paimon 里还有边缘 case 需要 test
- **Schema evolution** 跨工具（Debezium → Flink CDC → Paimon）传播仍然不是零配置

### 选型简化建议

- **新项目 + 流为主**：**Paimon + Flink CDC 3.0+**
- **多引擎批 + 偶尔 upsert**：Iceberg v2 + MoR delete file
- **Spark 栈 + upsert 历史投入**：Hudi（不换）
- **Databricks 栈**：Delta + Change Data Feed

## 典型陷阱

- **小文件雪崩**：高频流写必须配周期 compaction
- **DDL 同步**：上游表结构变化，CDC 链路要能传到下游（Debezium schema registry + 湖表 [Schema Evolution](schema-evolution.md)）
- **乱序 / 回滚**：Kafka 消费 offset 回退或重放时要保证幂等
- **全增量混合**：初始化时要先快照再消费增量，需要 watermark 桥接（Flink CDC 2.0+ 原生支持）

## 相关

- [Apache Paimon](paimon.md) —— 流式 upsert 原生
- [Apache Hudi](hudi.md) —— CoW / MoR 先驱
- [Delete Files](delete-files.md) —— row-level delete 细节
- 场景：[流式入湖](../scenarios/streaming-ingestion.md)

## 延伸阅读

- *Debezium: Stream changes from your database* 文档
- *Real-time Data Lake with Paimon* —— 社区博客系列
- Flink CDC: <https://github.com/apache/flink-cdc>
