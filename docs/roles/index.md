---
title: 按角色入门
description: 根据你在团队的位置，给一张优先阅读清单
hide:
  - toc
---

# 按角色入门

不同角色需要关心的知识面完全不同。选一条对应身份进去。

<div class="grid cards" markdown>

-   :material-database-cog: **数据工程师**

    ---

    湖仓表格式、入湖、Schema 演化、Compaction、性能调优

    [→ 数据工程师](data-engineer.md)

-   :material-robot: **ML / AI 工程师**

    ---

    向量检索、Embedding、RAG、Feature Store、Model Serving

    [→ ML / AI 工程师](ml-engineer.md)

-   :material-cog-outline: **平台 / 基础设施工程师**

    ---

    Catalog、权限治理、可观测性、成本优化、多租户、迁移

    [→ 平台工程师](platform-engineer.md)

-   :material-chart-bar: **BI / 数据分析师**

    ---

    湖上 SQL、OLAP 建模、物化视图、加速副本、Dashboard 模式

    [→ BI 分析师](bi-analyst.md)

</div>

---

## 不确定自己是哪个

- 写 Spark / Flink 作业、维护湖表？→ **数据工程师**
- 训模型 / 做 RAG / 调向量检索？→ **ML / AI 工程师**
- 管 Catalog / 权限 / 成本 / K8s？→ **平台工程师**
- 写 SQL 出报表 / 看仪表盘？→ **BI 分析师**

多个角色兼有时看**主要时间花在哪**。

## 所有角色共读

不管什么身份，这 3 条都值得读：

- [首页架构视图](../index.md) —— 理解全局
- [一周新人路径](../learning-paths/week-1-newcomer.md)
- [FAQ](../faq.md) —— 常见问题速答
