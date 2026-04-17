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
- [多租户隔离](multi-tenancy.md) —— 5 层视角（命名空间 / 权限 / 存储 / 计算 / 成本）+ 爆炸半径
- [灾难恢复 · DR / Backup](disaster-recovery.md) —— 4 种灾难类型 + Iceberg Snapshot + 演练
- [迁移手册](migration-playbook.md) —— Hive → Iceberg / DW → 湖仓 / Milvus → LanceDB
- [故障排查手册](troubleshooting.md) —— 12 类常见问题的排查树

## 待补

- 容量规划与资源配额
- 多云 / 跨区域部署
