---
title: 运维与生产
description: 把湖仓和检索系统稳定地跑在生产上所需要的工程能力
---

# 运维与生产

## 可观测性与调优

- [可观测性](observability.md) —— 四个平面（写入 / Catalog / 查询 / 数据质量）
- [性能调优](performance-tuning.md) —— 先治数据布局，再调执行器
- [故障排查手册](troubleshooting.md) —— 12 类常见问题的排查树

## 成本与容量

- [成本优化](cost-optimization.md) —— 存储 / 计算 / API / 出口四条线
- [**TCO 模型**](tco-model.md) —— 自建 vs 云 vs SaaS 的真实成本分析（含决策矩阵）
- [**容量规划**](capacity-planning.md) —— 集群规模与资源预估

## 安全 / 合规 / 治理

- [安全与权限](security-permissions.md) —— 身份 + 资源 + SQL 细粒度 + 凭证，四层防线
- [数据治理](data-governance.md) —— 血缘、质量、契约、合规
- [**合规**](compliance.md) —— GDPR / HIPAA / PDPA / 个保法 / 跨境
- [多租户隔离](multi-tenancy.md) —— 5 层视角 + 爆炸半径

## 稳定性 / 迁移

- [灾难恢复 · DR / Backup](disaster-recovery.md) —— 4 种灾难类型 + Snapshot + 演练
- [迁移手册](migration-playbook.md) —— Hive → Iceberg / DW → 湖仓 / Milvus → LanceDB

## 工程智慧

- [**湖仓 20 反模式**](anti-patterns.md) —— 上线前自查清单

## 待补

- SLA/SLO 工程化（规划中）
- 多云 / 跨区域部署
- 权限矩阵标准模板
