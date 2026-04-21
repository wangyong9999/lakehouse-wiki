---
title: 查询加速 · 数据布局 + 二级索引 + 加速副本机制
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: Iceberg 1.10+/v3 · Delta Liquid Clustering · Paimon 1.4+ · StarRocks/Doris · Puffin · Lance
tags: [bi, optimization, lakehouse, clustering, index, accelerator]
aliases: [查询加速, 数据布局优化, Data Layout Optimization]
related: [materialized-view, olap-modeling, lake-table, compaction, dashboard-slo]
systems: [iceberg, delta, paimon, starrocks, trino, spark]
status: stable
---

# 查询加速 · 数据布局 + 二级索引 + 加速副本机制

!!! tip "一句话定位"
    **把物理数据按查询 pattern 重新排 + 建索引 + 必要时同步到本地列存副本**——让谓词下推跳过绝大部分数据。不改 SQL 不加机器 · 也能把查询从 30s 降到 3s。湖仓 BI 性能调优的头等招式。

!!! abstract "TL;DR · 三层加速栈"
    - **第一层 · 数据布局**：分区 · Sort · Z-order · Liquid Clustering（Delta 独有 GA · Iceberg 侧 2026 Public Preview）
    - **第二层 · 二级索引**：Parquet footer stats · Bloom Filter · Iceberg Puffin · Lance 向量/标量索引
    - **第三层 · 加速副本**：当湖上引擎仍打不到仪表盘 SLO（p95<1s / 并发>100）· 上 StarRocks/ClickHouse/Doris 镜像
    - **决策顺序**：布局优化 → 二级索引 → MV → 加速副本 · 层层递进 · **别一上来就副本**
    - **和 [物化视图](materialized-view.md) 互补不互斥** · 加速让扫快 · MV 让不扫

## 1. 核心原理 · 扫得少比扫得快重要

湖表查询的瓶颈通常不是"扫得慢"而是"扫了太多没必要扫"。每层文件 metadata 都是潜在的剪枝点：

| 层级 | 含什么 | 剪什么 |
|---|---|---|
| **Iceberg manifest list** | 每 manifest 的 partition range | 整批 manifest |
| **Iceberg manifest** | 每 data file 的 partition value + 列 min/max | 整个文件 |
| **Parquet footer** | 每 row group 的列 min/max + bloom filter | row group |
| **Parquet page index** (2022+) | 每 page 的列 min/max | data page |
| **Puffin / Lance 外挂索引** | 值-文件/位置倒排 · 向量 ANN | file 或 row |

**关键**：min/max 有没有用 · 取决于数据**物理是否聚集**。同一 `user_id` 分散在 1000 个文件 · 每个文件 min/max 都是 `[0, max]` · 剪枝失败。

**加速的本质**就是让**物理排列**匹配**查询 pattern**。

## 2. 数据布局 · 第一层

### 2.1 分区（Partitioning）· 粗粒度

粗粒度按列值切目录/文件组。典型 `PARTITIONED BY (days(ts), bucket(16, shop_id))`。

- **Iceberg Hidden Partitioning** · SQL 直接 `WHERE ts >= '...'` 自动走分区 · **不要用 `extract(year)` 这类表达式**（破坏 partition pruning）
- **Partition Evolution** · Iceberg 独有 · 不用重写历史数据改分区
- **过度分区坑**：每分区 < 100MB 就是小文件灾难 · 健康是 256MB-1GB
- **bucket transform** · 打散防倾斜 · 对 join key 或 high-cardinality 列有用

### 2.2 Sort Order · 单列范围查询

把数据按某列**全局排序**再重写。

- **Iceberg `rewrite_data_files(sort_order=...)`** · 按时间列排序 · 时间范围查询极快
- **Paimon Order / Zorder** · 物理排序 compaction 时生效
- **局限**：单列 sort 对其他列完全无帮助 · `ORDER BY ts` 对 `WHERE user_id = ...` 0 收益

### 2.3 Z-order · 多维 Morton 曲线

把 2-5 列通过 Morton 交错编码映射到一维 · 保留多维局部性。

- **Delta `OPTIMIZE ... ZORDER BY (col1, col2)`**
- **Iceberg `rewrite_data_files(sort_order=...)` + Z-order strategy**
- **效果递减**：每列都受益但都**不如单列 sort 好**；3-5 列 Z-order 是效果极限 · 再多就每维都差
- **不是万能**：基数极高列（如 UUID）Z-order 意义小

### 2.4 Liquid Clustering · Databricks Delta 2024 GA · Iceberg 侧 Public Preview

**痛点**：传统 Sort/Z-order 需要**预定义列** + 大量重写。数据/查询 pattern 变了 · 改分区键是 O(N) 代价。

**Liquid Clustering 的想法**：
- **不预定义**分区键 · 系统按 **clustering keys** 自适应组织数据
- 根据**实际查询历史**自动调整 clustering
- **增量 reorganize** · 不需要全量重写
- 多 key 聚集 · 比 Z-order 理论最优

**2026-04 生产状态**：
- **Delta Lake · GA**（Databricks 2024 推出 · 2025 生态广泛）
- **Apache Iceberg 侧** · 规范本身**还没有统一的 clustering**（只有 sort_order）· Databricks 2026-04 V3 Public Preview 里支持 managed Iceberg 的 liquid clustering · 但**不在 Iceberg spec 本身**
- **社区 proposal 进行中** · 但跨引擎统一支持仍未到位

**选型提示**：Databricks 生态用 · 其他引擎等规范 · 暂用 Z-order 替代。

### 2.5 三者决策树

```
查询 pattern 稳定 · 1 个主排序列？
  └─ 单列 Sort · 最简最有效
查询 pattern 稳定 · 2-4 列组合 filter？
  └─ Z-order 这 2-4 列
查询 pattern 经常变 · 在 Databricks 生态？
  └─ Liquid Clustering
查询 pattern 经常变 · 不在 Databricks 生态？
  └─ 目前仍是 Z-order + 定期 review · 或改走加速副本
```

## 3. 二级索引 · 第二层

Parquet footer 的列 min/max 是**天然索引**但有局限：

- 只对**物理聚集**的数据有效（见 §1）
- 无法点查（`WHERE user_id = X` 只有 min/max 是范围命中 · 不是精确命中）
- 高基数离散列效果差

因此需要**外挂二级索引**。

### 3.1 Parquet Bloom Filter · 点查命中

每 row group 一个 Bloom Filter · 判断 "某值是否可能存在"。

- **Iceberg / Delta / Spark / Trino 都支持写入 Parquet bloom**
- **点查命中率高**（低 false positive）· 范围查询帮不上
- **写入开销** · 每 row group 多几 KB · 大 table 可观

```sql
-- Iceberg 写入时指定 bloom
ALTER TABLE orders SET TBLPROPERTIES (
  'write.parquet.bloom-filter-enabled.column.user_id' = 'true'
);
```

### 3.2 Iceberg Puffin · 元数据 sidecar 格式

Iceberg 在 spec 层定义了 **Puffin** · 让**任意 blob 元数据**挂到 snapshot。

- **目前主要用途** · NDV sketch（COUNT DISTINCT 加速）· Bloom filter · 定制统计
- **未来可期** · 社区在推 bitmap index / BSI / 向量索引 走 Puffin
- **对比 Lance** · Puffin 是 metadata 外挂 · 不改变 Parquet 格式 · 和 Iceberg 生态更自然
- **详见** [Puffin vs Lance](../compare/puffin-vs-lance.md)

### 3.3 Lance · 索引即一等公民

Lance 文件格式原生支持：
- **标量索引**（B-tree / Bitmap）· 点查/范围
- **向量索引**（IVF/HNSW）· ANN
- **FTS 索引**（BM25）· 全文检索

BI 场景下 · Lance 适合**单表高频查询 + 索引驱动**的加速副本场景 · 传统湖表 + Puffin 的组合仍是主流。

### 3.4 Bitmap / Bit-sliced Index · 高基数聚合

- **Bitmap Index** · 每可能值一个位图 · 低基数列最优（性别/状态/类别）· 高基数膨胀
- **Bit-sliced Index (BSI)** · 数值列的位切片 · 支持范围 + 聚合 · 高基数数值友好
- **Druid / Pinot** 原生使用 · 湖仓侧通过 Puffin 或加速副本引入

### 3.5 索引使用的代价

| 类型 | 写入代价 | 读取收益 | 适合 |
|---|---|---|---|
| **Zone Maps (min/max)** | 几乎 0 | 需物理聚集才生效 | 全场 |
| **Parquet Bloom** | 几 KB/row group | 点查 · 非范围 | user_id/order_id 等 |
| **Puffin NDV** | 小 · per-column sketch | COUNT DISTINCT 10-100× | 去重聚合 |
| **Bitmap** | 中 · per-value bitmap | 低基数 filter | status/category |
| **BSI** | 较高 | 数值范围 + 聚合 | 数值度量 |
| **Lance 标量索引** | 中 | 点/范围查 10-100× | 单表高频 |

## 4. 加速副本 · 第三层（机制视角）

当湖上引擎（Trino/Spark）调优到极限仍打不到目标 SLO · 上**本地列存副本**。

### 4.1 什么信号触发

- 仪表盘 **p95 硬要求 < 1s** · Trino 即使走 MV 也 2-3s
- **并发 > 100 QPS** · 长查询挤占短查询
- **高基数精确去重**（COUNT DISTINCT）· 湖上无 BSI 算不动
- **用户面 Dashboard**（SaaS 客户自己看）· 延迟和成本都敏感

### 4.2 副本的机制本质

**加速副本 = 湖表的物化视图 + 就地列存 + 专门执行引擎**

- **湖是真相源** · 副本挂了能重建
- **增量同步** · 通常基于湖表 snapshot 差量 · StarRocks/Doris 原生支持 Iceberg 外表 + 增量 MV
- **专门执行引擎** · 副本引擎针对单表 OLAP 优化（向量化 · BSI · runtime filter · pipeline 执行）· 打得赢 Trino 的通用 DAG

### 4.3 同步路径

```
Iceberg/Paimon (真相源 · S3)
       │
       │ 路径 A · 副本引擎直读外表 + 本地 MV
       │ 路径 B · 外部同步器（Flink CDC · SeaTunnel）
       ↓
StarRocks / ClickHouse / Doris (本地列存)
       ↓
BI Dashboard
```

- **路径 A（推荐）**：StarRocks 的 **Iceberg Catalog + 异步增量 MV** 在副本引擎里自动同步 · 运维简单
- **路径 B**：ClickHouse 无湖原生支持 · 依赖外部同步 · 运维重

### 4.4 陷阱

- **副本当真相源** · 挂了数据找不回 · 每次副本架构设计先问"能重建吗？"
- **全量拷贝** · 成本爆 · 只同步**热分区**（近 30-90 天）
- **同步延迟无监控** · 副本 lag 2 小时 · 业务看的数据过时 · 必须监控同步 lag
- **副本间一致性** · 多副本 + 写入路径多 · 不一致是常见 bug

**产品横比**：详见 [OLAP 加速副本横比](../compare/olap-accelerator-comparison.md) · StarRocks / ClickHouse / Doris / Druid / Pinot。

## 5. CBO + 统计收集 · 让优化器做正确的事

布局和索引都到位 · **优化器不用**仍是 0 收益。

### 5.1 ANALYZE · 收集统计

```sql
-- Trino / Spark / StarRocks 都有 ANALYZE
ANALYZE TABLE orders COMPUTE STATISTICS FOR COLUMNS user_id, amount, region;

-- Iceberg 1.4+ 写 Puffin NDV sketch
CALL system.rewrite_manifests('db.orders');
CALL system.add_files(...);  -- 伴随统计
```

**关键统计**：
- **NDV（Number of Distinct Values）** · Join 顺序决策
- **列 min/max** · 分区裁剪
- **Histogram** · 偏斜列的 CBO 关键（Iceberg Puffin 在加）
- **Table size** · Join side 决策

### 5.2 CBO 失败信号

- **明明数据布好了 · 查询不走布局键** · 查 `EXPLAIN` 看 planner 决策
- **小表被当大表 Join** · NDV 没更新
- **过度 broadcast** · 或**该 broadcast 不 broadcast** · 都是统计问题
- **Runtime Filter / Dynamic Filter 没触发** · 检查引擎开关（Trino `enable_dynamic_filtering`）

### 5.3 统计更新的 pipeline

```
ETL 完成 → ANALYZE 增量 → Puffin 写 sketch → CBO 读到
```

生产建议：ANALYZE **放进 ETL 末尾** · 不要单独调度（容易忘）。

## 6. 实战配方 · Top 10 查询法

1. **找 Top 10 热查询**（BI 系统访问日志 · 每查询出现频次 × 平均延迟 = 总成本）
2. 看它们的 `WHERE` / `JOIN` / `GROUP BY` 列
3. 第一档优化 · **按这些列调分区 + Sort/Z-order**
4. 第二档优化 · 高频点查列加 **Bloom Filter**
5. 第三档优化 · 仍慢的 Top 3 打 **物化视图**
6. 第四档优化 · 仍打不到 SLO · 上**加速副本**
7. Benchmark 前后对比 · **先期通常 3-10×** 加速 · 别过度工程

## 7. 陷阱

- **不 compact 就不生效** · 新写入文件是乱的 · 要靠定期 `rewrite_data_files` / `OPTIMIZE`
- **排序列选太多** · 全选 = 谁都不好 · Z-order 3-5 列是实际上限
- **分区和布局互斥思维** · 分区是粗粒度 · Sort/Z-order 是细粒度 · **互补不互斥**
- **忽略写入代价** · Z-order / Liquid Clustering 写入更贵 · 按收益-成本权衡
- **Bloom Filter 全开** · 每列都加 · row group metadata 膨胀 · 只加点查 Top 列
- **一上来就加速副本** · 湖上 80% 查询 Trino 调优后够用 · 副本是最后一招
- **副本同步没 lag 监控** · 看板数据过时业务先发现
- **不收集 ANALYZE** · CBO 全靠默认估计 · 查询计划烂
- **Hidden Partitioning 不用** · 在 SQL 里写 `extract(year from ts)` · 破坏 partition pruning

## 8. 相关

- [物化视图](materialized-view.md) · 预聚合 · 和本页互补
- [Compaction](../lakehouse/compaction.md) · rewrite/sort 的载体
- [OLAP 建模](olap-modeling.md) · 建模层决定哪些列该被加速
- [仪表盘 SLO](dashboard-slo.md) · 把加速手段映射到 SLO 目标
- [性能调优](../ops/performance-tuning.md) · 通用引擎调优
- [OLAP 加速副本横比](../compare/olap-accelerator-comparison.md) · 副本产品选型
- [Puffin vs Lance](../compare/puffin-vs-lance.md) · 二级索引载体对比
- [谓词下推](../query-engines/predicate-pushdown.md) · 下推原理

## 9. 延伸阅读

- **[Iceberg Table Spec · Partitioning](https://iceberg.apache.org/spec/#partitioning)**
- **[Iceberg Puffin Spec](https://iceberg.apache.org/puffin-spec/)**
- **[Delta Liquid Clustering](https://docs.delta.io/latest/delta-liquid.html)**
- **[Databricks Iceberg V3 Liquid Clustering Public Preview (2026-04)](https://www.databricks.com/blog/next-era-open-lakehouse-apache-icebergtm-v3-public-preview-databricks)**
- **[Parquet Page Index](https://parquet.apache.org/docs/file-format/pageindex/)**
- **[Lance Columnar Format](https://lancedb.github.io/lance/)**
- **[ClickHouse Skipping Indexes](https://clickhouse.com/docs/en/optimize/skipping-indexes)** · 外部对照
