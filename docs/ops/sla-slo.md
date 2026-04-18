---
title: SLA · SLO · 数据产品可靠性工程
type: reference
depth: 资深
level: A
last_reviewed: 2026-04-18
applies_to: 2024-2025 SRE + Data Engineering 实践
tags: [ops, sla, slo, reliability, data-product]
aliases: [SLO/SLA/SLI, Data Reliability Engineering]
related: [observability, data-governance, troubleshooting]
status: stable
---

# SLA · SLO · 数据产品可靠性

!!! tip "一句话定位"
    **把"数据工程"升级为"数据产品"的关键环节**——用 SLI（指标）+ SLO（目标）+ SLA（承诺）体系管理数据质量与可用性。**没有 SLO 的数据栈本质是"尽力而为"**。2024-2025 数据 SRE（DRE）在头部公司已是专职岗位。

!!! abstract "TL;DR"
    - **SLI**：实际可观测的指标（延迟 / 新鲜度 / 完整度 / 正确性）
    - **SLO**：内部目标（"95% 查询 p95 < 2s"）
    - **SLA**：对外承诺（违约有后果）
    - **数据侧特色 SLI**：新鲜度 · 完整度 · 口径一致 · 血缘完整
    - **Error Budget**：允许的失败预算，花完了就停发新功能
    - **不做 SLO 的代价**：故障无法复盘、用户投诉吃流程、团队持续救火

## 1. 业务痛点 · 为什么数据团队需要 SLO

### 没有 SLO 的典型困境

- **"数据又不准了"**：业务方投诉，团队到处查
- **"昨天跑的数字今天变了"**：snapshot 没锁，排查 3 天
- **"ETL 又挂了没人知道"**：Airflow DAG 失败告警被忽略
- **"谁负责这张表"**：新人离职、owner 不明
- **优先级混乱**：大事故和小 bug 一样紧急？

这些都是**没有可靠性工程**的症状。

### 数据可靠性 vs 软件可靠性

传统 SRE（服务）：
- SLI：可用性、延迟、错误率
- 衡量**服务是否正常**

数据侧（DRE）：
- 除了上述，还有：
- **新鲜度（Freshness）**：数据有多老
- **完整度（Completeness）**：记录有没有缺失
- **正确性（Correctness）**：数字对不对
- **口径一致（Consistency）**：和其他数据源对得上吗
- **血缘完整（Lineage）**：从源头到下游可追溯吗

## 2. SLI · SLO · SLA 三层

### SLI（Service Level Indicator）· 可观测指标

**数据侧典型 SLI**：

| 类别 | 指标 | 如何测 |
|---|---|---|
| **新鲜度** | 最新 snapshot 距今时间 | `NOW() - MAX(snapshot.committed_at)` |
| **完整度** | 期望行数 / 实际行数 | 对比上游事件数 vs 下游表行数 |
| **准点率** | ETL 在 SLA 时间内完成比例 | Airflow task 成功 + 准点 / 总 runs |
| **查询延迟** | p50/p95/p99 | Trino metrics |
| **查询成功率** | 成功 / 总数 | Trino logs |
| **数据准确** | 对账通过率 | 定时抽样 vs ground truth |
| **Schema 稳定** | schema 变更次数 / 月 | 变更日志 |

### SLO（Service Level Objective）· 内部目标

```
SLO 声明格式：
"<SLI> should be <threshold> <percentage>% of the time in <window>"

例：
- "订单表每日 ETL 在 08:00 前完成 99% of the time in 30-day window"
- "推荐向量库查询 p99 < 50ms，99% of time"
- "用户画像表新鲜度 < 1 hour，95% of time"
```

### SLA（Service Level Agreement）· 对外承诺

- **违约有后果**（退款 / 罚款 / 赔偿）
- 典型在 **数据产品对外商业化** 时需要
- 大多数内部数据栈只到 SLO 就够

## 3. Error Budget · 失败预算

SLO = 99.5% → 允许 0.5% 失败。

**Error Budget 机制**：
- 累计失败消耗 budget
- Budget 用完 → **暂停发新功能，专注修稳定性**
- Budget 有富余 → 可以更大胆推新

### 30 天 Error Budget 举例

- SLO：99.5% 准点
- 30 天 × 24 小时 = 720 小时总时间
- Budget：0.5% × 720 = **3.6 小时可以不准点**

### 数据侧 Budget 操作

- 每次 ETL 晚点 > 10 分钟算一次违约
- 月末看累计违约时长
- 超预算 → 下月重点是"让 ETL 更稳"

## 4. 数据产品分级

不是所有表都需要 99.9% SLO。**分级**让资源投入合理：

| 级别 | 例 | SLO |
|---|---|---|
| **T0 · 核心** | 收入报表、KPI 指标、合规审计表 | 99.9% 准点 + 100% 准确 |
| **T1 · 重要** | 运营指标、活跃用户、业务仪表盘 | 99.5% + 95% 准确（近似可接受）|
| **T2 · 常规** | 分析师探索表、辅助指标 | 95% |
| **T3 · 尝试** | 新模型特征、实验数据 | Best effort |

**T0 表**对应投入：
- 主备集群 / DR
- 实时监控 + oncall
- 严格的 code review
- 质量 gate + 灰度发布

## 5. 工程落地

### 工具链

| 环节 | 工具 |
|---|---|
| **数据可观测** | Monte Carlo / Great Expectations / Soda / Elementary |
| **ETL 监控** | Airflow / Dagster 内置 + Prometheus |
| **查询性能** | Trino metrics + Datadog / Grafana |
| **血缘** | DataHub / OpenMetadata / OpenLineage |
| **SLO 管理** | Nobl9（商业）· 自建 Postgres + Grafana |
| **告警路由** | PagerDuty / OpsGenie / 钉钉 / 企业微信 |

### SLO 管理的生命周期

```
1. 定义 SLI（可测量）
2. 设 SLO 目标（合理 · 业务可接受）
3. 测量 + 仪表盘
4. 违约 → 告警 + Oncall
5. Postmortem（无过错）
6. Action Items + 跟踪
7. 季度 review SLO 是否调整
```

### SLO 定义示例（YAML 格式参考）

```yaml
name: orders_daily_etl_freshness
sli:
  metric: etl_completion_time
  source: airflow
  good_events: etl finished by 8:00 AM
  total_events: total daily runs
slo:
  objective: 99.5
  window: 30d
alert:
  fast_burn:        # 1 小时消耗 2% budget → 告警
    threshold: 2
    window: 1h
  slow_burn:        # 24 小时消耗 5% budget → 告警
    threshold: 5
    window: 24h
```

## 6. 数据侧特有的实践

### 数据契约（Data Contract）

**上游对下游的承诺**：

```yaml
contract:
  table: prod.sales.orders
  owner: sales_team
  schema:
    - name: order_id
      type: bigint
      not_null: true
    - name: amount
      type: decimal(18,2)
      not_null: true
  SLO:
    freshness: < 1 hour
    completeness: > 99%
  breaking_change_policy: 30-day notice
```

上游**修改 schema 要和下游协商**，不能拍脑袋。

### 质量 Gate（自动化）

```python
# Great Expectations 例
expect_column_values_to_not_be_null("order_id")
expect_column_values_to_be_unique("order_id")
expect_column_sum_to_be_between("amount", 1000000, 2000000)
expect_row_count_to_be_between(90000, 110000)

# dbt tests
models:
  orders:
    columns:
      - name: order_id
        tests: [unique, not_null]
      - name: amount
        tests:
          - dbt_utils.expression_is_true:
              expression: "amount > 0"
```

运行在每次 ETL 后，挂 pipeline 失败 → 告警 → 人介入。

### Postmortem · 无过错复盘

故障后**不指责个人**，focus on：
- 根因是什么（why 5 次）
- 为什么没发现（监控盲区）
- 如何避免（Action Items）
- 时间线（从故障到修复）

谷歌 SRE 手册的**Blameless Postmortem** 文化。

## 7. 组织 · 文化

### DRE（Data Reliability Engineer）角色

在头部公司 2024+ 已是专职：
- 负责数据 SLO 体系
- 搭建可观测工具链
- 推动数据契约
- Oncall

### 数据团队的 Oncall 轮值

- 和服务 SRE 一样 oncall 24/7
- 响应 P0 数据事故
- 工具：PagerDuty + Slack

### 文化建设

- **数据产品化**（Data as Product）思维
- **Owner 明确**：每张关键表有 owner
- **无过错复盘**
- **SLO > Feature**：出事停发新功能

## 8. 性能数字 · 行业参考

| 指标 | 业界常见 SLO |
|---|---|
| ETL 准点率（T0）| 99.5% |
| 表新鲜度（分钟级 pipe） | < 15 min 95% of time |
| 查询 p99（BI） | < 5s 99% of time |
| 数据 bug 修复时间（T0 MTTR）| < 4 hours |
| Incident 数量/月（成熟团队）| T0: 1-2 · T1: 5-10 |

## 9. 现实检视

### 不是每个团队都需要 DRE

**先不要上 SLO 的情况**：
- 团队 < 5 人 · 数据量 < 1TB
- 业务对数据可靠性不敏感
- ETL 稳定率已经 > 99%

**建议路径**：先做 [可观测性](observability.md) + [数据治理](data-governance.md)，**有持续痛点再上 SLO**。

### 工具陷阱

- **Monte Carlo / Great Expectations 装上就好**：工具是辅助，**文化才是核心**
- **SLO 太严**：99.99% 可能永远做不到，失去意义
- **SLO 太松**：99% 谁都过，没约束

### 2026 前瞻

- **Data Contract + ML Contract** 会成为新标准
- **AI / LLM 输出的 SLO** 是新领域（hallucination rate、token budget）
- **自愈系统**：告警 → 自动修复（简单场景）

## 10. 陷阱与反模式

- **一刀切 SLO**：所有表 99.9% → 资源浪费 + 不可能完成
- **SLO 做了没 owner**：背起来的 Oncall 是谁？
- **违约不 postmortem**：重复事故
- **Error Budget 花完继续发新功能**：制度失效
- **可观测不血缘**：数据坏了不知道影响谁
- **告警太多**：淹没真实告警，狼来了
- **数据团队不做 Oncall**：8 点 ETL 挂了 10 点才有人处理

## 11. 延伸阅读

- **[*Site Reliability Engineering* (Google SRE Book)](https://sre.google/sre-book/table-of-contents/)** —— SLO 起源
- **[*The Site Reliability Workbook*](https://sre.google/workbook/table-of-contents/)** —— 实操指南
- **[Monte Carlo *Data Reliability Engineering*](https://www.montecarlodata.com/blog/)**
- **[dbt *Data Contracts*](https://docs.getdbt.com/docs/collaborate/govern/model-contracts)**
- **[OpenLineage](https://openlineage.io/)** —— 开源血缘规范
- **[Nobl9 SLO 教程](https://www.nobl9.com/resources)**

## 相关

- [可观测性](observability.md) · [数据治理](data-governance.md)
- [故障排查手册](troubleshooting.md) · [容量规划](capacity-planning.md)
- [反模式](anti-patterns.md)
