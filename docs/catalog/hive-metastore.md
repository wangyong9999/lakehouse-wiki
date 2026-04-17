---
title: Hive Metastore (HMS)
type: system
tags: [catalog, legacy]
category: catalog
repo: https://github.com/apache/hive
license: Apache-2.0
status: stable
---

# Hive Metastore (HMS)

!!! tip "一句话定位"
    事实标准的**湖表注册中心**，诞生于 Hadoop 时代。现代湖仓很多年继续兼容 HMS，但其"目录即表"的古老假设正在被 Iceberg REST / Nessie / Unity 等新协议逐步接替。

## 它是什么

HMS 维护三件核心元数据：

1. **Database / Schema**
2. **Table** —— 表的 schema、分区列、底层存储路径
3. **Partition** —— 每个分区的目录、统计、位置

存储后端是一个关系型 DB（MySQL / Postgres / Derby）。对外暴露 Thrift API，几乎所有 Hadoop 时代的工具都认它。

## 为什么今天它还活着

- **生态包围**：Spark / Trino / Presto / Hive / Flink / Impala 原生支持
- **零迁移成本**：大量团队历史数据都在 HMS 下注册
- **作为 Iceberg / Delta / Paimon 的底座** —— 它们都支持"把表元数据指针存到 HMS"，复用已有治理与权限体系

## 为什么它正在被接替

HMS 设计年代太早，短板很硬：

- **"目录即分区"的假设** —— 读写依赖 `LIST` 对象存储，对 S3 不友好
- **没有事务语义** —— 跨表原子性完全不支持
- **RDBMS 成为瓶颈** —— 大量分区 / 大量表时 HMS 自身成为热点
- **无版本化 / 无分支** —— 现代工作流（数据 Git-flow）做不出来
- **API 表达能力弱** —— 现代表格式（Iceberg）的能力无法原生暴露

## 和 Iceberg Catalog / Nessie / Unity 的关系

- **Iceberg on HMS** —— 用 HMS 存 "表 → current metadata.json 指针"，读写走 Iceberg 协议，分区由 Iceberg manifest 管理；**HMS 只剩注册中心角色**
- **Iceberg REST Catalog** —— 目标是取代 HMS 作为 Iceberg 的标准 Catalog 协议
- **Nessie** —— 提供 Git-like 能力，HMS 没有的东西
- **Unity / Polaris** —— Databricks / Snowflake 的现代替代方案

## 陷阱与坑

- 大集群下 HMS JDBC 链接爆炸是常见事故
- HMS 的 schema 不能乱升级，很多公司被卡在老版本
- 权限模型（`GRANT` / `Ranger`）各家落地差异大，跨集群迁移痛苦

## 延伸阅读

- Hive Metastore architecture overview
- *Apache Iceberg: The Definitive Guide* —— 第 4 章讲多种 Catalog 选择
