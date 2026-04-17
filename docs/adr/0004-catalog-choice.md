---
title: 0004 Catalog 选型：Iceberg REST + 逐步引入 Unity Catalog
type: adr
status: accepted
date: 2026-04-17
deciders: [wangyong9999]
---

# 0004. Catalog 选型

## 背景

团队选定 [Iceberg 作为主表格式](0002-iceberg-as-primary-table-format.md) 和 [LanceDB 作为多模向量库](0003-lancedb-for-multimodal-vectors.md)。下一步选 Catalog——湖仓的"治理平面"。

候选：HMS / Iceberg REST Catalog 自建 / Nessie / Unity Catalog / Polaris / Gravitino。详见 [Catalog 全景对比](../compare/catalog-landscape.md)。

团队诉求（按重要性）：

1. 原生 Iceberg REST 协议兼容（多引擎开放）
2. 支持多模资产（表 + 向量 + 模型 + 文件 Volume）
3. 治理能力（行列级权限、血缘、审计）
4. 可控演化，短期能落地，长期不卡死

## 决策

**分两阶段**：

- **阶段 1（0-6 月）**：自建 **Iceberg REST Catalog 服务**（或 Polaris），实现表管理 + 基本 RBAC
- **阶段 2（6-18 月）**：引入 **Unity Catalog OSS**，替代阶段 1，扩展到多模资产 + 治理

**过渡期**：旧作业继续走 HMS；新 Iceberg 表默认进 REST Catalog。

## 依据

### 为什么分两阶段

- 一步到位上 Unity Catalog 运维复杂度高，短期难落地
- 自建 Iceberg REST 可以 2-4 周出 v1，先解锁 Iceberg 生态
- Unity OSS 生态在 2025-2026 快速演化，半年后成熟度更高

### 为什么不直接 Nessie

- Nessie 的 Git-like 能力当前团队不强需求（版本化通过 Iceberg tag 已够）
- Unity / Polaris 的多模资产路线和团队未来更契合

### 为什么不直接 Gravitino

- 需求是"把表 / 向量 / 模型**管起来**"而不是"把多个既有 Catalog **统一起来**"
- 团队起步阶段不应该引入联邦层

### 为什么不留在 HMS

- 新能力（向量资产、Model 资产、行级权限、血缘）无法表达
- REST 协议才是未来

## 后果

**正面**：

- 短期（阶段 1）快速解锁 Iceberg 生态
- 长期（阶段 2）拥有完整治理能力
- 中间过渡可控

**负面**：

- 团队要运维两代 Catalog 各一段时间
- 迁移（阶段 1 → 2）是一次工程投入

**后续**：

- 阶段 1：选 Polaris（Apache 开源）or 自研 Iceberg REST（看运维容量）
- 建立 Catalog 表命名规范（`<domain>.<schema>.<table>`）
- 新写 ADR：0008 Catalog 迁移路径细节

## 相关

- [Catalog 全景对比](../compare/catalog-landscape.md)
- [Iceberg REST Catalog](../catalog/iceberg-rest-catalog.md)
- [Unity Catalog](../catalog/unity-catalog.md)
- [Apache Polaris](../catalog/polaris.md)
- [ADR-0002 选择 Iceberg](0002-iceberg-as-primary-table-format.md)
- [ADR-0003 选择 LanceDB](0003-lancedb-for-multimodal-vectors.md)
