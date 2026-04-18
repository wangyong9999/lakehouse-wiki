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

## 模板

见 [`docs/_templates/adr.md`](https://github.com/wangyong9999/lakehouse-wiki/blob/main/docs/_templates/adr.md)。
