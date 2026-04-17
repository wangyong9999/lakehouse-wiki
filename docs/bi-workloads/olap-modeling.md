---
title: OLAP 建模（星型 / 雪花 / 宽表）
type: concept
tags: [bi, modeling, olap]
aliases: [数据建模, Dimensional Modeling]
related: [materialized-view, query-acceleration, lake-table]
systems: [iceberg, paimon, starrocks, trino]
status: stable
---

# OLAP 建模（星型 / 雪花 / 宽表）

!!! tip "一句话理解"
    OLAP 有三种典型建模：**星型**（事实表 + 维度表）、**雪花**（维度表再拆层）、**宽表**（一张 flat 表把一切 join 进来）。湖仓时代**宽表压倒式胜出**，除非维度频繁变化。

## 三种模型

### 星型（Star Schema）

```
fact_orders
  ├── dim_user
  ├── dim_product
  ├── dim_time
  └── dim_region
```

事实表存可聚合的"发生了什么"，维度表存"谁、什么、何时、何地"的描述属性。查询时 join。

- **优点**：维度解耦、空间紧凑、维度变更简单
- **缺点**：查询时每次 join 都花钱

### 雪花（Snowflake Schema）

维度表再规范化（`dim_user → dim_city → dim_country`）。

- **优点**：进一步去冗余
- **缺点**：join 更多层，查询更慢
- **实战**：湖仓场景几乎不用——空间省不了多少，查询代价增加

### 宽表（Flat Wide Table）

所有维度 **预 join** 进事实表成一张几十到几百列的大表。

- **优点**：查询零 join，谓词下推 + 列剪裁直接起飞
- **缺点**：维度变化会引发重写；存储空间大
- **实战**：**湖仓场景的默认选择**

## 为什么湖仓偏爱宽表

- **列式 + 列剪裁**：宽但不读的列零成本
- **压缩好**：维度属性低基数，字典压缩压到极致
- **没有 join 成本**：一次扫描就出结果
- **存储便宜**：对象存储 GB 成本远低于计算 CPU·h
- **分析工具友好**：BI 工具直接查宽表，业务不用懂 join

经验：**存储多 5–10 倍 ↔ 查询快 5–20 倍 ↔ 总成本更低**。

## 构建宽表的两条路

### 路径 A：批定期 rebuild

```
ods_orders + ods_users + ods_products ──Spark─→ dwd_orders_flat
                                                 ↑ 每日全量或分区覆盖
```

简单，适合维度变化慢的场景。

### 路径 B：流式维度 join

```
fact_stream ──Flink 维表 Lookup Join──→ dwd_orders_flat
```

维度变了下一批就对齐；适合高频维度。

## 维度变化（SCD）

维度属性会变（用户改名、产品改价）。三种处理策略：

- **SCD Type 1**：覆盖（只留最新）—— 最简单
- **SCD Type 2**：保留历史 + 有效区间（`effective_from` / `effective_to`）
- **SCD Type 3**：只保留上一版本

湖表 + Time Travel 某种意义上天然就是 SCD Type 2（每个 snapshot 都是历史）。

## 分层约定

典型湖仓分 4 层：

| 层 | 职责 | 表形态 |
| --- | --- | --- |
| **ODS** | 业务库 CDC 原样 | 按业务表 |
| **DWD** | 清洗 + 宽表 | 主要宽事实表 |
| **DWS** | 汇总层 | 不同粒度的聚合表 |
| **ADS** | 应用层 / 集市 | 面向 BI 的最终表 |

越往下游越宽、越汇总、越为查询优化。

## 建模陷阱

- **维度过多列 NULL**：某些维度只对部分记录有意义 → 宽表里很多列 NULL → 压缩虽好但语义混乱。考虑拆宽表
- **事实表粒度不清**：一行代表什么？"一个订单" vs "一个订单行"？这个问题不想清楚后面全部歪
- **没有 `partition_date` / `dt`**：湖表没分区 = 查询全扫
- **时间列时区不一致**：跨时区业务最常见灾难

## 相关

- [物化视图](materialized-view.md)
- [查询加速](query-acceleration.md)
- [湖表](../lakehouse/lake-table.md)
- 场景：[BI on Lake](../scenarios/bi-on-lake.md)

## 延伸阅读

- *The Data Warehouse Toolkit* (Kimball & Ross) —— 维度建模圣经
- *One Big Table vs. Many Small Tables*（业内多篇对比）
