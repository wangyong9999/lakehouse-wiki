---
title: Trino vs Spark vs Flink vs DuckDB · 计算引擎对比
applies_to: "2024-2026 主流"
type: comparison
level: B
depth: 进阶
prerequisites: [oltp-vs-olap]
tags: [comparison, query-engine, trino, spark, flink, duckdb]
subjects: [trino, spark, flink, duckdb]
status: stable
last_reviewed: 2026-04-22
---

# Trino vs Spark vs Flink vs DuckDB · 计算引擎对比

!!! tip "读完能回答的选型问题"
    我现在这个查询 / 作业，应该跑在 Trino、Spark、Flink 还是 DuckDB？四者能力相互重叠又有显著差异，选错轻则慢 10 倍，重则成本与运维翻倍。

!!! abstract "TL;DR"
    - **Trino**：交互式 BI / 联邦查询 / 仪表盘。秒级响应为王
    - **Spark**：重型批 ETL · 大 shuffle · ML 数据准备。分钟-小时级可接受
    - **Flink**：真流处理 · CDC · 低延迟状态计算。端到端秒级
    - **DuckDB**：单机 / 嵌入式 / 开发态 / CI。无集群开销
    - 多数团队**都要**：Trino + Spark + Flink + DuckDB 四件套分工明确
    - 加一条 StarRocks / ClickHouse 作为"BI 加速副本"按需选

## 对比维度总表

| 维度 | Trino | Spark | Flink | DuckDB |
| --- | --- | --- | --- | --- |
| **主场** | 交互式 SQL / 联邦 | 批 ETL + Structured Streaming | 真流 + 事件时间 | 单机 OLAP |
| **执行模型** | 内存 pipeline，无 shuffle 落盘 | DAG + shuffle 可落盘 | dataflow streaming | 单进程向量化 |
| **启动延迟** | 秒级（集群常驻） | 分钟（启 Driver）| 秒-分钟（集群常驻） | 毫秒 |
| **典型查询延迟** | 亚秒-秒 | 分钟-小时 | 流上秒级 | 亚秒-秒（单机规模）|
| **并发** | 数百 QPS 设计上支持 | 低（批作业少并发） | 作业级独立 | 单会话 |
| **规模上限** | 数百 TB / 查询 | PB 级 / 作业 | 无硬上限 | 几百 GB / 查询 |
| **内存模型** | 内存为主，溢出差 | 可溢出磁盘 | 状态后端 RocksDB | 内存，溢出支持 |
| **容错** | 查询重跑 | Stage 级重试 | Checkpoint + 续跑 | 进程崩溃即失败 |
| **SQL 完整度** | ANSI 标准强 | SQL + DataFrame | SQL + Table API | SQL 标准强 |
| **湖表支持** | Iceberg / Delta / Hudi / Paimon | 全部 | Paimon 首席 + Iceberg / Hudi | Iceberg / Delta 扩展 |
| **流式读湖表** | 不支持（批扫）| Structured Streaming 微批 | 真流 | 不支持 |
| **Python UDF** | 新特性 | 原生 PySpark | 有但较新 | Python binding 极强 |
| **运维 / 学习曲线** | 中（Coordinator + Worker） | 高（Driver+Executor+Shuffle 调优） | 高（事件时间 + Watermark + 状态）| 零（单二进制）|
| **典型部署** | K8s 上常驻集群 | 按作业拉起 / 常驻池 | 常驻 | 嵌入应用 / CI / 开发机 |

## 场景决策

### "我要跑一个 BI 仪表盘查询"
→ **Trino**。秒级响应、高并发、联邦能力。

### "我要做 T+1 批 ETL，TB 级 shuffle"
→ **Spark**。最成熟，AQE + Tungsten + 可溢出；Resource-aware scheduling 到位。

### "我要做 CDC 入湖，保证端到端 < 5min 延迟"
→ **Flink**（写 Paimon）。事件时间 / Watermark / 2PC sink 原生。

### "我要做机器学习训练的特征拉取 + PIT Join"
→ **Spark**（和 Iceberg Time Travel 天作之合）；也可 **Ray Data** 替代。

### "我在本地想查一张 200GB 的 Iceberg 表"
→ **DuckDB**。`duckdb -c "SELECT ... FROM iceberg_scan('s3://...')"` 完事。

### "我想做复杂 join（5 张表）+ 毫秒级 p99"
→ 不适合 Trino。考虑 **StarRocks / ClickHouse** 加速副本（不是本四者）。

### "我要在 CI 里验证一条 SQL 的逻辑"
→ **DuckDB**（毫秒启动）。

## 架构差异（简化）

### Trino

```
Coordinator
  ├── Parse + Plan
  └── Distribute plan fragments
Workers (N)
  ├── Read from connector (Iceberg / Hive / Kafka / MySQL / ...)
  └── Pipeline execute → return to coordinator
```

**无 shuffle spill** → 大 join 爆内存，不适合重型 ETL。

### Spark

```
Driver
  ├── DAG scheduler
  └── Task scheduler
Executors (N)
  ├── Task execution
  └── Shuffle manager → disk / memory
```

**Shuffle 可落盘** → TB 级 join 不爆；AQE 动态调分区。代价：启动慢、资源预留要多。

### Flink

```
JobManager (Coordinator)
  └── Schedule operators to TaskManagers
TaskManagers (Workers)
  ├── Operators execute in pipelined dataflow
  ├── State backend (RocksDB on local disk)
  └── Checkpoint to durable storage (S3)
```

**流即一等公民**；批模式是流的特例（有限流）。

### DuckDB

```
Single process
  ├── Parser → Planner → Optimizer
  ├── Vectorized executor (columnar batches)
  └── Reader (Parquet / CSV / Iceberg / HTTP)
```

**零集群** → 单机性能极强，但无分布式。

## 性能典型值（同机同硬件粗估）

| 查询类型 | Trino | Spark | Flink | DuckDB |
| --- | --- | --- | --- | --- |
| 10GB 单表扫描 + 聚合 | 2-5s | 30s（启动成本）| — | 1-3s |
| 100GB 5 表 join | 30s-2min | 3-10min | — | 不支持规模 |
| 流式 1 分钟窗口聚合 | — | 1-2 min latency | < 30s latency | — |
| 1GB 探索性 SQL | 2s（含网络）| 30s | — | < 1s |

## 选型速记

```
                           低延迟 ←──────→ 高吞吐
                           
 单机 / 嵌入 / CI       DuckDB
 
 秒级交互 BI            Trino
 
 流式 / 事件时间                         Flink
 
 批 ETL / ML 数据准备                         Spark
```

四件套**分工明确，不要相互替代**。

## 团队的组合

参考 [ADR-0005](../adr/0005-engine-combination.md)：Trino + Spark + Flink + DuckDB 四件套常驻，StarRocks 作为按需加速副本。

## 常见决策陷阱

- **用 Trino 跑 TB 级 join** → 爆内存 / 超时。改 Spark
- **用 Spark 跑仪表盘** → 启动 30s 不能接受。改 Trino / StarRocks
- **用 Flink 跑批一次性作业** → 运维复杂度不划算。改 Spark
- **用 DuckDB 扛分布式负载** → 单机上限；多数据只能分散处理
- **Trino 作为加速副本** → 它本身就是联邦 / 交互查询。需要加速用 StarRocks / ClickHouse

## 相关

- [Trino](../query-engines/trino.md) · [Spark](../query-engines/spark.md) · [Flink](../query-engines/flink.md) · [DuckDB](../query-engines/duckdb.md)
- [ADR-0005 查询引擎组合](../adr/0005-engine-combination.md)
- [StarRocks](../query-engines/starrocks.md) · [ClickHouse](../query-engines/clickhouse.md) —— 加速副本候选
- 相关对比：[DB 引擎 vs 湖表](db-engine-vs-lake-table.md)

## 延伸阅读

- TPC-DS benchmark（社区对各引擎的标准对比）
- *Presto / Trino Architecture*（Trino docs）
- *Lightning-Fast Big Data Analytics with Spark*
- *Stream Processing with Flink*（Akidau）
- Benchmark 参考：[Benchmark 参考](../benchmarks.md)
