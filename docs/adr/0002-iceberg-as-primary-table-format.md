---
title: 0002 选择 Iceberg 作为主表格式
type: adr
status: accepted
date: 2026-04-17
deciders: [wangyong9999]
---

# 0002. 选择 Iceberg 作为主表格式

## 背景

团队在多模一体化湖仓路线上需要选一个**主表格式**作为 BI 事实表和 AI 训练集的事实来源。候选：

- Apache Iceberg
- Apache Paimon
- Apache Hudi
- Delta Lake

各有长处（见对比页 [Iceberg vs Paimon vs Hudi vs Delta](../compare/iceberg-vs-paimon-vs-hudi-vs-delta.md)）。

## 决策

采用 **Apache Iceberg 作为主表格式**；**Paimon 作为流式 CDC 入湖的辅助格式**共存。

- 事实表、数据集市、训练集表、多模 asset 表 **全部用 Iceberg**
- 高频 CDC / upsert 表（订单流 / 点击流）**用 Paimon**，下游必要时聚合到 Iceberg

## 依据

### 为什么 Iceberg

1. **协议中立与多引擎开放** —— 我们要同时服务 Spark 批、Trino 交互、Flink 流、DuckDB 开发；Iceberg 是当前对所有引擎支持最均衡的格式
2. **Catalog 生态最丰富** —— Unity / Polaris / Nessie / Gravitino / HMS / Glue 全覆盖；未来切换 Catalog 无需换表格式
3. **Schema / Partition Evolution 最成熟** —— 列 ID 机制 + hidden partitioning + 分区演化零重写
4. **Puffin 侧车文件** —— 为向量索引下沉到湖表预留了标准口子，是一体化路线的关键前置
5. **Apache 顶级 + 治理独立** —— 没有单一商业公司主导，长期风险最小
6. **主力引擎（Spark / Trino）与 Iceberg 的集成最深**

### 为什么 Paimon 共存

流式 CDC + 高频 upsert 场景 Iceberg 的 MoR 性能不如 Paimon。让这条路径独立走 Paimon：

- CDC 订单流 → Paimon Primary Key 表
- 下游 Flink 可以流消费 changelog
- 需要和 BI 批分析对接时，聚合成 Iceberg 表

### 为什么不 Delta

- Databricks 生态耦合较深，治理自主性降低
- UniForm 兼容改善但仍在演进
- 我们没用 Databricks 托管

### 为什么不 Hudi

- 配置复杂度高
- 社区在表格式大战中的份额有所下降
- Paimon 在相同场景下更轻

## 后果

**正面**：

- 引擎选型解耦，未来切换容易
- Catalog 可独立演进（下一个 ADR 会决定 Catalog 选型）
- 向量下沉路径（Puffin）不堵死
- 行业主流一致，社区知识可复用

**负面**：

- 双格式共存增加运维复杂度（Iceberg + Paimon）
- 团队需要同时掌握两套元数据机制
- Paimon ↔ Iceberg 的桥接流程要设计

**后续**：

- 建立 Paimon → Iceberg 聚合流水线模板
- 统一 Compaction 策略
- 统一 Catalog（见 ADR-0003 待写）

## 相关

- [Iceberg vs Paimon vs Hudi vs Delta](../compare/iceberg-vs-paimon-vs-hudi-vs-delta.md)
- [Apache Iceberg](../lakehouse/iceberg.md) / [Apache Paimon](../lakehouse/paimon.md)
- [Lake + Vector 融合架构](../unified/lake-plus-vector.md)
- 下一条：ADR-0003 多模向量存储方案（LanceDB）
