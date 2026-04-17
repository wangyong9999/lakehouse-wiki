---
title: Compaction（合并）
type: concept
tags: [lakehouse, ops, maintenance]
aliases: [文件合并, File Compaction]
related: [lake-table, streaming-upsert-cdc, delete-files]
systems: [iceberg, paimon, hudi, delta]
status: stable
---

# Compaction（合并）

!!! tip "一句话理解"
    把湖表里**过多的小文件 + 过多的 delete 文件**重写成更紧凑的大文件。不 compaction 的湖表几个月内会烂——查询变慢、元数据膨胀、成本失控。**不是可选项，是必修课**。

## 为什么会产生小文件

湖表的写入方式决定了小文件是必然：

- **流式 upsert** —— 每个 commit 都落一个新文件
- **多 writer 并发** —— 每个 writer 自己写文件
- **分区粒度细** —— 每个分区每个 commit 一个文件
- **delete 文件** —— row-level delete 在 MoR 下一直累加

几百万小文件会发生什么：

- 查询要打开 N 个文件句柄（IO 放大）
- 元数据扫描（LIST / HEAD）比数据扫描还贵
- Parquet 每个文件的 footer 固定成本摊不开
- 存储系统（S3）API 调用收费线性上升

## 两类操作

### Bin-pack / Rewrite

把若干**小文件合并成一个大文件**，内容不变（保持排序可能变）。

```sql
-- Iceberg
CALL system.rewrite_data_files(
  table => 'db.events',
  options => map(
    'target-file-size-bytes', '536870912',  -- 512MB
    'min-file-size-bytes',    '67108864'    -- < 64MB 算小
  )
)
```

### Merge / Clean（处理 delete）

MoR 表要周期合并 **base + delta** 成新 base，丢弃已 compact 的 delete 文件。否则每次读都要做昂贵的运行时 merge。

Hudi 称之为 `compaction`，Paimon 叫 `full-compaction`，Iceberg 叫 `rewrite_position_deletes` + `rewrite_data_files`。

## 调度策略

| 触发条件 | 说明 | 适合场景 |
| --- | --- | --- |
| 小文件数 > 阈值 | 最常见触发 | 大多数批/流 |
| delta / base 比 > X% | 应对 MoR 合并 | 高频 upsert |
| 分区内 max 文件大小 < Y | 追求查询稳定 | BI 仪表盘 |
| 时间窗（每天 / 每小时） | 最简单 | 稳定流入湖 |

生产上通常是"时间窗 + 阈值"组合，避开业务高峰。

## 成本估算

- **读放大**：输入小文件总大小 × 1（重写一次）
- **写放大**：输出新文件总大小
- **对象存储 API 成本**：LIST / GET / PUT 计费
- **计算资源**：Spark/Flink compaction 作业的 CPU·h

Benchmark 经验：没 compaction 的表可能让查询成本高 **3–10 倍**；compaction 自身成本通常只占总 IO 成本的 5–15%。

## 陷阱

- **和写入竞争**：并发 commit 冲突，需要 Catalog 层 CAS 与重试策略
- **压缩时读 IO 打爆**：大表 rewrite 一次是几 TB IO，要限流
- **失败后 orphan 文件**：compact 中途崩了遗留垃圾，靠 `remove_orphan_files` 清理
- **排序丢失**：bin-pack 不保证排序；如果查询依赖 Z-order / Liquid Clustering，要用 sort-compaction

## 和运维的关系

大规模湖表的 **Compaction 其实就是"运维的主要开销"**。Databricks / Tabular 等商业平台把它做成"自动托管"是有原因的——自己搞要持续维护若干 Spark/Flink 作业、监控、告警。

## 相关

- [Streaming Upsert / CDC](streaming-upsert-cdc.md) —— 小文件的主要来源
- [Delete Files](delete-files.md) —— MoR compaction 的第二个主题
- [性能调优](../ops/performance-tuning.md) —— compaction 是其中一环
- [成本优化](../ops/cost-optimization.md)

## 延伸阅读

- Iceberg Maintenance: <https://iceberg.apache.org/docs/latest/maintenance/>
- *The Hidden Costs of a Data Lake*（Onehouse / Tabular 各有博客）
