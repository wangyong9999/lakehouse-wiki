---
title: DuckDB · 嵌入式 OLAP 引擎
type: system
depth: 进阶
level: A
last_reviewed: 2026-04-20
applies_to: DuckDB 1.0+ (2024-06 GA) · 1.1/1.2/1.3 (2024-2025)
tags: [query-engine, olap, embedded]
category: query-engine
repo: https://github.com/duckdb/duckdb
license: MIT
status: stable
---

# DuckDB

!!! tip "一句话定位 · 嵌入式纯查询引擎"
    **嵌入式 OLAP 查询引擎**——SQLite 之于 OLTP，DuckDB 之于 OLAP。单文件二进制、进程内运行、直接读 Parquet / Iceberg / Delta。在湖仓场景里扮演"**开发 / 调试 / 轻量 BI / notebook**"的主力工具。**不是生产集群级引擎**——GB 到 TB 级单机可用；大规模走 Trino / Spark。

!!! info "向量化 ≠ 向量检索 · 和 retrieval/ 章节的边界"
    DuckDB 通过 **`vss` extension**（2024）提供向量索引 + 相似度查询；与 Lance 生态也有集成。区分同前：

    - **"向量化执行"** = DuckDB 本身的列式 SIMD 执行 · 所有查询都走
    - **"向量检索"** = vss extension 的 ANN 能力 · 详见 [多模检索](../retrieval/index.md)

    DuckDB 的向量能力**定位**在"本地分析里附带做向量查询"——和 LanceDB 形态接近但 LanceDB 是湖原生向量格式。纯向量工作负载走 [Milvus / LanceDB](../retrieval/vector-database.md)。

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

### Iceberg / Delta 扩展的现实边界

"读湖表" 概念简单，生产落地要认清 **extension 的边界**：

| 维度 | Iceberg extension | Delta extension |
|---|---|---|
| **读** | v2 表基础 CRUD OK · partition pruning 逐步完善 | 成熟度不错 |
| **写** | 仍在演进（append 先行 · upsert / merge 滞后）| 同 |
| **Catalog 对接** | 原生支持 REST Catalog / Glue · HMS 需额外配置 · Nessie / Polaris 依赖最新扩展版本 | Unity Catalog 兼容度持续完善 |
| **Branch / Tag / V3 Deletion Vector** | 跟进有滞后 · 追最新特性不建议 DuckDB | 同 |
| **大规模 metadata** | 超大 manifest（百万分区级）会在客户端处理 · 内存压力大 | 同 |

**实务建议**：**DuckDB 在湖表上的甜区是"读中小表 + 本地分析 + 快速验证"**——成长到百 GB-TB 单机够；PB 级或需要复杂 upsert / merge 的生产路径仍走 Spark / Trino。

### 对象存储鉴权 / 远程元数据的现实约束

- **S3 凭证**：需要配置 `httpfs` + 设置 access key / session token · 跨账号场景要处理 `AWS_PROFILE`
- **Vended Credentials**：REST Catalog 签发的临时凭证在最新扩展里支持 · 老版本手动管 credential
- **远程 metadata.json 读取**：每次 open table 要走对象存储 API · 大表可能数秒延迟
- **没有 metadata cache**（相对 Trino / Spark 的 Catalog client）· 高频 open/close 要自己层面做 cache

### 适合开发态的上限

**DuckDB 在湖仓里能推到哪里就不建议再走了**：

- **数据规模**：单机 GB - TB（内存越大越远）· **不超过 5-10 TB**（磁盘 spill 开始显性）
- **并发**：单用户 / 少并发 · **不是多租户生产引擎**
- **持续运行**：适合短任务 · 长驻 serving 场景建议换成 Trino 或 MotherDuck（云托管 DuckDB）
- **复杂湖表写**：MERGE / UPDATE / DELETE 在 extension 里仍在演进 · 生产写不推荐

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
