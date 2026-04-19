---
title: Iceberg Branching & Tagging
type: concept
depth: 进阶
applies_to: Iceberg spec v2+ · 引擎 1.2+（Spark/Flink/Trino）
prerequisites: [snapshot, time-travel]
tags: [lakehouse, iceberg, branch]
related: [snapshot, time-travel, nessie]
systems: [iceberg]
status: stable
---

# Iceberg Branching & Tagging

!!! tip "一句话理解"
    Iceberg **spec v2 引入**（引擎侧 1.2+ 普遍可用）、表级别支持 Git-like **分支** 和 **标签**。分支给你一条独立的写路径；标签给你一个不变的时点快照。和 Nessie 的跨表 Git-like 不同，这是**单表内**的分支机制。

!!! abstract "TL;DR"
    - **Branch**：一个命名的写入路径；每次 commit 只推进该分支
    - **Tag**：不变的 snapshot 引用；**不会被 `expire_snapshots` 清掉**
    - 用途：ETL 隔离、审计快照、AB 测试、热修复
    - 和 **Nessie 的多表事务** 不互斥：Iceberg 分支是单表，Nessie 是跨表

## 概念

### Branch（分支）

每个分支 = 一个独立的 snapshot 演进序列。默认分支 `main`：

```sql
-- 默认写 main 分支
INSERT INTO orders VALUES (...);

-- 创建新分支
ALTER TABLE orders CREATE BRANCH dev SNAPSHOT 12345;

-- 在 dev 分支上写
INSERT INTO orders.branch_dev VALUES (...);

-- 读 dev 分支
SELECT * FROM orders.branch_dev;

-- fast-forward main 到 dev
CALL system.fast_forward('orders', 'main', 'dev');
```

分支之间 **独立**，互不影响。

### Tag（标签）

命名的 snapshot 引用，只读：

```sql
-- 给当前 snapshot 打 tag
ALTER TABLE orders CREATE TAG audit_2026_q1 
  SNAPSHOT 98765
  RETAIN 365 DAYS;

-- 读 tag
SELECT * FROM orders.tag_audit_2026_q1;
```

**重要特性**：带 tag 的 snapshot **不会被 `expire_snapshots` 清理**。合规审计、训练集冻结都靠它。

## WAP · Write-Audit-Publish 工作流

**WAP** 是 Iceberg 分支最成熟的工作流——把"先写、再验证、最后公开"变成原子操作：

```
    Write              Audit              Publish
 ┌─────────┐        ┌──────────┐       ┌──────────┐
 │ branch  │  ───→  │ 数据质量 │ ───→  │ 合并到   │
 │ etl-YYY │        │ 校验     │       │ main     │
 └─────────┘        └──────────┘       └──────────┘
                        ↓
                    失败就丢弃 branch
```

典型模板（Iceberg Spark Procedure）：

```sql
-- 1. Write: 短 branch 写入
ALTER TABLE db.orders CREATE BRANCH `etl-${run_id}` RETAIN 7 DAYS;
INSERT INTO db.orders.branch_etl_20260418 SELECT ... ;

-- 2. Audit: 在分支上跑 DQ 校验
SELECT COUNT(*) FROM db.orders.branch_etl_20260418;
-- 业务侧 assert: 行数、空值率、去重数等

-- 3. Publish: 通过就快进合并
CALL system.fast_forward('db.orders', 'main', 'etl-20260418');
-- 不过关就丢
ALTER TABLE db.orders DROP BRANCH `etl-20260418`;
```

**WAP 的价值**：
- 失败作业**完全不污染**生产 main 分支（不是先写后回滚，而是"根本没写到 main"）
- 同一批数据可以多作业并行验证（各自 branch）
- 下游消费者永远看到"通过校验的 main"

是湖上 ETL 严肃化的核心工具。

## 四个典型用法

### 用法 1：ETL 作业的隔离写入

```sql
-- 每日作业开一个短 branch
CALL system.create_branch('orders', 'etl_20260417');

-- 作业在该分支上写、验证
INSERT INTO orders.branch_etl_20260417 SELECT ...;
CALL system.validate_data_quality('orders.branch_etl_20260417');

-- 通过后合并到 main
CALL system.fast_forward('orders', 'main', 'etl_20260417');

-- 不通过就丢弃
CALL system.drop_branch('orders', 'etl_20260417');
```

**价值**：失败作业不污染生产。

### 用法 2：审计时点

季报、合规报告、外部审计要"以某时刻为准"：

```sql
ALTER TABLE orders CREATE TAG q1_2026_audit SNAPSHOT 98765 RETAIN 5 YEARS;
```

5 年内 `expire_snapshots` 不碰这个 snapshot，审计可以随时回看。

### 用法 3：训练集冻结

ML 训练用的数据集一定要冻结：

```sql
ALTER TABLE features CREATE TAG recsys_v3_train RETAIN 365 DAYS;
```

模型版本 metadata 里记这个 tag 名。一年内能复现训练。

### 用法 4：AB 测试 / 热修复

```sql
-- 发现 main 分支某批数据有问题
CALL system.create_branch('events', 'hotfix', SNAPSHOT => 12300);

-- 在 hotfix 上重写
DELETE FROM events.branch_hotfix WHERE ...;
INSERT INTO events.branch_hotfix SELECT fixed_data ...;

-- 验证后 fast-forward main
```

## 分支模型 vs Nessie

| 维度 | Iceberg 原生 | Nessie |
| --- | --- | --- |
| **粒度** | 单表 | 跨表（catalog 级别） |
| **原子跨表提交** | ❌ | ✅ |
| **Git-like merge / cherry-pick** | 简单 fast-forward | 完整 |
| **审计** | snapshot + tag | commit log + 多表一致 |
| **复杂度** | 低 | 中 |
| **适合** | 单表作业隔离、tag 冻结 | 数据版本化工作流 |

**不互斥**：可以把 Iceberg 表放 Nessie Catalog，跨表用 Nessie 分支，单表内用 Iceberg branch 细化。

## 运维

### Branch 清理

```sql
-- 列出所有 branch
SELECT * FROM orders.refs;

-- 删除不用的 branch
ALTER TABLE orders DROP BRANCH etl_20260401;
```

### Tag 生命周期

`RETAIN` 子句指定保留期；到期后 `expire_snapshots` 可以回收相关数据。关键合规 tag 可设 `RETAIN FOREVER`。

### 和 Snapshot Expiry 的交互

```sql
CALL system.expire_snapshots(
  'orders',
  TIMESTAMP '2026-01-01'
);
-- 不会清理：1) main / 其他 branch 的 current snapshot;
--          2) 带 RETAIN 未过期的 tag 指向的 snapshot
```

## 陷阱

- **分支太多**：每个分支是一条引用，太多会让 metadata.json 膨胀
- **忘记清理 branch**：ETL 的短分支如果失败未清理 → 引用越攒越多
- **Tag 没 RETAIN** → 默认可能被清
- **Reader 不认 branch**：老版本 Iceberg / 老引擎可能不识别
- **Branch 间无法跨表事务**：跨表要靠 Nessie

## 相关

- [Snapshot](snapshot.md)
- [Time Travel](time-travel.md)
- [Nessie](../catalog/nessie.md)
- [Apache Iceberg](iceberg.md)

## 延伸阅读

- Iceberg Branching and Tagging spec: <https://iceberg.apache.org/docs/latest/branching/>
- *Git for Data*（Dremio / Tabular 博客系列）
