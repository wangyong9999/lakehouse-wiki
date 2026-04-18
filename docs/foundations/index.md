---
title: 基础
description: 存储、文件格式、计算、分布式等前置知识
---

# 基础

湖仓与多模检索系统的共同"石头地基"。先把这一节过掉，再读后面 Snapshot、ANN、向量化执行就不会卡壳。

!!! tip "按时间预算选路径"
    - **2 小时最小路径**：[对象存储](object-storage.md) → [Parquet](parquet.md) → [存算分离](compute-storage-separation.md) · 了解"湖仓存什么、怎么存、怎么算"
    - **一周标准路径**：最小路径 + [列式 vs 行式](columnar-vs-row.md) · [向量化执行](vectorized-execution.md) · [谓词下推](predicate-pushdown.md) · [MVCC](mvcc.md) · 理解"为什么湖仓快 / 并发如何保证"
    - **完整路径**：加上 [Arrow 生态](arrow-ecosystem.md) · [一致性模型](consistency-models.md) · [事件时间 · Watermark](event-time-watermark.md) · 覆盖流批共性
    - **导读**（湖仓来龙去脉）：[数据系统演进史](data-systems-evolution.md) + [Modern Data Stack 全景](modern-data-stack.md) —— 不急着读，但做架构决策前翻一翻很值

---

## 导读（历史与生态）

> 这两篇是"战略 context"，不是技术底层。新人先跳过，做方案评审前回头读。

- [**三代数据系统演进史**](data-systems-evolution.md) ⭐ —— 从关系数据库到数仓到湖仓的 50 年史
- [**Modern Data Stack 全景**](modern-data-stack.md) ⭐ —— 现代数据栈十大环节

## 技术底层 · 存储

- [对象存储](object-storage.md) —— S3/GCS/OSS 语义、原子性与一致性
- [存算分离](compute-storage-separation.md) —— 现代湖仓的架构原语
- [Parquet](parquet.md) · [ORC](orc.md) · [Lance Format](lance-format.md) —— 三种列式格式
- [列式 vs 行式存储](columnar-vs-row.md)

## 技术底层 · 计算

- [向量化执行](vectorized-execution.md) —— 现代 OLAP 的核心技术
- [谓词下推](predicate-pushdown.md) —— 湖仓性能的关键机制
- [MVCC](mvcc.md) —— 多版本并发控制，湖仓 Snapshot 的思想源头

## 技术底层 · 分布式 / 并发

- [OLTP vs OLAP](oltp-vs-olap.md) —— 两种负载为什么物理底层相反
- [一致性模型](consistency-models.md) —— CAP / SI / Eventual 和湖仓的位置
- [事件时间 · Watermark · 乱序](event-time-watermark.md) —— 流处理的时间维度

## 生态协议

- [Arrow · FlightSQL · ADBC](arrow-ecosystem.md) —— 内存交换与传输的公共层
