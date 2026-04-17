---
title: 故障排查手册
type: concept
depth: 进阶
prerequisites: [observability, performance-tuning]
tags: [ops, troubleshooting]
related: [observability, performance-tuning, compaction]
systems: [iceberg, spark, trino, flink]
status: stable
---

# 故障排查手册

!!! tip "一句话理解"
    生产湖仓经常出的 12 类问题 + 排查树 + 修复姿势。**出事时不慌**的唯一方法 = 提前见过这些形状。

!!! abstract "TL;DR"
    - 80% 的"慢"来自**数据布局 + 小文件 + delete files**
    - 80% 的"写挂"来自 **commit 冲突 + schema 漂移 + 外部 Catalog 问题**
    - 80% 的"数据对不上"来自 **CDC offset / snapshot 选错 / 时区**
    - **先看观测面板再动手** —— 观察 > 假设

## 问题 1：查询突然变慢

**检查顺序**：

1. EXPLAIN 看扫了多少字节 / 文件数
2. 如果文件数暴增 → 小文件未 compact，跑 `rewrite_data_files`
3. 如果扫描字节远超预期 → 谓词下推失效，检查 WHERE 是否有 UDF / CAST
4. 如果并发增加 → 引擎 resource group / queue 是否公平
5. 如果特定时间段慢 → 和 compaction / ETL 高峰冲突

**工具**：Trino Web UI / Spark History Server / Iceberg metadata tables (`table.files` / `table.snapshots`)

## 问题 2：Commit 冲突（concurrent modification）

**现象**：`ValidationException: Cannot commit, conflicting write`

**原因**：两个写作业对同一张表并发 commit，基于同一个 parent snapshot，只有一个成功。

**修复**：

- 写作业内置重试（Spark / Flink 默认有但次数有限）
- 不同作业**分不同分区写**（物理避免冲突）
- 批作业和流作业不要写同一张表（除非协调）
- 看 Catalog 是否正确实现 CAS

## 问题 3：小文件海啸

**现象**：某表查询慢、元数据 list 慢、S3 费用异常。

**检查**：

```sql
SELECT count(*) FROM my_table.files WHERE file_size_in_bytes < 16 * 1024 * 1024;
```

超过几千个 16MB 以下文件 = 需要治理。

**修复**：

- `rewrite_data_files` with target size
- Flink sink `sink.parallelism` + `bucket` 配合，控制并行度
- CDC 频率降低（增加 checkpoint interval）

## 问题 4：Delete file 积压

**现象**：MoR 表查询延迟缓慢上升。

**检查**：

```sql
SELECT count(*), sum(record_count) 
FROM my_table.delete_files;
```

和数据文件的比例如果 > 30%，该合了。

**修复**：

```sql
CALL system.rewrite_position_deletes('my_table');
CALL system.rewrite_data_files('my_table', strategy => 'sort');
```

## 问题 5：Schema 演化破坏下游

**现象**：下游作业报错 "column not found" 或类型不兼容。

**常见来源**：

- 上游偷偷 drop column
- 类型从 INT 改成 STRING
- 字段重命名且下游 hardcode 了名字

**预防**：

- CI 对 schema 变化做 **breaking change** 检测
- 下游作业用 Iceberg 列 ID 引用
- 契约化（[数据治理](data-governance.md)）

**应急**：回滚 Snapshot + 通知上游。

## 问题 6：Time Travel 不到

**现象**：`VERSION AS OF xxx` 报错 "Snapshot not found"。

**原因**：`expire_snapshots` 清了。

**修复**：

- 重要 snapshot 打 **tag**（带 RETAIN）
- 调整保留策略拉长
- 这次只能从备份恢复或重跑 ETL

## 问题 7：CDC 延迟 / 数据丢

**现象**：Paimon 表落后上游分钟到小时级。

**检查**：

1. Flink CDC source offset lag
2. Kafka consumer group lag
3. Flink checkpoint interval
4. Sink 端小文件导致的 commit 慢

**修复**：

- 增加 Flink 并行度（但注意 Kafka partition 数上限）
- 调 checkpoint interval
- 加压 sink（多 writer 并行）

## 问题 8：向量检索召回异常下降

**现象**：同一套 embedding，recall@10 从 0.85 掉到 0.70。

**排查**：

1. Embedding 模型版本有没有悄悄变？
2. 向量索引重建策略 / 新 fragment 是否及时建索引？
3. 查询侧 `ef` / `nprobe` 参数是否被改？
4. 数据分布是否发生漂移（新类别涌入）？

**修复**：
- 固定 model + version；严格版本 pinning
- 监控 index lag
- 调整 ANN 参数

## 问题 9：Catalog 服务慢 / 挂

**现象**：所有引擎查询超时，或 commit 卡死。

**检查**：

- Catalog 服务端 CPU / 内存
- 背后 RDBMS（HMS / Unity 后端 Postgres）是否打爆
- 网络连通

**修复**：

- 读副本分流
- 连接池大小调优
- 重启 Catalog 服务（保留 Snapshot，重启后 self-heal）

## 问题 10：对象存储 API 费用异常

**现象**：S3 LIST / GET 费用月增 3 倍。

**原因**（排列组合）：

- 小文件爆炸 → list 次数暴增
- 客户端轮询
- 跨区读取
- 某个作业高频 HEAD 同一批 key

**修复**：

- 聚合小文件
- 限流 bad-client
- 使用 inventory 报告统计访问模式

## 问题 11：训练集复现不了

**现象**：同样代码、同样模型、和一周前训的结果不一样。

**原因**：

- 训练集依赖的 Iceberg snapshot 被过期了（只有一个指针 latest，latest 变了）
- 模型代码依赖 LLM / Embedding API，API 模型升级

**修复**：

- 训练集物化成独立表 + Tag（见 [离线训练数据流水线](../scenarios/offline-training-pipeline.md)）
- 记 `dataset_snapshot_id` / `model_version` / `embedding_version`

## 问题 12：权限异常

**现象**：某用户本应能读 A 表却 403；另一用户应看不到 B 的 PII 却看到。

**排查**：

1. Catalog 层 ACL（`SHOW GRANTS ON TABLE A TO USER x`）
2. 存储层：STS token 权限是否限制到这张表
3. 行列级 policy 是否生效（`EXPLAIN` 看 filter 应用）

**修复**：按 [安全与权限](security-permissions.md) 的四层防线排查，从上到下。

## 通用原则

- **先看 dashboard 再动手**：不要凭感觉
- **别刻意 "快速修复"**：临时补丁变永久坑
- **改动留 ADR**：一年后你能回头知道为啥
- **事后复盘**：每次 P1 写 postmortem

## 相关

- [可观测性](observability.md)
- [性能调优](performance-tuning.md)
- [Compaction](../lakehouse/compaction.md)
- [Delete Files](../lakehouse/delete-files.md)

## 延伸阅读

- Iceberg Maintenance Guide
- *Debugging Spark Applications*（各种博客）
- *The Site Reliability Workbook* (Google SRE)
