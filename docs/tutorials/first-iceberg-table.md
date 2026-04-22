---
title: 你的第一张 Iceberg 表
type: tutorial
depth: 入门
applies_to: pyiceberg 0.9+ · DuckDB 1.5.2+（2026-Q2）
last_reviewed: 2026-04-18
tags: [tutorial, iceberg, duckdb, pyiceberg]
status: stable
---

# 你的第一张 Iceberg 表

!!! tip "你会做完"
    - 本地跑起来一个 Iceberg 目录（不用集群、不用云）
    - 建一张 Iceberg 表，写入 10 万行，跑 SQL 查
    - 体验 **Snapshot / Schema Evolution / Time Travel** 三大核心能力
    - 全程 **30 分钟**，全部在 Python + DuckDB

## 前置

- Python 3.10+
- 没了。

## Step 1 · 装两个包

```bash
pip install "pyiceberg[duckdb,sql-sqlite]" pandas pyarrow
```

`pyiceberg[duckdb,sql-sqlite]` 安装 Iceberg 的 Python 客户端 + DuckDB 查询后端 + 用 SQLite 做 Catalog（最轻量选择）。

## Step 2 · 建一个"假湖"目录

```bash
mkdir -p /tmp/iceberg_lab/warehouse
cd /tmp/iceberg_lab
```

对象存储就用本地文件系统模拟。Catalog 就用一个 SQLite 文件。

## Step 3 · 配 Catalog

```python
# lab.py
from pyiceberg.catalog.sql import SqlCatalog

catalog = SqlCatalog(
    "local",
    **{
        "uri": "sqlite:///iceberg_catalog.db",
        "warehouse": "file:///tmp/iceberg_lab/warehouse",
    },
)
catalog.create_namespace("lab")
print("Catalog ready.")
```

```bash
python lab.py
```

**预期输出**：`Catalog ready.`

## Step 4 · 建表 + 写入 10 万行

```python
# populate.py
import pandas as pd
import pyarrow as pa
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, IntegerType, StringType, DoubleType, TimestampType

catalog = SqlCatalog("local", uri="sqlite:///iceberg_catalog.db",
                     warehouse="file:///tmp/iceberg_lab/warehouse")

schema = Schema(
    NestedField(1, "order_id", IntegerType(), required=True),
    NestedField(2, "user_id", IntegerType(), required=True),
    NestedField(3, "region", StringType(), required=True),
    NestedField(4, "amount", DoubleType(), required=True),
    NestedField(5, "ts", TimestampType(), required=True),
)

tbl = catalog.create_table("lab.orders", schema=schema)

# 生成 10 万行假数据
import random, datetime
random.seed(42)
rows = [
    {
        "order_id": i,
        "user_id": random.randint(1, 5000),
        "region": random.choice(["cn", "us", "eu", "sea"]),
        "amount": round(random.uniform(10, 1000), 2),
        "ts": datetime.datetime(2026, 1, 1) + datetime.timedelta(seconds=i * 37),
    }
    for i in range(100_000)
]
df = pd.DataFrame(rows)

tbl.append(pa.Table.from_pandas(df, preserve_index=False))
print("Wrote 100k rows. Snapshots:", [s.snapshot_id for s in tbl.metadata.snapshots])
```

```bash
python populate.py
```

**预期输出**：`Wrote 100k rows. Snapshots: [<数字>]`

到这里你应该能看到磁盘上：

```
/tmp/iceberg_lab/warehouse/lab.db/orders/
├── data/                      # Parquet 数据文件
│   └── 00000-*.parquet
└── metadata/
    ├── 00000-*.metadata.json  # 表根元数据
    ├── snap-*.avro            # manifest list
    └── *-m0.avro              # manifest
```

这就是**[湖表](../lakehouse/lake-table.md)的物理形态**——元数据文件 + 数据文件。

## Step 5 · 用 DuckDB 查

```python
# query.py
import duckdb

con = duckdb.connect()
con.sql("INSTALL iceberg; LOAD iceberg;")

# DuckDB 直接读 Iceberg 表目录
con.sql("""
  SELECT region, count(*) AS n, round(sum(amount), 2) AS total
  FROM iceberg_scan('/tmp/iceberg_lab/warehouse/lab.db/orders')
  GROUP BY region ORDER BY n DESC
""").show()
```

```bash
python query.py
```

**预期输出**：

```
┌─────────┬───────┬──────────┐
│ region  │   n   │  total   │
├─────────┼───────┼──────────┤
│ cn      │ 25068 │ ~12M     │
│ us      │ 24978 │ ~12M     │
│ eu      │ 24964 │ ~12M     │
│ sea     │ 24990 │ ~12M     │
└─────────┴───────┴──────────┘
```

**你刚刚用 DuckDB 读了一张 Iceberg 表，中间没有任何集群**。

## Step 6 · Schema Evolution（不重写历史）

```python
# evolve.py
from pyiceberg.catalog.sql import SqlCatalog

catalog = SqlCatalog("local", uri="sqlite:///iceberg_catalog.db",
                     warehouse="file:///tmp/iceberg_lab/warehouse")
tbl = catalog.load_table("lab.orders")

# 加一列
with tbl.update_schema() as update:
    update.add_column("channel", "string", required=False)

print("New schema:", tbl.schema())
```

```bash
python evolve.py
```

再查一次 Step 5，你会看到 `channel` 列存在但老数据是 NULL —— **历史没重写**，这就是 [Schema Evolution](../lakehouse/schema-evolution.md) 的意义。

## Step 7 · Time Travel

```python
# time_travel.py
from pyiceberg.catalog.sql import SqlCatalog

catalog = SqlCatalog("local", uri="sqlite:///iceberg_catalog.db",
                     warehouse="file:///tmp/iceberg_lab/warehouse")
tbl = catalog.load_table("lab.orders")

print("All snapshots (按时间排序):")
for s in sorted(tbl.metadata.snapshots, key=lambda s: s.timestamp_ms):
    print(f"  id={s.snapshot_id} ts={s.timestamp_ms} ops={s.summary}")
```

列出所有 snapshot。在 DuckDB 里用 `snapshot_id` 参数就能读回任意版本。

## 跑不通的自查

| 症状 | 可能原因 |
| --- | --- |
| `pyiceberg` 找不到 | Python 版本 < 3.10 |
| `ImportError: duckdb` | 装时没加 `[duckdb]` extra |
| SQLite "database is locked" | 两个 python 进程同时连了同一个 catalog.db |
| DuckDB `IO Error` | 路径拼错，写绝对路径试试 |
| 空表查询 | `append` 前 schema 定义错了 |

## 你现在明白了什么

- [湖表](../lakehouse/lake-table.md)是一组**元数据文件 + 数据文件**的协议，不是一个进程
- [Snapshot](../lakehouse/snapshot.md) 让时间旅行天然成立
- [Schema Evolution](../lakehouse/schema-evolution.md) 不重写历史
- DuckDB 作为**嵌入式 OLAP 引擎**能直接读 Iceberg 表

## 下一步

- [你的第二条路：多模检索 Demo](multimodal-search-demo.md)
- 系统读：[Apache Iceberg](../lakehouse/iceberg.md) · [Snapshot](../lakehouse/snapshot.md) · [Manifest](../lakehouse/manifest.md)
- 速查：[Apache Iceberg](../lakehouse/iceberg.md)
