---
title: 即席探索 / Notebook 分析 · 数据科学家的主战场
applies_to: "2024-2026 工业实践"
type: scenario
depth: 进阶
prerequisites: [lake-table, duckdb]
tags: [scenario, ad-hoc, notebook, data-science]
related: [bi-on-lake, business-scenarios, classical-ml]
status: stable
last_reviewed: 2026-04-18
---

# 即席探索 / Notebook 分析

!!! tip "一句话理解"
    **数据科学家 / 分析师打开 Jupyter 随手查数据**。延迟敏感（< 10s）、单机或小集群、Snapshot 锁定保复现。核心武器是 **DuckDB + pyiceberg + Polars**——零配置上路，对湖表直接读，不需要启动 Spark 集群。

!!! abstract "TL;DR"
    - **核心要求**：启动快 · 本地跑 · < 10s 出结果 · Snapshot 锁定可复现
    - **黄金组合**：**DuckDB + pyiceberg + Polars + Jupyter + Quarto**
    - **规模感**：单机 Notebook 扛 **TB 级湖表**没问题
    - **不适合**：百 TB+ 超大规模或高并发（需要 Trino / Spark）
    - **典型场景**：验证假设、出图、特征实验、一次性分析

## 1. 场景定位

### 和其他分析场景的区别

| | 即席探索 | BI 仪表盘 | ETL |
|---|---|---|---|
| 用户 | 分析师 / DS | 业务 | 数据工程 |
| 频率 | 每次都不同 | 固定 | 固定 |
| 延迟 | < 10s | < 3s（走 MV）| 分钟-小时 |
| 并发 | 低（几人）| 高（百人）| 低 |
| 复现 | 重要 | 重要 | 次要 |
| 工具 | Notebook | BI 工具 | Airflow |

### 典型工作流

```
假设：女性用户 18-25 岁的 VIP 转化率显著高于其他群体
    ↓
查一下各性别 × 年龄段 × VIP 的比例
    ↓
DuckDB 对 Iceberg 直接 SELECT
    ↓
Polars 处理 + matplotlib 出图
    ↓
发现：假设不成立，但 25-35 岁男性 VIP 转化率高
    ↓
继续验证 ...
```

## 2. 技术栈

### 核心：DuckDB + pyiceberg

**DuckDB**：
- **嵌入式 OLAP DB**（类比 SQLite 之于 OLTP）
- 单机、零配置
- C++ 列式执行引擎，极快
- **Iceberg 扩展** + **Delta 扩展** + **S3** 支持

**pyiceberg**：
- Iceberg 的 Python 原生客户端
- 支持 REST / Hive / Glue catalog
- 懒加载 metadata，只拉 snapshot
- 集成 PyArrow / Polars / Pandas

### 辅助

- **Polars**：DataFrame 操作，比 Pandas 快 5-10×
- **Pandas**：生态最广但慢
- **Plotly / matplotlib / altair**：可视化
- **Quarto**：可复现 notebook 转 HTML / PDF

### 快速起步

```bash
pip install duckdb pyiceberg polars pyarrow ipykernel
```

## 3. 核心管线示例

### 从 Iceberg 读取 + 本地分析

```python
import duckdb
import polars as pl
from pyiceberg.catalog.rest import RestCatalog

catalog = RestCatalog(
    "prod",
    uri="https://catalog.corp/v1",
    warehouse="s3://lake/warehouse",
)

table = catalog.load_table("db.orders")

# 方法 1: 直接用 pyiceberg 查 + PyArrow
arrow_table = table.scan(
    row_filter="ts >= '2024-12-01'",
    selected_fields=["user_id", "amount", "region"],
).to_arrow()

df = pl.from_arrow(arrow_table)

# 方法 2: 用 DuckDB 查 Iceberg（需 DuckDB Iceberg 扩展）
duckdb.sql("INSTALL iceberg; LOAD iceberg;")
result = duckdb.sql("""
SELECT region, SUM(amount) AS gmv
FROM iceberg_scan('s3://lake/warehouse/db/orders', allow_moved_paths=true)
WHERE ts >= '2024-12-01'
GROUP BY region
""").pl()
```

### Snapshot 锁定保复现

```python
# 锁定到特定 snapshot
table = catalog.load_table("db.orders").snapshot(snapshot_id=1234567890)
```

Notebook 开头记录 snapshot_id，**别人重跑拿到同样结果**。

### 混合 Pandas / Polars / DuckDB

```python
# 从 Iceberg 拉数据
pdf = table.scan(row_filter=...).to_pandas()

# DuckDB SQL over DataFrame
duckdb.sql("SELECT region, AVG(amount) FROM pdf GROUP BY region").pl()

# Polars 高性能
pl_df = pl.from_pandas(pdf)
result = (pl_df.group_by("region")
               .agg(pl.col("amount").mean())
               .sort("amount", descending=True))
```

## 4. 性能 / 规模

### DuckDB 单机规模

| 数据规模 | 场景可行 |
|---|---|
| < 100 GB | 完全本地（笔记本 16GB 内存）|
| 100 GB - 1 TB | 单机云服务器（c5.2xlarge 32GB） |
| 1-10 TB | 单机大内存机（r5.4xlarge 128GB）|
| > 10 TB | 走 Trino / Spark |

### 典型 Iceberg Scan 性能

| 操作 | 本地 DuckDB |
|---|---|
| 10 GB Iceberg 表聚合 | 5-15s |
| 100 GB 过滤 + 聚合 | 30-60s |
| 1 TB 大扫描 | 5-15 分钟 |
| 分区裁剪后扫 | 快 10×+ |

**关键**：
- **Predicate Pushdown** 让 `WHERE ts >= ...` 只读匹配分区
- **Column Pruning** 只读需要的列
- **Manifest + 统计** 让 file-level skip 有效

## 5. 工程细节

### 本地开发 + 远程存储

- AWS credentials 在 `~/.aws/credentials`
- DuckDB `CREATE SECRET (TYPE S3, ...)` 管理
- 不要硬编码 credential 到 notebook

### Notebook 最佳实践

- **开头锁 snapshot** + 记录环境（pip freeze）
- **避免太多 print**（大 DataFrame 别直接输出）
- **缓存中间结果**（`%store` 或 pickle）
- **Quarto 发布**：notebook → HTML 报告

### 大规模探索的降级

如果 DuckDB 本地扛不住：

1. **先缩数据**：`SAMPLE 0.01`  看趋势
2. **走 Trino**：pyarrow / pyiceberg 连 Trino
3. **走 Spark**：Spark Connect 远程调用

### 并发注意

DuckDB 单机**不适合高并发**。多人同时开 Notebook 查同一 Iceberg 表是 OK 的（每人本地 DuckDB），但**共享 DuckDB 实例**不推荐。

## 6. 代码示例 · 完整一个分析

```python
# 场景：分析本月 VIP 用户的购买漏斗
import polars as pl
import duckdb
import matplotlib.pyplot as plt
from pyiceberg.catalog.rest import RestCatalog

# 1. 连接 + 锁定 snapshot
cat = RestCatalog("prod", uri="...", warehouse="s3://...")
orders = cat.load_table("db.orders")
print(f"Using snapshot: {orders.current_snapshot().snapshot_id}")

# 2. 拉用户 + 订单数据
users_df = cat.load_table("db.users").scan(
    row_filter="vip_level > 0"
).to_polars()

orders_df = orders.scan(
    row_filter="ts >= '2024-12-01'",
    selected_fields=["user_id", "order_id", "status", "amount", "ts"]
).to_polars()

# 3. Polars 聚合
funnel = (orders_df
    .join(users_df.select(["user_id", "vip_level"]), on="user_id")
    .group_by(["vip_level", "status"])
    .agg([
        pl.count().alias("count"),
        pl.sum("amount").alias("gmv"),
    ])
    .sort(["vip_level", "status"]))

print(funnel)

# 4. 可视化
funnel.to_pandas().pivot(index="vip_level", columns="status", values="count") \
    .plot(kind="bar", stacked=True)
plt.title("VIP Level × Status")
plt.savefig("vip_funnel.png")
```

## 7. 陷阱与反模式

- **数据全拉到 Pandas**：10 GB 爆内存；用 Polars 或 DuckDB
- **没锁 snapshot**：今天 AUC 0.85 明天 0.83 → 数据变了
- **Notebook 一堆全局状态**：别人重跑拿不到同结果；用 Papermill / Quarto
- **直连 OLTP 探索**：业务系统崩 → 走湖表副本
- **把 DuckDB 当 production**：单机 OK 但高并发 / 服务不行
- **没 `LIMIT`**：`SELECT *` 等几分钟
- **忽视分区**：`WHERE year > 2020` 比 `WHERE extract(year from ts) > 2020` 快 10×（分区裁剪）
- **本地 notebook 直接写生产**：应该只读；写走 ETL pipeline

## 8. 可部署参考

- **[DuckDB + Iceberg Tutorial](https://duckdb.org/docs/extensions/iceberg)**
- **[pyiceberg Getting Started](https://py.iceberg.apache.org/)**
- **[Jupyter + DuckDB cookbook](https://motherduck.com/blog/)**
- **[Quarto + Notebook](https://quarto.org/)**
- **[MotherDuck](https://motherduck.com/)** —— DuckDB-as-a-Service 商业版

## 9. 和其他场景的关系

- **vs [BI on Lake](bi-on-lake.md)**：BI 是**稳定高并发仪表盘**，探索是**灵活单人分析**
- **vs [经典 ML](classical-ml.md)**：探索常是 ML 的前置环节（特征发现）
- **vs [Text-to-SQL](text-to-sql-platform.md)**：Text-to-SQL 让业务"类探索"，但上限有限

## 延伸阅读

- **[DuckDB 文档](https://duckdb.org/docs/)** · **[DuckDB 论文 (SIGMOD 2020)](https://dl.acm.org/doi/10.1145/3299869.3320212)**
- **[Polars Cookbook](https://docs.pola.rs/)**
- **[pyiceberg](https://py.iceberg.apache.org/)**
- **[*Jupyter Cookbook* (O'Reilly)](https://www.oreilly.com/library/view/jupyter-cookbook/9781788839440/)**
- **[Quarto Guides](https://quarto.org/docs/guide/)**

## 相关

- [BI on Lake](bi-on-lake.md) · [经典 ML 预测](classical-ml.md)
- [DuckDB](../query-engines/duckdb.md) · [Trino](../query-engines/trino.md)
- [业务场景全景](business-scenarios.md)
