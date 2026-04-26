---
title: 参考资料 · Catalog / 治理平面
type: reference
status: stable
tags: [reference, references, catalog]
description: Iceberg REST / Unity Catalog / Polaris / Nessie / Gravitino 文档
last_reviewed: 2026-04-25
---

# 参考资料 · Catalog / 治理平面

## 协议层 / Spec

- **[Apache Iceberg REST Catalog Specification](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml)** _(official-doc)_ —— 已成事实标准的 Catalog 协议。
- **[Iceberg Catalog Implementations](https://iceberg.apache.org/concepts/catalog/)** _(official-doc)_ —— 各 Catalog 实现的对比。

## OSS Catalog 实现

- **[Apache Polaris Documentation](https://polaris.apache.org/)** _(official-doc)_ —— Snowflake 开源、2026-02 进 ASF TLP。
- **[Project Nessie Documentation](https://projectnessie.org/)** _(official-doc)_ —— Git-like 数据版本控制 Catalog。
- **[Apache Gravitino Documentation](https://gravitino.apache.org/)** _(official-doc)_ —— 多模 Catalog (表 + 模型 + 文件 + topic)。
- **[Unity Catalog OSS Documentation](https://docs.unitycatalog.io/)** _(official-doc)_ —— Databricks 2024 开源版。
- **[LinkedIn OpenHouse](https://github.com/linkedin/openhouse)** _(official-doc)_ —— LinkedIn 2024 开源的 Catalog + 治理平面。

## 商业 / 托管

- **[Databricks Unity Catalog Documentation](https://docs.databricks.com/aws/en/data-governance/unity-catalog/)** _(official-doc)_ —— UC 完整版（含 Volume / Function / 多模资产）。
- **[Snowflake Polaris Documentation](https://docs.snowflake.com/en/user-guide/tables-iceberg-polaris-catalog)** _(official-doc)_ —— Polaris 商业版。
- **[AWS Glue Data Catalog Documentation](https://docs.aws.amazon.com/glue/latest/dg/components-overview.html)** _(official-doc)_ —— AWS 托管 Catalog（兼容 Hive Metastore）。

## 工业博客 / 设计深度

- **[Tabular - The Future of Open Data Catalogs](https://tabular.io/blog/iceberg-rest/)** _(blog, 2024 已被 Databricks 收购)_ —— Iceberg REST 设计深度。
- **[Snowflake - Why Polaris](https://www.snowflake.com/blog/introducing-polaris-catalog/)** _(2024, blog)_ —— **厂商主张**。
- **[Databricks - Unity Catalog Architecture](https://www.databricks.com/blog/whats-new-unity-catalog)** _(blog)_ —— **厂商主张**。
- **[Netflix - Metacat](https://netflixtechblog.com/metacat-making-big-data-discoverable-and-meaningful-at-netflix-56fb36a53520)** _(2018, blog)_ —— 大规模 Metadata service 早期工业实践。

## 治理 / RBAC / 血缘

- **[OpenLineage Specification](https://openlineage.io/docs/)** _(official-doc)_ —— 开放数据血缘标准。
- **[Apache Atlas Documentation](https://atlas.apache.org/)** _(official-doc)_ —— Hadoop 生态治理。
- **[Marquez](https://marquezproject.ai/)** _(official-doc)_ —— OpenLineage 参考实现。

---

**待补**：Iceberg v3 spec 后 Catalog 相关变更；Polaris ASF 后社区演进
