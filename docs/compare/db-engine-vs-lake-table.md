---
title: DB 存储引擎 vs 湖表
applies_to: "2024-2026 主流"
type: comparison
tags: [comparison, lakehouse, storage]
subjects: [db-storage-engine, lake-table]
status: stable
last_reviewed: 2026-04-17
---

# DB 存储引擎 vs 湖表

!!! tip "读完能回答的选型问题"
    面对一份数据，到底应该放进一个"数据库"里，还是落成一张"湖表"？两者的根本差异在哪？边界在哪？

## 对比维度总表

| 维度 | 数据库存储引擎（InnoDB、RocksDB、dstore…） | 湖表（Iceberg、Paimon、Hudi、Delta） |
| --- | --- | --- |
| **物理单位** | Page（KB 级） | File（百 MB 级 Parquet/ORC） |
| **并发控制** | 进程内锁 + MVCC | 对象存储原子 rename / CAS + Snapshot 切换 |
| **修改粒度** | 原地更新行 / 页 | 写新文件 + Manifest 差量 |
| **服务进程** | 必须有一个 DB 进程居中 | 无状态，读写方各自直连对象存储 |
| **读写协同** | 共享内存 / WAL / 锁 | 元数据协议 |
| **主要场景** | OLTP、明细点查、强事务 | 明细分析、批量、流式湖仓、AI 数据准备 |
| **典型数据量/表** | GB – 中 TB | TB – PB |
| **写入延迟** | 毫秒 | 秒–分钟（commit 粒度） |
| **读取延迟** | 微秒–毫秒（索引） | 百毫秒–秒（文件扫描） |
| **典型 throughput** | 万 QPS 写 | GB/s 批量写 |
| **索引** | B+Tree / LSM / Hash / Bitmap | Min-Max / Bloom / Z-order / Puffin（可扩展） |
| **行级修改** | 直接支持 | 靠 delete vector / MoR 合并 |
| **开放性** | 引擎私有格式 | 开放格式 + 开放协议，任意引擎可读写 |
| **生态** | 垂直（每个 DB 自己一套） | 水平（Spark / Flink / Trino / DuckDB / …） |

## 每位选手的关键差异

### DB 存储引擎

**"把表藏在进程之后"**。所有读写都通过一个共享进程排队、加锁、走 WAL、写 Page。这让它天生擅长：

- 低延迟的行级读写
- 强一致、高频的小事务
- 基于索引的点查 / 小范围扫描

代价是：计算必须贴着这个进程跑；数据格式私有；扩容与多引擎共享困难。

### 湖表

**"把表摊在对象存储里"**。表 = 一堆不可变文件 + 一组元数据。读写方各自直连对象存储，只通过元数据协议协同。这让它天生擅长：

- PB 级批量分析
- 多引擎（Spark / Flink / Trino / DuckDB / 自家引擎）读同一张表
- 流式入湖、批分析共存
- AI 数据准备（训练数据需要被多种引擎消费）

代价是：commit 粒度偏粗；行级修改贵；不适合高频点查。

## 什么时候选谁

- **选 DB 存储引擎如果**
    - 在线业务事务：订单、账户、库存、会话
    - 高频小事务、强一致性、毫秒延迟
    - 单引擎独占即可，不需要跨系统共享

- **选湖表如果**
    - 明细事实表、行为日志、埋点
    - 需要多个引擎（Spark 批、Trino 交互、DuckDB 开发）读同一份数据
    - 需要时间旅行、Schema/Partition 演化
    - 要被 AI 消费（训练集、检索语料、特征离线表）

- **可以混用的中间带**
    - OLTP → CDC → 湖仓：业务库留在 DB 里，用 Flink CDC / Debezium 把变化实时同步到 Paimon / Iceberg
    - 湖仓 → 加速层：Trino/StarRocks 直读湖表；热数据通过物化视图或 ClickHouse 加速

## 混用 / 迁移路径

**入湖**（DB → Lake）：
几乎都走 CDC。Flink CDC / Debezium → Kafka → Paimon（流式原生）或 Iceberg（通过 Spark Streaming）。

**出湖**（Lake → DB）：
较少见。通常是把湖仓聚合结果写回 OLTP/OLAP 做在线服务；此时湖仓只是"产出源"。

## 相关

- [湖表](../lakehouse/lake-table.md) —— 湖表侧的深入
- [Apache Iceberg](../lakehouse/iceberg.md) —— 湖表的参考实现
- [对象存储](../foundations/object-storage.md) —— 湖表的物理载体

## 延伸阅读

- *Lakehouse: A New Generation of Open Platforms* (CIDR 2021)
- *Architecture of a Database System* (Hellerstein, Stonebraker, Hamilton, 2007)
- Apache Iceberg Spec v2: <https://iceberg.apache.org/spec/>
