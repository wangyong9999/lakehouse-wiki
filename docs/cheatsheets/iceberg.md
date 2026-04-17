---
title: Iceberg 速查
description: 建表 / 维护 / 时间旅行 / 分支一张表
tags: [cheatsheet, iceberg]
---

# Iceberg 速查

## 建表模板

```sql
CREATE TABLE db.events (
  id         BIGINT,
  ts         TIMESTAMP,
  user_id    BIGINT,
  amount     DECIMAL(18,2),
  payload    STRING
) USING iceberg
PARTITIONED BY (days(ts), bucket(16, user_id))
TBLPROPERTIES (
  'write.format.default' = 'parquet',
  'write.parquet.compression-codec' = 'zstd',
  'write.target-file-size-bytes' = '536870912',     -- 512MB
  'write.distribution-mode' = 'hash',
  'history.expire.max-snapshot-age-ms' = '2592000000',  -- 30d
  'history.expire.min-snapshots-to-keep' = '20'
);
```

## 写入

```sql
INSERT INTO db.events VALUES (...);
INSERT OVERWRITE db.events PARTITION (dt='2026-04-17') VALUES (...);
MERGE INTO db.events t USING updates s ON t.id = s.id
  WHEN MATCHED THEN UPDATE SET ...
  WHEN NOT MATCHED THEN INSERT ...;
```

## Schema 演化

```sql
ALTER TABLE db.events ADD COLUMN device STRING;
ALTER TABLE db.events RENAME COLUMN payload TO raw_payload;
ALTER TABLE db.events ALTER COLUMN amount TYPE DECIMAL(20,2);
ALTER TABLE db.events DROP COLUMN device;
```

## Partition 演化

```sql
-- 查看当前分区规范
SELECT * FROM db.events.partitions LIMIT 5;

-- 加维度
ALTER TABLE db.events ADD PARTITION FIELD region;

-- 改粒度
ALTER TABLE db.events REPLACE PARTITION FIELD days(ts) WITH hours(ts);

-- 删
ALTER TABLE db.events DROP PARTITION FIELD region;
```

## 时间旅行

```sql
-- 按 snapshot id
SELECT * FROM db.events VERSION AS OF 123456789;

-- 按时间戳
SELECT * FROM db.events TIMESTAMP AS OF '2026-04-01 10:00:00';

-- 增量读取（两个 snapshot 之间的新增）
SELECT * FROM db.events.incremental_changes(
  start_snapshot => 100,
  end_snapshot   => 200
);
```

## 维护（一定定期跑）

```sql
-- 合并小文件
CALL system.rewrite_data_files(
  table => 'db.events',
  options => map('target-file-size-bytes', '536870912')
);

-- 合并 delete 文件
CALL system.rewrite_position_deletes('db.events');

-- 过期 snapshot
CALL system.expire_snapshots(
  'db.events',
  TIMESTAMP '2026-03-01'
);

-- 清理孤儿文件（出过问题才跑）
CALL system.remove_orphan_files(
  table => 'db.events',
  older_than => TIMESTAMP '2026-03-01'
);
```

## 分支与标签

```sql
-- 分支
ALTER TABLE db.events CREATE BRANCH dev;
INSERT INTO db.events.branch_dev VALUES (...);
CALL system.fast_forward('db.events', 'main', 'dev');

-- 标签（审计 / 训练集冻结）
ALTER TABLE db.events CREATE TAG audit_2026_q1 RETAIN 1825 DAYS;
SELECT * FROM db.events.tag_audit_2026_q1;
```

## 元数据表（观测 / 调试）

```sql
SELECT * FROM db.events.snapshots;            -- 所有 snapshot
SELECT * FROM db.events.manifests;            -- manifest 列表
SELECT * FROM db.events.files;                -- 每个 data file
SELECT * FROM db.events.history;              -- 变更历史
SELECT * FROM db.events.partitions;           -- 当前分区
SELECT * FROM db.events.refs;                 -- 分支 / 标签引用
```

## 性能诊断速查

| 症状 | 先看 | 常见原因 |
| --- | --- | --- |
| 查询慢 | `files`、`manifests` 数量 | 小文件没合 |
| 写入冲突 | `snapshots` 顺序 | 并发 commit |
| 空间膨胀 | `snapshots` count | 过期未清理 |
| Time travel 失败 | `snapshots` 保留 | `expire_snapshots` 过狠 |
| 列出分区慢 | 分区粒度 | 粒度太细或无 |

## 典型 property 参考

```
write.target-file-size-bytes        = 536870912 (512MB)
write.parquet.row-group-size-bytes  = 134217728 (128MB)
write.parquet.page-size-bytes       = 1048576   (1MB)
write.parquet.compression-codec     = zstd | snappy
write.parquet.compression-level     = 3
history.expire.max-snapshot-age-ms  = 604800000 (7d)
commit.manifest-merge.enabled       = true
commit.retry.num-retries            = 4
```

## 相关

- [Apache Iceberg](../lakehouse/iceberg.md) · [Snapshot](../lakehouse/snapshot.md) · [Compaction](../lakehouse/compaction.md) · [Branching & Tagging](../lakehouse/branching-tagging.md)
- Iceberg Maintenance docs: <https://iceberg.apache.org/docs/latest/maintenance/>
