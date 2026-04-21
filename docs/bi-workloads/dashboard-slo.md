---
title: 仪表盘 SLO · 并发 × 延迟 × 新鲜度工程
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: Trino · StarRocks/Doris · ClickHouse · Druid · Pinot · Snowflake · Databricks
tags: [bi, slo, dashboard, concurrency, latency]
aliases: [Dashboard SLO, BI SLA, 仪表盘工程]
related: [query-acceleration, materialized-view, olap-modeling, performance-tuning]
status: stable
---

# 仪表盘 SLO · 并发 × 延迟 × 新鲜度工程

!!! tip "一句话定位"
    仪表盘的"快慢好坏"**必须用 SLO 量化**——**并发 · QPS · p95 延迟 · 数据新鲜度 · 可用性**五维度。这页讲如何从业务目标**反推**技术手段 · 不是罗列 Trino 调优参数。

!!! abstract "TL;DR"
    - **五维 SLO**：并发（同时在线用户）· QPS（查询 per sec）· p50/p95/p99 延迟 · 数据新鲜度（freshness）· 可用性
    - **三类仪表盘** × **三档 SLO 打法**：内部分析（宽松）· 业务运营（中档）· 用户面 / SaaS（严苛）
    - **隔离是第一要义**：长查询不能拖垮短查询 · Resource Group + Admission Control + 多集群
    - **新鲜度与延迟是两个 SLO** · 互相独立 · 别混
    - **副本是补救不是万能** · 先把布局/MV/隔离做好 · 再上副本

## 1. 为什么要 SLO 化

不定义 SLO 的团队有四类典型投诉循环：

- **"仪表盘慢"** · 没数据化 · 不知道慢到什么程度 · 不知道该优化谁
- **"我的查询卡了"** · 缺乏**可预期性** · 有时 2 秒有时 20 秒
- **"数据不对"** · 数据其实对 · 只是**不知道该多新鲜** · SLO 没说
- **"我们扩容吧"** · 资源 10× 但体验仍差 · 因为**没有优化目标**

**SLO 的价值**：
- **把体验翻译成数字** · 可监控可归因
- **倒逼架构决策** · "p95 < 1s" 逼着选对应技术栈
- **隔离责任** · ETL 延迟 ≠ 查询延迟 · 各背各的锅
- **退场标准** · 什么时候宣告优化完成 · 什么时候决定上副本

## 2. 五维 SLO · 定义与度量

### 2.1 并发（Concurrent Active Users）

**定义**：同一时刻有多少用户正在**操作仪表盘**（不是注册用户 · 不是 DAU）。

- **运营大屏** · 几人看（决策层）
- **分析师仪表盘** · 20-200 人同时用
- **用户面 Dashboard**（SaaS 客户）· 千-万级
- **度量**：前端埋点 · 后端活跃 session

### 2.2 QPS（Queries Per Second）

**定义**：查询引擎**每秒接收**的查询数。

- 和并发不是线性关系——一个 user 打开一个仪表盘可能触发 5-20 个 query
- **度量**：Trino query log · StarRocks audit log · 前端请求监控
- **峰值 QPS / 平均 QPS** 差异大 · 按峰值设计

### 2.3 延迟（Latency）

**三分位必须都看**：
- **p50** · 中位数 · "一般情况下" 的体验
- **p95** · 95% 快于此 · **绝大多数用户的体验上限**
- **p99** · 1% 慢于此 · **长尾体验**

**度量口径**：
- 从客户端**发起请求**到**收到第一行**（或全部行）
- 不要漏算**等待/排队时间**——queued 时间也是用户等待
- **按仪表盘 + query 类型分桶** · 一个仪表盘快 ≠ 全局快

### 2.4 数据新鲜度（Data Freshness / Staleness）

**定义**：看板显示的最新数据和**真实业务事件**之间的时间差。

```
event_ts (业务事件发生)
   ↓ CDC / ingestion
landing_ts (落到 Bronze)
   ↓ ETL
silver_ts (进入 Silver)
   ↓ 聚合 / MV 刷新
mart_ts (进入 ADS / MV)
   ↓ 缓存失效 / BI 刷新
view_ts (用户看到)

freshness = view_ts - event_ts
```

**不同场景目标**：
- **财务 T+1 报表** · 24h freshness · 批刷新
- **运营仪表盘** · 10 min - 1 h · 增量 MV
- **实时大屏** · < 30 s · StarRocks/ClickHouse Stream
- **监控看板** · < 10 s · 专用流处理

**陷阱**：**延迟 ≠ 新鲜度** · 查询可能 100ms · 但数据是 24 小时前的——两个 SLO 独立。

### 2.5 可用性（Availability）

- 99.9% · 每月 43 min 宕机预算
- 99.95% · 每月 22 min
- 99.99% · 每月 4.3 min（用户面 SaaS 通常目标）

- **度量**：成功率 · query 失败率 + 超时率 + 拒绝率
- **失败语义**：queue full / OOM / timeout / engine 不可用

## 3. 三档仪表盘 × 三档 SLO 打法

### 3.1 内部分析仪表盘（宽松档）

**典型**：数据团队内部看板 · 分析师探索 · 工程监控

| 维度 | 目标 |
|---|---|
| 并发 | < 20 |
| QPS | < 10 |
| p95 | < 10s |
| 新鲜度 | 小时-天 |
| 可用性 | 99% |

**手段**：
- **Trino + Iceberg 够用**
- 分区 + Sort Order · 不需 MV
- Resource Group 基础隔离即可

### 3.2 业务运营仪表盘（中档）

**典型**：销售/运营日看板 · 管理层周会 · BI 工具全公司开放

| 维度 | 目标 |
|---|---|
| 并发 | 50-500 |
| QPS | 50-200 |
| p95 | < 3s |
| p99 | < 8s |
| 新鲜度 | 10min-1h |
| 可用性 | 99.9% |

**手段**：
- Trino **需要** Resource Group + Dynamic Filter + MV
- **Top 10 查询打 MV** · 命中率 > 70%
- ADS 层单独 Clustering 优化
- 监控接入告警

### 3.3 用户面 / SaaS Dashboard（严苛档）

**典型**：B2B SaaS 给客户看的 Dashboard · 对外 SLA 合同

| 维度 | 目标 |
|---|---|
| 并发 | 1000-10000+ |
| QPS | 500-5000 |
| p95 | < 1s |
| p99 | < 3s |
| 新鲜度 | 分钟-小时 |
| 可用性 | 99.99% |

**手段**：
- **必须加速副本** · StarRocks / ClickHouse / Doris 本地列存
- **多租户物理隔离** · 大客户独立集群 · 小客户共享资源组
- **结果缓存** · CDN / BI 层缓存 · 相同 query 复用
- **增量 MV + 副本同步** · lag 严格监控
- **降级策略** · 副本挂了可回源查 · 有数据兜底

## 4. 并发隔离 · 第一要义

长查询挤占短查询是**仪表盘崩溃的头号原因**。隔离手段由强到弱：

### 4.1 多集群物理隔离（最强）

- 不同业务域不同 Trino/StarRocks 集群
- **成本**：资源冗余 · 运维工作量×N
- **收益**：一个业务崩不影响别的
- **适合**：大企业 + 明确的业务边界

### 4.2 Resource Group（中等）

```sql
-- Trino resource groups 示例（JSON 配置）
{
  "rootGroups": [
    {
      "name": "dashboard",
      "softMemoryLimit": "40%",
      "maxQueued": 100,
      "maxRunning": 20,
      "schedulingPolicy": "weighted_fair",
      "schedulingWeight": 10
    },
    {
      "name": "etl",
      "softMemoryLimit": "40%",
      "maxQueued": 200,
      "maxRunning": 5,
      "schedulingWeight": 2
    },
    {
      "name": "exploration",
      "softMemoryLimit": "20%",
      "maxQueued": 50,
      "maxRunning": 10,
      "schedulingWeight": 3
    }
  ],
  "selectors": [
    {"source": "superset", "group": "dashboard"},
    {"user": "etl_bot", "group": "etl"},
    {"group": "exploration"}
  ]
}
```

**关键点**：
- **maxRunning** · 并发上限 · 超过进 queue
- **maxQueued** · queue 上限 · 超过直接拒（admission control）
- **schedulingWeight** · 资源争抢的权重
- **selectors** · 按 user/source 自动分组

### 4.3 单查询限制（兜底）

- **query timeout** · 单 query 不能跑超过 60s · BI 场景更短
- **query memory limit** · 单 query 不能吃超过 40% 集群内存
- **result size limit** · 单 query 不能返回超过 1M 行
- **cancel on disconnect** · 用户关浏览器后端立刻取消

### 4.4 Admission Control · 排队 vs 拒绝

**过载时的策略**：
- **排队** · 超量 query 进 queue · 用户等 · 等太久体验烂
- **拒绝** · 直接告诉用户 "忙 · 稍后" · 比卡死体验好
- **降级** · 返回缓存/近似结果 · 告知 "数据可能延迟"

**典型策略**：
- 内部分析 · 排队为主
- 用户面 · 先服务已在运行的 · 新请求拒绝（queue full → 503）· 后端稳
- **永远不要无限 queue** · 雪崩的常见原因

## 5. 新鲜度工程

### 5.1 新鲜度链路监控

```
event_ts → landing_ts → silver_ts → mart_ts → view_ts
```

**每一段的 lag 都要监控** · 任何一段卡住都会影响最终 freshness。

**指标**：
- **CDC lag** · 从业务库到 Bronze 的延迟
- **ETL lag** · Silver 作业完成时间 vs SLA
- **MV refresh lag** · MV 最后刷新时间 vs 源表 snapshot
- **Cache TTL** · BI 工具缓存 TTL 设置

### 5.2 新鲜度 SLO 的典型目标 · 按 lag 段分拆

只看端到端 "event→view" 目标不够 · 配置 SLO 时要拆到每段（否则哪段卡住无法定位）：

| 场景 | event→view 目标 | CDC lag | ETL lag | MV refresh lag | 实现 |
|---|---|---|---|---|---|
| 财务月报 | T+1 | N/A | T+1 批完成 | 每日一次 | 批调度 |
| 运营日报 | < 4h | < 15min | < 3h | < 30min | 批调度 + 重试 |
| 运营实时看板 | < 15min | < 2min | < 10min | < 3min | 增量 MV · StarRocks 异步 |
| 监控告警 | < 30s | < 5s | < 20s | 无 MV · 直查 | Flink + 流存 · ClickHouse 直消费 |
| 实时大屏 | < 5s | < 1s | < 3s | 无 MV · 直查 | Flink + Kafka + 专用引擎 |

**监控维度**：每段 lag 独立 SLI + 分段告警 · 端到端 SLO 是各段的松弛累加（留 20-30% buffer）。

### 5.3 陷阱

- **新鲜度靠 ETL 完成时间判断不够** · ETL 在跑但**还没更新 ADS** · 用户看的仍是旧的
- **BI 工具缓存 TTL 和后端不对齐** · 后端数据新了 BI 还显示旧
- **MV 刷新失败无告警** · 仪表盘继续显示陈旧数据 · 一两天后才发现
- **时区不统一** · event_ts 是 UTC · view 是本地时区 · freshness 计算错

## 6. SLO 治理

### 6.1 监控架构

```
查询引擎 (Trino/StarRocks) → metrics (Prometheus)
ETL 管线 (Airflow/Flink)  → lag metrics
BI 工具 (Superset/Tableau) → 前端埋点
  ↓
Grafana / 内部 SLO 看板
  ↓
告警 (PagerDuty / 钉钉)
```

### 6.2 SLO 报告

每月/每季度产出：
- 各仪表盘的 p50/p95/p99 达成率
- 未达成的仪表盘 · 根因分析
- 命中 MV 的查询比例
- 资源组使用率 · 拒绝率
- 新鲜度达成率 · 每段 lag 的分位

### 6.3 Error Budget

- 月度 SLO 目标 99.9% · 允许 43 min 失败
- 预算**耗完之前** · 可以推新功能、调整副本
- 预算**耗完之后** · 冻结新功能 · 修稳定性

这是 Google SRE 思想的 BI 版。

## 7. 陷阱（SLO 反模式）

- **没定义 SLO 就开始优化** · 优化往哪个方向? 到哪算完? 永远焦虑
- **只看平均延迟** · p50 好看 · p99 灾难 · 长尾用户体验最差却没人代言
- **SLO 一刀切** · 所有仪表盘一个标准 · 用户面和内部用同档 · 要么浪费要么崩
- **新鲜度 = 数据完成** · 错 · 新鲜度 = 用户能看到 · 包含 cache/MV 的传播延迟
- **扩容当银弹** · 硬件 2× 性能可能 1.2× · 架构问题扩容解决不了
- **Admission Control 配成无限 queue** · 雪崩前一刻还在入队 · 挂了全挂
- **BI 工具缓存和后端不协调** · 用户看到的数据和 SLO 声明的不一致
- **Error Budget 没人管** · 用完了继续上线新功能 · SLO 变装饰
- **只看查询侧 SLO 不看 ETL SLO** · ETL 挂了 · 查询再快也没数据

## 8. 相关

- [查询加速](query-acceleration.md) · SLO 的底层手段（布局/索引/副本）
- [物化视图](materialized-view.md) · 命中率是 p95 SLO 的关键
- [性能调优](../ops/performance-tuning.md) · 通用引擎调优
- [SLA / SLO](../ops/sla-slo.md) · 通用可靠性工程
- [多租户](../ops/multi-tenancy.md) · Resource Group / 物理隔离设计
- [BI on Lake 场景](../scenarios/bi-on-lake.md) · 端到端 SLO 打法
- [OLAP 加速副本横比](../compare/olap-accelerator-comparison.md) · 副本产品选型

## 9. 延伸阅读

- **[Google SRE Book · SLOs Chapter](https://sre.google/sre-book/service-level-objectives/)** · SLO 方法论经典
- **[Trino Resource Groups Docs](https://trino.io/docs/current/admin/resource-groups.html)**
- **[StarRocks Resource Isolation](https://docs.starrocks.io/docs/administration/resource_group/)**
- **[*Database Reliability Engineering* (Campbell & Majors, O'Reilly)](https://www.oreilly.com/library/view/database-reliability-engineering/9781491925935/)**
- **[*Implementing SLOs* (Betsy Beyer et al., 2018)](https://sre.google/workbook/implementing-slos/)**
