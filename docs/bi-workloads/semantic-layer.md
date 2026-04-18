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
    - **主流产品**：**dbt Semantic Layer**（2023 收购 Transform） · **Cube** · LookML（Looker 专属）· **Malloy**（Google 实验）
    - **核心抽象**：entities · measures · dimensions · time_spine
    - **落地成熟度**：**2024 才算真正生产可用**；早期（2020-2022）大多停在 POC
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

### Malloy（Google 实验）

**定位**：Google 开源的新语言（非 SQL），2022+。

**特点**：
- 优雅的组合式查询
- 仍是实验阶段
- 社区小

### 其他

- **MetricFlow**（已合并入 dbt）
- **Transform**（已被 dbt 收购）
- **AtScale**（商业 OLAP + 语义层）
- **Minerva**（Airbnb 内部）· **Metric Flow**（Uber）· **Amberfl**（LinkedIn）—— 大厂内部

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

### 成熟度评估

- **dbt Semantic Layer**：2023 发布后经历了一轮整合痛期，**2024 下半年起算生产可用**
- **Cube**：已稳定，中小规模首选
- **LookML**：老牌稳定，但**Looker 本身在 Google 内部优先级降低**
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

## 10. 陷阱与反模式

- **指标漫无边际**：500+ 指标没 owner → 失去治理
- **语义层当 ETL 用**：复杂转换应该在 dbt models 里，不在 Semantic Layer
- **Pre-agg 没配**：每查都走底表 → 语义层反而慢
- **组织没共识就强推**：技术上线但业务继续各自算
- **废弃指标不 deprecate**：老指标堆积成山
- **跨团队共享 entity 定义不协调**：同一个 "user_id" 意义不同

## 11. 延伸阅读

- **[dbt Semantic Layer 文档](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)**
- **[MetricFlow（OSS）](https://github.com/dbt-labs/metricflow)**
- **[Cube 官方](https://cube.dev/)**
- **[Looker LookML 文档](https://cloud.google.com/looker/docs/what-is-lookml)**
- **[Malloy](https://github.com/malloydata/malloy)**
- **[Airbnb Minerva 博客](https://medium.com/airbnb-engineering/)**
- *Headless BI movement* —— Benn Stancil / Tristan Handy 等人推动

## 相关

- [OLAP 建模](olap-modeling.md) —— 语义层建在维度建模之上
- [物化视图](materialized-view.md) · [查询加速](query-acceleration.md)
- [Modern Data Stack](../frontier/modern-data-stack.md) —— Semantic Layer 是其中一环
- [BI on Lake 场景](../scenarios/bi-on-lake.md)
