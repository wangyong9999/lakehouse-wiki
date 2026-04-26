---
title: 参考资料 · 湖仓 / 表格式
type: reference
status: stable
tags: [reference, references, lakehouse]
description: Iceberg / Delta / Paimon / Hudi 论文、官方 spec、经典博客
last_reviewed: 2026-04-25
---

# 参考资料 · 湖仓 / 表格式

## 论文

- **[Lakehouse: A New Generation of Open Platforms](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)** _(2021, paper)_ —— Databricks 团队 CIDR 2021，奠定 "Lakehouse 范式" 概念框架。**厂商主张**（Databricks）但论文本身已被广泛引用。
- **[Apache Iceberg: An Architectural Look Under the Covers](https://www.dremio.com/wp-content/uploads/2021/05/Apache-Iceberg-An-Architectural-Look-Under-the-Covers.pdf)** _(2021, blog/whitepaper)_ —— Dremio 视角的 Iceberg 架构剖析。
- **[Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores](https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf)** _(2020, paper)_ —— VLDB 2020，Delta Lake 的奠基论文。**厂商主张**（Databricks）。
- **[Apache Hudi - The Data Lake Platform](https://hudi.apache.org/blog/2021/07/21/streaming-data-lake-platform/)** _(2021, blog)_ —— Uber 团队对 Hudi 设计哲学的总结。
- **[Apache Paimon: A Stream-Lake Storage System](https://paimon.apache.org/docs/master/concepts/overview/)** _(2024+, official-doc)_ —— Paimon 官方设计文档，LSM on object store。

## 官方文档与 Spec

- **[Apache Iceberg Documentation](https://iceberg.apache.org/docs/latest/)** _(official-doc)_ —— 顶级分类：Tables（含 Branching/Config/Evolution/Maintenance/Performance/Reliability/Schemas/Partitioning）/ Catalogs / Storage / Migration / Integrations。**与本 wiki lakehouse/ 章节组织对齐**。
- **[Iceberg Table Spec v2/v3](https://iceberg.apache.org/spec/)** _(official-doc)_ —— v2 已 ratified，v3 incubating（含 Variant / Geometry / Row Lineage 等）。
- **[Delta Lake Protocol](https://github.com/delta-io/delta/blob/master/PROTOCOL.md)** _(official-doc)_ —— Delta 的开源协议 spec。
- **[Apache Iceberg REST Catalog Spec](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml)** _(official-doc)_ —— REST 协议事实标准。
- **[Puffin Spec](https://iceberg.apache.org/puffin-spec/)** _(official-doc)_ —— Iceberg 索引侧车格式。

## 经典工业博客

- **[Netflix Tech Blog - Iceberg Series](https://netflixtechblog.com/tagged/iceberg)** _(blog)_ —— Iceberg 诞生地的实战博客。**工业验证**。
- **[Tabular - The Iceberg Ecosystem](https://tabular.io/blog/)** _(blog, 2024 已被 Databricks 收购)_ —— Iceberg 生态深度内容。
- **[Apple - Iceberg at Scale](https://eng.apple.com/blog/apache-iceberg-at-apple)** _(blog)_ —— 大规模 Iceberg 工业实践。

## 综述 / 教科书

- **[Designing Data-Intensive Applications](https://dataintensive.net/)** _(2017, book - Kleppmann)_ —— 第三章存储与检索是湖表理解的基础。
- **[The Data Engineering Lifecycle](https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/)** _(2022, book)_ —— Joe Reis & Matt Housley，含 Lakehouse 章节。

## 待补 / 关注

- Iceberg v3 GA 后的新版 spec 解读
- Delta Lake 4.0 协议变更
- Paimon 2.0 后的流批一体演进

---

**贡献**：发现新权威 PR 加条目，按主页格式：`- **[标题](URL)** _(年份, 类型)_ —— 价值描述`。
