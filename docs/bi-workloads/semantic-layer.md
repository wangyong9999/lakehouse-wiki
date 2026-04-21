---
title: 语义层 · Semantic Layer / Metrics Layer
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-18
applies_to: dbt Semantic Layer · Cube.js · MetricFlow · LookML · Malloy
tags: [bi, semantic-layer, metrics, dbt, cube]
aliases: [指标中台, Metrics Layer, Headless BI]
related: [olap-modeling, materialized-view, modern-data-stack]
status: stable
---

# 语义层 · Semantic Layer

!!! tip "一句话理解"
    **把"指标定义"从 BI 工具里抽出来，集中到一处**。一个 "GMV" 在 SQL / Python / Tableau / API 里都是同一个定义——消除"同一指标十个报表十个数字"的老问题。2024-2025 **dbt Semantic Layer + Cube** 成为事实标准。

!!! abstract "TL;DR"
    - **核心问题**：指标口径不一致、BI 工具各自实现逻辑、业务对不齐
    - **解法**：一处定义 + 多端消费（Headless BI）
    - **主流产品**：**dbt Semantic Layer**（2023 收购 Transform） · **Cube** · LookML（Looker 专属）· **Malloy**（malloydata 开源 · 实验）
    - **核心抽象**：entities · measures · dimensions · time_spine
    - **落地成熟度**：**2024 下半年起生产可用** · **2025-2026 dbt SL / Cube 进入稳定采用期**
    - **2026 新变革** · **LLM × Semantic Layer** 成为 Text-to-SQL / Auto-Insight 的**知识抓手**（详见 §10）
    - **何时需要**：业务指标 > 50 个、BI 工具多 > 2 个、跨团队用数据

## 1. 业务痛点 · 不做语义层会怎样

### 典型事故

**场景**：公司月度经营会上 3 个报表给出不同的 GMV：
- **财务报表**：¥1.2 亿（含税后退款前）
- **运营大屏**：¥1.3 亿（税前含退款）
- **分析师 Notebook**：¥1.1 亿（过滤了已删除订单）

团队花 2 天时间查"谁算对了"。结论：**三个都"对"**——各自定义不同、没写在一起。

### 症结

| 问题 | 后果 |
|---|---|
| **SQL 分散在多处**（Tableau / Looker / Superset / Python notebook） | 改指标要改 N 处 |
| **业务术语不统一**（"活跃用户"有 5 种定义）| 对不齐 |
| **维度层级无共享**（"时间：日/周/月/季"每工具自己算） | 重复劳动 |
| **权限和脱敏分散** | 安全漏洞 |
| **BI 工具锁定** | 换工具要重写所有指标 |

### 语义层的价值

**一处定义、多端消费**：

```
    dbt Semantic / Cube 定义层
           │
    ┌──────┼──────┐
    │      │      │
  Tableau Super-  Python   API
          set     Notebook 查询
```

同一个 "GMV" 四个工具拿到同一个数字。

## 2. 核心抽象

### Entity · Measure · Dimension

```yaml
# dbt Semantic Layer 示例
semantic_models:
  - name: orders
    model: ref('fct_orders')
    entities:
      - name: order_id
        type: primary
      - name: user_id
        type: foreign
    measures:
      - name: gmv
        expr: amount
        agg: sum
      - name: order_count
        expr: "1"
        agg: count
    dimensions:
      - name: region
        type: categorical
      - name: order_ts
        type: time
        type_params:
          time_granularity: day
```

### Metric（指标）

```yaml
metrics:
  - name: monthly_gmv
    type: simple
    type_params:
      measure: gmv
    filter: "{{ Dimension('order__status') }} = 'completed'"
  - name: gmv_growth_mom
    type: derived
    type_params:
      expr: (gmv - gmv_prev_month) / gmv_prev_month
```

### Time Spine

语义层统一的时间表，支持跨粒度查询：
```sql
-- 语义层自动 resolve
SELECT * FROM {{ metric('monthly_gmv') }}
WHERE {{ dimension('order__order_ts__week') }} >= '2024-01-01';
```

## 3. 主流产品对比

### dbt Semantic Layer（2023+，行业主流）

**历史**：dbt Labs 2023 收购 Transform（MetricFlow），整合成 dbt Semantic Layer。

**核心**：
- **SQL-first + YAML 定义**
- 通过 dbt Cloud 的 **Semantic Layer API** 暴露
- 支持 GraphQL / JDBC 查询

**优**：
- 和 dbt 生态深度集成
- 业界采用快速上升
- 开源版 MetricFlow 有

**劣**：
- 生产级功能需要 **dbt Cloud 订阅**
- 查询路由 / 缓存仍在演进

### Cube（Cube.js / Cube Cloud）

**历史**：开源 2017，独立发展。

**核心**：
- 独立**语义层 API**
- 内建 **Pre-aggregation** 缓存
- 支持 JS / Python / SQL 定义

**优**：
- **开源** + 商业版
- 成熟的 API 层（REST / GraphQL / SQL）
- 强大的 Pre-aggregation 缓存机制
- 不绑定 dbt

**劣**：
- 语法和 dbt 不同（双栈维护）
- 中文社区较小

### LookML（Looker 专属）

**历史**：Google Looker 的语义层（2012 起）。

**特点**：
- 业界最早的成熟语义层
- **只在 Looker 生态**（2019 Google 收购后仍绑定）
- 强大但锁定

**2026 迁出信号**：
- Google 内部优先级下降 · 新资源投向 Gemini/BigQuery
- 客户反馈"Looker 功能冻结感" · 开始迁 Tableau / dbt+Hex / ThoughtSpot
- **迁出策略** · 先把 LookML 里的指标定义翻译到 **dbt SL 或 Cube**（工具：`dbt2looker` 反向 · 或人工迁移）· 再换前端。**Malloy 不适合作为 Looker 替代**（仍属实验 · 见下方 § 3.4）
- **风险** · LookML 的 dimension `sql_table_name` 在 dbt SL 不完全等价 · 要测试

### Malloy（malloydata 开源 · 社区主导）

**定位**：新语言（非 SQL · 组合式） · 2022+ 由 Lloyd Tabb（前 Looker CTO）主导。

**2026 状态**：
- 仓库归 [malloydata 组织](https://github.com/malloydata/malloy)（不再挂 googleapis · 治理偏社区化）
- Google 仍有 backing（Lloyd 等前 Looker 人）· 但**未成为 Google 官方产品**
- 连接 BigQuery / DuckDB / Postgres / Snowflake · VS Code 扩展是主要入口
- **仍属实验** · 不推荐生产作为主力语义层 · 但**作为 IDE 探索工具**值得一试

**为什么值得关注**：Malloy 的**嵌套结果集 + 组合查询**表达力显著强于 SQL · 若 LLM 生成 Malloy 比 SQL 容易对 · 可能成为 Text-to-SQL 中转语言。

### 其他

- **MetricFlow**（已合并入 dbt · 作为 dbt SL 底层引擎）
- **Transform**（已被 dbt 收购）
- **AtScale**（商业 OLAP + 语义层 · 老牌 MOLAP 转型）
- **Kyligence / Apache Kylin**（多维 Cube 派 · 2024 起加语义层能力 · 中国厂商）
- **Semantic Layer in Essbase / SSAS** · 传统 BI 的 cube-based 语义层 · 仍在金融等遗产场景
- **Minerva**（Airbnb 内部 · 基于 SQL + YAML · 未开源）· **Metric Flow**（Uber · 和 dbt 的 MetricFlow 命名冲突 · 不同系统）· **Amberfl**（LinkedIn · 主打可信指标治理）—— 大厂内部

## 4. 能力对比

| 能力 | dbt Semantic | Cube | LookML | Malloy |
|---|---|---|---|---|
| 开源 | ⚠️（MetricFlow 开源，SL API 商业）| ✅ | ❌ | ✅ |
| 语法 | SQL + YAML | JS/YAML/SQL | LookML（专属）| Malloy（新语言） |
| 缓存 / Pre-agg | 依赖 dbt | **强** | 强 | 初级 |
| API 暴露 | JDBC / GraphQL | REST / SQL / GraphQL | Looker 专属 | 弱 |
| BI 工具集成 | Tableau / Hex / 等 | 几乎所有 | Looker | 少 |
| 成熟度 | 2024 快速成熟 | 成熟 | 成熟 | 实验 |

## 5. 工程落地

### 路径 A · dbt-native

```
dbt core models/      # 传统 dbt 转换
dbt models/semantic/  # 语义模型定义
  ↓
dbt Cloud Semantic Layer API
  ↓
Tableau / Hex / Superset / 自有 App
```

### 路径 B · Cube（独立 API）

```
Cube Schema (JS / YAML)
  ↓
Cube Cloud / 自部署
  ↓
REST / GraphQL / SQL API
  ↓
前端（React 组件）/ BI 工具 / Python
```

### 路径 C · 大厂自研（Airbnb Minerva 等）

**通常不推荐中小团队**；成本巨大。

## 6. 生产部署注意

### 性能

- **Pre-aggregation 是关键**：热查询走预聚合，否则每次打底表
- Cube 有成熟 Pre-agg
- dbt SL 依赖下层 warehouse（Snowflake / Databricks）的 MV / 缓存

### 权限

- 语义层统一**行级 / 列级 / 指标级**权限
- 比在每个 BI 工具配置一遍安全得多

### 监控

- 慢查询 → 追哪个 metric / dimension 组合
- 缓存命中率
- API QPS

## 7. 和 BI 工具的集成

| BI 工具 | dbt Semantic | Cube |
|---|---|---|
| Tableau | ✅ JDBC | ✅ Cube SQL API |
| PowerBI | 部分 | ✅ |
| Looker | — | ⚠️（有摩擦） |
| Superset | ✅ | ✅ |
| Metabase | ✅ | ✅ |
| Hex / Observable / Mode | ✅ | ✅ |
| Python (BI Tool) | ✅ | ✅ |

## 8. 现实检视 · 2026 视角

### 成熟度评估（2026-Q2 视角）

- **dbt Semantic Layer**：2023 发布 · 2024 下半年起生产可用 · **2025-2026 进入稳定采用期** · 生态：Tableau/Hex/Mode/Lightdash JDBC 接入稳定 · dbt MCP server 让 LLM 可直接调 SL
- **Cube**：中小规模首选 · 多前端 API 成熟 · Cube AI 模块 2024-2026 集成 LLM 入口
- **LookML**：老牌稳定 · 但 **Looker 在 Google 内部优先级下降** · 企业**新项目不建议上 Looker** · 老项目考虑迁出（见 §3 迁出策略）
- **Malloy**：社区维护 · 实验阶段 · 探索性使用 · 不推荐生产
- **Kyligence / AtScale**：传统 OLAP Cube 转型 · 在有 Cube 遗产的企业可考虑 · 新项目优先 dbt SL / Cube
- 大厂内部方案基本不对外开放

### 落地障碍

- **组织共识**：团队先同意"统一口径是重要的" → 再推技术
- **历史负担**：老 BI 报表里嵌的 SQL 要慢慢迁
- **学习曲线**：YAML + 维度建模都要懂
- **性能**：语义层不能暗中把简单查询变慢

### 什么时候**不要**上

- 团队 < 10 人
- 指标 < 30 个
- BI 工具只有 1 个（直接在 BI 里定义就好）
- 业务口径稳定、变化少

### 什么时候**应该**上

- ✅ 团队 20+ 人用数据
- ✅ 指标 50+
- ✅ 多个 BI 工具 / 产品 / API 消费
- ✅ 已有指标"口径乱"的投诉
- ✅ 已经在用 dbt（这时 dbt SL 是自然延伸）

## 9. 代码示例

### dbt Semantic Layer 完整配置

```yaml
# models/marts/semantic/sem_orders.yml
semantic_models:
  - name: orders
    defaults:
      agg_time_dimension: order_ts
    model: ref('fct_orders')
    
    entities:
      - name: order_id
        type: primary
      - name: user_id
        type: foreign
      - name: product_id
        type: foreign
    
    measures:
      - name: gmv
        expr: amount
        agg: sum
      - name: order_count
        expr: "1"
        agg: count
      - name: unique_users
        expr: user_id
        agg: count_distinct
    
    dimensions:
      - name: region
        type: categorical
      - name: status
        type: categorical
      - name: order_ts
        type: time
        type_params:
          time_granularity: day

metrics:
  - name: gmv_completed
    type: simple
    type_params:
      measure: gmv
    filter: "{{ Dimension('orders__status') }} = 'completed'"
  
  - name: aov  # Average Order Value
    type: ratio
    type_params:
      numerator: gmv_completed
      denominator: order_count
  
  - name: gmv_wow_growth
    type: derived
    type_params:
      expr: (gmv_completed - gmv_completed_prev_7d) / gmv_completed_prev_7d
      metrics:
        - name: gmv_completed
        - name: gmv_completed
          alias: gmv_completed_prev_7d
          offset_window: 7 days
```

### Cube 示例

```javascript
// schema/Orders.js
cube('Orders', {
  sql: `SELECT * FROM fct_orders`,
  
  measures: {
    gmv: {
      sql: `amount`,
      type: 'sum',
      format: 'currency'
    },
    orderCount: {
      type: 'count'
    }
  },
  
  dimensions: {
    region: { sql: `region`, type: 'string' },
    status: { sql: `status`, type: 'string' },
    orderTs: { sql: `order_ts`, type: 'time' }
  },
  
  preAggregations: {
    dailyGmvByRegion: {
      measures: [gmv, orderCount],
      dimensions: [region],
      timeDimension: orderTs,
      granularity: 'day',
      refreshKey: { every: '1 hour' }
    }
  }
});
```

### 查询 API

```python
# Cube REST API
import requests
r = requests.post("https://cube.corp/cubejs-api/v1/load", json={
    "query": {
        "measures": ["Orders.gmv"],
        "timeDimensions": [{"dimension": "Orders.orderTs", "granularity": "month"}],
        "filters": [{"dimension": "Orders.status", "operator": "equals", "values": ["completed"]}]
    }
})
```

## 10. LLM × Semantic Layer · 2026 核心变革

!!! info "本节定位"
    本节讲 **语义层视角的 LLM 集成机制**（SL 里的 metrics 如何被 LLM 消费 · SL 对 Text-to-Query 的必要性）。**端到端 BI+LLM 产品对比** 和 **架构选型决策** 见 [BI × LLM](bi-plus-llm.md)。

!!! info "2026 最大转折"
    语义层从 "BI 口径治理" 转变为 **"LLM 访问企业数据的知识抓手"**。Databricks Genie · Snowflake Cortex Analyst · dbt SL MCP · Cube AI 都在走这条路。

### 10.1 为什么 LLM 需要语义层

直接 Text-to-SQL 的问题（详见 [Text-to-SQL 平台](../scenarios/text-to-sql-platform.md)）：

- **Schema 理解难** · 几千张表 + 上万列 · 列名 `usr_amt_1` 是什么？
- **口径不一致** · "GMV" 在表里找不到 · 业务词在 SQL 里没位置
- **Join 路径复杂** · LLM 猜 FK 关系经常错
- **时间语义** · "上周" 对齐到 ISO week 还是自然周？

**语义层把这些全部解决**：
- **Entity + Measure + Dimension** 是 LLM 可理解的**业务语义抽象**
- **Metric 定义**里写清楚 "GMV = SUM(amount) WHERE status='completed'" · LLM 不用猜
- **Time Spine** 统一时间语义 · "上周" 就是 SL 里定义的 last_week
- **Join 关系**预编在 entities 里 · LLM 不用画关系图

### 10.2 典型 LLM × SL 架构

```mermaid
flowchart LR
  user[用户自然语言<br/>"上周华北 GMV"] --> llm[LLM]
  sl_schema[(SL 元模型<br/>metrics + dimensions)] -.-> llm
  llm --> sl_query[生成 SL Query<br/>metric=gmv · dim=region · time=last_week]
  sl_query --> sl_api[Semantic Layer API]
  sl_api --> sql[编译 SQL]
  sql --> wh[(Warehouse)]
  wh --> result[结果]
  result --> llm2[LLM 解释]
  llm2 --> user2[返回]
```

**关键点**：LLM **不直接写 SQL** · 而是写**语义层查询**（dimension/metric 组合）· SL 负责翻译成 SQL。

**好处**：
- LLM 只需理解**有限的 entity/metric 词汇**（几百个）· 不是几千表几万列
- SL 的权限/脱敏**一路保持** · 不会被 LLM 生成的 SQL 绕过
- **可审计** · 每个 query 有语义层 query plan · 业务能看懂

### 10.3 产品矩阵（2026-Q2）

| 产品 | 架构 | 状态 | 说明 |
|---|---|---|---|
| **dbt Semantic Layer + MCP** | dbt SL API · LLM 走 MCP 调用 | 2025 发布 dbt MCP · 2026 集成度提升 | dbt 生态天然配套 |
| **Databricks AI/BI Genie** | Unity Catalog metadata + instruction + LLM | **GA**（2025 年内）· 4000+ accounts | 商业栈领跑 |
| **Snowflake Cortex Analyst** | Snowflake Semantic Model YAML + LLM | Public Preview 2024+ · 2026 大规模采用 | Snowflake 栈 |
| **Cube AI** | Cube schema + LLM · REST 层 | 2024+ · 稳定 | 多前端生态 |
| **Tableau GPT / Pulse** | Tableau 元数据 · LLM 生成 viz | GA | 前端为主 |
| **ThoughtSpot Sage / Spotter** | ThoughtSpot Search + LLM | 成熟 | 搜索式 BI 老牌 |
| **自研 + MCP** | 内部语义层 + Claude/GPT MCP server | 2025-2026 兴起 | 灵活但工作量大 |

### 10.4 落地的关键环节

1. **语义模型要详细**（description · synonyms · sample_queries）
   - LLM 靠这些理解业务词汇
   - `description: "本周 GMV 定义是 dt >= date_trunc('week', current_date)"`

2. **Few-shot examples** 存在 SL 里
   - "GMV 按地区" → `metric=gmv, dimension=region`
   - LLM 调用时把示例作为 context

3. **错误回流**
   - 用户标"这个不对" → 加到 few-shot 或 synonyms
   - 指标被高频问 → 确认定义并加详细 description

4. **模糊查询处理**
   - "销量" 是 GMV 还是 order_count？LLM 先反问确认
   - SL 要提供**候选 metric** 能力（LLM 判定 "可能是这几个"）

5. **输出格式**
   - 数字 + 语义层 query plan（可审）+ 自然语言解释
   - 可视化建议（chart type）可由 LLM 生成 Vega-Lite

### 10.5 陷阱

- **把 SL 当 LLM schema 但 SL 本身稀薄** · metric/description 糊弄 · LLM 效果和直接查 DB 无差别
- **绕过 SL 直接让 LLM 写 SQL** · 失去口径治理 · 失去权限保护 · 2026 大多数失败案例是这原因
- **Schema 膨胀到 LLM 塞不下** · 即使 SL 也需要 RAG 检索相关 entity · 不能全塞 prompt
- **一次性上线** · LLM × SL 必须迭代 · feedback loop 是生产关键
- **没有降级** · LLM 不确定时不要强编 SQL · 反问 + 候选 + 引导到人工

详见 [BI × LLM 专题](bi-plus-llm.md)。

## 11. 指标 lineage · 可信指标的血缘

### 11.1 什么是指标 lineage

- **上游 lineage** · 这个指标依赖哪些 dbt model / warehouse table / 原始字段
- **下游 lineage** · 这个指标被哪些 dashboard / report / API / downstream metric 使用
- **变更影响** · 改了 `gmv` 定义 · 哪些消费者受影响

### 11.2 为什么 2026 重要

- **合规** · 财报数字怎么算的 · 审计要溯源
- **可信** · 业务"这个数字我信不信" · lineage 是证据
- **LLM × SL** · LLM 答 "GMV 怎么算" 要有 lineage 给它看 · 不能瞎编
- **变更管理** · 改指标定义前必须知道影响面

### 11.3 工具

- **dbt** · `dbt docs` 生成的 DAG 是基础 lineage · 但到 metric 粒度要 SL
- **dbt Semantic Layer + dbt docs** · metric lineage 从 2024 起逐步完善
- **Apache Atlas / DataHub / OpenMetadata** · 企业 catalog · 加上 metric lineage 能力
- **Unity Catalog** · Databricks 生态的 lineage 源
- **Collibra / Alation** · 商业 data catalog · 偏治理

### 11.4 实践建议

- **把 metric 当一等公民** · 不只是 SQL 片段 · 是有 owner/stakeholder/变更历史的资产
- **变更走 PR** · metric 定义改动必须 code review
- **下游通知** · 改了 GMV 定义 · 自动 notify 所有使用方
- **deprecation 流程** · 老指标不是删 · 是标 deprecated · 设下线日期 · 通知消费者

## 12. 陷阱与反模式

- **指标漫无边际**：500+ 指标没 owner → 失去治理
- **语义层当 ETL 用**：复杂转换应该在 dbt models 里，不在 Semantic Layer
- **Pre-agg 没配**：每查都走底表 → 语义层反而慢
- **组织没共识就强推**：技术上线但业务继续各自算
- **废弃指标不 deprecate**：老指标堆积成山
- **跨团队共享 entity 定义不协调**：同一个 "user_id" 意义不同

## 13. 延伸阅读

- **[dbt Semantic Layer 文档](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)**
- **[MetricFlow（OSS）](https://github.com/dbt-labs/metricflow)**
- **[Cube 官方](https://cube.dev/)**
- **[Looker LookML 文档](https://cloud.google.com/looker/docs/what-is-lookml)**
- **[Malloy](https://github.com/malloydata/malloy)**
- **[Airbnb Minerva 博客](https://medium.com/airbnb-engineering/)**
- **[Databricks AI/BI Genie (GA)](https://www.databricks.com/blog/aibi-genie-now-generally-available)**
- **[Snowflake Cortex Analyst 文档](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)**
- **[dbt MCP 服务器](https://github.com/dbt-labs/dbt-mcp)** · LLM × dbt SL
- **[Malloy 官方](https://www.malloydata.dev/)**
- *Headless BI movement* —— Benn Stancil / Tristan Handy 等人推动

## 相关

- [OLAP 建模](olap-modeling.md) —— 语义层建在维度建模之上
- [物化视图](materialized-view.md) · [查询加速](query-acceleration.md)
- [BI × LLM](bi-plus-llm.md) · LLM 时代的 BI 入口 · SL 是其知识抓手
- [Text-to-SQL 平台](../scenarios/text-to-sql-platform.md) · 走 SL API 路径的 Text-to-SQL
- [MCP](../ai-workloads/mcp.md) · dbt SL 通过 MCP 暴露给 LLM
- [Modern Data Stack](../frontier/modern-data-stack.md) —— Semantic Layer 是其中一环
- [BI on Lake 场景](../scenarios/bi-on-lake.md)
