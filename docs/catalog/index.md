---
title: 元数据与 Catalog
type: reference
status: stable
tags: [index, catalog]
description: 湖仓的"表注册中心" —— 协议 / OSS 实现 / 商业托管 / 联邦层 四层视角
applies_to: Iceberg REST v1 / Polaris 1.3+ (2026-02 TLP) / Gravitino 1.0+ (TLP) / Unity Catalog OSS 0.4.1+ / AWS Glue / Snowflake Open Catalog / Hive 4.0
last_reviewed: 2026-04-20
---

# 元数据与 Catalog

!!! info "本章组织"
    本章按 4 层 + 1 个总入口：
    
    - **总入口**：[Catalog 策略 · 选型决策](strategy.md)
    - **协议层**：[Iceberg REST Catalog](iceberg-rest-catalog.md)
    - **OSS 实现层**：[Polaris](polaris.md) / [Nessie](nessie.md) / [Unity Catalog](unity-catalog.md) / [Gravitino](gravitino.md)
    - **商业托管层**：[AWS Glue Data Catalog](glue.md)
    - **存量 / 历史**：[Hive Metastore](hive-metastore.md)
    - **横向对比**：[Catalog 全景对比](../compare/catalog-landscape.md)
    
    外部权威：[`docs/references/catalog/`](../references/catalog/index.md)（Iceberg REST spec · Polaris / Nessie / UC / Gravitino 官方文档）。

Catalog 是湖仓的"表注册中心"。一体化湖仓时代它的角色已膨胀成"**治理平面**"——不只注册表，还要管向量、模型、文件 Volume、权限、血缘。

!!! warning "读这一章前先理清四层 · 否则很容易选错"
    Catalog 世界 2026-Q2 的**最大混淆**是把下面四层揉成一类看：

    ```mermaid
    flowchart TD
      proto[协议层<br/>Iceberg REST spec v1 · View Spec · Multi-table commit] --> oss
      proto --> managed

      subgraph oss[OSS 实现层 · 按能力定位分流]
        pol[Apache Polaris<br/>Iceberg-first · 纯净 REST]
        nes[Nessie<br/>Git-like + 跨表事务]
        uc[Unity Catalog OSS<br/>多模治理平面]
      end

      subgraph managed[商业托管层]
        sw[Snowflake Open Catalog]
        db[Databricks UC 商业版]
        glue[AWS Glue Data Catalog]
        s3t[AWS S3 Tables]
      end

      subgraph fed[联邦层 · 叠在上面]
        grav[Apache Gravitino]
      end

      pol -.托管.-> sw
      uc -.托管.-> db

      grav -.联邦.-> oss
      grav -.联邦.-> managed
      grav -.联邦.-> hms

      hms[HMS<br/>存量兼容层] -.逐步退场.-> oss
    ```

    **四层职责不混**：
    - **协议层 · Iceberg REST spec**：定义接口，不做实现
    - **OSS 实现层**：协议的开源落地 · Polaris / Nessie / UC OSS **不是同赛道**（定位/能力/生态完全不同）
    - **商业托管层**：厂商运营的产品 · Snowflake / Databricks / AWS 各自为政
    - **联邦层**：Gravitino——不替代上述任何层，只做聚合

    **读者最容易的 3 个踩坑**：
    1. 以为 **Apache Polaris OSS ≈ Snowflake Open Catalog** —— 不是（代码基同源，**差别主要在运维形态 + SLA 保障 + 能力交付时效**）
    2. 以为 **UC OSS ≈ Databricks UC 商业版** —— 不是（OSS 仅交付核心 Catalog API + 基础 RBAC；AI 治理 / 列级血缘 / 行级过滤等治理功能仍商业独占）
    3. 以为 **Polaris / Unity / Nessie 在同一赛道横比** —— 不是（三者**关注点不同层**：Polaris 聚焦 Iceberg REST 协议实现 · Unity 聚焦多资产治理平面 · Nessie 聚焦版本化工作流）

## 2026-Q2 生态时间线

过去 2 年（2024-2026）是 Catalog 生态格局剧变的窗口：

- **2024-06** · Databricks 收购 Tabular · Iceberg REST spec 话语权向 Databricks 重心位移
- **2024-06** · Databricks 在 Data+AI Summit 开源 Unity Catalog · 提交 LF AI & Data 沙箱
- **2024-08** · Snowflake 把 Polaris 捐献 Apache 孵化
- **2024-12** · AWS re:Invent 发布 **S3 Tables**（Iceberg 原生托管，独立于 Glue 的另一条路径）
- **2025-06** · Gravitino 从孵化毕业为 Apache Top-Level Project
- **2025-2026** · Iceberg REST spec 持续演进：Scan Planning / OAuth2 / Vended Credentials / Multi-table Commit
- **2026-01** · Polaris 1.3-incubating 发布 · Generic Table GA / SigV4 / KMS per-catalog
- **2026-02-19** · Polaris 从孵化毕业 · 成为 Apache Top-Level Project（孵化 18 个月 · 6 次 release · ~100 位 contributor · 2800+ PR 合并）

**HMS 仍是大量存量系统的注册中心**——不是被淘汰，而是进入 **"新建项目不采用、存量系统长期共存"** 的阶段。

## 产品页 · 按四层组织

### 协议层

- [Iceberg REST Catalog](iceberg-rest-catalog.md) —— 下一代标准协议 · spec 定义 · 所有 OSS/商业实现都对此兼容

### OSS 实现层（定位不同 · 不是同赛道横比）

- [Apache Polaris](polaris.md) —— **Iceberg REST 服务端实现** · Snowflake 开源 · **2026-02 毕业 Apache TLP**
- [Nessie](nessie.md) —— **版本化 Catalog** · Git-like 分支 + 跨表事务是差异化
- [Unity Catalog OSS](unity-catalog.md) —— **治理平面产品的开源核** · Databricks 开源 · 仍 0.x
- [Apache Gravitino](gravitino.md) —— **联邦层** · 2025-06 毕业 TLP · 叠在别的 Catalog 上，不与它们横比

### 商业托管层

- **Snowflake Open Catalog** · 基于 Apache Polaris 上游 + 商业 SLA · 详见 [polaris.md](polaris.md) 内 "Open Catalog vs OSS" 段
- **Databricks Unity Catalog** 商业版 · 详见 [unity-catalog.md](unity-catalog.md) 内 "商业 vs OSS" 段
- [AWS Glue Data Catalog](glue.md) —— **AWS 栈的事实默认** · Athena / EMR / Lake Formation 深度捆绑

### 存量 / 历史层

- [Hive Metastore](hive-metastore.md) —— Hadoop 时代事实标准 · 新建不选 · 存量长期兼容

## 横向对比 · 选型决策

- [Catalog 全景对比](../compare/catalog-landscape.md) —— 多选手选型决策树
- [统一 Catalog 策略](../catalog/strategy.md) —— 现代选型决策

## 选型速览 · 4 步决策

!!! tip "从场景到选型"
    **Step 1 · 栈生态强绑定？**

    - 强 **AWS** 用户 → **Glue**（Athena / Lake Formation 生态不可替代）或 **S3 Tables**（新 Iceberg 工作负载）
    - 强 **Databricks** → **Unity Catalog 商业版**（OSS 治理能力仍不完整）
    - 强 **Snowflake** → **Snowflake Open Catalog**（基于 Polaris + 商业 SLA）
    - 中立多引擎 → 往下看

    **Step 2 · 需要 Git-like 分支 / 跨表事务？**

    - 是 → **Nessie**（工作流纪律成本自担）
    - 否 → **Apache Polaris** 自托管（Iceberg-first 纯净）或 **Iceberg REST 自建**

    **Step 3 · 已有 ≥ 2 个 Catalog 需要统一？**

    - 叠一层 **Gravitino**（联邦 · 不替换底层 · 记住联邦固有限制）

    **Step 4 · 历史 HMS 存量？**

    - 新建走上述之一
    - 老 HMS 作为 Iceberg 指针载体继续兼容（但 HMS 自身瓶颈不会因此消失）
