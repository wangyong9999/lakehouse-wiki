---
title: 对象存储 (Object Storage)
type: concept
depth: 进阶
tags: [foundations, storage]
aliases: [Object Store, 对象存储]
related: [lake-table, parquet, consistency-models]
systems: [s3, gcs, oss, minio, r2]
applies_to: S3 API (2020+ 强一致 · 2024+ Conditional Writes) · GCS · Azure Blob · OSS · R2
last_reviewed: 2026-04-18
status: stable
---

# 对象存储 (Object Storage)

!!! tip "一句话理解"
    把"文件"作为不可变的**对象（Object）**放在一个扁平的键值命名空间里；没有目录结构，没有原地改写。**2020 年强一致成为标配，2024 年 Conditional Writes 让湖仓终于能做"CAS 级提交"不再依赖外部锁。**

!!! abstract "TL;DR"
    - **接口语义**：对象不可变 · 无目录 · 无跨对象事务 · LIST 有成本
    - **关键里程碑**：2020 S3 强一致 · 2023 Express One Zone · 2024 S3 Conditional Writes (`If-None-Match: *`)
    - **Conditional Writes 的意义**：Iceberg / Delta / Paimon 的"元数据指针切换"终于可以在 S3 原语层面做，而不必依赖 DynamoDB / 外部 Catalog 做锁
    - **各家对标**：GCS 一直有 precondition · Azure 有 ETag 并发控制 · S3 2024 才补齐
    - **湖仓三约束**：不可改写 → Snapshot · 无跨对象事务 → CAS + Manifest · LIST 贵 → Manifest 索引

## 1. 它是什么

对象存储把数据组织为**对象**：每个对象是一段**不可变**（immutable）的字节流 + 一组元数据（Content-Type、ETag、用户自定义 kv）+ 一个全局唯一的 key。典型接口：

- `PUT key, bytes` —— 写一个新对象或覆盖
- `GET key` —— 读完整对象或 byte range
- `DELETE key` —— 删除
- `LIST prefix` —— 按 key 前缀列出
- `HEAD key` —— 只取元数据（ETag / size / last-modified）

**没有**的接口：原地追加（S3 无，Azure Append Blob 有）、原地改写任意位置、跨对象事务、目录 rename。

## 2. 关键语义（湖仓依赖的那几条）

| 语义 | S3 2026 现状 | 历史 | 其他云 |
|---|---|---|---|
| **PUT 之后 GET** | 强一致（read-after-write） | 2020 前最终一致 | GCS / Azure / OSS 长期强一致 |
| **LIST 一致性** | 强一致（2020+） | 早期有延迟 | 同上 |
| **原子覆盖** | 单对象 PUT 原子 | 一直如此 | 同上 |
| **Compare-And-Swap** | `If-None-Match: *`（Conditional Writes, 2024-08 GA） | 早期没有，需外部锁 | GCS `x-goog-if-generation-match` · Azure `If-Match` |
| **原子追加** | 不支持 | — | Azure Append Blob 支持 |
| **Rename** | 不存在（Copy + Delete 非原子、字节计费） | — | 同上 |
| **Multipart Upload** | 大对象分片上传 + 组装 | 一直有 | 各家都有 |

## 3. 2024 S3 Conditional Writes —— 对湖仓是什么量级的变化

**在此之前**（2010-2024 的痛）：S3 没有 CAS。湖仓要保证"两个 writer 同时提交不互相覆盖元数据指针"，必须依赖**外部服务做锁**：
- AWS Glue Catalog / Hive Metastore 做乐观锁
- Iceberg 可选 DynamoDB Catalog 用 DynamoDB 的 conditional write
- Delta Lake 早期靠 Databricks 的 transaction log 协调

**2024 之后**：`PUT metadata.json If-None-Match: *` 原生支持 CAS，意味着：
- Iceberg REST Catalog **可以原生在 S3 上做 commit**（早期需要 DynamoDB 补位）
- Delta 的 `_delta_log/` 原子写入更干净
- 小型湖仓 / 单租户场景**彻底不需要额外 Catalog 服务**

**关于兼容**：
- MinIO 2024-Q3+ 支持
- Cloudflare R2 · Backblaze B2 陆续跟进
- 国内云（OSS · COS · OBS）进度不一，**生产前要验**

## 4. 为什么它对湖仓至关重要

湖仓把"一张表"映射到"对象存储里的一堆不可变文件 + 少量元数据文件"。对象存储这三个约束决定了湖仓的所有设计：

1. **不可改写** → 更新只能写新文件，旧文件靠 [Snapshot](../lakehouse/snapshot.md) 和回收处理
2. **无跨对象事务** → 提交靠"写一个新的元数据对象 + 原子指针切换（CAS）"
3. **LIST 贵 + 延迟** → 不能靠扫目录发现数据，必须有 [Manifest](../lakehouse/manifest.md)

理解这三条，就能理解 [湖表](../lakehouse/lake-table.md) 里几乎所有的设计选择。

## 5. 成本与性能的实用事实

**请求计费**（以 S3 Standard 为例，量级参考）：
- `PUT / POST / LIST`：贵（每千次 ~$0.005）→ **LIST 风暴 = 账单风暴**
- `GET`：便宜（每千次 ~$0.0004）
- **出口流量**：跨区域 / 出公网昂贵（$0.02-0.09/GB）
- **Deep Archive**：取回 12h、$0.00099/GB·月 存储，但取回费高

**性能量级**：
- 单 Bucket 写吞吐 ~3500 PUT/s · 读吞吐 ~5500 GET/s per prefix（S3 通过自动分区缓解）
- 首字节延迟（TTFB）Standard 约 50-200ms · Express One Zone 约 10ms 以下
- **大对象读用 Range 请求并发**能打满本地 NIC

## 6. 主流对象存储对比

| 云 / 系统 | API | 强一致 | CAS | 特色 |
|---|---|---|---|---|
| **AWS S3** | S3 | 2020+ | 2024+（`If-None-Match`） | 生态最全 · Express One Zone 超低延迟 |
| **GCS** | GCS（兼容 S3 有限） | 一直 | `if-generation-match` | 跨区域强一致、composite objects |
| **Azure Blob** | Blob / ADLS Gen2 | 一直 | `If-Match` | Append Blob / Hierarchical Namespace |
| **阿里云 OSS** | 兼容 S3 部分 | 一直 | 可选 | 国内主流 · 层次命名空间 OSS-HDFS |
| **Cloudflare R2** | 兼容 S3 | 一直 | 2024+ | **零出口费**，跨云首选 |
| **Backblaze B2** | 兼容 S3 | 一直 | 跟进中 | 存储最便宜 |
| **MinIO** | 兼容 S3 | 一直 | 2024+ | 自建 · K8s 原生 |
| **Ceph RGW** | 兼容 S3 | 一直 | 支持 | 自建 · 多协议 |
| **JuiceFS** | POSIX 层 | — | — | **不是对象存储**，是对象存储之上的 FS 层，常用于给老应用加 POSIX |

## 7. 现实检视

- **"对象存储一致性已经不是问题"** —— 对 S3 是，**对部分国内云和自建 Ceph 不一定**；上线前用 warp · s3-bench 验
- **"Conditional Writes 让 Catalog 可选"** —— 理论上是，但**REST Catalog 仍有价值**（权限、审计、跨表事务、schema 管理不是单对象 CAS 能解决的）
- **"对象存储比本地盘慢"** —— 是，但**Express One Zone / GCS Rapid Storage 差距已到 2-3× 而不是 10×**；并发 + 缓存可进一步缩小
- **"LIST 可以随便用"** —— 错。**LIST 是对象存储最贵的操作之一**，Manifest 的设计初衷就是消除 LIST

## 8. 陷阱

- **跨区域流量爆账单**：compute 和 bucket 不在同一 region → 带宽成本占比可达 30%+
- **小对象（<1MB）泛滥**：S3 最小计费单位 · LIST 成本陡增 → 必须 Compaction
- **Presigned URL 过期 / 权限泄露**：有效期管理 + bucket policy 要严
- **Versioning 没开启**：误删不可恢复（湖仓 Time Travel 依赖这个）
- **Lifecycle 乱配**：把 Iceberg 未提交 snapshot 的数据文件过早归档 / 删除 → 表损坏
- **跨云 S3 兼容**：R2 / B2 / MinIO 有语义微差（multipart · ETag 计算），上游库版本要够新
- **Object Lock / WORM**：合规场景有用，但误启用会让 Compaction 失败

## 9. 延伸阅读

- **[S3 Strong Consistency 公告 · AWS 2020](https://aws.amazon.com/blogs/aws/amazon-s3-update-strong-read-after-write-consistency/)**
- **[S3 Conditional Writes 公告 · AWS 2024-08](https://aws.amazon.com/blogs/aws/amazon-s3-now-supports-conditional-writes/)**
- **[S3 Express One Zone · AWS 2023](https://aws.amazon.com/s3/storage-classes/express-one-zone/)** —— 单 AZ 超低延迟
- **[GCS Consistency](https://cloud.google.com/storage/docs/consistency)** · **[Azure Blob Concurrency](https://learn.microsoft.com/en-us/azure/storage/common/storage-concurrency)**
- **[Iceberg · Conditional Writes 讨论](https://github.com/apache/iceberg/issues/7198)** —— 对 Iceberg commit 路径的影响
- **[R2 vs S3 经济学 · Cloudflare 博客](https://blog.cloudflare.com/r2-ga/)**
- **[*The S3 Decade* · Werner Vogels 2023](https://www.allthingsdistributed.com/)** —— S3 设计演进回顾

## 相关

- [湖表](../lakehouse/lake-table.md) —— 湖仓表怎么在对象存储上做 ACID
- [一致性模型](consistency-models.md) —— 强一致 vs 最终一致 · 与湖仓 Snapshot 的关系
- [Parquet](parquet.md) —— 湖仓最主流的数据文件格式
- [存算分离](compute-storage-separation.md) —— 对象存储让存算分离成为可能
