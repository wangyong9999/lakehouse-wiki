---
title: Iceberg REST Catalog
type: system
tags: [catalog, iceberg, protocol]
category: catalog
repo: https://github.com/apache/iceberg
license: Apache-2.0
status: stable
---

# Iceberg REST Catalog

!!! tip "一句话定位"
    Iceberg 官方定义的 **HTTP/REST 层 Catalog 协议**。把"表在哪里、哪个 snapshot 是当前的、怎么 commit"标准化为一套 API，任何实现遵守协议即可互通。正在成为取代 HMS 的事实标准。

## 它解决什么

早期 Iceberg 每家 Catalog 自己一套实现：HiveCatalog、GlueCatalog、JDBCCatalog、NessieCatalog… 引擎端要各自适配。对上游使用者：

- 想在云 A 用 Glue、云 B 用自研 Catalog？引擎得两份代码
- 想自己做一个轻量 Catalog 服务？没有标准 API 可参考
- 企业想托管 Catalog 给多租户用？没有统一协议

REST Catalog 把这些问题统一：**一份协议，任何实现自取**。

## 协议能力

主要 endpoint：

| 类别 | endpoint 示例 |
| --- | --- |
| namespace | `GET /v1/namespaces` / `POST` / `DELETE` |
| table | `GET /v1/{ns}/tables/{t}` / `POST` / `DELETE` / `PUT`（rename） |
| snapshot | `POST /v1/{ns}/tables/{t}/commit` |
| config | `GET /v1/config` |
| view | `GET /v1/{ns}/views/{v}` |

引擎（Spark / Trino / Flink）通过 `org.apache.iceberg.rest.RESTCatalog` 连接，URL 是服务端地址。

## 实现方

- **Tabular / Snowflake Open Catalog / Databricks UC** —— 商业服务
- **Apache Polaris**（Snowflake 开源） —— 开源参考实现
- **Apache Gravitino** —— 多引擎 / 多格式的统一元数据层，支持 Iceberg REST
- **Nessie** —— 同时暴露自有协议和 Iceberg REST
- **自研** —— 一些公司基于 Iceberg 社区参考实现包装内部服务

## 为什么重要

对"多模一体化湖仓"路线的影响特别大：

- 把**引擎和元数据解耦**后，团队可以独立演进 Catalog 能力（分支、权限、多模资产管理）
- 新能力（比如"向量表"作为一类表资产）可以通过 REST 协议扩展而不影响引擎
- 跨云 / 跨区域场景只需部署 REST Catalog 服务即可统一管理

## 陷阱与坑

- **协议在演进**：关注 Iceberg 社区的协议版本，老版本客户端和新版本服务端的兼容不一定完美
- **认证 / 多租户**：协议本身规定较松，OAuth / Bearer Token 是常见做法，实现时要一致
- **commit 性能**：commit 路径的延迟和并发设计是服务端实现的核心差异

## 延伸阅读

- Iceberg REST Catalog spec: <https://iceberg.apache.org/docs/latest/rest-catalog/>
- Apache Polaris: <https://github.com/apache/polaris>
