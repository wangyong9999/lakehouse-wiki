---
title: Apache Doris
type: system
tags: [query-engine, olap, mpp]
category: query-engine
repo: https://github.com/apache/doris
license: Apache-2.0
status: stable
---

# Apache Doris

!!! tip "一句话定位"
    MPP 分析型数据库，和 [StarRocks](starrocks.md) 同源（都源自百度 Palo）。定位、架构、能力高度重合；近年在**湖仓融合**方向（直读 Iceberg / Hudi / Paimon）投入很大。中国社区活跃。

## 它解决什么

和 StarRocks 基本一致：高并发 OLAP + 多表 join + 物化视图 + 直读湖表。在国内社区选型时常常和 StarRocks 放一起比较。

## 架构

- **FE（Frontend）** + **BE（Backend）** 架构（与 StarRocks 同构）
- 存算一体（Internal Table）+ 存算分离（Compute Node 直读湖表）
- 向量化执行 + Pipeline 执行模型

## 对湖仓的关键能力

- 内部表：明细 / 主键 / 聚合 / Unique 多种模型
- 外部表 / Catalog：Hive / Iceberg / Hudi / Paimon / JDBC
- **Asynchronous Materialized View** —— 跨内部表 + 外部表
- **存算分离模式**：数据在对象存储，计算节点弹性伸缩

## 和 StarRocks 怎么选

两者非常相近，在实战差异：

| 维度 | StarRocks | Doris |
| --- | --- | --- |
| **开源治理** | Linux Foundation（原 StarRocks Inc.）| Apache 顶级 |
| **向量化深度** | 内部重写更彻底，benchmark 略优 | 持续追平 |
| **湖仓集成（Iceberg / Paimon）** | 较早，成熟 | 近年快速补齐 |
| **社区生态** | 全球更活跃，国际案例多 | 中国社区深厚 |
| **企业背书** | StarRocks Inc. 商业公司 | 飞轮、百度、选手多 |

**没有"绝对更好"**。建议：

- 已有选型的继续跟进
- 新项目两者都 POC 一轮，看自家负载

## 什么时候选

- 需要 MPP + 湖仓融合
- 中国内需求 / 社区支持偏好
- 想要 Apache 社区治理（Doris）

## 陷阱

- **版本差异**：两者的 roadmap 非一致，某些特性名字相同含义不同
- **生态二选一成本低但运维分流** —— 两套都用成本更高，建议选一个
- **存算分离模式**还相对新，生产案例积累中

## 相关

- [StarRocks](starrocks.md) —— 主要对比对象
- [Trino](trino.md) / [ClickHouse](clickhouse.md) —— 其他 OLAP 选项
- 场景：[BI on Lake](../scenarios/bi-on-lake.md)

## 延伸阅读

- Apache Doris docs: <https://doris.apache.org/>
- *A Deep Comparison: Apache Doris vs StarRocks* —— 社区多篇对比文
