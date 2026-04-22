---
title: ADR（架构决策记录）
description: 团队级别的技术决策留痕
---

# 架构决策记录

Architecture Decision Records：我们**做过什么决定、为什么这么决定、代价是什么**。

编号按四位数单调递增，不复用；状态只有 `proposed | accepted | deprecated | superseded`。

## 已有

- [0001 选择 MkDocs Material 作为站点框架](0001-mkdocs-material.md)
- [0002 选择 Iceberg 作为主表格式](0002-iceberg-as-primary-table-format.md)
- [0003 多模向量存储选 LanceDB（辅以 Milvus）](0003-lancedb-for-multimodal-vectors.md)
- [0004 Catalog 选型：Iceberg REST → Unity Catalog](0004-catalog-choice.md)
- [0005 查询引擎组合：Spark + Trino + Flink + DuckDB（+ StarRocks）](0005-engine-combination.md)
- [0006 章节结构与维度划分 · 多维并存 + canonical source 原则](0006-chapter-structure-dimensions.md)
- [0007 版本刷新 SOP · known_versions.yml + version_scan.py + 季度刷新](0007-version-refresh-sop.md)
- [0008 对抗评审 SOP · 季度 Agent 驱动 + 人工复核](0008-adversarial-review-sop.md)
- [0009 frontier → main 下沉判据 · 成熟度门槛 + 周期审视](0009-frontier-to-main-migration.md)
- [0010 废除 frontier 章节 · 前沿内容按主题归属](0010-abolish-frontier-chapter.md)

## 模板

见 [`docs/_templates/adr.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/adr.md)。
