---
title: DuckDB
type: system
tags: [query-engine, olap, embedded]
category: query-engine
repo: https://github.com/duckdb/duckdb
license: MIT
status: stable
---

# DuckDB

!!! tip "一句话定位"
    **嵌入式 OLAP 引擎**——SQLite 之于 OLTP，DuckDB 之于 OLAP。单文件二进制、进程内运行、直接读 Parquet / Iceberg / Delta。在湖仓场景里扮演"开发 / 调试 / 轻量 BI"的主力工具。

## 它解决什么

不是每一次查询都值得拉起集群。DuckDB 解决：

- **本地探索** —— `duckdb -c "SELECT ... FROM 's3://.../*.parquet'"` 一行命令
- **CI 测试** —— 快速跑完一批 SQL，无需外部服务
- **Edge BI** —— Python / Node / 浏览器里嵌入，单机对几十 GB Parquet 做分析
- **学习与教学** —— 无服务端，学湖仓概念的最佳工具

## 技术亮点

- **向量化执行**：列式 + SIMD，吞吐非常高
- **零拷贝读 Parquet / Arrow / JSON / CSV**
- **Iceberg / Delta 扩展**：直接打开湖表
- **HTTP FS / S3 FS**：直接读远程对象存储
- **WASM build**：能在浏览器里跑 OLAP

## 和湖仓的关系

- **读** —— 对 Parquet 极致优化，Iceberg / Delta 作为 extension 支持
- **写** —— 直接写 Parquet / Iceberg（extension 支持度不如读）
- **角色**：主力不是生产查询引擎，而是"开发态的湖上 SQL 瑞士刀"

## 和 Trino / Spark 的差异

- **单机**：DuckDB 不分布式（生产场景分布式诉求仍然选 Trino / Spark）
- **进程内**：像库一样嵌入应用，没有服务端
- **启动零延迟**：毫秒级启动，对 CI / 轻量分析极其友好

## 典型用法

```bash
# 命令行直接查湖上 Parquet
duckdb -c "SELECT count(*) FROM 's3://bucket/table/*.parquet' WHERE ts > '2026-01-01'"

# 打开 Iceberg 表
duckdb -c "INSTALL iceberg; LOAD iceberg; \
           SELECT * FROM iceberg_scan('s3://bucket/warehouse/db.table')"

# Python 集成
import duckdb
df = duckdb.sql("SELECT avg(price) FROM 'data.parquet'").to_df()
```

## 陷阱与坑

- **分布式诉求**要另选引擎；DuckDB 不是为集群设计
- **写入湖表的生产依赖** 还不成熟，主力仍应放在 Spark / Flink
- **版本迭代极快**，语法与 extension 偶有 breaking change

## 延伸阅读

- DuckDB docs: <https://duckdb.org/docs/>
- *DuckDB: an embeddable analytical database* (SIGMOD 2019)
