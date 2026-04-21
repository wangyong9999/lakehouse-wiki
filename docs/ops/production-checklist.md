---
title: 生产上线检查清单 · 湖仓 + AI 全栈
type: reference
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: 湖仓 · ML 平台 · AI 应用 · 2024-2026 实践
tags: [ops, checklist, production, go-live, launch]
aliases: [Production Checklist, Go-Live Checklist, 上线检查]
related: [observability, sla-slo, disaster-recovery, incident-management, change-management, security-permissions, compliance]
status: stable
---

!!! warning "章节分工声明"
    - **本页**：**上线前 · 成熟度自检用的跨能力清单**（能力 × 维度 · 便于 go-live review）
    - 各能力的**方法论** / **原理**分别在：[observability](observability.md) · [sla-slo](sla-slo.md) · [cost-optimization](cost-optimization.md) · [security-permissions](security-permissions.md) · [multi-tenancy](multi-tenancy.md) · [disaster-recovery](disaster-recovery.md) · [incident-management](incident-management.md) · [change-management](change-management.md)
    - 本页只是**清单形态**的 review · 不重复方法论。

# 生产上线检查清单

!!! tip "一句话理解"
    **"做不做"先于"做多好"**。这份 **50 条清单** 按能力组划分 · 对照打勾 · 任何一项 **"未通过"** 都应阻塞上线或设定明确缓解期。

!!! abstract "使用方式"
    - **M（Must）**：不通过不能上线
    - **S（Should）**：建议完成 · 不通过需记录风险并设定缓解期
    - **N（Nice）**：成熟度提升项 · 上线后持续完善
    - 上线 review 时逐条打勾 · 留存记录（ADR / 上线单）

## 组 1 · 可观测性（Observability）

**canonical**：[observability](observability.md)

| # | 项 | 级别 | 通过标准 |
|---|---|---|---|
| 1 | 业务 SLI 已定义 · 有 Dashboard | **M** | p50/p95 延迟 · 错误率 · 吞吐 · 新鲜度 至少 4 项落图 |
| 2 | 引擎层 metrics 接入 Prometheus | **M** | Spark/Trino/Flink/向量库 的 key metrics 均可查 |
| 3 | 日志聚合到统一平台 | **M** | Loki / Elastic / Datadog · TraceID 可检索 |
| 4 | 分布式 Trace 接入 | **S** | OpenTelemetry · 关键链路可追 |
| 5 | Data Lineage（OpenLineage） | **S** | 关键表的上下游可视化 |
| 6 | 数据质量观测（Elementary / Monte Carlo） | **S** | 异常列 / 缺失率 / 漂移监控 |
| 7 | AI/LLM 专用观测（token / 幻觉率 / 召回） | **M**（AI 应用）| 成本 · 质量 · 延迟三件事上图 |
| 8 | 告警分级（P0-P3）已配 + 路由到 on-call | **M** | 不是所有告警都 page · 分级清晰 |

## 组 2 · SLA / SLO / DRE

**canonical**：[sla-slo](sla-slo.md)

| # | 项 | 级别 | 通过标准 |
|---|---|---|---|
| 9 | SLO 已定义 · 有 Error Budget | **M** | 至少"延迟 SLO"+"可用性 SLO" · budget 消耗有告警 |
| 10 | 每个关键服务有 **RPO / RTO 目标** | **M** | 写在文档 · DR 演练可验证 |
| 11 | DRE（Data Reliability Engineering）roadmap | **S** | 3-6 月内的可靠性提升计划 |

## 组 3 · 成本 / FinOps

**canonical**：[cost-optimization](cost-optimization.md) · [tco-model](tco-model.md)

| # | 项 | 级别 | 通过标准 |
|---|---|---|---|
| 12 | 对象存储 lifecycle policy 已配 | **M** | IA / Glacier / 过期清理 |
| 13 | Compute 成本可按团队/项目归因 | **S** | Kubecost / 云 tag / chargeback 报表 |
| 14 | LLM token 成本有 budget + 告警 | **M**（AI 应用）| 人均 / 租户 / 应用三个维度可观测 |
| 15 | GPU 利用率监控 · SM 利用率 ≥ 60% | **S**（有训练负载）| 低于目标值触发 review |

## 组 4 · 安全 / 权限 / 合规

**canonical**：[security-permissions](security-permissions.md) · [compliance](compliance.md) · [data-governance](data-governance.md)

| # | 项 | 级别 | 通过标准 |
|---|---|---|---|
| 16 | 身份 · OIDC / OAuth 2.1 接入 | **M** | 不用个人 PAT 做长期 auth |
| 17 | 权限最小化 · 无 admin 兜底 | **M** | 关键角色 review · 无 root 常驻 |
| 18 | Secrets 走 Vault / Secrets Manager | **M** | 无明文写在 config / 代码 |
| 19 | 数据分级 · PII 列已标记 | **M** | data-governance 标签体系落地 |
| 20 | 行列级脱敏 / 审计日志 | **M**（含 PII）| 可查谁何时访问过哪条记录 |
| 21 | 传输加密（TLS） + 存储加密 | **M** | mTLS / Service Mesh 优先 |
| 22 | 合规映射（GDPR / HIPAA / EU AI Act 等） | **M**（相关场景）| 合规矩阵文档 · 审计可查 |
| 23 | Prompt 注入 / 输出 guardrail | **M**（LLM 应用）| Llama Guard / Prompt Shield 等已启用 |
| 24 | AI 供应链 SBOM · 模型卡 | **S**（AI 应用）| 模型来源 · license · 训练数据说明 |

## 组 5 · 多租户 / 隔离

**canonical**：[multi-tenancy](multi-tenancy.md)

| # | 项 | 级别 | 通过标准 |
|---|---|---|---|
| 25 | Namespace / Catalog 按租户隔离 | **M** | 跨租户不能互访 |
| 26 | Resource quota（CPU/Mem/GPU/Storage） | **M** | 单租户不可 starve 其他 |
| 27 | QoS / 优先级（在线 > 离线 > 探索） | **S** | 队列 / YARN / K8s priority 已配 |
| 28 | 向量库 · GPU · LLM token 三类 AI 资源隔离 | **S**（有 AI 负载）| per-tenant quota 可观测可限流 |

## 组 6 · DR / Backup

**canonical**：[disaster-recovery](disaster-recovery.md)

| # | 项 | 级别 | 通过标准 |
|---|---|---|---|
| 29 | 关键表 `expire_snapshots` 保留 ≥ 30 天 | **M** | 误操作可回滚 |
| 30 | 里程碑自动打 Tag | **S** | 季末 / 发布 / 大变更 |
| 31 | 对象存储 Versioning + 跨区复制已开 | **M** | bucket level 已配 |
| 32 | Catalog 后端 DB 有 daily snapshot | **M** | Postgres PITR / mysqldump |
| 33 | 不可变备份（S3 Object Lock） | **S** | 关键数据 Compliance mode · 防勒索 |
| 34 | 至少做过 1 次 DR 演练 · 有记录 | **M** | 未演练 = 不存在 |
| 35 | AI 资源 DR（向量库 · Model Registry） | **S**（有 AI 负载）| 按独立策略备份 |

## 组 7 · 事故 / 变更

**canonical**：[incident-management](incident-management.md) · [change-management](change-management.md)

| # | 项 | 级别 | 通过标准 |
|---|---|---|---|
| 36 | Oncall 轮值已建立 · PagerDuty/OpsGenie | **M** | 告警能找到人 |
| 37 | SEV 分级 + 响应 SLA 已文档化 | **M** | P0 < 15min · P1 < 1h 等 |
| 38 | Postmortem 模板 + Blameless 文化 | **M** | 每次 P1 有 postmortem |
| 39 | CI/CD 流水线（dbt slim CI · 单测 · 质量 gate） | **M** | PR 自动跑 · 不依赖人眼 |
| 40 | Schema 变更走 review · breaking change 有 30 天 notice | **M** | Data Contract 机制 |
| 41 | 关键变更有 Feature Flag | **S** | 启用 / 回滚独立控制 |
| 42 | 回滚 Runbook 已写 · 可演练 | **M** | 不在个别人脑子里 |

## 组 8 · 性能 / 容量

**canonical**：[performance-tuning](performance-tuning.md) · [capacity-planning](capacity-planning.md)

| # | 项 | 级别 | 通过标准 |
|---|---|---|---|
| 43 | 压测 · 至少覆盖预期峰值的 1.5× | **M** | 报告存档 |
| 44 | 小文件治理 / Compaction 策略已配 | **M** | 自动定时跑 |
| 45 | 容量规划文档 · 3-6 月增长预估 | **S** | 存储 / Compute / GPU / 向量库 都估 |
| 46 | 向量索引参数 tuning 已做 | **S**（有检索负载）| recall / latency 权衡文档化 |

## 组 9 · 文档 / Runbook

| # | 项 | 级别 | 通过标准 |
|---|---|---|---|
| 47 | 架构图 + 上下游依赖图 | **M** | 新人可理解 |
| 48 | On-call Runbook（常见故障 → 处置） | **M** | 不靠口口相传 |
| 49 | ADR（重要决策）已归档 | **S** | 1 年后可追溯"为什么这样做" |
| 50 | 接入方对接文档 / SLA 公告 | **S**（对外服务）| 下游能自助 |

## 成熟度判定

- **< 30 项 Must 通过**：不应上线 · 先补齐
- **全部 Must + 50% Should**：可上线（P2 业务）
- **全部 Must + 80% Should + Nice 部分**：可上线 P0/P1 业务
- **长期目标**：全部 Must + 全部 Should + 80% Nice

## 配合机制

- **上线 review 会议**：业务方 + 平台 + SRE + 安全 + 合规 共同打分
- **清单存档**：每次上线留存打分记录（ADR / 上线工单）
- **每季度复查**：老系统按新清单补齐
- **清单演进**：新出现的故障类型（如 2025 的 prompt 注入 · 2026 的 MCP Server 安全）及时加入

## 相关

- [可观测性](observability.md)
- [SLA / SLO / DRE](sla-slo.md)
- [成本优化](cost-optimization.md) · [TCO 模型](tco-model.md)
- [安全与权限](security-permissions.md) · [合规](compliance.md) · [数据治理](data-governance.md)
- [多租户](multi-tenancy.md)
- [灾难恢复](disaster-recovery.md)
- [事故管理](incident-management.md) · [变更管理](change-management.md)
- [性能调优](performance-tuning.md) · [容量规划](capacity-planning.md)

## 延伸阅读

- Google SRE Book · *Launch Coordination Engineering*
- AWS Well-Architected Framework
- *The DevOps Handbook* · Production Readiness Review 章节
- FinOps Foundation · *FinOps Framework*
