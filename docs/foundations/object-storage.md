---
title: 对象存储 (Object Storage)
type: concept
tags: [foundations, storage]
aliases: [Object Store, 对象存储]
related: [lake-table, parquet]
systems: [s3, gcs, oss, minio]
status: stable
---

# 对象存储 (Object Storage)

!!! tip "一句话理解"
    把"文件"作为不可变的**对象（Object）**放在一个扁平的键值命名空间里；没有目录结构，没有原地改写，强一致性是近几年才标配的。

## 它是什么

对象存储把数据组织为**对象**：每个对象是一段**不可变**（immutable）的字节流 + 一组元数据（Content-Type、ETag、用户自定义 kv）+ 一个全局唯一的 key。典型接口：

- `PUT key, bytes` —— 写一个新对象或覆盖
- `GET key` —— 读完整对象或 byte range
- `DELETE key` —— 删除
- `LIST prefix` —— 按 key 前缀列出

**没有**的接口：原地追加、原地改写任意位置、跨对象事务、目录 rename。

## 关键语义（湖仓依赖的那几条）

| 语义 | S3 今天 | 早期差异 |
| --- | --- | --- |
| **PUT 之后 GET 的可见性** | 强一致（read-after-write）| 2020 年之前 S3 是最终一致 |
| **LIST 一致性** | 强一致 | 早期有延迟 |
| **原子覆盖** | 单对象 PUT 原子 | 但**没有** compare-and-swap |
| **Conditional Write** | S3 2024 支持 `If-None-Match: *` | 这是湖仓 commit 的新利器 |
| **Rename** | 不存在，只能 Copy + Delete | 代价高、非原子 |

## 为什么它对湖仓至关重要

湖仓把"一张表"映射到"对象存储里的一堆不可变文件 + 少量元数据文件"。对象存储这三个约束决定了湖仓的所有设计：

1. **不可改写** → 更新只能写新文件，旧文件靠 Snapshot 和回收来处理
2. **无跨对象事务** → 提交靠"写一个新的元数据对象 + 原子指针切换"
3. **LIST 贵且可能有延迟** → 不能靠扫目录发现数据，必须有 Manifest

理解这三条，就能理解 [湖表](../lakehouse/lake-table.md) 里几乎所有的设计选择。

## 相关概念

- [湖表](../lakehouse/lake-table.md) —— 湖仓表怎么在对象存储上做 ACID
- [Parquet](parquet.md) —— 湖仓最主流的数据文件格式

## 延伸阅读

- S3 Strong Consistency: <https://aws.amazon.com/blogs/aws/amazon-s3-update-strong-read-after-write-consistency/>
- S3 Conditional Writes: <https://aws.amazon.com/blogs/aws/amazon-s3-now-supports-conditional-writes/>
- *The Log-Structured Merge-Tree* (LSM) —— 对象存储上写入模型的思想来源
