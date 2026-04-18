---
title: Schema Evolution
type: concept
tags: [lakehouse, table-format]
aliases: [模式演化, Schema 演化]
related: [lake-table, snapshot, iceberg]
systems: [iceberg, paimon, delta, hudi]
status: stable
---

# Schema Evolution（模式演化）

!!! tip "一句话理解"
    **不重写历史数据的前提下**改表结构：加列、删列、改名、转类型。湖仓做到这件事的关键是用"列 ID"而不是"列名"定位数据。

## 为什么它难

传统 Hive + Parquet 的坑：

- 加一列 → 旧数据文件没有这列，读出来怎么办？全部重写？
- 改列名 → 读旧文件时对不上
- 改类型 → 旧数据得转换一遍

一旦表有几十 TB 的历史，每一次 `ALTER TABLE` 重写成本都让人望而却步。湖仓必须让 schema 变化**零重写**。

## Iceberg 的做法：列用 ID 定位

Iceberg 规格里每一列有一个**永不复用的整数 ID**。数据文件（Parquet）写入时，字段名映射到这个 ID。读取时按 ID 反查当前表 schema：

```
写入时: {"field_id": 1, "name": "user_id"}
        {"field_id": 2, "name": "age"}

重命名 age → user_age:
        {"field_id": 1, "name": "user_id"}
        {"field_id": 2, "name": "user_age"}    ← 只改 schema，数据文件不动

读旧文件: Parquet 里还写着 "age"，
          但 Iceberg 按 field_id=2 反查当前名字 "user_age" 返回
```

- **加列** → 新列 = 新 ID；读旧文件时该列返回 NULL
- **删列** → 从 schema 移除 ID，但 ID 永久不复用
- **改名** → 仅改 schema 里的 name，数据文件照旧
- **改类型** → 有限允许：int → long、float → double、decimal 扩位等；不允许反向或无损不保证的转换

## 支持矩阵（简）

| 操作 | Iceberg | Delta | Hudi | Paimon |
| --- | --- | --- | --- | --- |
| 加列 | ✅ | ✅ | ✅ | ✅ |
| 删列 | ✅ | ✅（需启用） | 部分 | ✅ |
| 改名 | ✅ | ✅（需启用） | 部分 | ✅ |
| 扩位类型 | ✅ | ✅ | 部分 | ✅ |
| 收窄 / 有损类型 | ❌ | ❌ | ❌ | ❌ |
| 嵌套结构演化 | ✅ | 部分 | 部分 | ✅ |

## 常见坑

- **删列不能复用 ID** —— 否则旧文件里的数据会被错误地当成新列解析
- **改类型要懂 reader 兼容性** —— 扩位通常安全，但收窄会出读错误
- **改分区键**（Partition Evolution）是**另一个独立能力**，不等于 schema evolution

## 相关概念

- [湖表](lake-table.md)
- [Apache Iceberg](iceberg.md)
- Partition Evolution —— Iceberg spec v2 支持，见 [Iceberg](iceberg.md) 分区演进段

## 延伸阅读

- Iceberg spec v2 - Schemas: <https://iceberg.apache.org/spec/#schemas-and-data-types>
- *Schema Evolution at Scale* - Ryan Blue
