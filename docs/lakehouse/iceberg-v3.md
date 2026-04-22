---
title: Iceberg v3 · spec 演进与采用
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-22
applies_to: Iceberg spec v3 · 2025-06 ratified · Spark 4.0+ / Trino 450+ / Flink 1.19+ rolling out
tags: [iceberg, lakehouse, spec, v3]
aliases: [Iceberg V3, Iceberg Next Spec]
related: [iceberg, lake-table, manifest, snapshot, delta-lake]
status: stable
---

# Iceberg v3 · spec 演进与采用

!!! tip "一句话理解"
    Iceberg **v3 spec** 于 **2025-06 ratified**（自 v2 2021 MoR delete file 以来最大协议升级）· 核心：**Deletion Vectors · Row Lineage · Multi-Table Transaction · Geo 类型 · Variant 类型**。**2026 初引擎侧 rolling out** · Spark 4.0 / Trino 450+ 已部分支持 · 生产采用正在扩散。

!!! abstract "TL;DR"
    - **v3 五大能力**：Deletion Vectors（替代 Equality Delete）· Row Lineage · Multi-Table Transaction · Geo 类型 · Variant 类型
    - **兼容性**：v3 表可被 v2 读（只读路径 · 不含新特性）· v2 客户端升级才能写 v3
    - **状态 2026-Q2**：spec 稳定 · 主流引擎 rolling out · 生产早期扩散
    - **实务建议**：**看 v3 能力是否解决明确痛点**（删除频繁 / 跨表原子 / 合规 Row Lineage / GIS）· 是则采用 · 否则 v2 稳定继续
    - **Delta 融合**：Databricks 2024 收购 Tabular 后 · v3 是 **Iceberg / Delta 协议融合**的关键（Deletion Vectors 两家已等价）

## 1. 为什么 v3

### v2 的局限

v2（2021 引入）解决了行级删除 + MoR · 但：

- **Equality Delete 效率低**：按 key 过滤昂贵 · 查询 merge 时 I/O 放大
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
COMMIT;  -- ← 实际是三个独立 commit · 不原子
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

**目标**：每行记录**来源** · 合规与审计友好。

```
Row: {id: 123, amount: 500, _source: "orders-etl-2024-12-01", _created_at: "..."}
```

两种实现方式：
- **显式列**：预留 `_source_file` / `_source_commit` 字段
- **Lineage Metadata**：单独的 lineage 表追踪

**v3 提供协议层约定** · 具体实现由引擎选择。

### 能力 4 · Geo 类型

原生 Geometry / Geography 类型 · 配合空间索引：

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

类似 Snowflake VARIANT · 动态 schema 字段：

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
v2 表 → v3（前向升级 · 不破坏 v2 客户端读）
```

**关键**：v3 表的新特性（Deletion Vector / Multi-Table / Row Lineage）需要 v3 客户端。

## 4. 当前状态（2026-Q2）

### spec 和引擎进度

| 项 | 状态 |
|---|---|
| Iceberg spec v3 | **2025-06 ratified**（社区投票通过） |
| Spark 4.0 | v3 基础支持（Deletion Vector · Variant）· Row Lineage / Geo rolling out |
| Trino 450+ | v3 读 GA · 写部分特性 |
| Flink 1.19+ | v3 读写基础 · 高级特性滞后 |
| pyiceberg | v3 metadata read 支持 · 写入跟进中 |
| DuckDB | v3 支持跟进中（基础读） |

**实际进度以 [Iceberg 社区](https://iceberg.apache.org/) 和各引擎 release notes 为准** · 本表可能滞后。

### 生产采用信号

- **Databricks**：Deletion Vector 在 Delta 先落 · 2025 起贡献到 Iceberg v3 · UC 支持 v3 表
- **AWS**：Glue Data Catalog 2025-Q4 起支持 v3 元数据 · Athena 读写分阶段
- **Netflix / LinkedIn**：Iceberg 原生大户 · 已开始内部 v3 灰度
- **Snowflake**：Iceberg 外部表支持 v3 读

## 5. 和 Delta Lake 融合

2024.06 Databricks 收购 Tabular（Iceberg 创始团队）是标志事件。后续信号：

- **Delta Uniform**：Delta 表被 Iceberg 客户端读
- **Databricks 承诺**：持续支持 Iceberg + 推动 v3
- **Deletion Vectors**：两家协议基本等价 · 互读成本低
- **Row Lineage**：两家设计接近

**长期预测**（2026+）：
- **协议层逐步统一**（Iceberg v3 + Delta v4 趋同）
- **Uniform / 双向互读**作为过渡
- **新表默认 Iceberg** · 老 Delta 表保留

## 6. 实务建议

### 采用决策

- **Deletion Vector 对你的场景价值大**（高频删除 · MoR 查询慢）→ 早期采用 v3
- **Multi-Table Transaction 刚需**（金融 / 医疗 / 多表一致）→ 尝试 v3 或 Nessie 并行
- **Row Lineage 合规要求**（EU AI Act 数据追溯 / 金融审计）→ 提前规划 v3
- **仅需基本 CRUD + 查询**：v2 稳定 · 不急迁

### 迁移时

1. **评估新特性价值**：不要为了版本数字升
2. **客户端全栈升级**：Spark / Trino / Flink / pyiceberg 同时升 · 测试混合读写
3. **灰度迁移**：先小表试点 · 观察 Delta / Iceberg 双栈兼容
4. **Catalog 兼容**：REST Catalog 要支持 v3 协议扩展（UC / Polaris / Nessie 2025-2026 都在跟进）

### 不要做

- 为了追"最新版"盲目切
- 老表一次性全升（破坏生产）
- 混用 v2 / v3 客户端不测试

## 7. 现实检视 · 争议与未定

### 仍在演进的问题

- **Multi-Table Transaction 范围**：跨 namespace 清晰 · 跨 catalog 尚在讨论
- **Row Lineage 语义**：存储开销 vs 查询性能的平衡 · 各引擎实现差异
- **Variant 类型与 PyArrow 映射**：上游生态支持不统一
- **v2 → v3 迁移工具**：社区逐步完善 · 大规模迁移工具链尚未成熟

### 对比 Delta v4

Delta Lake 也在推进类似能力 · 两家**协议融合**是长期方向。短期内保持各自节奏 · 应用层 Uniform 过渡。

### 典型企业采用时间线

- spec 稳定（2025-06）→ 引擎完整支持（2025-Q4 - 2026-Q2）→ 生产大规模扩散（2026-Q3+）
- 合规严 / 规模大的团队：2026 年底前完成关键表 v3 迁移
- 中小规模 / 无明确痛点：v2 可继续用到 2027+

## 8. 对团队决策的影响

### 短期（2026）

- 新项目按需评估 v3 能力
- 既有 v2 表可继续用 · 无新特性需求不急迁
- Catalog 侧确认支持 v3（UC / Polaris / Nessie 升级）

### 中期（2026-2027）

- Deletion Vector 预计成为主流场景默认
- Multi-Table Transaction 在企业级合规场景扩散
- Row Lineage 合规驱动普及

### 长期（2027+）

- v3 成为主流 · v2 长期兼容
- **Iceberg / Delta 协议可能最终统一**

## 9. 延伸阅读

- **[Iceberg Spec repository](https://github.com/apache/iceberg/tree/main/format)** —— spec 演进最权威
- **[Iceberg Dev 邮件列表归档](https://lists.apache.org/list.html?dev@iceberg.apache.org)**
- **[v3 Proposal 讨论 issue](https://github.com/apache/iceberg/issues?q=label%3Aspec-v3)**
- **[Iceberg Summit 演讲](https://www.iceberg-summit.org/)**
- **[Databricks 收购 Tabular 博客](https://www.databricks.com/blog/)**
- [Delta Lake Deletion Vectors 参考实现](https://docs.databricks.com/en/delta/deletion-vectors.html)

## 相关

- [Apache Iceberg](iceberg.md) · 主页（含 §机制 6 v3 概述）
- [Delta Lake](delta-lake.md) · 融合对标
- [Manifest](manifest.md) · [Snapshot](snapshot.md)
- [湖仓厂商格局](../vendor-landscape.md) · 协议演进的商业背景
