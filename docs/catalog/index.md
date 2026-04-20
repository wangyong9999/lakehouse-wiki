---
title: 元数据与 Catalog
description: 湖仓的"表注册中心" —— Hive / REST / Nessie / Unity / Polaris / Gravitino
applies_to: Iceberg REST v1 / Polaris 1.3-incubating / Gravitino 1.0+ (TLP) / Unity Catalog OSS 0.x / Hive 4.0
last_reviewed: 2026-04-20
---

# 元数据与 Catalog

Catalog 是湖仓的"表注册中心"。一体化湖仓时代它的角色已膨胀成"**治理平面**"——不只注册表，还要管向量、模型、文件 Volume、权限、血缘。

!!! info "2026-Q2 生态全景 · 站在当前时点看"
    过去 2 年（2024-2026）是 Catalog 生态格局剧变的窗口：

    - **2024-06** · Databricks 收购 Tabular · Iceberg REST spec 话语权向 Databricks 重心位移
    - **2024-06** · Databricks 在 Data+AI Summit 开源 Unity Catalog · 提交 LF AI & Data 沙箱
    - **2024-08** · Snowflake 把 Polaris 捐献 Apache 孵化
    - **2025-06** · Gravitino 从孵化毕业为 Apache Top-Level Project · Catalog 生态中少数已毕业项目
    - **2025-2026** · Iceberg REST spec 持续演进：Scan Planning / OAuth2 / Vended Credentials / Multi-table Commit
    - **2026-01** · Polaris 1.3-incubating 发布 · Generic Table GA / SigV4 / KMS per-catalog

    **HMS 仍是大量存量系统的注册中心**——不是被淘汰而是**新建不选 · 存量兼容**的分叉期。

## 产品页（按成熟度 + 场景组织）

### 协议层（Iceberg REST Catalog 标准）

- [Iceberg REST Catalog](iceberg-rest-catalog.md) —— 下一代标准协议 · Scan Planning / OAuth2 / Vended Credentials / 跨实现兼容矩阵

### 开源实现

- [Apache Polaris](polaris.md) —— Snowflake 开源 · Iceberg-first · 2026-Q2 仍孵化（1.3.0-incubating）
- [Unity Catalog](unity-catalog.md) —— Databricks 开源 · 多模资产（Table/Volume/Model/Function/Vector/Share）· LF AI 沙箱 · OSS 仍 0.x
- [Nessie](nessie.md) —— Git-like 事务 Catalog · 跨表原子 commit + 分支
- [Apache Gravitino](gravitino.md) —— 多 Catalog 联邦 · 2025-06 毕业 TLP · AI 方向（Fileset/Model）强化

### 历史 / 存量

- [Hive Metastore](hive-metastore.md) —— Hadoop 时代事实标准 · 新建不选 · 存量长期兼容

## 横向对比 · 选型决策

- [Catalog 全景对比](../compare/catalog-landscape.md) —— 六大选手的选型决策树
- [统一 Catalog 策略](../unified/unified-catalog-strategy.md) —— 现代选型决策

## 选型速览 · 4 步决策

!!! tip "从场景到选型"
    **Step 1 · 栈生态绑定？**

    - 强 Databricks → **Unity Catalog**（OSS 或托管）
    - 强 Snowflake → **Snowflake Open Catalog**（基于 Polaris）
    - 中立多引擎 → 往下看

    **Step 2 · 需要 Git-like 分支 / 跨表事务？**

    - 是 → **Nessie**
    - 否 → **Apache Polaris**（Iceberg-first 纯净）或 **Iceberg REST 自建**

    **Step 3 · 已有 ≥ 2 个 Catalog 需要统一？**

    - 叠一层 **Gravitino**（联邦 · 不替换底层）

    **Step 4 · 历史 HMS 存量？**

    - 新建走上述之一 · 老 HMS 作为 Iceberg 指针载体继续兼容
