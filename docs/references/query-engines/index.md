---
title: 参考资料 · 查询引擎
type: reference
status: stable
tags: [reference, references, query-engine]
description: Trino / Spark / Flink / DuckDB / StarRocks / ClickHouse 经典论文与权威文档
last_reviewed: 2026-04-25
---

# 参考资料 · 查询引擎

## 经典论文

- **[Presto: SQL on Everything](https://research.facebook.com/file/1166468/Presto-SQL-on-everything.pdf)** _(2019, paper - Meta)_ —— Presto/Trino 架构论文。
- **[Spark SQL: Relational Data Processing in Spark](https://people.csail.mit.edu/matei/papers/2015/sigmod_spark_sql.pdf)** _(2015, paper - Databricks)_ —— Spark SQL + Catalyst。
- **[Apache Flink: Stream and Batch Processing in a Single Engine](https://www.cs.kent.edu/~rothstei/spring_15/oamcs_papers/p28.pdf)** _(2015, paper)_ —— Flink 架构论文。
- **[DuckDB: an Embeddable Analytical Database](https://mytherin.github.io/papers/2019-duckdbdemo.pdf)** _(2019, paper)_ —— DuckDB 论文。
- **[ClickHouse - Lightning Fast Analytics for Everyone](https://clickhouse.com/docs/whitepaper)** _(whitepaper)_ —— ClickHouse 架构。
- **[StarRocks - The Linux Foundation Project](https://www.starrocks.io/blog)** _(blog)_ —— StarRocks 设计博客系列。

## 优化器 / 执行

- **[The Volcano Optimizer Generator](https://infosys.cs.uni-saarland.de/teaching/15ws/dis-extensible-DBMS/papers/Volcano.pdf)** _(1993, paper)_ —— Volcano 优化器框架。
- **[Vectorized Query Execution](https://15721.courses.cs.cmu.edu/spring2020/papers/02-modern/p225-boncz-cidr05.pdf)** _(2005, paper - MonetDB/X100)_ —— 向量化执行经典。
- **[Apache Arrow Format](https://arrow.apache.org/docs/format/Columnar.html)** _(official-doc)_ —— Arrow 内存格式 + FlightSQL + ADBC。

## 官方文档

- **[Trino Documentation](https://trino.io/docs/current/)** _(official-doc)_
- **[Apache Spark Documentation](https://spark.apache.org/docs/latest/)** _(official-doc)_
- **[Apache Flink Documentation](https://flink.apache.org/docs/)** _(official-doc)_
- **[DuckDB Documentation](https://duckdb.org/docs/)** _(official-doc)_

---

**待补**：Adaptive Query Execution 综述；向量化执行最新论文；查询引擎跨界对比
