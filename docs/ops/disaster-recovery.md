---
title: 灾难恢复 · DR / Backup · 含 AI 场景
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: Iceberg / Paimon Snapshot · Nessie · 向量库备份 · Model Registry 备份 · 不可变备份 · 2024-2026 实践
prerequisites: [object-storage, snapshot, time-travel]
tags: [ops, dr, backup, recovery, ai-dr, ransomware]
aliases: [Disaster Recovery, Backup]
related: [snapshot, time-travel, multi-tenancy, migration-playbook, incident-management, change-management]
systems: [iceberg, paimon, nessie, milvus, lancedb]
status: stable
---

!!! warning "章节分工声明"
    - **本页**：湖仓 + AI 的 **DR / Backup 工程实践**
    - **误操作回滚机制** → [change-management](change-management.md) §回滚
    - **事故响应流程** → [incident-management](incident-management.md)
    - **迁移**（不同系统搬迁）→ [migration-playbook](migration-playbook.md)

# 灾难恢复 · DR / Backup

!!! tip "一句话理解"
    湖仓的 DR 不是"把一份数据复制到另一个地方"那么简单。**有 4 种灾难，各自的恢复策略不同**：数据误删 / Catalog 挂 / 区域不可用 / 数据损坏。而 Iceberg 自带的 Snapshot **已经解决了一半**——只要你别关错开关。

!!! abstract "TL;DR"
    - **RPO**（允许丢多少数据）和 **RTO**（允许多久恢复）先定清楚
    - 四种灾难：**误操作 / Catalog 挂 / Region 挂 / 数据文件损坏**
    - Iceberg Snapshot + Tag 是**时间维度的 DR**（对付误操作）
    - Catalog 需要**独立备份**（数据和 Catalog 都挂 = 双击死亡）
    - 跨 Region DR 用 **对象存储原生复制 + Catalog 异地副本**
    - 定期**演练**，不然备份就是"心理安慰"

## 先定义 RPO / RTO

| 术语 | 含义 | 典型目标 |
| --- | --- | --- |
| **RPO**（Recovery Point Objective） | 允许丢多长时间的数据 | 分钟级到小时级 |
| **RTO**（Recovery Time Objective） | 允许多久才能恢复 | 小时级到天级 |

不同业务目标不同：
- 财务数据 BI：RPO 1 天 / RTO 4 小时（能接受 T+1）
- 在线推荐 RAG：RPO 15 分钟 / RTO 1 小时（业务会掉）
- 审计 / 合规数据：RPO 0 / RTO 24 小时（不能丢，可以慢恢复）

## 四种灾难分开处理

### 灾难 1 · 误操作（最常见）

**典型**：某同事运行 `DROP TABLE` 或 ETL 作业 bug 写错分区。

**Iceberg / Paimon 自带的救命稻草**：

```sql
-- 查错之后先看历史
SELECT * FROM db.t.snapshots ORDER BY committed_at DESC;

-- 看当时数据
SELECT * FROM db.t VERSION AS OF 12345;

-- 回滚
CALL system.rollback_to_snapshot('db.t', 12345);
```

**前提**：`expire_snapshots` **没在这段时间内清掉那个 snapshot**。

**实操要求**：
- 关键表的 `history.expire.max-snapshot-age-ms` ≥ **30 天**（默认 5 天不够）
- 每次大版本发布 / 季末等**关键节点打 Tag**（Tag 默认不过期）

### 灾难 2 · Catalog 挂

**典型**：Unity Catalog / Nessie / HMS 服务不可用或后端 RDBMS 损坏。

**灾难性**：引擎找不到"当前表指针"在哪 → **所有查询失败**，即使数据完整。

**对策**：

- Catalog **后端 RDBMS 做标准 DB 备份**（Postgres PITR、mysqldump 定时）
- **Catalog 服务本身多副本** + 跨 AZ 部署
- **元数据二级快照**：定期把 Catalog 里所有"表 → 当前 metadata.json 指针"导出到对象存储
- 灾难时：用最近一份元数据快照 + 数据文件 + 重建 Catalog 服务 = 恢复

Nessie / Polaris 场景下的额外工作：它们的 commit history 本身是可序列化的，备份它们的 version store 即可。

### 灾难 3 · Region 不可用（云服务整体故障）

**典型**：整个 AWS us-east-1 挂了 6 小时。

**分级对策**：

#### 被动方案（大部分团队的选择）：

- **对象存储跨 Region 异步复制**（S3 Cross-Region Replication / GCS Multi-region）
- **Catalog 后端异地灾备副本**
- **引擎可以重新起集群**（K8s 在另一个 Region）
- **RTO ~ 小时级**

#### 主动方案（高可用要求极高）：

- 双 Region 同步写入（复杂：需要湖表格式支持 active-active，Iceberg 原生不擅长）
- 高成本，需要认真权衡

**多数团队的合理选择**：异步 + 人工切流，RTO 4-8h 可接受。

### 灾难 4 · 数据文件损坏

**典型**：Parquet 文件部分字节损坏、S3 对象版本被覆盖成坏数据。

**对策**：

- **对象存储开启 Versioning**（S3/GCS 都支持）
- **保留期设足够长**（30-90 天）
- 恢复时：回到前一个 object version

**Iceberg 层面**：`remove_orphan_files` **慎用**——它会物理删除。配合 `--dry-run` 和人工 review。

## AI 资源 DR（2024-2026 新增）

### 向量库 DR

**典型问题**：向量库（Milvus / LanceDB / Pinecone）和主数据不一定在同一套备份策略。

**做法**：

| 向量库 | 备份方式 |
|---|---|
| **Milvus** | `backup` API · 支持 S3 远程备份 · 跨集群恢复 |
| **LanceDB**（嵌入式 · 基于对象存储）| 对象存储本身的版本控制 · 或 Lance format 的 snapshot |
| **Pinecone / 托管服务** | 厂商侧 backup（2024+ 支持）· 限制多 |
| **自建 Qdrant** | Snapshot API · S3 存储 |
| **湖上向量**（Iceberg Puffin / Lance）| 跟着湖表走 · 不用独立 DR |

**关键**：
- **和主数据关联备份**（向量是 embedding → 源文档；源文档挂了向量也要对应操作）
- **Embedding 可从源重建**（相比数据 · 向量是衍生物 · 必要时完全重建）
- 规模大时重建成本高（百亿向量回填几千 GPU·h · 所以备份仍需要）

### 模型 Artifact DR

**Model Registry 的 DR**：

- **MLflow metadata DB 备份**（PostgreSQL PITR · 按 DB 标准做）
- **artifact 对象存储备份**（S3 versioning + cross-region replication）
- **Unity Catalog Models**：跟 UC 元数据一起备份
- **HuggingFace Hub 托管**：有 version history · 但不完全 DR（依赖 HF）

**关键**：
- Model artifact **一般不会丢**（S3 versioning）· 真正担心的是 **metadata 丢**（哪个 version 是 champion 等）
- 所以**Registry 元数据备份**比 artifact 本身更重要

### AI 应用状态 DR

**Prompt 版本**：
- Registry / Git 版本化
- 跨仓库或跨 region 同步
- 关键 prompt 定期 snapshot

**RAG 索引**：
- **索引可从湖表重建**（记录 `source_snapshot_id`）
- 所以**源文档表 DR 是主要** · 索引是衍生物
- 但重建时间长（几 GB 向量需要几小时）· 关键场景也备份索引

**Agent 状态**：
- Stateful Agent 的 memory（会话历史 · 用户偏好）
- 存储位置（Redis / 数据库 / 向量库）
- 按其底层存储 DR 策略

## 不可变备份（Ransomware 防御 · 2024-2026 必备）

**背景**：2023-2025 年勒索软件攻击加剧 · 攻击者会**加密备份**。传统 S3 + 权限 **不够** · 需要 immutable backup。

### S3 Object Lock

- **Governance mode**：特权账号可删
- **Compliance mode**：**任何人** 都不能删（包括 root）· 直到保留期到
- 配合 **Legal Hold** · 法律冻结

**关键实践**：
- 关键数据 S3 Object Lock **Compliance mode** · 保留 30-90 天
- 攻击者即使拿到 AWS root · 不能改 · 不能删
- 恢复时从不可变版本取

### Cross-Region · Cross-Account

- **跨账号备份**（主账号挂了 / 被入侵 · 备份账号独立）
- **Cross-region replication** with different AWS account
- 攻击者即使拿到主账号全部权限 · 备份账号独立

### 3-2-1 原则（现代版）

- **3** 份数据
- **2** 种介质（对象存储 + 冷归档 Glacier Deep）
- **1** 份 off-site / off-account（不可变）

## 备份策略的 3 条

### 1 · 对象存储原生复制

- S3 / GCS / OSS 都有跨 Region 异步复制
- 开一下就行
- **重要**：目标 bucket 的权限策略独立设置，防止"源被改，目标同步改"
- 生命周期策略（冷归档）可叠加

### 2 · Catalog 元数据单独备份

- 每小时 dump 一次 Catalog 后端 DB
- 保留 30 天历史
- 可选：定期把 `metadata.json` 单独拷贝到独立 bucket（防止 Catalog 完全不可用时能手工重建）

### 3 · 定期演练（最容易被忽视）

每季度至少一次**DR 演练**：

- 选一张表，模拟"数据被误改"，从 snapshot 恢复 → 验证 RTO
- 模拟 Catalog 不可用，从备份恢复 Catalog → 验证 RTO
- 模拟 Region 切换（把流量切到灾备 Region）→ 验证可用性

**没演练的备份 = 不存在**。

## 检查清单（生产上线前）

- [ ] `expire_snapshots` 保留窗口 ≥ 30 天（关键表）
- [ ] 关键里程碑自动打 **Tag**（季末、发布、重大数据变更）
- [ ] 对象存储 Versioning 已开
- [ ] 对象存储跨 Region 复制已配
- [ ] Catalog 后端 DB 有 daily snapshot
- [ ] Catalog 服务多副本部署
- [ ] 有文档写清楚"灾难发生时的联系人 + 操作 runbook"
- [ ] 至少做过 **1 次 DR 演练**，结果有记录

## RPO / RTO 与成本的权衡

| 做法 | RPO | RTO | 成本倍率 |
| --- | --- | --- | --- |
| 仅依赖 Snapshot + 本 Region | T+N（取决保留窗） | 几小时 | 1.0× |
| + 对象存储异步跨区复制 | 同步延迟 ~ 秒-分 | 几小时 | 1.2× |
| + Catalog 异地副本 | 分钟级 | 1-2 小时 | 1.5× |
| + 双 Region 热备 | 接近 0 | 分钟级 | 2-3× |

**合理起点**：Snapshot + 异步跨区复制 + Catalog 备份，**1.5× 成本换 P2 级灾难抗性**。

## 陷阱

- **只备数据不备 Catalog** → 数据在，但查询全挂
- **备份不做生命周期** → 几个月后 bucket 成本爆
- **从不演练** → 真灾难时发现备份不完整 / 恢复脚本过期
- **RPO 定得过激** → 双活成本吃光预算
- **`remove_orphan_files` 随意跑** → 物理删除无法回退

## 相关

- [Snapshot](../lakehouse/snapshot.md) · [Time Travel](../lakehouse/time-travel.md) · [Branching & Tagging](../lakehouse/branching-tagging.md)
- [对象存储](../foundations/object-storage.md)
- [故障排查手册](troubleshooting.md)
- [迁移手册](migration-playbook.md)
- [多租户隔离](multi-tenancy.md)

## 延伸阅读

- AWS S3 Cross-Region Replication docs
- *Designing Data-Intensive Applications* · 第 5 章（Replication）
- *The Site Reliability Workbook*（Google）· DR chapter
- Iceberg Recovery Procedures（社区文档）
