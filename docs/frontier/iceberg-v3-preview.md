---
title: Iceberg v3 预览 · 2025-2026 spec 演进
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-18
applies_to: Iceberg spec v3（2024-2025 起草 · 2025-2026 推进）
tags: [frontier, iceberg, lakehouse, spec]
aliases: [Iceberg V3, Iceberg Next Spec]
related: [iceberg, lake-table, manifest, snapshot]
status: preview
---

# Iceberg v3 预览

!!! tip "一句话理解"
    Iceberg **v3 spec** 在 2024-2025 年推进，是自 v2（2021 引入 MoR delete file）以来最大的协议升级。核心：**删除向量（Deletion Vectors）· 行级血缘 · 地理空间类型 · 更强的跨引擎一致性**。**2026 初仍在完善期，生产采用要评估成熟度**。

!!! abstract "TL;DR"
    - **v3 重点能力**：Deletion Vectors（替代 Equality Delete）· 多表事务 · Row Lineage · Geo 类型 · Variant 类型
    - **兼容性**：v3 表可被 v2 读（只读路径）· v2 客户端升级才能写 v3
    - **时间表**：**2024 Q4 起草 · 2025 Q2 投票 · 2026 稳定**（预期）
    - **实务建议**：**新项目暂用 v2**；v3 重点特性明确规划后再切
    - **Delta Lake 的融合**：Databricks 2024 收购 Tabular 后，v3 是 **Iceberg / Delta 协议融合**的关键

## 1. 为什么 v3

### v2 的局限

v2（2021 引入）解决了行级删除 + MoR，但：

- **Equality Delete 效率低**：按 key 过滤昂贵、查询 merge 时 I/O 放大
- **无原生多表事务**：跨表操作要应用层协调
- **Row Lineage 缺失**：合规场景需要"这一行从哪里来"
- **地理空间不原生**：GIS 场景只能转字符串 hack
- **类型系统有限**：Variant / Semi-structured 支持不足

### v3 的价值命题

- **Deletion Vectors** 取代 Equality Delete → 查询更快
- **Row Lineage** 让每行追溯到源头
- **Multi-Table Transaction** 跨表原子
- **Geo** 类型（Point / Line / Polygon）原生支持
- **Variant / JSON** 更好的半结构化处理

## 2. 核心能力深度

### 能力 1 · Deletion Vectors

**v2 做法（Equality Delete）**：
```
Delete File 记录：
  { key_column: value }
查询时：
  读 Data File 每行 → 和 Delete File 的 key 对比 → 过滤
代价：
  I/O 放大、CPU 密集
```

**v3 做法（Deletion Vector）**：
```
Delete Vector 记录：
  { file_path: bitmap }
  bitmap[row_position] = 1 表示删除
查询时：
  读 Data File → 按 bitmap 跳过标记行
代价：
  接近 0（位图极小）
```

**效果**：
- 查询延迟降 2-5×（高删除率场景）
- 存储更省（bitmap vs 重复 key）
- 和 Delta Lake 2024+ 的 Deletion Vectors **协议基本等价** → 为未来融合奠基

### 能力 2 · Multi-Table Transaction

**v2 没有**原生多表事务：
```sql
-- v2 需要应用层协调
BEGIN;
INSERT INTO fact_orders ...;
UPDATE dim_inventory ...;
DELETE FROM staging_orders ...;
COMMIT;  -- ← 实际是三个独立 commit，不原子
```

**v3 原生支持**：
```sql
-- v3 单个 commit 跨多表
CALL system.transaction(
  fact_orders => INSERT ...,
  dim_inventory => UPDATE ...,
  staging_orders => DELETE ...
);
-- 要么全部成功要么全部回滚
```

**实现**：REST Catalog 协议扩展 + manifest 层联合 commit。

### 能力 3 · Row Lineage

**目标**：每行记录**来源**，合规与审计友好。

```
Row: {id: 123, amount: 500, _source: "orders-etl-2024-12-01", _created_at: "..."}
```

两种实现方式：
- **显式列**：预留 `_source_file` / `_source_commit` 字段
- **Lineage Metadata**：单独的 lineage 表追踪

**v3 提供协议层约定**，具体实现由引擎选择。

### 能力 4 · Geo 类型

原生 Geometry / Geography 类型，配合空间索引：

```sql
CREATE TABLE poi (
  id BIGINT,
  name STRING,
  location GEOMETRY -- v3 新类型
) USING iceberg;

SELECT * FROM poi
WHERE ST_Within(location, ST_MakeBox(lng1, lat1, lng2, lat2));
```

对接 Sedona、GeoPandas 等 GIS 生态。

### 能力 5 · Variant / Semi-Structured

类似 Snowflake VARIANT，动态 schema 字段：

```sql
CREATE TABLE events (
  id BIGINT,
  ts TIMESTAMP,
  payload VARIANT  -- JSON / 半结构化
) USING iceberg;

SELECT payload:user.email FROM events;  -- 路径查询
```

替代之前用 `MAP<STRING, STRING>` 或 `STRING` 存 JSON 的 hack。

## 3. 兼容性矩阵

### 读写兼容

| 客户端 \ 表格式 | v1 表 | v2 表 | v3 表 |
|---|---|---|---|
| v1 客户端 | ✅ | ❌ | ❌ |
| v2 客户端 | ✅ 读 | ✅ | ⚠️ **只读部分特性** |
| v3 客户端 | ✅ | ✅ | ✅ |

### 升级路径

```
v1 表 → 不推荐直接升 v3 → 先升 v2 → 再升 v3
v2 表 → v3（前向升级，不破坏 v2 客户端读）
```

**关键**：v3 表的新特性（Deletion Vector / Multi-Table / Row Lineage）需要 v3 客户端。

## 4. 实施时间线

### 官方节奏（预期）

| 时间 | 里程碑 |
|---|---|
| 2024 Q3 | spec v3 proposal 起草 |
| 2024 Q4 | 社区讨论 + 参考实现 PoC |
| 2025 Q1-Q2 | 社区投票通过 spec |
| 2025 Q3 | 主流引擎（Spark / Trino / Flink）支持 |
| 2025 Q4 | pyiceberg / 各 SDK 支持 |
| 2026 | 生产采用扩散 |

**实际进度需关注 [Iceberg 社区](https://iceberg.apache.org/) 更新**。

## 5. 和 Delta Lake 融合

2024.06 Databricks 收购 Tabular（Iceberg 创始团队）是标志事件。后续信号：

- **Delta Uniform**：Delta 表被 Iceberg 客户端读
- **Databricks 承诺**：持续支持 Iceberg + 推动 v3
- **Deletion Vectors**：两家都在实现、未来可能完全兼容
- **Row Lineage**：两家设计接近

**长期预测**（2026+）：
- **协议层逐步统一**（Iceberg v3 + Delta v4 趋同）
- **Uniform / 双向互读**作为过渡
- **新表默认 Iceberg**，老 Delta 表保留

## 6. 实务建议

### 现在（2026 初）应该做

- **新项目使用 v2**（稳定）
- **关注 v3 演进**（订阅 Iceberg Dev 邮件列表 / GitHub）
- **别急着迁**：等 v3 在主流引擎（Spark 4 / Trino / Flink）完整支持后再评估

### 规划 v3 迁移时

1. **评估新特性价值**：是否真的需要 Deletion Vector / Multi-Table / Row Lineage / Geo？
2. **客户端全栈升级**：Spark / Trino / Flink / pyiceberg 同时升
3. **灰度迁移**：先小表试点
4. **Catalog 兼容**：REST Catalog 支持 v3 协议扩展

### 不要做

- 为了追"最新版"盲目切
- 老表一次性全升（破坏生产）
- 混用 v2 / v3 客户端不测试

## 7. 现实检视 · 争议与未定

### 未定的问题

- **Multi-Table Transaction 范围**：跨 namespace？跨 catalog？
- **Row Lineage 语义**：存储开销 vs 查询性能的平衡
- **Variant 类型与 PyArrow 映射**：上游生态如何支持
- **v2 → v3 迁移工具**：社区尚在讨论

### 对比 Delta v4

Delta Lake 也在推进类似能力。两家**谁先稳定**对采用有影响。

### 生态准备度（2026 初参考）

| 引擎 | v3 支持 |
|---|---|
| Spark | PoC 阶段 |
| Trino | 计划中 |
| Flink | 计划中 |
| pyiceberg | 规划 |
| DuckDB | 不确定 |

**典型企业采用时间线**：spec 稳定后 6-12 个月才大规模生产。

## 8. 对团队决策的影响

### 短期（2025）

- v3 不应影响**当前新项目选型**
- 继续用 v2 + 关注社区进度

### 中期（2026）

- 如果**Deletion Vector 对你的场景价值大**（高频删除）→ 早期采用 v3
- 如果**多表事务刚需**（金融 / 医疗）→ 尝试 v3 或 Nessie 并行
- **Row Lineage** 对合规严团队值得提前规划

### 长期（2027+）

- v3 成为主流（但 v2 仍长期兼容）
- v2 仍兼容但新功能倾斜 v3
- **Iceberg / Delta 协议可能最终统一**

## 9. 延伸阅读

- **[Iceberg Spec repository](https://github.com/apache/iceberg/tree/main/format)** —— 跟 spec 演进最权威
- **[Iceberg Dev 邮件列表归档](https://lists.apache.org/list.html?dev@iceberg.apache.org)**
- **[v3 Proposal 讨论 issue](https://github.com/apache/iceberg/issues?q=label%3Aspec-v3)**
- **[Iceberg Summit 演讲](https://www.iceberg-summit.org/)**
- **[Databricks 收购 Tabular 博客](https://www.databricks.com/blog/)**
- [Delta Lake Deletion Vectors 参考实现](https://docs.databricks.com/en/delta/deletion-vectors.html)

## 相关

- [Apache Iceberg](../lakehouse/iceberg.md) —— 当前 v2 详细
- [Delta Lake](../lakehouse/delta-lake.md) —— 融合对标
- [Manifest](../lakehouse/manifest.md) · [Snapshot](../lakehouse/snapshot.md)
- [湖仓厂商格局](vendor-landscape.md) —— 协议演进的商业背景
