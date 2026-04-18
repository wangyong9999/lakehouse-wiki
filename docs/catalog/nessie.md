---
title: Project Nessie · Git-like Lakehouse Catalog
type: system
depth: 资深
level: A
last_reviewed: 2026-04-18
applies_to: Nessie 0.97+ / 2024-2025 生产
tags: [catalog, lakehouse, git-like, branching]
category: catalog
repo: https://github.com/projectnessie/nessie
license: Apache-2.0
status: stable
---

# Project Nessie · Git-like Lakehouse Catalog

!!! tip "一句话定位"
    **给湖仓带来 Git 工作流**——分支、提交、合并、标签、回滚。独特的**跨表原子提交**能力在数据工程事故恢复和 CI/CD 场景非常强。但作为 Catalog 生态的一员，它主要在**有数据分支刚需的团队**落地，不是 Iceberg REST Catalog 的通用替代。

!!! abstract "TL;DR"
    - **核心能力**：Branch / Commit / Merge / Tag，跨多表**原子事务**
    - **协议**：兼容 Iceberg REST Catalog + 自有 API
    - **Merkle-tree 存储**：类似 Git 内部结构
    - **Version Store 可插拔**：RocksDB / JDBC (Postgres) / MongoDB / DynamoDB
    - **最适合**：数据 CI/CD · ETL 隔离 · 审计严 · 跨表原子 commit
    - **不适合**：中小团队、没分支诉求、或者已深度绑 Glue / Unity

## 1. 它解决什么 · 没有 Nessie 世界的痛

### 传统 Catalog 的局限

HMS / Glue / Unity 都只维护"**最新表状态**"。**数据工程师日常痛点**：

| 痛点 | 传统做法 | Nessie 做法 |
|---|---|---|
| ETL 中途挂，半成品污染生产表 | 事后 Rollback 麻烦 | **分支跑，失败丢弃** |
| 测试新模型要一张隔离的表 | 复制表、占空间 | **零拷贝分支** |
| 发布前审核数据 | SQL 比对 | **diff 两个 branch** |
| 一次变更涉及 5 张关联表 | 分别 commit、不原子 | **一个 commit 跨表** |
| 审计"6 月份发布那一刻表是什么样" | 拼 timestamp 查 Snapshot | **checkout tag** |

Nessie 的命题：**"数据像代码一样协作"**。

### 历史

- **Dremio 2020** 开源 Project Nessie
- 社区治理后独立演化
- 2024+ 与 Apache Iceberg REST Catalog 协议深度兼容
- 生态仍**比 Glue / Unity 小**，但在金融 / 监管严的场景有采用

## 2. 架构深挖

```mermaid
flowchart LR
  subgraph "客户端"
    spark[Spark]
    trino[Trino]
    flink[Flink]
    pyice[pyiceberg]
  end

  subgraph "Nessie Server"
    api[REST API<br/>Iceberg REST + Nessie]
    graph[Commit Graph<br/>Merkle Tree]
    auth[AuthN/AuthZ]
    gc[GC]
  end

  subgraph "Version Store"
    rocks[(RocksDB)]
    pg[(Postgres)]
    mongo[(MongoDB)]
    dynamo[(DynamoDB)]
  end

  subgraph "对象存储"
    s3[(S3 / GCS / OSS)]
  end

  spark & trino & flink & pyice -->|Iceberg REST| api
  api --> graph
  graph --> rocks & pg & mongo & dynamo
  api -.-> s3
```

### 核心对象

| 对象 | 类比 Git |
|---|---|
| **Commit** | Git commit |
| **Branch / Tag** | 分支 / 标签 |
| **Reference** | HEAD / ref |
| **Merge** | 合并分支 |
| **Content Key** | 文件路径（表 ID） |
| **Content** | 文件内容（表 metadata 引用） |

### 存储模型（Merkle Tree）

```
Commit C  (parent=B, op=[add_table(a)])
Commit B  (parent=A, op=[update_metadata(b)])
Commit A  (root)
```

每次写 = 新 commit。分支指向某 commit；**切分支几乎零成本**（只改指针）。

## 3. 关键机制

### 机制 1 · 分支与提交

```sql
-- 创建分支
CALL nessie_branch_create('etl-2024-12-01');

-- 在分支上写入（Iceberg SQL + Nessie 扩展）
USE REFERENCE 'etl-2024-12-01';
INSERT INTO db.orders ...
UPDATE db.inventory ...

-- 验证后合并
CALL nessie_merge('main', 'etl-2024-12-01');

-- 失败丢弃
CALL nessie_branch_delete('etl-2024-12-01');
```

### 机制 2 · 跨表原子 Commit

Nessie 核心优势：**一个 commit 可以同时改多张表**。

```sql
-- 一个 transaction 涉及 3 张表
BEGIN TRANSACTION;
INSERT INTO orders ...
UPDATE inventory ...
DELETE FROM sessions WHERE ...
COMMIT;
-- → Nessie 产生 1 个 commit 涉及 3 张表
```

读方看到**要么全看到、要么一个都看不到**。

### 机制 3 · Tag

```sql
-- 发布时打 tag
CALL nessie_tag_create('release-2024-12');
```

Tag 是只读 ref，审计时直接 checkout。

### 机制 4 · GC

清理被丢弃分支 / 过期 commit 的数据文件：

```
nessie-cli gc --after '2024-12-01'
```

和 Iceberg 自己的 `expire_snapshots` 要协调。

### 机制 5 · 冲突解决

数据不是代码，**冲突语义微妙**：
- 两个分支改同一张表 → 合并时冲突
- Nessie 默认**拒绝合并**冲突
- 解决：`--force` 或 cherry-pick

## 4. 工程细节

### Version Store 选择

| 存储 | 适合 | 吞吐 |
|---|---|---|
| **RocksDB**（单机）| 测试 / 小规模 | 高但单点 |
| **JDBC (Postgres)** | 生产主流 | 中 + HA |
| **MongoDB** | 遗留 Mongo 栈 | 中 |
| **DynamoDB** | AWS 深度 | 高 + Serverless |
| **BigTable** | GCP | 高 |

**生产推荐**：JDBC Postgres + Multi-AZ。

### 部署（Docker）

```yaml
version: "3"
services:
  nessie:
    image: ghcr.io/projectnessie/nessie:latest
    ports: ["19120:19120"]
    environment:
      QUARKUS_DATASOURCE_JDBC_URL: jdbc:postgresql://postgres:5432/nessie
      QUARKUS_DATASOURCE_USERNAME: nessie
      QUARKUS_DATASOURCE_PASSWORD: pass
      NESSIE_VERSION_STORE_TYPE: JDBC
  postgres:
    image: postgres:15
```

### Spark 连接

```scala
spark.conf.set("spark.sql.catalog.nessie", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.nessie.catalog-impl", "org.apache.iceberg.nessie.NessieCatalog")
spark.conf.set("spark.sql.catalog.nessie.uri", "http://nessie:19120/api/v2")
spark.conf.set("spark.sql.catalog.nessie.ref", "main")
spark.conf.set("spark.sql.catalog.nessie.warehouse", "s3://lake/warehouse")
```

### CLI

```bash
nessie-cli --url http://nessie:19120
> BRANCH etl-test
> SHOW LOG
> MERGE BRANCH etl-test INTO main
```

## 5. 现实检视 · Nessie 在 2026

### Nessie 的实际采用情况

- **Dremio** 产品内嵌 Nessie（主推厂商）
- **金融 / 监管严场景** 有中等规模采用
- **多数互联网公司** 仍用 Glue / Unity / REST Catalog（不需要 Git 能力）
- 社区**稳定但不算飞速增长**

### 独特价值没被替代

- **跨表原子事务**：Iceberg v3 有 multi-table transaction 但**语义和 Nessie 的跨 commit 不完全等价**
- **Git-like 分支工作流**：**没有其他 Catalog 有**
- **数据 CI/CD**：Nessie + Trino/Spark → 数据的 "PR" 流程

### 不适合的场景

- 团队不用 Git 思维
- 没有跨表 commit 需求
- 已经深度绑 Glue / Unity
- 中小规模（几十张表）

### 2024-2026 格局

- **Iceberg REST Catalog 主导**，Nessie 是 **Iceberg REST 的超集实现**
- **Unity Catalog 和 Polaris** 在治理 / 权限发力
- Nessie 聚焦**版本化数据**垂直
- 未来可能和 Iceberg Branch/Tag 机制进一步融合

## 6. 代码示例

### Trino 用 Nessie Catalog

```properties
# catalog/nessie.properties
connector.name=iceberg
iceberg.catalog.type=nessie
iceberg.nessie-catalog.uri=http://nessie:19120/api/v2
iceberg.nessie-catalog.ref=main
iceberg.nessie-catalog.default-warehouse-dir=s3://lake/warehouse
```

```sql
-- 查 main 分支
SELECT * FROM nessie.db.orders;

-- 切到实验分支
USE nessie."ref" = 'experiment';
SELECT * FROM nessie.db.orders;
```

### ETL 分支隔离模式

```python
from pynessie import init_client
nessie = init_client(endpoint="http://nessie:19120/api/v2")

# 1. 创建临时分支
branch = f"etl-{date.today()}"
nessie.create_reference(branch, base_ref="main")

try:
    # 2. 在分支上跑作业
    spark.conf.set("spark.sql.catalog.nessie.ref", branch)
    run_etl_pipeline()
    
    # 3. 数据质量检查
    assert_checks(branch)
    
    # 4. 成功合并
    nessie.merge(branch, "main")
except Exception as e:
    # 5. 失败丢弃
    nessie.delete_reference(branch)
    raise
```

### Tag 用于发布

```python
# 每次发布打 tag
nessie.create_tag(
    tag_name=f"release-{release_version}",
    from_ref="main",
    hash_=current_head_hash
)

# 审计：查看 tag 时刻的表
spark.conf.set("spark.sql.catalog.nessie.ref", "release-2024-12")
```

## 7. 陷阱与反模式

- **长期分支不合并**：偏离 main 太远、合并冲突多
- **GC 和 Iceberg expire 不协调**：孤儿文件
- **Version Store 用 RocksDB 上生产**：单点
- **Merge 不做 data quality 检查**：冲突没被发现
- **把 Nessie 当 Git UI 用**：没匹配的 Web UI，生态弱
- **PR 流程太重**：小修改还走 branch + review 效率低
- **权限管理弱**：Nessie 本身权限机制比 Unity 简单

## 8. 延伸阅读

- **[Nessie 官方文档](https://projectnessie.org/)**
- **[Nessie GitHub](https://github.com/projectnessie/nessie)**
- **[*Iceberg REST Catalog 兼容性*](https://projectnessie.org/iceberg/iceberg/)**
- **[Dremio Lakehouse 案例](https://www.dremio.com/blog/)**
- **[*Data Versioning for Lakehouses* 社区讨论](https://github.com/projectnessie/nessie/discussions)**

## 相关

- [Iceberg REST Catalog](iceberg-rest-catalog.md) · [Apache Polaris](polaris.md) · [Unity Catalog](unity-catalog.md)
- [Catalog 全景对比](../compare/catalog-landscape.md)
- [湖表](../lakehouse/lake-table.md) · [Snapshot](../lakehouse/snapshot.md) · [Branching & Tagging](../lakehouse/branching-tagging.md)
