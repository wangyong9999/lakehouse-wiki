---
title: Apache Spark
type: system
tags: [query-engine, batch, streaming, ml]
category: query-engine
repo: https://github.com/apache/spark
license: Apache-2.0
status: stable
---

# Apache Spark

!!! tip "一句话定位"
    湖仓上的"**重型瑞士军刀**"：批 ETL、流（Structured Streaming）、机器学习、图计算、SQL 都能跑。湖表格式（Iceberg / Delta / Paimon / Hudi）的一等公民执行引擎。

## 它解决什么

Spark 最擅长的是**大规模 shuffle + 长链 DAG 的 ETL** 和**需要迭代计算的 ML**。湖仓上的典型场景：

- **明细事实表的每日批量生成**（shuffle + join + 聚合）
- **CDC 入湖**（Structured Streaming 写入 Delta / Iceberg / Paimon）
- **训练数据准备**（feature 生成、采样、划分）
- **大规模 Compaction 作业**

相比 Trino 是"秒级交互"，Spark 是"分钟到小时的批+近实时流"。

## 架构一览

- **Driver + Executor** 模型；DAG Scheduler 把作业切成 stage，stage 切成 task
- **Catalyst 优化器** + **Tungsten 执行器**（代码生成 + 列式向量化）
- 原生支持 Iceberg / Delta / Paimon / Hudi 的 DataFrame + SQL 接口
- **Structured Streaming** —— 微批 / 连续处理两种模式

## 对湖仓的关键能力

| 能力 | 说明 |
| --- | --- |
| Iceberg / Delta / Paimon / Hudi | 一等公民写入 |
| AQE（Adaptive Query Execution） | 动态调整分区数 / join 策略 / skew |
| DynamicPartitionPruning | 谓词下推到湖表 |
| Spark Connect | 解耦 client / server，远程提交作业 |
| MLlib + Spark MLflow | 配合湖上训练集做批训练 |

## 什么时候选它

- 需要稳定的大规模 ETL / 数据准备
- 流 + 批同语义（Structured Streaming）
- ML Pipeline 想和湖上数据 native 集成
- 已有 Spark 历史积累，迁移成本低

## 什么时候不选

- 秒级交互式查询 → Trino / StarRocks
- 单机分析 / 探索 → DuckDB
- 超低延迟流 → Flink

## 陷阱与坑

- **Catalog 配置**：Iceberg / Delta / Paimon 在 Spark 各自配置 `spark.sql.catalog.*`，多个同时启用时容易混淆
- **Shuffle 分区数** 是调优的重点，默认 200 常常不合适
- **小文件**：Structured Streaming 入湖要开启 compaction job

## 延伸阅读

- Spark SQL / DataFrame Guide: <https://spark.apache.org/docs/latest/sql-programming-guide.html>
- Iceberg + Spark: <https://iceberg.apache.org/docs/latest/spark-getting-started/>
