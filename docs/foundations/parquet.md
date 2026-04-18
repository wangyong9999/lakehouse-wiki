---
title: Parquet
type: concept
depth: 进阶
tags: [foundations, file-format]
aliases: [Apache Parquet]
related: [lake-table, object-storage, compression-encoding, predicate-pushdown]
systems: [parquet-mr, arrow-rs, duckdb]
applies_to: Parquet v1 / v2 · 2024-2026 主流实现
last_reviewed: 2026-04-18
status: stable
---

# Parquet

!!! tip "一句话理解"
    开源列式文件格式，把"按列组织 + 字典/RLE 压缩 + 内嵌统计信息"三件事做到了事实基线。湖仓 99% 的数据文件都是 Parquet。

!!! abstract "TL;DR"
    - **三层物理**：File → Row Group (~128-512MB) → Column Chunk → Page (~1MB)
    - **Footer 是元数据中心**：schema + 每 Row Group 每列的 `min/max/null_count` + 可选 Bloom Filter + 可选 Page Index
    - **读取路径**：先读 Footer → 决定哪些 Row Group / Page 需要读 → 只下载必要字节
    - **调优三刀**：Row Group 大小 · Page 大小 · 编码 / 压缩算法（见 [压缩与编码](compression-encoding.md)）
    - **Parquet v2**（2016+）加 Delta 编码 · Byte Stream Split · Page Index；主流引擎都已支持，但老生态仍跑 v1

## 1. 物理结构

```
File
├── Row Group 1                (一批行，默认 128-512MB)
│   ├── Column Chunk (col_a)
│   │   ├── Page Header
│   │   ├── Dictionary Page    (可选，低基数列)
│   │   └── Data Page 1, 2, ...  (每 Page ~1MB，最小 IO 单位)
│   ├── Column Chunk (col_b)
│   └── ...
├── Row Group 2
├── ...
└── Footer
    ├── File Metadata
    │   ├── Schema
    │   └── Per Row Group × Per Column 的统计:
    │       └── min · max · null_count · distinct_count · size
    ├── Column Index / Offset Index  (Parquet v2 的 Page Index)
    └── Footer Length + Magic "PAR1"
```

**阅读顺序**：读 Parquet 文件**必然先读 Footer**（文件末 4 字节是 `footer_length + "PAR1"`），所以对象存储上**尾部读取是关键优化**——用 HTTP Range 读最后 8-16KB 就能拿到 metadata。

## 2. 为什么重要

Parquet 让湖仓能做到**"只读必要的列、只读必要的 Row Group、只读必要的 Page"**：

1. **列剪裁** —— `SELECT a, b` 只读 a、b 两列的 Column Chunk，跳过其他
2. **Row Group 级谓词下推** —— `WHERE ts > '2026-01-01'` 先看每 RG 的 `min/max`，直接跳过不可能命中的 RG
3. **Page 级谓词下推**（v2 Page Index）—— 在命中的 RG 内，继续按 Page 过滤，粒度从 128MB 细到 1MB
4. **字典 / RLE / Bit-pack 编码** —— 见 [压缩与编码](compression-encoding.md)
5. **嵌套结构** —— 通过 definition/repetition levels（Dremel 论文的核心）支持 List / Map / Struct

## 3. Page Index · Parquet v2 的关键升级

**老 v1**：Row Group 级统计就够了，Page 内全读 → 128MB Row Group 命中 1 行也要读 128MB。

**v2 Page Index**：footer 里额外存
- **Column Index**：每 Page 的 min/max/null_count
- **Offset Index**：每 Page 的 file offset + 行数范围

读取时：Row Group 级过滤后 → 再查 Page Index 过滤 Page → **只下载命中的 Page**。对点查 / 小范围扫描是 10-100× 加速。

**注意**：
- Page Index 默认可能**不写**（某些 writer 需显式 `write_page_index=True`）
- 读端必须**显式开启** Page Index（例如 `pyarrow.parquet.ParquetFile(..., read_options=...)`）

```python
import pyarrow.parquet as pq

# 写：开 Page Index（v2.0 默认 False，需显式）
pq.write_table(
    table, 'events.parquet',
    compression='zstd',
    write_page_index=True,      # 关键
    data_page_version='2.0',
    row_group_size=1_000_000,   # 行数，不是字节
    data_page_size=1 << 20,     # 1 MiB
)

# 读：谓词下推由引擎自动做，但可以观察
pf = pq.ParquetFile('events.parquet')
print(pf.metadata)                  # 全文件元数据
print(pf.metadata.row_group(0))     # 第 0 个 RG 的统计
print(pf.schema_arrow)              # Arrow schema
```

## 4. Bloom Filter

**Row Group 级**可选 Bloom Filter，主要用于**高基数等值过滤**（`WHERE user_id = 'xxx'`）——min/max 对 uuid/hash 无用，Bloom 能排除"一定没有"的 RG。

**取舍**：
- 每列独立开关（Parquet writer 参数 `bloom_filter_columns`）
- 空间成本几 KB 到几十 KB 每 RG · 查询时额外读一次
- **只对高基数 + 频繁等值过滤的列开**（user_id / order_id / uuid）

## 5. 调优三刀

### Row Group 大小

| 场景 | 建议 |
|---|---|
| BI 大扫描 | 256-512 MB（减少 metadata 开销 + 利用并行） |
| 频繁点查 / 小范围 | 64-128 MB（提升过滤粒度） |
| 对象存储高延迟 | 较大（摊薄 Range 请求开销） |

**Iceberg / Paimon 默认写 128MB**，一般不必改。

### Page 大小

默认 1MB；**v2 + Page Index** 场景可以考虑降到 256KB-512KB 提升过滤粒度（代价是 Page Header 开销）。

### 压缩 + 编码

见 [压缩与编码](compression-encoding.md)。**默认用 Zstd level 3**，极端场景再调。

## 6. 湖仓里的实际使用

- Iceberg · Paimon · Hudi · Delta 的**默认数据文件格式**都是 Parquet
- Row Group 大小 + 压缩算法 **继承表级 property**（`write.parquet.row-group-size-bytes`）
- 大多数引擎（Spark / Trino / DuckDB / Flink）都支持 v2 Page Index；**遇到老读端**需要降级到 v1

## 7. 现实检视

- **"Parquet 是列式数据压缩的事实基线"** —— 是。但 2024+ **Lance / Vortex / Nimble（Meta）**在挑战 Parquet 的"随机读 + 编码效率"短板，未必会取代但值得关注
- **"开 Page Index 就一定快"** —— 不一定。大扫描场景 Page Index 额外开销 > 收益；只对**选择率低（< 1%）**的查询明显有效
- **"Bloom Filter 万灵"** —— 空间 + 读放大成本可观，**低基数列反而有害**（min/max 已足够）

## 8. 陷阱

- **小文件爆炸**：写端 RG 太小（< 32MB）→ footer 占比大、读 amplification 严重。每张表定期 Compaction
- **Schema 跨文件漂移**：Parquet 自身不管 schema 演化，依赖上层（Iceberg / Delta）
- **Timestamp 单位混乱**：v1 的 INT96（已弃用）vs v2 的 `TIMESTAMP(MILLIS/MICROS/NANOS)`，跨引擎可能读成本地时区错位 → **统一用 UTC + MICROS**
- **Snappy 老默认**：2020 前写的表大量用 Snappy，**Compaction 时可以切 Zstd 额外省 30-50% 空间**
- **读端不显式传 filters**：PyArrow / DuckDB / Spark 都支持 `filters=[...]` 下推；忘记传就全表读

## 9. 和邻居的关系

- **[ORC](orc.md)** —— Hive 生态更偏爱，语义与 Parquet 高度重合但细节不同（Stripe ≈ Row Group）
- **[Lance Format](lance-format.md)** —— 专为向量 / 机器学习加入行级随机读与向量索引原生支持
- **[Arrow](arrow-ecosystem.md)** —— 内存格式而非文件格式，但和 Parquet 是"同一个社区两个镜像"
- **Vortex · Nimble**（2024+ 新）—— 更激进的编码 · 延迟解码 · 向量化友好

## 10. 延伸阅读

- **[Parquet format spec](https://github.com/apache/parquet-format)** —— 二进制细节一手来源
- **[Parquet Encodings](https://github.com/apache/parquet-format/blob/master/Encodings.md)** —— 每种编码的 layout
- **[*Dremel · Interactive Analysis of Web-Scale Datasets*](https://research.google/pubs/pub36632/)** (Google, VLDB 2010) —— Parquet 嵌套表示的理论源头
- **[DuckDB · Parquet Internal](https://duckdb.org/2023/03/03/parquet-whitepaper.html)** —— 工程博客：一个现代引擎如何读 Parquet
- **[Parquet File Format · Influx Data 深入](https://parquet.apache.org/docs/file-format/)**

## 相关

- [对象存储](object-storage.md) —— Parquet 文件的物理载体
- [湖表](../lakehouse/lake-table.md) —— 怎么把一堆 Parquet 文件组织成"一张表"
- [压缩与编码](compression-encoding.md) · [谓词下推](predicate-pushdown.md) · [列式 vs 行式](columnar-vs-row.md)
