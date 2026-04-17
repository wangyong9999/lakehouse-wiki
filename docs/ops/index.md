---
title: 运维与生产
description: 把湖仓和检索系统稳定地跑在生产上所需要的工程能力
---

# 运维与生产

## 已有

- [可观测性](observability.md) —— 四个平面（写入 / Catalog / 查询 / 数据质量）
- [性能调优](performance-tuning.md) —— 先治数据布局，再调执行器
- [成本优化](cost-optimization.md) —— 存储 / 计算 / API / 出口四条线
- [安全与权限](security-permissions.md) —— 身份 + 资源 + SQL 细粒度 + 凭证，四层防线
- [数据治理](data-governance.md) —— 血缘、质量、契约、合规

## 待补

- 容量规划与资源配额
- 多租户隔离
- 灾难恢复（DR / Backup）
- 迁移手册（Hive → Iceberg、独立向量库 → LanceDB 等）
