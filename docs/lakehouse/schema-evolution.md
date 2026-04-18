---
title: Schema Evolution
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-18
applies_to: Iceberg v2+, Delta 3+, Paimon 0.9+, Hudi 0.14+
tags: [lakehouse, table-format, schema]
aliases: [模式演化, Schema 演化]
related: [lake-table, snapshot, iceberg, manifest]
systems: [iceberg, paimon, delta, hudi]
status: stable
---

# Schema Evolution（模式演化）

!!! tip "一句话理解"
    **不重写历史数据的前提下**改表结构：加列、删列、改名、转类型、动嵌套结构。做到这件事的关键是用"**列 ID**"而不是"列名"定位数据——文件里存 ID、schema 维护 `id → name` 映射。

!!! abstract "TL;DR"
    - **核心机制**：数据文件里存 `field_id`，schema 单独维护 `id → name` 映射
    - **Iceberg**：spec 强制 `field_id`；Parquet 写入时绑到 `PARQUET:field_id` key-value metadata
    - **Delta**：默认靠**列名**匹配（改名/删列会破历史）；需启用 **Column Mapping**（`name` / `id` 两种 mode）才安全
    - **Hudi / Paimon**：近年向 Iceberg 做法对齐
    - **零重写**的边界：扩位类型安全、收窄不允许、嵌套各家能力差异大

## 1. 为什么它难 · Hive 时代的痛

传统 Hive + Parquet 靠**列名**匹配数据，一旦改结构：

- **加一列** → 旧数据文件没这列，读出来怎么办？全部重写吗？
- **改列名** → 读旧文件时对不上，引擎返回 null 或直接报错
- **改类型** → 旧数据得全表转换一遍
- **动嵌套** → Parquet 的 struct 字段名改了就定位不到

一旦表有几十 TB 历史，每次 `ALTER TABLE` 重写几百 GB - TB 数据成本让人望而却步。湖仓必须做到 schema 变化**零重写**——这件事的技术本质是**把"名字"换成"ID"**。

## 2. Iceberg 的做法 · 列用 ID 定位

Iceberg spec 给每一列（包括嵌套 struct 里的字段）分配一个**全表唯一、永不复用**的整数 ID。

```
schema_v1: id=1 user_id BIGINT, id=2 age INT
写 Parquet: 每列存 PARQUET:field_id=<N> key-value metadata

重命名 age → user_age:
schema_v2: id=1 user_id BIGINT, id=2 user_age INT   ← 只改 schema，数据文件不动

读旧文件:
  Parquet 里存的 column name 仍是 "age"
  但 Iceberg reader 按 field_id=2 反查 schema_v2 的当前名字 "user_age"
  返回列名 user_age 给上层
```

### Column ID 分配规则

- **Create 时**：按 schema 的 DFS 顺序编号，从 1 开始
- **后续加字段**（包括加到 struct 内部）：分配新的未用过的 ID
- **删字段**：ID 从 schema 移除，但**永久不复用**——否则旧文件里那个 ID 的数据会被错误解释成新字段
- **改名**：只改 schema 里 `id → name` 的映射；文件不动

### Parquet field_id 绑定

Iceberg 写 Parquet 时，每列的 `SchemaElement` 上会带一个 `PARQUET:field_id` 的 key-value metadata。Iceberg reader 读 Parquet 时**按 id 反查**当前 schema 的 name，而不是按 Parquet 文件里存的 name。这使得"改名不动文件"成为可能。

## 3. Delta Column Mapping（需启用）

Delta 默认靠**列名**匹配——改名 / 删列直接破历史。要做到和 Iceberg 同级的 schema evolution，必须启用 **Column Mapping**：

| Mode | 机制 | Reader / Writer 要求 |
|---|---|---|
| `name` | 物理列名使用 UUID 风格的稳定标识（不是逻辑名） | Reader V2, Writer V5 |
| `id` | 按 field ID 匹配，同 Iceberg 做法 | Reader V2+, Writer V5+ |

启用方式：

```sql
ALTER TABLE events SET TBLPROPERTIES (
  'delta.columnMapping.mode' = 'name',
  'delta.minReaderVersion' = '2',
  'delta.minWriterVersion' = '5'
);
```

**注意**：已有表启用 Column Mapping 后要做一次 OPTIMIZE，让文件里写入新的物理列名映射。未启用的老表改列名仍会破历史。

## 4. 允许 / 不允许的类型转换

| 从 | 到 | Iceberg | Delta | 说明 |
|---|---|---|---|---|
| int | long | ✅ | ✅ | 扩位 |
| float | double | ✅ | ✅ | 扩位 |
| decimal(9, s) | decimal(18, s) | ✅ | ✅ | precision 扩 |
| decimal(p, 2) | decimal(p, 4) | ✅ | 部分 | scale 扩（Iceberg 允许，Delta 视版本） |
| decimal(9, 2) | decimal(9, 0) | ❌ | ❌ | scale 收窄 |
| long | int | ❌ | ❌ | 收窄 |
| string | int | ❌ | ❌ | 不保证 |
| date | timestamp | ❌ | ❌ | 语义不同 |

**原则**：任何**无损、单向**转换允许；任何**可能丢精度 / 改变语义**的不允许。

## 5. 嵌套类型演化

Iceberg 把嵌套结构（struct / list / map）里的字段也按 ID 管理：

```sql
-- 原始：struct<user: struct<id BIGINT, name STRING>>

-- 在内层 struct 加字段（分配新 field_id）
ALTER TABLE events ADD COLUMN user.email STRING;

-- 改内层字段名（只改 schema 映射）
ALTER TABLE events RENAME COLUMN user.name TO user.display_name;

-- 删内层字段（ID 不复用）
ALTER TABLE events DROP COLUMN user.email;
```

| 操作 | Iceberg | Delta (Column Mapping) | Hudi | Paimon |
|---|---|---|---|---|
| struct 加字段 | ✅ | ✅ | 部分 | ✅ |
| struct 删字段 | ✅ | ✅ | 部分 | ✅ |
| struct 改名 | ✅ | ✅ | 部分 | ✅ |
| list/array 元素 evolve | ✅ | 部分 | 部分 | ✅ |
| map value evolve | ✅ | 部分 | 部分 | ✅ |

Iceberg 在嵌套演化能力上最完整；Delta 需启用 Column Mapping 后能做大多数。

## 6. 跨格式支持矩阵

| 操作 | Iceberg | Delta（Column Mapping）| Hudi | Paimon |
| --- | --- | --- | --- | --- |
| 加列 | ✅ | ✅ | ✅ | ✅ |
| 删列 | ✅ | ✅ | 部分 | ✅ |
| 改名 | ✅ | ✅ | 部分 | ✅ |
| 扩位类型 | ✅ | ✅ | 部分 | ✅ |
| 收窄 / 有损 | ❌ | ❌ | ❌ | ❌ |
| 嵌套演化 | ✅ | 部分 | 部分 | ✅ |
| **字段重排序** | ✅ | ✅ | ✅ | ✅ |

## 7. 代码示例

```sql
-- Iceberg · Spark SQL
ALTER TABLE events ADD COLUMN region STRING AFTER user_id;
ALTER TABLE events RENAME COLUMN age TO user_age;
ALTER TABLE events ALTER COLUMN amount TYPE DECIMAL(18, 2);
ALTER TABLE events DROP COLUMN obsolete_flag;

-- 查看 schema 历史
SELECT * FROM events.schemas;

-- Delta · 启用 Column Mapping
ALTER TABLE events SET TBLPROPERTIES (
  'delta.columnMapping.mode' = 'name',
  'delta.minReaderVersion' = '2',
  'delta.minWriterVersion' = '5'
);
ALTER TABLE events RENAME COLUMN age TO user_age;
```

## 8. 常见坑

- **删列不能复用 ID** —— spec 保证不复用，但如果手工改 metadata.json 就会出问题
- **改类型要懂 reader 兼容性** —— 扩位一般安全，收窄会出读错误
- **Delta 未启用 Column Mapping 就改名** —— 历史数据立刻读不到（列名对不上）
- **Parquet 文件用非 Iceberg 工具写** —— 没有 `PARQUET:field_id` metadata → Iceberg 读时按位置映射 → schema evolution 失效
- **改分区键**（Partition Evolution）是另一个独立能力，不要混成一回事，见 [Partition Evolution](partition-evolution.md)
- **Schema 版本查询**：Iceberg 每个 snapshot 带 `schema-id`，读旧 snapshot 会自动用那时的 schema

## 9. 相关

- [湖表](lake-table.md) · [Snapshot](snapshot.md) · [Manifest](manifest.md)
- [Apache Iceberg](iceberg.md) · [Delta Lake](delta-lake.md)
- [Partition Evolution](partition-evolution.md) —— 分区维度的独立演化能力

## 10. 延伸阅读

- **[Iceberg spec · Schemas](https://iceberg.apache.org/spec/#schemas-and-data-types)**
- **[Delta Column Mapping](https://docs.delta.io/latest/delta-column-mapping.html)**
- **[Parquet field_id · Logical Types](https://github.com/apache/parquet-format/blob/master/LogicalTypes.md)**
- *Schema Evolution at Scale* — Ryan Blue, Netflix
