---
title: OLTP vs OLAP
type: concept
tags: [foundations, workload]
aliases: [Transactional vs Analytical]
related: [columnar-vs-row, lake-table, mvcc]
systems: [postgres, innodb, clickhouse, iceberg]
status: stable
---

# OLTP vs OLAP

!!! tip "一句话理解"
    **OLTP**（Online Transaction Processing）是"每次改几行、每秒几千次、强一致"；**OLAP**（Online Analytical Processing）是"每次扫几十 GB、每秒几次、强吞吐"。两种负载的物理底层几乎**完全相反**——所以湖仓 (OLAP) 不是 DB (OLTP)。

## 两种负载对比

| 维度 | OLTP | OLAP |
| --- | --- | --- |
| 典型查询 | `SELECT * FROM orders WHERE id = ?` | `SELECT region, sum(amt) FROM orders GROUP BY region` |
| 数据量/次访问 | 几行 | 百万–百亿行 |
| 并发 | 万–十万级 | 十–百级 |
| 延迟目标 | 毫秒 | 秒 |
| 写频率 | 高，行级 | 低，批级 |
| 读/写比 | 相近或偏写 | 读 >> 写 |
| 一致性 | 强（ACID） | 弱-中（最终或快照） |
| 存储 | 行式（页 16KB） | 列式（文件百 MB） |
| 索引 / 跳过结构 | B+Tree、LSM、Hash | Min/Max、Zone Map、Bloom、Page Index |
| 计算 | 单进程 / 主备 | 分布式 / MPP |

## 为什么它们在物理底层对立

1. **存储结构不同**：OLTP 要"整行快"，列式天然慢；OLAP 要"少列快"，行式白扫
2. **并发模型不同**：OLTP 高并发 → MVCC / 锁；OLAP 少查询 → 无共享进程，各算各的
3. **延迟目标不同**：毫秒级 vs 秒级 → 索引深度 + 数据分布选择完全两码事
4. **一致性模型不同**：ACID 强约束 vs 快照/最终一致

## 两个世界的代表

- **OLTP**：PostgreSQL、MySQL InnoDB、Oracle、SQL Server、dstore 等业务库
- **OLAP**：ClickHouse、StarRocks、Snowflake、Iceberg/Paimon/Delta 湖仓、BigQuery
- **HTAP（混合）**：TiDB、SingleStore、GaussDB DWS 等 —— 想"一个系统两种用"，但通常两头不极致

## 中间地带

- **半 OLTP**（高频写分析）：ClickHouse MergeTree + ReplacingMergeTree
- **流式湖仓**（高频入湖 + 近实时查）：Paimon / Hudi
- **向量库**：更像 OLAP（批写 + 向量检索）但有自己一套

## 怎么在一体化湖仓里处理 OLTP

一体化湖仓**不是要取代 OLTP**，是要把 OLTP 的变化**高效落到 OLAP 侧**：

- OLTP 继续用 Postgres / MySQL / dstore 跑业务
- Flink CDC / Debezium 实时抽 binlog
- 落到 Paimon / Iceberg（湖上 OLAP 侧表）
- BI / AI 从湖消费

详见 [流式入湖](../scenarios/streaming-ingestion.md)。

## 陷阱

- **用 OLTP 做 BI** —— 慢且影响主业务；数据量上来会直接崩
- **用 OLAP 做点查** —— 毫秒 SLA 做不到
- **HTAP 万能幻觉** —— 宣称"一栈解决"的系统在极端场景下都要妥协

## 相关

- [列式 vs 行式](columnar-vs-row.md)
- [MVCC](mvcc.md)
- [湖表](../lakehouse/lake-table.md)
- [DB 引擎 vs 湖表](../compare/db-engine-vs-lake-table.md)

## 延伸阅读

- *Architecture of a Database System* (Hellerstein, Stonebraker, Hamilton)
- *The Seattle Report on Database Research* (2022) —— 对近 10 年演进的综述
