---
title: 故障响应 · SEV · Oncall · Postmortem
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: Google SRE 无过错 Postmortem · PagerDuty / OpsGenie · SEV 分级 · 2024-2026 实践
tags: [ops, incident, oncall, postmortem, sev, sre]
aliases: [Incident Response, Incident Management, 故障响应, 故障管理]
related: [sla-slo, observability, troubleshooting, production-checklist, disaster-recovery, change-management]
systems: [pagerduty, opsgenie]
status: stable
---

# 故障响应 · Incident Management

!!! tip "一句话定位"
    **生产事故发生时如何响应 + 事后如何学**。覆盖 **SEV 分级 · oncall 流程 · 战时响应 · Postmortem 框架 · 改进闭环**。事故不可避免 · 响应能力决定损失大小。

!!! warning "章节分工声明"
    - **本页**：故障响应**流程和组织**（如何响应）
    - **具体问题排查方法**（查询慢 / commit 冲突等）→ [troubleshooting](troubleshooting.md)（如何诊断）
    - **预防（SLO / Error Budget）** → [sla-slo](sla-slo.md)
    - **预防（可观测）** → [observability](observability.md)
    - **灾难恢复** → [disaster-recovery](disaster-recovery.md)
    - 本页关注"**Shit happens · 怎么办**"

!!! abstract "TL;DR"
    - **SEV 分级**（P0-P3）· 决定响应速度
    - **Oncall** · 24/7 轮值 · PagerDuty / OpsGenie
    - **事故响应 5 阶段**：检测 → 响应 → 缓解 → 恢复 → 复盘
    - **Blameless Postmortem** · 无过错文化（Google SRE）
    - **Action Items 跟踪**是闭环的关键（80% 团队死在这步）
    - **AI 事故特殊维度**：幻觉 / 越狱 / Agent 失控

## 1. SEV 分级

### 1.1 分级标准（业界常见）

| 级别 | 定义 | 响应 | 例子 |
|---|---|---|---|
| **SEV 0 / P0** | 业务完全不可用 · 财务 / 合规 / 安全 · 高管级 | **立即**（5 min 内）· 全员进 war room | 数据泄露 · 核心 BI 全挂 · 合规审计发现重大问题 |
| **SEV 1 / P1** | 核心功能受损 · 用户能感知 | **< 30 min** · 核心 oncall + 相关领域 | 主 ETL pipeline 挂 · LLM 服务错误率飙 · Catalog 慢但没挂 |
| **SEV 2 / P2** | 辅助功能受损 · 用户部分感知 | **< 2 hour** · oncall | 某个业务线数据迟 · 非核心模型 drift · Dashboard 慢 |
| **SEV 3 / P3** | 小问题 · 有 workaround | **工作时间** | 小表 schema 错 · 单个 query 慢 |

### 1.2 分级决策

不确定时倾向**更高级**（宁可过度响应 · 不漏响应）。由 oncall 初始定级 · incident commander 后续调整。

## 2. Oncall 轮值

### 2.1 基本流程

- **一周轮一次**（周一 10:00 交班）
- **主 oncall + 次 oncall**（次 oncall 备胎 · 主不响应 15 min 后接过）
- **值班补偿**（周末 / 凌晨 oncall 额外工时）
- **团队 oncall ≠ 个人 oncall**（一个领域至少 3+ 人轮 · 防疲劳）

### 2.2 工具链

| 工具 | 用途 |
|---|---|
| **PagerDuty**（商业 · 最广）| 告警路由 · 轮值 · 升级策略 |
| **OpsGenie**（Atlassian）| 同类 · 企业常用 |
| **Grafana OnCall**（OSS）| 开源替代 · 基础功能 |
| **自建 + Slack + PD webhook** | 小团队定制 |

### 2.3 告警到 oncall 的路由

```
告警（Prometheus / Datadog / Grafana）
  ↓ webhook / integration
PagerDuty 规则
  ↓ 按 service / severity 路由
值班人手机 push + Slack + 电话
  ↓ 15 min 未 ack
次 oncall + 团队 Lead
  ↓ 30 min 未 ack
升级（总监 / VP）
```

### 2.4 Alert Fatigue 处理

**告警疲劳**是 oncall 头号敌人：
- 每周 oncall review · 看哪些告警是**噪声**
- **Alert SLO**（某条告警**必须**可执行）
- Runbook 关联 · 告警带排查步骤

## 3. 事故响应 5 阶段

### 3.1 检测（Detection）

告警进 oncall · 或用户投诉进支持通道 · 升级为 incident。

### 3.2 响应（Response）

- **创建 war room**（Slack channel / Zoom）
- **Incident Commander**（IC）指定 · 协调所有人
- **Scribe** 记录时间线（postmortem 原料）
- **对外沟通**（Comms）· 客户 / 高管通知

**RACI**：
- IC · Responsible for 事故流程
- Oncall 技术负责人 · Responsible for 修
- Scribe · Accountable for 时间线记录
- Comms · Accountable for 外部沟通

### 3.3 缓解（Mitigation）

**核心目标**：**尽快止血** · 不追求根因解决。

- **回滚**（新版本上线就挂 · 先回滚再说）
- **切流量**（Alias / feature flag 关 / 路由切备用）
- **降级**（丢弃非核心功能 · 保住核心）
- **扩容**（临时加资源硬扛）

**黄金 30 分钟**：事故前 30 min 做的决策对损失影响最大。

### 3.4 恢复（Recovery）

- 验证**业务指标恢复**（不只是技术指标）
- **观察期**（15-60 min）· 看没有二次故障
- 正式关闭事故

### 3.5 复盘（Postmortem · §4 详述）

## 4. Blameless Postmortem · 无过错复盘

### 4.1 核心原则（Google SRE 文化）

- **不指责个人** · 针对系统 / 流程
- **所有人都可能犯错** · 好的系统不依赖个人不犯错
- **Focus on future** · 怎么防止类似发生

### 4.2 Postmortem 模板

```markdown
## Incident Postmortem: <事故名>

**Severity**: SEV 1
**Date**: 2026-04-20
**Duration**: 14:30 - 16:45 (2h15m)
**Impact**: ~5000 用户查询失败 · 估计损失 $50k

## 时间线

- 14:30 · Alert 触发（Prometheus · ETL pipeline failure）
- 14:32 · Oncall ack
- 14:35 · war room 建
- 14:40 · 发现根因（Spark 集群 OOM · 上午扩容未生效）
- 14:55 · 缓解（回滚资源配置）
- 15:10 · 业务指标恢复
- 16:45 · 观察期结束 · 关闭

## 根因（Root Cause · Five Whys）

1. 为什么 pipeline 挂？→ Spark OOM
2. 为什么 OOM？→ 数据量突增 · memory 不够
3. 为什么扩容没生效？→ Terraform apply 失败 · 无人注意
4. 为什么 apply 失败无人注意？→ CI 结果没通知到 oncall
5. 为什么 CI 不通知？→ 告警规则缺失

## 影响

- 5000 查询失败
- 3 个业务方数据晚 2 小时
- 预估财务损失 $50k

## 做对的事

- Oncall 2 分钟内 ack
- war room 快速建
- 缓解正确（直接回滚而非诊断根因）

## 做错的事 / 可改进

- CI 失败告警缺失
- 资源变更未经过 Staging 验证
- Scale-up 流程没有 review

## Action Items（必须有 owner + 截止日）

| AI | Owner | 截止 | 状态 |
|---|---|---|---|
| 补 CI 失败告警 | @alice | 2026-04-27 | ongoing |
| Terraform 强制 staging 验证 | @bob | 2026-05-05 | ongoing |
| 资源变更 PR review 流程 | @alice | 2026-04-30 | ongoing |

## 经验 / 教训（非 AI · 知识沉淀）

- Scale-up 事故典型：扩容未验证 + 告警盲点 · 组合爆
- CI 告警应和生产告警一个通道
```

### 4.3 Postmortem 流程

- **事故 48 小时内**起草（记忆还新鲜）
- **一周内**团队 review meeting
- **Action Items 跟踪**（下次 review 看进度）

### 4.4 文化关键

- **领导率先承认 Action Items 延迟**（不背后甩锅）
- **Postmortem 公开**（团队内 · 必要时全公司）
- **Action Items 不做 = 白写**（最常见 · 事故重复发生）

## 5. AI 事故的特殊维度

### 5.1 AI 特有 SEV 分级

| 场景 | 分级 |
|---|---|
| **LLM 输出严重幻觉影响业务决策** | SEV 1 |
| **Agent 执行错误操作**（如误删数据 / 误发邮件）| SEV 0（爆炸半径大）|
| **越狱攻击**（安全 / 内容违规） | SEV 0 |
| **Prompt Injection 攻击** | SEV 1 |
| **LLM 响应时间上升但质量未降** | SEV 2 |

### 5.2 AI 事故 Postmortem 特殊维度

- **Prompt 审查**（事故时用的是哪个 prompt 版本？）
- **模型版本对比**（新旧模型在类似 query 上的 diff）
- **训练数据审查**（如果是模型输出问题）
- **Fairness 审查**（是否对特定群体有系统性错）

### 5.3 LLM 事故的 Mitigation 选项

- **回滚 Prompt**（Registry 切换到上一版）
- **模型降级**（GPT-4 → Mistral 或反向）
- **Guardrails 严格化**（临时加强输出过滤）
- **Feature Flag 关停**（关闭问题功能 · 不 rollback 全部）

## 6. 事故度量

### 6.1 关键指标

- **MTTD**（Mean Time To Detect）· 告警发出到 oncall 响应
- **MTTR**（Mean Time To Repair）· 响应到缓解
- **Incident Count / Month** · 分 SEV 统计
- **Recurring Incident Rate** · 重复事故占比

### 6.2 目标（成熟团队）

| 指标 | 目标 | `[来源未验证 · 业界经验]` |
|---|---|---|
| MTTD（P0）| < 5 min | |
| MTTR（P0）| < 1 hour | |
| MTTR（P1）| < 4 hour | |
| 重复事故率 | < 10% | 高于说明 Action Items 没落实 |

## 7. Runbook · 事故响应的武器库

### 7.1 Runbook 内容

每个 runbook 包含：
- **触发条件**（哪个告警对应这个 runbook）
- **快速诊断**（前 5 分钟看哪些指标）
- **缓解步骤**（step-by-step）
- **相关人员**（谁懂这个系统 · 标了 · 升级时找）
- **历史参考**（之前类似事故的 postmortem 链接）

### 7.2 Runbook 库

- 存 Git（和代码一起演进）· 或 wiki
- 告警直接 link runbook
- 每季度 review · 过时的 runbook 删除

## 8. 陷阱 · 反模式

- **告警疲劳 · 真实告警被淹**
- **Oncall 轮值少于 3 人** · 永远在 oncall · 疲惫
- **事故缓解没有时间窗口**（一直调错参数 · 30 分钟过去没进展 → 应该果断回滚）
- **Postmortem 找个人背锅**（文化崩塌 · 下次事故大家 CYA）
- **Action Items 写了不跟** · 事故重复发生
- **Oncall 没有权限 / 上下文** · 需要找 10 个人才能修
- **Comms 缺位**（客户懵 · 高管乱问）
- **不做 tabletop exercise**（桌面演练）· 真事故时手忙脚乱

## 9. 成熟度路径

**L0 起步**：有告警 · 有人响应 · 没流程
**L1**：Oncall 轮值 · 基本 runbook
**L2**：SEV 分级规范 · IC 文化 · Blameless Postmortem · Action Items 跟踪
**L3**：事故度量体系 · Tabletop 演练 · Chaos Engineering · 自愈系统

## 10. 相关

- [sla-slo](sla-slo.md) · SLO 预防事故（Error Budget 管控）
- [observability](observability.md) · 事故检测靠观测
- [troubleshooting](troubleshooting.md) · 具体问题的排查方法
- [disaster-recovery](disaster-recovery.md) · 灾难级事故的恢复
- [change-management](change-management.md) · 变更引起事故的防御
- [production-checklist](production-checklist.md) · 上线前减少事故源

## 11. 延伸阅读

- **[*Site Reliability Engineering* (Google SRE Book)](https://sre.google/sre-book/table-of-contents/)** · SRE 奠基作
- **[*The Site Reliability Workbook*](https://sre.google/workbook/table-of-contents/)** · 实操
- **[Google Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)** · Blameless Postmortem
- **[PagerDuty Incident Response Documentation](https://response.pagerduty.com/)** · 最全的开源 IR 文档
- *Site Reliability Engineering at Scale* · Netflix / LinkedIn tech blog 事故系列
