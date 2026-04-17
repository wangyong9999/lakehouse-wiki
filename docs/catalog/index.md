---
title: 元数据与 Catalog
description: 湖仓的"表注册中心" —— Hive / REST / Nessie / Unity / Polaris / Gravitino
---

# 元数据与 Catalog

Catalog 是湖仓的"表注册中心"。没有它，引擎就只能看见一堆 Parquet；有了它，才有"数据库 / schema / 表 / 版本"的层级。

## 主流实现

- [Nessie](nessie.md) —— Git-like 事务 Catalog

## 待补

- Hive Metastore / HMS —— 事实标准
- Iceberg REST Catalog —— 逐渐成为新标准的协议
- Unity Catalog —— Databricks 主推
- Apache Polaris —— Snowflake 开源
- Apache Gravitino —— 多引擎统一元数据
- Catalog 协议横向对比

## 相关

- 上游概念：[湖表](../lakehouse/lake-table.md)、[Snapshot](../lakehouse/snapshot.md)
