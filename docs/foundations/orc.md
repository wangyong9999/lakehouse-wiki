---
title: ORC
type: concept
tags: [foundations, file-format]
aliases: [Apache ORC, Optimized Row Columnar]
related: [parquet, lance-format]
systems: [hive, spark, trino]
status: stable
---

# ORC（Optimized Row Columnar）

!!! tip "一句话理解"
    和 Parquet 平行的另一套列式文件格式，由 Hive 社区主推。语义与 Parquet 高度重合，统计信息与谓词下推做得稍微精细，但**生态覆盖不如 Parquet**，新项目通常直接选 Parquet。

## 结构概要

```
File
├── Stripe 1         (默认 64MB，类似 Parquet 的 Row Group)
│   ├── Index Streams        (min/max、position、bloom filter)
│   ├── Data Streams (列 a)
│   ├── Data Streams (列 b)
│   └── Stripe Footer
├── Stripe 2
└── File Footer      (schema + 每 Stripe 每列的统计)
    └── Postscript   (指向 Footer 的元信息)
```

一个 Stripe 就是 Parquet 的 Row Group；一个 Column Stream 就是 Parquet 的 Column Chunk。

## 和 Parquet 的主要差异

| 维度 | ORC | Parquet |
| --- | --- | --- |
| 主社区起源 | Hive | Impala / Cloudera / Twitter |
| 统计精度 | 更细（索引层次更多）| 够用 |
| 嵌套类型 | 支持（定义/重复级别扁平化）| Dremel 式 levels |
| 字典压缩 | 支持 | 支持 |
| Bloom filter | 内建 | 可选（文件内独立 section · per column chunk · 和 Page Index 是两套机制） |
| 生态覆盖 | Hive 生态强 | 几乎所有引擎、工具、云服务 |
| 湖表格式支持 | Iceberg / Hudi 支持但非默认 | Iceberg / Paimon / Delta / Hudi 默认 |

## 什么时候还会遇到它

- **历史 Hive 存量** —— 很多公司的 ODS/DWD 长期是 ORC，迁湖仓时两种格式会并存一段时间
- **部分优化器场景** —— 某些引擎（Trino）对 ORC 的谓词下推做得略深
- **HDFS 时代遗物** —— 和 ZLIB/SNAPPY 老栈结合得特别稳

## 新项目要不要选

**默认选 Parquet**。Parquet 生态更广、工具更全、向量 / ML 方向（Arrow 同源）协同更好。ORC 在今天只是"兼容 Hive 存量"的存在。

## 相关

- [Parquet](parquet.md)
- [Lance Format](lance-format.md) —— 多模场景的下一代

## 延伸阅读

- Apache ORC docs: <https://orc.apache.org/>
- *Evolution of Data Formats at Hortonworks* 历史回顾
