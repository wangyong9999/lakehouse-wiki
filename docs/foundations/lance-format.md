---
title: Lance Format
applies_to: "通用基础概念 · 长期稳定"
type: concept
level: B
tags: [foundations, file-format, multimodal, vector]
aliases: [Lance]
related: [parquet, vector-database, lancedb]
systems: [lance, lancedb]
status: stable
last_reviewed: 2026-04-18
---

# Lance Format

!!! tip "一句话理解"
    为**多模 + 向量 + 随机访问**重写的列式文件格式。保持 Parquet 的"列式 + 压缩"优点，但额外支持**行级随机读**、**向量索引内嵌**、**Fragment 级原子替换**（更新 / 删除不需要整表重写，但仍需写新 Fragment + 更新 manifest，不是原地改）——让"湖上做向量检索 + 机器学习"成为一等公民。

!!! note "Lance 的双重身份"
    Lance 同时具备两种身份，在本手册里分视角讲：

    - **文件格式视角**（本页）：和 [Parquet](parquet.md) · [ORC](orc.md) 并列的列式文件格式 —— 讨论物理布局 / 编码 / 随机读
    - **湖表底座视角**：Lance 自带 fragment 级事务 + manifest 版本化，作为 [LanceDB](../retrieval/lancedb.md) 的表协议；在 Iceberg 生态里也可作为 data file 格式之一（见 [湖表](../lakehouse/lake-table.md) 的数据文件层段）

    这是 Lance 与 Parquet/ORC 最大的结构差异 —— Parquet/ORC 只做"文件"，Lance 把"文件 + 简易表"打包了。

## 它为什么出现

Parquet 是为**批扫描**设计的：行号不是一等公民，随机读一行等于"解压整个 Page"。这对 BI 完全够用，但对**机器学习训练 + 向量检索**就不行：

- 训练需要**按 row_id 打乱洗牌**，Parquet 随机读成本高
- 向量检索需要**按 ANN 图跳跃访问**，每次一行
- 多模数据（图 / 视频 embedding）期望和元数据同表存放，还要能单独加索引

Lance 针对这些诉求重做。

## 关键设计

| 特性 | Parquet | Lance |
| --- | --- | --- |
| 随机读单行 | 慢（Page 级解压） | 快（Fragment + Row offset 原生支持） |
| 向量索引 | 无 | 原生支持 IVF-PQ / HNSW，存在同一文件家族中 |
| 更新 / 删除 | 重写 Row Group 或外部 delete file | Fragment 级原子替换，无需整张表重写 |
| 版本化 | 靠上层（Iceberg / Delta） | 文件格式自带 manifest 与 version |
| 多模扩展 | 需外部方案 | 二进制大字段 + 向量列原生 |

物理结构核心是 **Fragment**：每个 Fragment 是一组数据文件 + 一个 manifest；表由若干 Fragment 拼成。向量索引文件和 Fragment 是兄弟关系而非外挂。

**关于"更新"的现实检视**：Lance 并非原地改数据文件。删除是软标记（`deletion vector`），更新 = 生成新 Fragment + manifest 指向新版本。"免全表重写"成立，但**仍有写放大**（新 Fragment + 老 Fragment 垃圾回收）。高频点更新场景 Lance 不是首选，仍然应该走 KV / OLTP。

## 和 Parquet 的关系

**不是替代，是互补**。在典型湖上，两者常这样分工：

- **Parquet** —— 宽表 / BI 分析 / 通用批处理
- **Lance** —— 向量表 / 多模资产表 / ML 训练集

[LanceDB](../retrieval/vector-database.md) 和 Iceberg + Puffin 的未来是"让这两个世界能在同一 Catalog 下共存"。

## 使用形态

- **嵌入式**：`lance` 库直接读写 `.lance` 文件 / 文件夹
- **配 LanceDB**：在 Lance 之上加了 catalog、事务、向量检索 API
- **配 Iceberg**：作为 Iceberg 的数据文件格式之一（仍在演进）

## 相关概念

- [Parquet](parquet.md) —— 对照起点
- [向量数据库](../retrieval/vector-database.md) —— Lance 的主要下游
- [Puffin](../lakehouse/puffin.md) —— Iceberg 侧的"放索引"方案

## 延伸阅读

- Lance format: <https://github.com/lancedb/lance>
- *Lance v2: A columnar container format for modern data* (blog): <https://blog.lancedb.com/>
- LanceDB docs: <https://lancedb.github.io/lancedb/>
