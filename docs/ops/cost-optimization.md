---
title: 成本优化
type: concept
tags: [ops, cost]
aliases: [Cost Optimization, FinOps]
related: [performance-tuning, compaction, observability]
systems: []
status: stable
---

# 成本优化

!!! tip "一句话理解"
    湖仓总成本 = **对象存储 + 计算 + API 调用 + 数据出口**。四项都要管。最大的隐藏成本是"**没用到的副本 + 没 compaction 的小文件 + 没归档的历史数据**"。

## 成本结构

典型云上湖仓一个月账单大致：

| 类别 | 占比 | 主要消耗 |
| --- | --- | --- |
| **对象存储** | 20–40% | 冷/热/多副本 |
| **计算** | 40–60% | Spark / Flink / Trino / 向量检索 |
| **API 调用** | 5–15% | S3 `LIST` / `GET` / `PUT` |
| **数据出口** | 0–20% | 跨区 / 跨云 traffic |

具体分布看负载类型，但**四项都不小**，哪个都不能忽略。

## 八条实操建议

### 1. 分层存储

- 热数据：S3 Standard
- 近线：S3 Infrequent Access（30 天以上不常访问）
- 冷数据 / 归档：S3 Glacier（合规存档）
- 规则用 **生命周期策略** 自动迁移，不手动搬

### 2. Snapshot 过期 + 孤儿文件清理

```sql
CALL system.expire_snapshots('db.t', TIMESTAMP '2026-03-01');
CALL system.remove_orphan_files('db.t', older_than => TIMESTAMP '2026-03-01');
```

不做这件事，**表占用会线性膨胀**，1 年 10 倍不稀奇。

### 3. Compaction 认真做

小文件让**每 GB 扫描成本翻倍**。参考 [Compaction](../lakehouse/compaction.md)。

### 4. 物化视图 & 加速副本的 ROI

每个 MV / StarRocks 副本都有成本。**按命中率裁剪**：

- 命中率 < 5% 的删
- 高命中的反而可以更激进地预计算

### 5. Compression Codec

- Parquet 默认 Snappy（快但压缩比弱）→ **Zstd level 3** 压缩比提升 20–30%，CPU 代价可接受
- Delete file 也记得压缩

### 6. 跨区 / 跨云慎配

S3 跨 region 的数据出口费贵。如果团队跨多云，用 **S3 对等 / 专用连接** 替代公网出口。

### 7. 列出"最贵 Top 10"

- 最贵的表（存储）
- 最贵的查询（计算 + IO）
- 最贵的作业（GPU·h / CPU·h）

每月 review 一次，Top 10 大概率藏着一个"**被遗忘的批作业 / 失控的索引重建**"。

### 8. 向量索引成本单独建账

GPU·h（embedding 生成）+ 索引内存 / SSD（索引存储）在快速增长的 AI 负载里常常被低估：

- HNSW 索引 = 原向量 × 1.2–1.5 内存
- 百亿向量 embedding 批量回填一次可能是数千 GPU·h

## 定期 review 清单

每季度至少一次：

- [ ] 过期 Snapshot / 孤儿文件回收是否在跑
- [ ] Top 10 大表 / 贵查询变化
- [ ] MV / 加速副本命中率
- [ ] 存储分层策略是否仍合理
- [ ] Compaction 作业健康度
- [ ] GPU / 向量相关开销
- [ ] 是否有 "阴间副本"（某团队一年前建的 debug 表）

## 陷阱

- **"存储便宜，算力贵" 的误区**：小文件问题让存储和算力**同时贵**
- **盲目开 caching / 加速副本**：没数据支持就是猜
- **把 Snapshot 保留窗拉很长**：90 天审计窗 = 90 天的重复文件
- **不关注出口**：开发者无感地从 S3 往外导 TB 级数据

## 相关

- [Compaction](../lakehouse/compaction.md)
- [性能调优](performance-tuning.md)
- [可观测性](observability.md)

## 延伸阅读

- *FinOps for Data Teams* —— a16z / Gradient Flow 等博客
- Databricks / Snowflake 官方 Cost Optimization 文档
