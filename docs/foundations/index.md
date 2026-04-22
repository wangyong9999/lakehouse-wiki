---
title: 基础
description: 存储、文件格式、计算、分布式等前置知识
---

# 基础

湖仓与多模检索系统的共同"石头地基"。先把这一节过掉，再读后面 Snapshot、ANN、向量化执行就不会卡壳。

!!! info "和 `lakehouse/` 的分界"
    **这一节是物理存储 + 通用计算原理**——对象存储、列式文件（Parquet / ORC / Lance）、编码、向量化、MVCC——都是**格式无关 / 引擎无关**的底层。

    **[湖表](../lakehouse/lake-table.md) 及其构件**（Snapshot / Manifest / Time Travel / Iceberg / Paimon）是**建在这些物理文件之上的逻辑协议层**，因此归到 `lakehouse/`。

    **Lance 是灰色地带**：既是列式文件格式（本节讨论），又自带 fragment 级事务（也有湖表属性）。从"文件格式"视角读 [Lance Format](lance-format.md)；从"湖表底座"视角参见 [湖表](../lakehouse/lake-table.md) 的数据文件层段。

## 一条主线 · 湖仓的性能与一致性因果链

这一节的核心页面**不是平行词条**，而是同一条因果链的不同层。理解这条链之后，上层内容（Iceberg commit 流程 / Trino pruning / StarRocks MV 加速 / Snapshot 时间旅行）会自然串起来。

```mermaid
flowchart TB
  OS[对象存储语义<br/>只读不改 · 强一致 · CAS]
  FMT[列式文件 + 编码<br/>Parquet · Dict / RLE / Zstd]
  STAT[footer · 统计 · 索引<br/>min/max · Page Index · Bloom]
  PUSH[谓词 / 投影下推<br/>Row Group 跳过 · 只读所需列]
  VEC[向量化执行<br/>SIMD · 延迟解码]
  MVCC[MVCC · 快照隔离<br/>Snapshot / Manifest CAS]
  LAKE[湖表 + 查询引擎]

  OS --> FMT --> STAT --> PUSH --> VEC --> MVCC --> LAKE
```

**湖仓"快且一致"不是某一层的魔法**——而是每层都能多剪一点数据、少抖一点一致性。上层引擎的优化经常是在这条链里换一个环节的实现（换编码、换索引、换下推时机、换 MVCC 粒度）。

**从"文件"到"表"有两条落地路径**：

- **两层分离（主流）**：Parquet / ORC 作纯文件格式，[Iceberg / Paimon / Hudi / Delta](../lakehouse/lake-table.md) 在上面定义多引擎共享的表协议。湖仓主流走这条；详细展开见 [`lakehouse/`](../lakehouse/index.md) 模块。
- **文件 + 表一体（AI 时代的另一条路）**：[Lance Format](lance-format.md) 把轻量表能力（fragment / manifest / version）直接打包进文件格式，为多模 + 向量 + 随机读重做；LanceDB 在此之上加 catalog 与检索 API。

两条路径不互斥：湖表生态也在把 Lance 接为 data file 格式之一（演进中）。读完基础主线之后再进 `lakehouse/`，视野会自洽。

### 主线推荐阅读顺序（4–6 小时建立心智模型）

1. [对象存储](object-storage.md) —— 湖仓地基的语义
2. [存算分离](compute-storage-separation.md) —— 这个架构为什么能成立
3. [Parquet](parquet.md) · [压缩与编码](compression-encoding.md) —— 文件内部怎么组织
4. [列式 vs 行式](columnar-vs-row.md) —— 为什么 OLAP 选列式
5. [谓词下推](../query-engines/predicate-pushdown.md) —— footer / 统计怎么变成"扫少"
6. [向量化执行](../query-engines/vectorized-execution.md) —— 扫进来的 batch 怎么算快
7. [MVCC](mvcc.md) · [一致性模型](consistency-models.md) —— 湖表 commit 的思想源头

赶时间只读前三条（约 2 小时）也能建立最小可用心智模型；做架构评审 / 深度选型时再回来补完整 7 条。

---

## 主线之外 · 特定场景的前置

- [OLTP vs OLAP](oltp-vs-olap.md) —— 两种负载的物理底层为什么相反
- [事件时间 · Watermark · 乱序](../pipelines/event-time-watermark.md) —— 流处理时间维度（做流式入湖 / 实时湖仓时读）
- [ORC](orc.md) —— Parquet 之外的传统列式格式（选型对比时读）
- [Lance Format](lance-format.md) —— AI 时代"文件 + 轻表一体化"的另一条路径（见上文主线收尾的路径对照）
- [Arrow · FlightSQL · ADBC](../query-engines/arrow-ecosystem.md) —— 内存交换与传输公共层

> 想看"湖仓怎么来的"或"现代数据栈十大环节"这类**历史与生态视角**？见附录 [数据系统演进史](../data-systems-evolution.md) 与 [Modern Data Stack 全景](../modern-data-stack.md)。
