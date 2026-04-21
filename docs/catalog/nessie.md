---
title: Project Nessie · Git-like Lakehouse Catalog
type: system
depth: 资深
level: A
last_reviewed: 2026-04-18
applies_to: Nessie 0.107.4+ (2025) / 2024-2026 生产
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

!!! note "示例语法标注 · 不是跨引擎通用 SQL"
    下面示例使用的 `CALL nessie_branch_create` / `USE REFERENCE` 等写法**依赖具体引擎和 Nessie 扩展**：
    - Spark：`nessie-spark-extensions` 插件提供这些 SQL
    - Trino：通过 Iceberg connector + Nessie catalog 配置 · 语法不完全一致
    - **直接 HTTP / CLI**：`nessie-cli` 用不同的命令风格
    
    不同客户端的精确语法请查各自文档；**概念是通用的，SQL 字面不是**。

```sql
-- Spark + nessie-spark-extensions 示例
CALL nessie_branch_create('etl-2026-04-20');

-- 在分支上写入（Iceberg SQL + Nessie 扩展）
USE REFERENCE 'etl-2026-04-20';
INSERT INTO db.orders ...
UPDATE db.inventory ...

-- 验证后合并
CALL nessie_merge('main', 'etl-2026-04-20');

-- 失败丢弃
CALL nessie_branch_delete('etl-2026-04-20');
```

### 机制 2 · 跨表原子 Commit · 边界和限制

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

**严格的原子性边界**（重要）：

- ✅ **通过 Nessie Catalog 的写**（Spark / Flink 用 Nessie catalog、Nessie CLI、Iceberg Nessie 客户端）是事务的一部分
- ❌ **绕过 Nessie 直写对象存储**（Spark 直接 `save("s3://...")` 或用非 Nessie catalog）**不参与** Nessie commit
- ❌ **多引擎混合不协同**：Trino（Nessie catalog）和 Spark（Hive catalog）同时写同一张表时，Nessie 只能看到 Trino 那半

**结论**：跨表原子**只对"经过 Nessie 的操作集合"成立**——不是"所有写这张表的操作"。**生产中必须保证所有写入都通过 Nessie Catalog**（否则跨表原子性无法保证 · Nessie commit graph 会与实际存储状态不一致）。

### Nessie 跨表 vs Iceberg spec multi-table commit 的差异

Iceberg spec 2024-2025 也在推 **multi-table transaction**（REST Catalog 层的原子多表），和 Nessie 的 Git-like commit **不完全等价**：

| 维度 | Nessie 跨 commit | Iceberg REST multi-table |
|---|---|---|
| 粒度 | Catalog 层 commit graph（可累积多 commit）| 单个 REST API 调用（单次原子） |
| 典型用例 | 长期 ETL 分支 · 跨表 WAP | 单次应用里协调 2-3 表的原子写 |
| 分支能力 | 一等公民（多 commit 跨表）| 无分支语义 · 仅单次调用原子 |
| 实现复杂度 | 高（需要 Nessie server）| 中（REST Catalog 实现） |
| 读侧语义 | 通过分支 / commit id 选视图 | 按 snapshot id 读一致视图（要协调多表）|

**适用选择**：要**长期分支 + 多 commit 累积跨表一致**选 Nessie；要**单次应用层原子多表**（如"下单扣库存+写 order"）· Iceberg multi-table commit 更轻量。

### 机制 3 · Tag

```sql
-- 发布时打 tag
CALL nessie_tag_create('release-2024-12');
```

Tag 是只读 ref，审计时直接 checkout。

### 机制 4 · GC · 与 Iceberg expire_snapshots 的协调

Nessie GC 是 **mark-and-sweep 两阶段**（官方 CLI `nessie-gc-tool`）：

- **mark 阶段**（别名 `identify`）：遍历所有 named references（分支 / tag）· 收集所有"live content"（活跃引用到的 snapshot）· 存入一个 live-contents-set
- **sweep 阶段**（别名 `expire`）：对照 live-contents-set · 列出表的所有文件 · 把**不在 live-set 里的文件**删掉

**和 Iceberg `expire_snapshots` 的协调逻辑**（运维关键）：

```
盲目分别跑的失败模式：
  Iceberg expire_snapshots 清掉了 snapshot X
  → 但 snapshot X 其实被 Nessie 的某个分支 / tag 引用
  → Nessie 分支查询: "snapshot not found" · 写入中断

正确做法：让 Nessie GC 成为唯一的清理者
  1. 运行 nessie-gc mark · 生成 live-contents-set
  2. 运行 nessie-gc sweep · 只清 live-set 外的文件
  3. **不要再独立跑 Iceberg expire_snapshots**（GC 本身已经代行 snapshot 过期语义）
```

**最常见的 Nessie 生产事故**：同时跑 Nessie GC 和 Iceberg 原生 expire——两者视角不同 · expire 把 Nessie 引用的文件清了 · 查询炸裂。**Nessie 栈下只用 Nessie GC 一条清理路径**。

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

### 真正的门槛不是技术 · 是工作流纪律

Nessie 的失败案例中，**不是装 server 有多难**，而是团队**低估了"Git for data"背后的组织成本**：

| 纪律要求 | 不遵守的后果 |
|---|---|
| **统一写入路径都走 Nessie** | 旁路直写 S3 的作业绕过 Nessie → 跨表原子消失 · 版本 graph 错乱 |
| **分支管理规范** | ETL 分支没人管 → 几百个悬挂分支 → metadata 膨胀、GC 无法推进 |
| **合并策略决策** | 冲突时是 reject / force / cherry-pick？**业务侧要定义规则**（谁有 merge 权限、什么时候可以 force）|
| **GC 和 Iceberg expire 协调** | 两边独立跑 → snapshot not found 运行时错（见机制 4）|
| **Tag 保留策略** | Tag 永不过期则 snapshot 永不回收 → 存储成本爆 |
| **跨团队分支可见性** | 多团队各用各分支 · 缺命名约定 → 治理视图混乱 |

**结论**：上 Nessie 约等于**把"版本化" 作为团队的一级工程实践**——不是一次技术选型，是一套工作流纪律。没有这个准备，装了 Nessie 也发挥不出它的真正价值。

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
