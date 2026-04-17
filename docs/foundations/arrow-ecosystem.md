---
title: Arrow · FlightSQL · ADBC
type: concept
depth: 进阶
prerequisites: [columnar-vs-row, parquet]
tags: [foundations, arrow, interchange]
related: [parquet, duckdb, spark, vectorized-execution]
systems: [arrow, duckdb, polars, pyspark, lance]
status: stable
---

# Arrow · FlightSQL · ADBC · 内存与传输的公共层

!!! tip "一句话理解"
    **Parquet 是磁盘格式，Arrow 是内存格式**。DuckDB / Spark / Polars / Iceberg Python / LanceDB 都用 Arrow 作为公共内存布局 —— 零拷贝跨组件传数据。**FlightSQL** 是 Arrow 数据的 gRPC 协议，**ADBC** 是统一的 SQL 客户端 API。三件一起把"读数据"从"串行化三次"降到"几乎零拷贝"。

!!! abstract "TL;DR"
    - Parquet（磁盘）↔ Arrow（内存）是现代数据栈的**双层标准**
    - Arrow 列式内存布局 → SIMD 友好、跨语言、零拷贝
    - **FlightSQL**：把 Arrow 当传输格式的 SQL 协议，比 JDBC / ODBC 快 10–100×
    - **ADBC**：类似 ODBC 但默认 Arrow，去序列化开销
    - 你已经在用 Arrow：每次 DuckDB 读 Parquet、Pandas DataFrame、Polars、Iceberg Python 都经它

## Arrow：内存里的 Parquet

Arrow（Apache Arrow）定义**列式内存表示**：

- **列连续存放**：每列一个连续内存块（SIMD-friendly）
- **固定偏移 + 变长数据**：字符串 / 数组 / 结构体都有标准表示
- **跨语言 ABI**：C / C++ / Rust / Java / Python / Go 对同一块内存的读法一致
- **零拷贝**：同一进程内不同库共享 buffer 指针，不做数据搬运

### 和 Parquet 的关系

| 维度 | Parquet | Arrow |
| --- | --- | --- |
| 位置 | 磁盘 / 对象存储 | 内存 |
| 是否压缩 | 是（字典 / RLE / Zstd） | 否（为了 SIMD） |
| 读取后 | 解压 + 解码到 Arrow | 直接可用 |
| 编辑性 | 只读 | 可构造 / 切片 |

读 Parquet 本质上就是"**Parquet → Arrow**"的解码过程；Arrow 是结果的通用内存形态。

## 为什么是基础设施级

几乎所有你在用的工具**共享 Arrow 作为 exchange 格式**：

```
┌─────────────────────────────────────────────────┐
│   Pandas  Polars  DuckDB  Spark  LanceDB        │
│   Dask    pyiceberg  Turbo-Vote  etc.           │
│                                                 │
│                    ▼                            │
│             Apache Arrow                        │
│      (列式内存 + 跨语言 ABI + 零拷贝)            │
│                    ▲                            │
│                                                 │
│   Parquet ↔ ORC ↔ CSV ↔ JSON ↔ Lance ↔ 对象存储   │
└─────────────────────────────────────────────────┘
```

- **Pandas → Polars**：`df.to_polars()` 零拷贝（都基于 Arrow）
- **Spark → Python UDF**：PySpark 用 Arrow 传数据到 Python（快 10 倍比旧 pickle 路径）
- **DuckDB → Pandas**：`con.execute(sql).df()` 零拷贝
- **Iceberg Python → 任意**：PyIceberg scan() 返回 Arrow Table，下游随便用
- **Lance ↔ Arrow**：Lance 文件读出即是 Arrow

**一句话**：Arrow 是现代数据栈的"以太网"——底层通用管道。

## FlightSQL：Arrow 专用的 SQL 协议

传统 `JDBC / ODBC`：
1. 服务端把列式数据序列化成"行"
2. 编码成 JDBC/ODBC wire format
3. 客户端反序列化回"行"
4. 再转成 Pandas / Polars 时还得变列式

3 次数据搬运 + 2 次格式转换。**慢**。

**FlightSQL**（Apache Arrow Flight SQL）：
1. 服务端直接发 Arrow batches
2. gRPC 流传输
3. 客户端直接 Arrow Table，零转换

吞吐提升 **10–100 倍**，延迟显著降低。典型使用：

- **Dremio** 作为默认查询协议
- **DuckDB FlightSQL** 作为服务端 adapter
- **Spark Connect** 底层基于 Arrow Flight
- **Iceberg REST** 在考虑作为结果传输协议

## ADBC：统一的 "Arrow 友好"客户端

**ADBC**（Arrow Database Connectivity）= 对 ODBC 的重做，默认 Arrow in/out：

```python
import adbc_driver_postgresql.dbapi

conn = adbc_driver_postgresql.dbapi.connect("postgresql://...")
cursor = conn.cursor()
cursor.execute("SELECT * FROM events")
arrow_table = cursor.fetch_arrow_table()   # 直接 Arrow，不是 list of tuples
df = arrow_table.to_pandas()               # 零拷贝
```

驱动层面覆盖 Postgres / Snowflake / BigQuery / DuckDB / FlightSQL 等。**统一接口替代 ODBC + 性能 10×**。

## 生态关键 OSS

- **pyarrow**：Arrow 的 Python 包，事实标准
- **arrow-rs / arrow-cpp**：底层实现
- **parquet-cpp / parquet-rs**：Parquet reader，输出 Arrow
- **DataFusion**：Apache 项目，Rust 实现的 Arrow-native 查询引擎（Ballista 分布式版）
- **Polars**：Rust 写的 DataFrame 库，Arrow-native
- **DuckDB**：虽然不直接暴露 Arrow 内存布局，但 I/O 层全是 Arrow

## 工程启示

- **Python 数据代码优先用 Arrow / Polars，少用 Pandas**：Pandas 基于 NumPy，字符串 / 嵌套类型性能差
- **跨服务传数据走 FlightSQL 或 Arrow IPC**：比 JSON / Protobuf 快一个数量级
- **ETL 输出优先 Parquet（磁盘）+ Arrow（内存交换）** 组合
- **Iceberg + PyArrow**：`pyiceberg` 的 `scan().to_arrow()` 是团队数据流水线首选入口

## 陷阱

- **Arrow 内存模型假设列连续**：行级随机访问成本高（Lance 就是为了解决这个问题设计的）
- **Arrow 不是压缩格式**：内存占用 > Parquet；Spill to disk 要搭配 Parquet
- **跨进程用 IPC，不用 Shared Memory**：进程间用 Arrow IPC stream；不要盲目 mmap
- **ADBC 驱动覆盖仍在扩展**：MySQL 等某些库还缺

## 相关

- [Parquet](parquet.md) —— 磁盘侧的孪生
- [列式 vs 行式](columnar-vs-row.md) —— 基础
- [向量化执行](vectorized-execution.md) —— Arrow 内存布局的直接受益
- [DuckDB](../query-engines/duckdb.md) —— 典型 Arrow-native 引擎
- [Lance Format](lance-format.md) —— Arrow-native，但加了随机访问

## 延伸阅读

- Apache Arrow 官方：<https://arrow.apache.org/>
- Arrow Flight SQL spec
- *The Composable Codex*（InfluxData / Voltron 等多家推广的数据栈模块化观点）
- *In-memory Databases – A Sync Between Bytes and Computation*（Red Book 章节）
