---
title: Bulk Loading（批量装载）
type: concept
depth: 进阶
prerequisites: [lake-table, iceberg]
tags: [pipelines, ingestion, migration]
related: [iceberg, compaction, migration-playbook]
systems: [spark, iceberg, hive]
status: stable
---

# Bulk Loading（批量装载）

!!! tip "一句话理解"
    把一大块**已有的历史数据**（TB–PB 级）一次性装进湖表。包括首次冷启动、Hive 表迁移、外部系统导入、过期数据修复。流式入湖的"兄弟场景"，套路完全不同。

!!! abstract "TL;DR"
    - 冷启动湖仓的**第一件大事**，方法对错直接影响 3 个月的性能
    - 核心是**避免小文件 + 合理分区 + 写入并行度匹配**
    - Hive → Iceberg 有 **register-only** 和 **rewrite** 两条路
    - 大规模装载常常要**分批 + compaction 穿插**，避免一轮"大写入 + 大 compact" 爆开
    - 和流式入湖**不要混用一个作业**，各跑各的更稳

## 四种典型 Bulk Load 场景

### 场景 A：冷启动

新建湖仓第一次把历史数据灌进来。

- 选择**当前快照**作为截断点
- 之后切流式入湖承接增量

### 场景 B：Hive → Iceberg 迁移

两条路：

- **Register-only（零重写）** —— 不动数据文件，把 Hive 表的 Parquet 作为 Iceberg 数据文件注册
  - 最快，几分钟
  - 不利用 Iceberg 的新能力（hidden partitioning、列 ID）
  - 长期要重写成 native Iceberg 布局
- **Rewrite（全重写）** —— 按 Iceberg native spec 重写一遍
  - 慢，按 TB 级看分钟到小时
  - 直接获得 Iceberg 全部能力

**推荐**：先 register-only 解锁读写，半年内逐步 rewrite。

### 场景 C：外部系统导入

第三方 Parquet / CSV / JSON 堆栈灌湖。

- 先建 **staging 表**（Iceberg 或 Paimon append-only）
- 验证 schema / 基数 / NULL 率
- 再 INSERT 到目标事实表

### 场景 D：回填 / 修复

历史数据出错，批量重写某段分区。

- 用 Iceberg `REPLACE PARTITION` 或 `MERGE INTO`
- **不要**直接删再写 —— 中间不可用窗口
- 利用 Snapshot 事后可 rollback

## 工程要点

### 1. 文件大小

**目标 128MB – 1GB**。小文件一旦造成后面几乎救不回来：

```
# 装载后立即跑
CALL system.rewrite_data_files(
  table => 'db.t',
  options => map(
    'target-file-size-bytes', '536870912'  -- 512MB
  )
);
```

### 2. 写入并行度

- **分区数 = 文件数**（大致）
- 并行写 100 个分区 = 100 个文件的同时写
- 和 target file size 呼应：期望每个并行 writer 产出 ~target size

### 3. 分区设计

冷启动就是你**决定分区策略**的唯一便宜机会。Iceberg Hidden Partitioning 是首选：

```sql
CREATE TABLE orders (
  order_id BIGINT,
  ts TIMESTAMP,
  user_id BIGINT,
  amount DECIMAL
) USING iceberg
PARTITIONED BY (days(ts), bucket(16, user_id));
```

这两个维度（时间 + hash 散列）适合绝大多数事实表。

### 4. 分批 vs 一次性

PB 级别装载一次性扔给 Spark：

- Executor 内存炸
- Shuffle 爆
- 失败重试代价昂贵

**分批**：按时间分区或按主键范围分批，每批 10–100GB。批之间穿插 compaction 让表保持健康。

### 5. 事务边界

- Spark `saveAsTable` / `write.insertInto` —— 一次 commit
- **不建议**一次性 commit PB 级（失败 roll back 很贵）
- 小分批 commit，每批成功独立进账

## Spark 装载示例

```python
# Hive → Iceberg native rewrite
spark.sql("""
  CREATE TABLE warehouse.db.orders
  USING iceberg
  PARTITIONED BY (days(ts), bucket(16, user_id))
  TBLPROPERTIES (
    'write.parquet.compression-codec' = 'zstd',
    'write.target-file-size-bytes' = '536870912'
  )
  AS SELECT * FROM hive_db.orders_legacy
""")

# 后续每日增量
spark.sql("""
  INSERT INTO warehouse.db.orders
  SELECT * FROM hive_db.orders_legacy
  WHERE dt = '2026-04-15'
""")
```

## Paimon 装载

流式湖表也有批装载场景：

```sql
-- Paimon primary key 表的初始化
INSERT INTO paimon_orders
SELECT * FROM mysql_snapshot_dump;

-- 随后切流式 CDC 承接增量
```

Paimon 的 `dynamic-bucket` 模式在初始化时特别有用——写入时自动决定分桶，不要预估分桶数。

### Paimon `bucket` vs Iceberg `hidden partitioning` 对照

初始化装载时两家的分区/分桶策略**理念不同**：

| 维度 | Paimon | Iceberg |
|---|---|---|
| **分组粒度** | **Partition + Bucket** 双层（粗+细）| 纯 **Partition**（hidden transforms）|
| **细粒度策略** | Bucket 按主键 hash · 决定**并行写**和**合并粒度** | 分区 transform（`bucket(N, col)` / `days(ts)` 等）· 决定**剪枝粒度** |
| **初始化灵活性** | **`dynamic-bucket`** 模式写入时自动定桶数 · 免预估 | 分区 spec 改动需 `PARTITION SPEC` evolution（协议层支持演化 · 数据不动）|
| **失败回退** | 错了改 bucket 数要 rescale | 错了改 spec 不影响历史数据（见 Iceberg Partition Evolution）|
| **初装建议** | 从 16 bucket 起 · 或用 dynamic | 先小粒度分区试跑 · 再按查询路径 evolve |

**结论**：初次装载时**两家都不用过度预估**——Paimon 有 dynamic-bucket 兜底；Iceberg 有 partition evolution 事后可改。详见 [湖仓表格式 · Partition Evolution](../lakehouse/partition-evolution.md)。

## 常见陷阱

- **装载时关闭 compaction → 小文件海啸**
- **装载后不立即 `rewrite_data_files`**：Zone Maps / 排序缺失，后续查询慢
- **分区选反**（按低基数列分区） → 几十万分区，Catalog 压垮
- **装载作业和业务流共用 Spark 集群** → 资源抢占，全都慢
- **Hive register-only 后立刻删 Hive 表** → 旧目录被 Iceberg manifest 引用，数据丢失

## 和流式入湖的配合

一旦历史装载完，切到流式：

```
Bulk Load (一次性)  → 冷启动截断点 → Flink CDC 增量流
```

**不要**让两者同时写同一张表（除非明确设计过）。典型做法：

- 装载作业写到临时 staging 表
- 流式入湖从装载截断点开始（给 offset 明确值）
- 两者通过**主键**保证幂等

## 相关

- [Kafka 到湖](kafka-ingestion.md) —— 流式侧
- [流式入湖](../scenarios/streaming-ingestion.md)
- [Compaction](../lakehouse/compaction.md)
- [Apache Iceberg](../lakehouse/iceberg.md)

## 延伸阅读

- Iceberg Migration Guide
- *Migrating to Iceberg at Scale* —— Netflix / Tabular 博客
- Paimon 批初始化文档
