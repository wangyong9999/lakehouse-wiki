---
title: OLAP 建模 · 星型 / 雪花 / 宽表 / Data Vault
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-18
applies_to: Kimball 维度建模（1996+）· Data Vault 2.0 · 湖仓宽表范式
tags: [bi, modeling, olap, kimball]
aliases: [数据建模, Dimensional Modeling, Data Warehouse Modeling]
related: [materialized-view, query-acceleration, lake-table, semantic-layer]
systems: [iceberg, paimon, starrocks, trino, dbt]
status: stable
---

# OLAP 建模

!!! tip "一句话理解"
    数仓建模有**四个主流范式**：Kimball 星型 / 雪花 / 宽表 / Data Vault 2.0。**湖仓时代宽表压倒式胜出**（列存 + 存储便宜 + 工具友好），但仍需理解 Kimball 的**事实表 / 维度表思维**——它是一切良好建模的基础。**2025 后 SCD Type 2 + 湖表 Time Travel 融合成为新范式**。

!!! abstract "TL;DR"
    - **四种范式**：星型（Kimball）· 雪花（Kimball 规范化）· **宽表 / One Big Table**（湖仓默认）· Data Vault 2.0（企业级审计）
    - **湖仓首选宽表**：列存 + 列剪裁 + 零 Join + BI 友好
    - **事实表粒度**是建模的第一问题（一行代表什么？）
    - **SCD Type 2** 记录维度演化 · Iceberg Time Travel 天然支持
    - **Medallion 分层**：ODS → DWD → DWS → ADS
    - **和语义层（dbt Semantic Layer / Cube）** 配合给业务一致的指标口径

## 1. 业务痛点 · 为什么要建模

### 不建模的代价

直接把 OLTP 表丢给 BI：
- **查询慢**：OLTP 行存 + 无聚合索引 → 分钟级
- **复杂 Join**：业务分析往往跨 5-10 张表
- **口径乱**：不同报表算不同的 GMV
- **维度变化不留痕**：用户改名，历史报表全错

建模的本质：**为"分析"而非"事务"组织数据**。

### 建模历史的三段

| 年代 | 范式 | 代表 |
|---|---|---|
| 1990s | Inmon 三范式 | 企业数仓 EDW |
| 1996+ | **Kimball 维度建模** | 星型 / 雪花 |
| 2010+ | Data Vault 2.0 | 审计级企业仓 |
| 2020+ | **宽表 / One Big Table** | 湖仓默认 |
| 2023+ | **OBT + Semantic Layer** | 现代数据栈 |

## 2. Kimball 维度建模 · 仍然必须懂

### 事实表 + 维度表

**事实表**：记录**发生的事情**（可聚合）
- 订单金额、点击次数、收入

**维度表**：记录**描述性属性**（可筛选）
- 谁下单（用户）、什么产品、什么地区、什么时间

### 星型（Star Schema）

```
        dim_user
           │
           ↓
dim_time → fact_orders ← dim_product
           ↑
           │
        dim_region
```

查询：
```sql
SELECT d_time.week, d_region.country, SUM(amount)
FROM fact_orders f
JOIN dim_time d_time ON f.time_key = d_time.time_key
JOIN dim_region d_region ON f.region_key = d_region.region_key
WHERE d_time.year = 2024
GROUP BY d_time.week, d_region.country;
```

### 雪花（Snowflake Schema）

维度再规范化：

```
dim_user → dim_city → dim_country
```

**湖仓几乎不用雪花**——存储省不了多少，Join 多一层。

### 星座（Galaxy / Fact Constellation）· 多事实共享维度

```
                dim_user
              ↗        ↘
     fact_orders     fact_page_view
              ↘        ↗
                dim_time
```

- 多个事实表**共享维度**（`dim_user`, `dim_time`, `dim_product`）· 这才是企业现实
- **一致性维度（Conformed Dimensions）** · Kimball 的核心治理概念——同一个 `dim_user` 在 orders/clicks/支付多个事实表里**必须是同一个定义**
- 湖仓落地：维度表物理只存一份 · 多事实表 join 时指向同一张——**避免每个事实表自己复制维度**（这是 OBT 宽表的反模式之一）

### 事实表三种粒度（关键）

| 类型 | 含义 | 例 |
|---|---|---|
| **Transactional**（事务）| 每笔记录 | 订单行、点击、支付 |
| **Periodic Snapshot** | 周期性快照 | 日结余额、月末库存 |
| **Accumulating Snapshot** | 累积过程 | 订单全生命周期（下单→支付→发货→签收）|

**最常见错误**：没想清粒度就建表。

### 事实表数值类型

| 类型 | 可聚合方式 |
|---|---|
| **加法**（amount, count）| SUM 任意维度 |
| **半加法**（balance, inventory）| 不能跨时间 SUM |
| **不加**（price, ratio）| 不能 SUM，只能 AVG / MIN / MAX |

## 3. 宽表（One Big Table, OBT）· 湖仓首选

### 湖仓为什么偏爱宽表

| 因素 | 效果 |
|---|---|
| **列存 + 列剪裁** | 宽但不读的列零成本 |
| **字典压缩** | 维度属性低基数 → 压缩比极高 |
| **没有 Join** | 扫一次出结果 |
| **存储便宜** | S3 GB 成本 ≪ CPU·h |
| **BI 友好** | 业务不用懂 Join |

经验：**存储多 5-10 倍 ↔ 查询快 5-20 倍 ↔ 总成本更低**。

### 宽表构建的两条路

**路径 A · 批 Rebuild**：
```
ods_orders + ods_users + ods_products
        ↓ Spark 日批
dwd_orders_flat (200 列)
```
适合维度变化慢。

**路径 B · 流式 Lookup Join**：
```
fact_stream ─Flink lookup join─→ dwd_orders_flat
       ↑ Redis / Cassandra / Paimon 维表
```
维度变了下一条就对齐；适合高频维度。

### 宽表的代价

- **重写开销**：维度变动要 rebuild
- **列 NULL**：某些维度只对部分记录有意义
- **Schema 演化复杂**：200 列加新列要 coordinate

### 宽表的反方观点 · 别盲信

宽表被吹过了。**以下场景宽表是反模式**：

- **高基数维度** · `dim_product` 有百万 SKU · 每行事实都拍平 = 存储膨胀
- **多事实共享维度** · 10 个 fact 表都拍一份 `dim_user` · 维护成本爆炸 · 违反一致性维度原则
- **维度频繁变更** · 宽表要全表 rebuild · 星型只改一个维度表
- **语义漂移** · 200 列宽表没人敢动 · 业务口径悄悄飘
- **多团队协作** · 不同团队建不同事实表但指向同一 `dim_user`——宽表让每个团队自建一份 · 口径必然分化

**务实建议**：
- **ADS 层**（面向 BI 的末层）· 宽表 + 星型混合 · 看业务 pattern
- **DWD/DWS 中间层** · 星型 + 一致性维度为主 · 宽表作为特定场景的短路
- **避免 300+ 列怪兽表** · 200 列内是健康上限 · 超过要拆分主题

### Iceberg 分区 × Kimball 建模的结合

湖仓特有：**Iceberg 的 bucket partition** 自然等价 Kimball 的**桶维度**。

```sql
CREATE TABLE fact_orders (
  order_id BIGINT, user_id BIGINT, product_id BIGINT,
  amount DECIMAL, order_ts TIMESTAMP
) USING iceberg
PARTITIONED BY (days(order_ts), bucket(64, user_id));
```

- `days(order_ts)` · 时间维度 · 查询剪枝
- `bucket(64, user_id)` · 按 user_id 哈希打散 · **等价于 Kimball 的 bucket dimension** · 防热点 + 利于 join
- Iceberg 的**Hidden Partitioning** 让 SQL 不用感知这些 partition transforms · 建模层面写自然 SQL 即可

**要点**：分区**不是建模** · 是物理布局 · 但和建模必须一致——事实表的主要 filter/join 列应该在分区键里。

## 4. Data Vault 2.0 · 企业级审计建模

### 什么场景需要

- **金融 / 医疗 / 合规严格**
- 需要**完整审计轨迹**
- 多源数据集成、口径多变

### 三个核心表类型

| 类型 | 作用 | 例 |
|---|---|---|
| **Hub** | 业务主键 + meta | `hub_customer (customer_id, load_ts, source)` |
| **Link** | 关联关系 + meta | `link_order_customer` |
| **Satellite** | 描述属性 + 时序 | `sat_customer_profile`（随时间变化） |

### 优势 / 劣势

- ✅ **审计完整**：每条变更记录 source + load timestamp
- ✅ **灵活加源**：新数据源加 Hub/Link 不破坏现有
- ❌ **查询复杂**：Join 多、需要 **Presentation Layer** 翻译给 BI
- ❌ **学习曲线陡**

**实务**：Data Vault 做底层 EDW、上面建**宽表 Mart** 给 BI。**DV + OBT 混合**是大型企业主流。

## 5. Medallion 分层（湖仓 de facto）

```
ODS (Bronze)    ← 原始 CDC / 日志
  ↓
DWD (Silver)    ← 清洗 + 标准化 + 宽事实表
  ↓
DWS (Gold)      ← 主题域汇总宽表
  ↓
ADS (Platinum)  ← 面向业务的指标表
```

### 各层职责

| 层 | 存储 | 更新 | 消费者 |
|---|---|---|---|
| **ODS** | Paimon / Iceberg 原始 | 实时 CDC | 数据工程 |
| **DWD** | Iceberg 宽事实表 | 小时 / 天 | 分析师 / 下游 |
| **DWS** | Iceberg + 分区 + Clustering | 天 | BI / 集市 |
| **ADS** | Iceberg + MV / 加速副本 | 小时 / 天 | BI 工具 / API |

## 6. SCD · Slowly Changing Dimension

维度会变。如何处理：

| 类型 | 机制 | 适合 |
|---|---|---|
| **Type 0** | 不变 · 历史值不更新 | 生日、出生地等事实属性 |
| **Type 1** | 覆盖，只留最新 | 人名改错、简单修正 |
| **Type 2** | 保留历史 + `valid_from` / `valid_to` + `is_current` | **合规 / 报表审计** |
| **Type 3** | 只保留上一版本（加 `prev_xxx` 列）| 快速前后对比 |
| **Type 4** | 历史放辅助表 · 主表只最新 | 大维度 · 历史访问少 |
| **Type 5** | 1+4 混合（mini-dimension + outrigger）| 快速变化的子属性 |
| **Type 6** | 1+2+3 混合（current + history + previous 都有）| 复杂业务 · 同时要当前 + 历史 + 一步回溯 |
| **Type 7** | 双键（surrogate for point-in-time + natural for current）| 最灵活 · 实现复杂 |

**实务选择**：
- **90% 场景用 Type 2** · 加 `valid_from/valid_to/is_current` 三列
- Type 4 用在大维度（百万行 · 多数历史冷数据）
- Type 6/7 只在业务明确要求"同时看当前和历史"时用
- Type 3 基本弃用——想要多历史用 Type 2 更通用

### Iceberg Time Travel 的新范式

**Iceberg Snapshot 天然就是 SCD Type 2**：
```sql
SELECT * FROM dim_users TIMESTAMP AS OF '2024-06-15';
```
查到 2024-06-15 那一刻用户的所有属性——**不需要显式维护 valid_from/valid_to**。

但生产仍**两者结合**：
- 显式 SCD Type 2 列给 BI 工具看
- Iceberg Snapshot 做审计回溯

### Kimball 进阶概念 · 宽表时代仍然管用

**Bridge Tables（桥接表）** · 多对多关系的维度（如用户-标签）：
- 不能拍进 fact 或单维度
- 独立桥表 + weight 列 · 避免重复计数

**Junk Dimensions（杂项维度）** · 低基数 flag 聚合：
- `is_vip`, `is_promotion`, `channel_type` 等
- 打进一张 `dim_junk` 避免 fact 表一堆小维度键

**Degenerate Dimensions（退化维度）** · 无属性的维度键（如 order_id）：
- 直接放 fact 表里 · 不建单独 dim 表
- 湖仓场景很多

**Role-playing Dimensions（角色扮演维度）** · 同一维度多角色（如 `dim_date` 同时做 `order_date` / `ship_date`）：
- 不复制维度 · 用 view 或 alias
- 湖仓用 view 更自然

## 7. 半结构化列 · VARIANT / STRUCT / JSON

湖仓 2024-2026 一个重要变化：**半结构化类型成为一等公民**。

- **Iceberg V3** · 新 `VARIANT` 类型（Databricks/Snowflake 共同推动）· 原生支持结构化 JSON
- **Delta** · 2024+ 支持 VARIANT
- **Parquet** · logical type 支持 STRUCT / MAP / LIST

**建模策略**：
- **高基数稀疏属性** · 如用户行为属性 · 200 个维度但每用户只有 20 个 · 用 VARIANT / JSON 列存 · 不打平
- **EAV 反模式** · 别把 (entity, attribute, value) 三列建表 · VARIANT 原生支持更好
- **访问性能** · VARIANT 列的点访问通过 shredded encoding（Iceberg V3 / Parquet 新 spec）接近列存性能
- **schema-on-read** · 新属性不需要改表结构 · 写入时放进 VARIANT

**限制**：
- BI 工具对 VARIANT 的支持参差——检查你的 Tableau/Superset 版本
- 聚合/过滤里的 JSON 路径 `variant_col.field1.sub2` 比列访问略慢
- 权限控制在 JSON 字段粒度目前仍弱——关键字段还是拍平建列

## 8. 建模陷阱

- **粒度不清就建表**：后面全部歪
- **事实表混 semi-additive 和 additive** 没标注
- **维度过多列 NULL**：语义混乱，考虑拆表或用 Sparse 格式
- **没有时间维度列**：无法做分区裁剪
- **时区不一致**：跨时区业务最常见灾难
- **手工维护 `valid_from` / `valid_to`**：容易错；**用 dbt snapshot 自动维护**
- **宽表无限扩列**：500+ 列的"怪兽表"没人改得动
- **Kimball + DV + OBT 混用无规范**：团队各按自己理解建，标签和口径乱

## 9. dbt + 现代建模

### 主流做法

```
models/
  staging/              # 1:1 源表清洗
    stg_orders.sql
  intermediate/         # 业务中间
    int_orders_with_user.sql
  marts/
    core/
      fct_orders.sql    # 事实表
      dim_users.sql     # 维度表
      dim_products.sql
    finance/
      fct_revenue.sql
    marketing/
      dim_campaigns.sql
```

### dbt Snapshot（SCD Type 2 自动）

```sql
{% snapshot dim_users_snapshot %}
{{
  config(
    target_schema='snapshots',
    unique_key='user_id',
    strategy='timestamp',
    updated_at='updated_at',
  )
}}
SELECT * FROM {{ ref('stg_users') }}
{% endsnapshot %}
```

运行 `dbt snapshot` 自动维护 SCD Type 2 列。

## 10. 性能数字

### 宽表 vs 星型（典型）

| 查询 | 星型 + Join | 宽表 |
|---|---|---|
| 简单聚合 | 5-15s | 1-3s |
| 多维分析 | 10-30s | 2-5s |
| 存储（10 亿行 × 200 列宽表）| 较少 | 多 2-3× |
| 增量更新成本 | 低 | 高 |

### 真实业务数据

- Pinterest：**主力用宽表**，查询 p95 < 5s
- Airbnb：**星型 + 宽表 Mart 双层**
- Shopify：**dbt + 宽表为主**，搭配 Kimball 思维

## 11. 延伸阅读 · 相关

### 权威阅读

- **[*The Data Warehouse Toolkit* (Kimball & Ross, 3rd ed., 2013)](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/)** —— 维度建模圣经
- **[*Building a Scalable Data Warehouse with Data Vault 2.0* (Linstedt, 2015)](https://www.elsevier.com/books/building-a-scalable-data-warehouse-with-data-vault-2-0/linstedt/978-0-12-802510-9)**
- **[dbt Best Practices](https://docs.getdbt.com/best-practices)**
- **[*Analytics Engineering with SQL and dbt* (O'Reilly, 2024)](https://www.oreilly.com/library/view/analytics-engineering-with/9781098142377/)**

### 横向相关

- [**语义层 · Semantic Layer**](semantic-layer.md) —— 指标中台
- [物化视图](materialized-view.md) · [查询加速](query-acceleration.md)
- [湖表](../lakehouse/lake-table.md) · [Iceberg Time Travel](../lakehouse/time-travel.md)
- [BI on Lake 场景](../scenarios/bi-on-lake.md)
