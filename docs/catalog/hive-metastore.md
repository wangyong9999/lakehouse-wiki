---
title: Hive Metastore (HMS) · 湖仓注册中心的"上一代"标准
type: system
depth: 进阶
level: A
last_reviewed: 2026-04-20
applies_to: Hive Metastore 2.x/3.x/4.0（Hive 4.0 GA 2024）
tags: [catalog, legacy, hive]
category: catalog
repo: https://github.com/apache/hive
license: Apache-2.0
status: stable
---

# Hive Metastore (HMS)

!!! tip "一句话定位"
    事实标准的**湖表注册中心**，诞生于 Hadoop 时代（2010s）。2026 视角下 HMS **不是被淘汰**，而是进入**"新建项目不选、存量系统长期兼容"的分叉期**——新建湖仓走 Iceberg REST / Polaris / Unity，历史 HMS 表继续活很多年。

!!! abstract "TL;DR"
    - **三件元数据**：Database / Table（schema + 路径）/ Partition（位置 + 统计）
    - **后端**：RDBMS（MySQL/Postgres/Derby）+ Thrift API
    - **2026 现状 · 分叉**：
        - **新建**：REST Catalog / Polaris / Unity / Nessie 是主推
        - **存量**：Spark/Trino/Iceberg 长期兼容 HMS；大量企业没有迁移预算
    - **版本注记**：Hive 3.x 主流生产版；Hive 4.0 GA 2024+ 在部分场景下逐步铺开
    - **"只剩注册中心角色"**：当 Iceberg / Delta 把实际元数据放自己文件里 · HMS 只存指针

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
- **Ranger / Sentry 权限生态**：企业已投入的治理方案都绑在 HMS 上

## 为什么新项目不选它

HMS 设计年代太早，短板很硬：

- **"目录即分区"的假设** —— 读写依赖 `LIST` 对象存储，对 S3 不友好
- **没有事务语义** —— 跨表原子性完全不支持
- **RDBMS 成为瓶颈** —— 大量分区 / 大量表时 HMS JDBC 连接池是热点
- **无版本化 / 无分支** —— 现代工作流（数据 Git-flow）做不出来
- **API 表达能力弱** —— 现代表格式（Iceberg）的能力无法原生暴露（新能力要塞 `TBLPROPERTIES`）
- **Schema 演化** —— Thrift DDL 升级困难，大公司被卡在老版本

## 2026 的分叉 · 新建 vs 存量两条路

### 新建湖仓（不选 HMS）

- **Iceberg REST Catalog** → 协议化 + 云原生 · 新项目默认
- **Polaris** / **Unity Catalog** / **Nessie** / **Gravitino** → 根据生态栈和治理需求选
- 详见 [Iceberg REST Catalog](iceberg-rest-catalog.md) · [Catalog 全景](../compare/catalog-landscape.md)

### 历史 HMS 栈的长期兼容策略

两种主流模式：

1. **HMS 作为 Iceberg 的指针存储**：HMS 只保留 "table → current metadata.json 路径" 这一条记录 · 实际元数据走 Iceberg manifest。可以**平滑过渡**：老 Hive 作业读 HMS 元数据，新 Spark/Trino 作业读 Iceberg
2. **迁移到 REST Catalog**：用 Iceberg `register_table` 或 Polaris 的迁移工具做批量导入；HMS 退役成只读副本（审计用）

## 和 Iceberg Catalog / Nessie / Unity 的关系

- **Iceberg on HMS** —— 用 HMS 存 "表 → current metadata.json 指针"，读写走 Iceberg 协议，分区由 Iceberg manifest 管理；**HMS 只剩注册中心角色**
- **Iceberg REST Catalog** —— 取代 HMS 作为 Iceberg 的标准 Catalog 协议（2024+ 主流新建）
- **Nessie** —— 提供 Git-like 能力，HMS 没有的东西
- **Unity / Polaris** —— Databricks / Snowflake 的现代替代方案

## 陷阱与坑

- **大集群下 HMS JDBC 连接爆炸**是常见事故——Thrift 连接池 + RDBMS 锁竞争；生产要配连接数限制和慢查询监控
- **HMS schema 不能乱升级**——很多公司被卡在老版本；跨版本 upgrade 会动 RDBMS 表结构
- **权限模型（`GRANT` / `Ranger`）各家落地差异大**，跨集群迁移痛苦
- **误以为 HMS "就是一个 RDBMS 就好"**——忽视它的 JDBC 连接池、Thrift session、metastore event listener 这些运维点
- **迁移预算低估**：从 HMS 迁 REST Catalog 看似"改配置"，实际要验证所有 Hive UDF / 分区函数 / 权限映射

## 相关

- [Iceberg REST Catalog](iceberg-rest-catalog.md) · [Nessie](nessie.md) · [Unity Catalog](unity-catalog.md)
- [Catalog 全景对比](../compare/catalog-landscape.md)

## 延伸阅读

- Hive 官方文档 · HMS architecture · <https://cwiki.apache.org/confluence/display/Hive/Design>
- *Apache Iceberg: The Definitive Guide* · 第 4 章讲多种 Catalog 选择
- Iceberg HMS Catalog 文档：<https://iceberg.apache.org/docs/latest/hive/>
