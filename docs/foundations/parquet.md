---
title: Parquet
type: concept
tags: [foundations, file-format]
aliases: [Apache Parquet]
related: [lake-table, object-storage]
systems: [parquet-mr, arrow-rs, duckdb]
status: stable
---

# Parquet

!!! tip "一句话理解"
    开源列式文件格式，把"按列组织 + 字典/RLE 压缩 + 内嵌统计信息"三件事做到了事实标准。湖仓 99% 的数据文件都是 Parquet。

## 它是什么

Parquet 是一种**开放的列式二进制文件格式**，最早由 Twitter + Cloudera 基于 Google Dremel 论文设计。一个 Parquet 文件的物理结构是三层：

```
File
├── Row Group 1             (一批行，默认 128MB)
│   ├── Column Chunk (col_a)
│   │   └── Page 1, Page 2, ...   (每 Page 是最小 IO 单位)
│   ├── Column Chunk (col_b)
│   └── ...
├── Row Group 2
└── Footer  (schema + 每 Row Group 每列的统计信息)
```

## 为什么重要

Parquet 让湖仓能做到**"只读必要的列和只读必要的 Row Group"**：

1. **列剪裁（column pruning）** —— 查询 `SELECT a, b` 只读 a、b 两列的 chunk，跳过其他
2. **谓词下推（predicate pushdown）** —— 查询 `WHERE ts > '2026-01-01'` 先看 Row Group 的 `min/max` 统计，直接跳过不可能命中的 Row Group
3. **字典 / RLE 压缩** —— 低基数列（枚举、状态）压缩比极高
4. **嵌套结构** —— 通过 definition/repetition levels 支持 List / Map / Struct，不必像 JSON 丢失类型

## 湖仓里的实际使用

- Iceberg / Paimon / Hudi / Delta 的**默认数据文件格式**就是 Parquet
- Row Group 大小和 Page 大小是**需要调优**的——太小会放大小文件问题，太大会削弱谓词下推

## 和邻居的关系

- **ORC** —— Hive 生态更偏爱，语义与 Parquet 高度重合但细节不同
- **Lance format** —— 专为向量 / 机器学习加入随机访问与向量索引原生支持
- **Arrow** —— 内存格式而非文件格式，但和 Parquet 是"同一个社区两个镜像"

## 相关概念

- [对象存储](object-storage.md) —— Parquet 文件的物理载体
- [湖表](../lakehouse/lake-table.md) —— 怎么把一堆 Parquet 文件组织成"一张表"

## 延伸阅读

- Parquet format spec: <https://github.com/apache/parquet-format>
- *Dremel* (Google, 2010): <https://research.google/pubs/pub36632/>
- *Impala: A Modern, Open-Source SQL Engine for Hadoop* (CIDR 2015)
