---
title: AWS Glue Data Catalog · AWS 栈的事实默认
type: system
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: AWS Glue Data Catalog (托管服务) · 与 Iceberg / Delta / Hudi / Spark / Trino / Athena 集成
tags: [catalog, aws, managed, glue]
category: catalog
license: AWS proprietary (托管服务)
status: stable
---

# AWS Glue Data Catalog

!!! tip "一句话定位"
    **AWS 栈里湖仓 Catalog 的事实默认**。不是产品发布的新选项——是大量 AWS 用户**开账号就在用、从 Hive/Athena 一路延伸过来**的那个 Catalog。**托管服务，不是开源实现**；协议兼容 HMS，近几年强化了对 Iceberg 的原生支持。

!!! abstract "TL;DR"
    - **托管、非开源**：AWS 服务（按请求/按存储收费）· 不能自部署
    - **协议谱系**：HMS 兼容 API + Iceberg native + Delta / Hudi 读支持
    - **和 Athena / EMR / Redshift / Lake Formation 深度捆绑**：这是它在 AWS 栈不可替代的原因
    - **Iceberg 支持路径**：Glue 作为 Iceberg Catalog 原生支持自 2022；2024-2025 随 S3 Tables 推进进一步深化
    - **权限**：走 AWS IAM + Lake Formation（行列级权限 / LF-tag）
    - **2024-12 S3 Tables 发布后**：AWS 同时拥有"Glue + S3 Tables"两条 Iceberg 路径，定位有分化
    - **协议层注记**：Glue 不走 Iceberg REST 协议 · Iceberg 客户端用 `GlueCatalog`（走 AWS SDK 直接调 Glue API）· **和 Polaris/Nessie 的 REST 客户端集成路径不同**

## 1. 为什么它在 AWS 栈是"不选也得用"

### AWS 产品生态的引力

| 服务 | 对 Glue 的依赖 |
|---|---|
| **Athena** | 默认读 Glue Catalog；换别的 Catalog 要额外 workaround |
| **EMR / EMR on EKS** | 新集群默认配 Glue 作 Hive metastore 替代 |
| **Redshift Spectrum** | 外表走 Glue |
| **Lake Formation** | 权限 / 行列级策略建在 Glue 之上 |
| **DataZone** | 数据市场 / 治理 · 以 Glue 为元数据底 |
| **S3 Tables** (2024-12) | 可以走 Glue 或独立 namespace，但 Glue 仍是老用户默认 |

**结论**：AWS 用户不走 Glue 意味着"把 Athena / Lake Formation / DataZone 的便利性全放弃"——很多团队权衡后选择接受 Glue 锁定。

### 价格模型

- **按 Catalog 对象数**（表/分区）月计费
- **按请求数**计费
- **和 Iceberg 配合时**：高频 commit 会产生高频 Glue API 调用，账单要盯

## 2. 协议能力

### 核心 API 谱系

- **HMS 兼容层**：老 Hive 工具用 `HiveMetaStoreClient` 直接访问
- **Glue native API**：新能力（Iceberg 特性）走这里
- **Iceberg GlueCatalog**：Iceberg Java / Python 客户端直接对接 Glue，不需要 REST 层

### 支持的表格式

| 格式 | 支持度 |
|---|---|
| **Iceberg** | 原生（GlueCatalog 实现 2022+）· 2024-2025 持续深化 |
| **Delta** | 读支持（Athena + EMR）· 写有限 |
| **Hudi** | 读支持 |
| **Hive Parquet / ORC** | 完整 |

### 和 S3 Tables 的关系（2024-12 之后）

**S3 Tables 不是 Glue 的替代，更像是专门为 Iceberg 优化的托管方案**：

- **Glue**：通用 Catalog，支持多表格式，深度集成 AWS 治理
- **S3 Tables**：S3 原生 Iceberg 托管（内置 compaction / snapshot expiry / 维护）· 独立 namespace

2024-2026 AWS 策略是**双轨并行**：新 Iceberg 工作负载可直接用 S3 Tables；有 Athena / Lake Formation 治理需求的仍走 Glue。**两者的整合方式**：AWS 2025 引入 **federated catalog `s3tablescatalog`**——启用后 Glue Data Catalog 自动发现 account + region 内的所有 S3 table bucket，**作为 federated child catalog 挂到 Glue 命名空间下**（非完全独立 namespace）；Lake Formation 可统一授权、Athena / EMR 可 `SELECT`。S3 Tables 有自己的元数据存储层 · Glue 通过 federated 引用聚合治理 · 读者可把它理解为"S3 Tables 是数据平面 · Glue 是治理平面"。

## 3. 和其他 Catalog 的边界

| 维度 | Glue | Iceberg REST (Polaris) | Nessie | Unity | HMS |
|---|---|---|---|---|---|
| **可自部署** | ❌（AWS 托管）| ✅ | ✅ | ✅ OSS | ✅ |
| **Iceberg 协议** | GlueCatalog（自家 API）| REST v1 | REST v1 + 自家 | REST v1 | HMS 兼容 |
| **跨云中立** | AWS-only | ✅ | ✅ | 中立（Databricks 重） | ✅ |
| **生态绑定** | Athena / EMR / LF | 多引擎 | Dremio / 多引擎 | Databricks | Spark / Hadoop |
| **权限模型** | IAM + Lake Formation | RBAC | Access 控制 | 多模 RBAC + 血缘 | Ranger / Sentry |
| **Git-like 分支** | ❌ | 依实现 | ✅ | ❌ | ❌ |

## 4. 工程细节

### Spark 配置（Iceberg + Glue）

```python
spark = SparkSession.builder \
    .config("spark.sql.catalog.glue", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.glue.catalog-impl",
            "org.apache.iceberg.aws.glue.GlueCatalog") \
    .config("spark.sql.catalog.glue.warehouse", "s3://my-bucket/warehouse/") \
    .config("spark.sql.catalog.glue.io-impl",
            "org.apache.iceberg.aws.s3.S3FileIO") \
    .getOrCreate()

spark.sql("CREATE TABLE glue.db.orders (...) USING iceberg")
```

### Trino 配置

```properties
connector.name=iceberg
iceberg.catalog.type=glue
hive.s3.aws-access-key=...
```

### Lake Formation 权限

```sql
-- 细粒度权限走 Lake Formation
GRANT SELECT ON TABLE db.orders TO IAM_ROLE 'arn:aws:iam::123:role/analyst'
  FILTER (region = 'US');

-- LF-tag · 批量打标 + 基于 tag 授权
ASSOCIATE LF-TAG ('pii', 'true') WITH TABLE db.users COLUMN email;
```

## 5. 陷阱与反模式

- **小文件 / 高频 commit 场景 Glue API 账单爆炸**：每次 Iceberg commit 要调 GetTable + UpdateTable · 秒级 commit 的流式 CDC 场景下 Glue API 调用数激增（可能比 Catalog 对象数月费还高出几倍）· 定期看账单的 API calls line item
- **跨账号访问配置复杂**：Glue Catalog resource policy + 跨账号 IAM + LF cross-account role 三层叠加 · 权限校验顺序中**任一层配错就 Access Denied** · 生产前做端到端烟测不可少
- **Athena 查询和 EMR 查询权限不一致**：Athena 走 Lake Formation 默认，EMR 可能走 IAM-only——同一张表权限表现不同
- **Iceberg 新特性跟进延迟**：Glue 对 Iceberg 新特性的支持通常**滞后上游 1-2 个版本周期** · 部分 v3 能力（如 row lineage / 部分 transform）2026-Q2 仍在逐步启用 · **追 Iceberg 最新能力的团队应该上游社区 REST Catalog 更合适**
- **迁出成本高**：Glue 没有原生 dump/restore，迁 Polaris / Nessie 要自己写迁移脚本（或用 Iceberg `register_table`）
- **HMS 兼容 API 的能力上限**：老 Hive 工具走兼容层时看不到 Iceberg 新特性

## 6. 选型判断

**选 Glue**：

- AWS 栈重度使用 · Athena / Lake Formation / DataZone 生态要保
- 运维预算有限 · 托管服务免维护
- 权限走 IAM + Lake Formation 已建好

**不选 Glue**：

- 多云或跨云中立需求（Glue 不跨云）
- 需要 Git-like 分支 → Nessie
- 需要跨 Catalog 联邦 → 上面叠 Gravitino
- 需要 Iceberg v3 新特性最早追 GA → 走社区 REST Catalog 更新快

**和 Polaris / REST Catalog 并存**：可以 · 不同 warehouse 用不同 Catalog，应用层选择；但治理一致性需自建。

## 7. 相关

- [Iceberg REST Catalog](iceberg-rest-catalog.md) · [Apache Polaris](polaris.md) · [Unity Catalog](unity-catalog.md)
- [Hive Metastore](hive-metastore.md)（Glue 的协议近亲）
- [Catalog 全景对比](../compare/catalog-landscape.md)

## 8. 延伸阅读

- **AWS Glue Data Catalog 文档**：<https://docs.aws.amazon.com/glue/latest/dg/components-overview.html>
- **Iceberg Glue Catalog 文档**：<https://iceberg.apache.org/docs/latest/aws/#glue-catalog>
- **AWS Lake Formation**：<https://docs.aws.amazon.com/lake-formation/>
- **S3 Tables 发布博客（2024-12）**：AWS re:Invent 公告
