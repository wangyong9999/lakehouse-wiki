---
title: 元数据与 Catalog
description: 湖仓的"表注册中心" —— Hive / REST / Nessie / Unity / Polaris / Gravitino
---

# 元数据与 Catalog

Catalog 是湖仓的"表注册中心"。一体化湖仓时代它的角色已膨胀成"治理平面"——不只注册表，还要管向量、模型、文件 Volume、权限、血缘。

## 已有

- [Hive Metastore](hive-metastore.md) —— Hadoop 时代的事实标准
- [Iceberg REST Catalog](iceberg-rest-catalog.md) —— 下一代标准协议
- [Nessie](nessie.md) —— Git-like 事务 Catalog
- [Unity Catalog](unity-catalog.md) —— Databricks 主推的多模资产统一目录

## 相关

- [统一 Catalog 策略](../unified/unified-catalog-strategy.md) —— 现代选型决策

## 待补

- Apache Polaris —— Snowflake 开源实现
- Apache Gravitino —— 多元数据源桥接
