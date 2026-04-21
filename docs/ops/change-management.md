---
title: 变更管理 · CI/CD · Schema Evolution · 回滚
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: dbt 1.8+ · Dagster · Airflow · GitOps · Feature Flags · Schema Registry · 2024-2026 实践
tags: [ops, change-management, ci-cd, schema-evolution, rollback, feature-flag]
aliases: [CI/CD for Data, Change Management, 变更流程]
related: [migration-playbook, production-checklist, incident-management, data-governance, data-quality-for-ml]
systems: [dbt, dagster, airflow, launchdarkly, unleash]
status: stable
---

# 变更管理 · Change Management

!!! tip "一句话定位"
    数据 pipeline + ML 模型 + AI 应用的**变更工程化** —— **CI/CD + Schema evolution + Breaking change + 回滚 + Feature Flag** 五件事合一。变更管理做不好 · 新版本上线事故是必然 · 不是概率。

!!! warning "章节分工声明"
    - **本页**：数据 / ML / AI 的**变更工程化流程**
    - **Data Contract** 机制 → [ml-infra/data-quality-for-ml](../ml-infra/data-quality-for-ml.md) §2 Data Contract canonical
    - **Schema Evolution 机制**（Iceberg / Paimon 支持）→ [lakehouse/schema-evolution](../lakehouse/schema-evolution.md)
    - **迁移**（不同系统间搬迁）→ [migration-playbook](migration-playbook.md)
    - **Canary / Rollback for ML / AI** → [ml-infra/model-serving §Rollback runbook](../ml-infra/model-serving.md) · [ml-infra/model-monitoring](../ml-infra/model-monitoring.md)

!!! abstract "TL;DR"
    - **五件事一体**：CI/CD · Schema evolution · Breaking change policy · 回滚机制 · Feature flag
    - **CI/CD 原则**：PR 触发 · 自动测试 · 灰度发布 · 可回滚
    - **Schema 变更分类**：additive（可兼容）· destructive（不兼容）· semantic（语义变）· 各有流程
    - **Breaking change 30 天通知**是 Data Contract 的核心承诺
    - **Feature Flag** 让"变更即发布"· 但"启用"是独立控制

## 1. CI/CD for Data Pipelines

### 1.1 dbt CI/CD 典型流程

```mermaid
flowchart LR
  dev[开发者改 dbt model] --> pr[PR 触发]
  pr --> slim[dbt Slim CI<br/>只跑变更模型]
  slim --> test[dbt test 质量检查]
  test --> compare[数据 diff<br/>vs 生产]
  compare --> review[Code Review]
  review --> merge[Merge main]
  merge --> deploy[部署到 prod]
  deploy --> ctest[生产冒烟测试]
```

**关键组件**：
- **dbt Slim CI**：只跑变更影响的模型 · 不全量跑
- **dbt test**：数据质量断言（unique / not_null / relationships / custom）
- **Data Diff**（Datafold / dbt-audit-helper）：新版 SQL vs 生产 · 对比结果差异

### 1.2 Dagster / Airflow CI/CD

| 工具 | CI/CD 实践 |
|---|---|
| **Dagster** | Asset-based · asset diff CI · 自动化 deploy |
| **Airflow** | DAG 版本化 · CI 跑 dry-run · sync 到生产 Airflow |
| **Prefect** | Flow 部署 · cloud + OSS 双轨 |

### 1.3 ML Pipeline CI/CD

- **训练代码 CI**：code review · unit test · 小样本训练 smoke test
- **模型 CI**：数据质量 gate → 训练 → 离线评估 → 注册 candidate alias → Shadow → Canary → champion
- 详见 [ml-infra/model-registry](../ml-infra/model-registry.md) §审批工作流 · [ml-infra/ml-evaluation](../ml-infra/ml-evaluation.md)

### 1.4 AI 应用 CI/CD

- **Prompt 版本控制**：Registry 存 · 每次调用记 prompt_version（见 [ai-workloads/prompt-management](../ai-workloads/prompt-management.md)）
- **评估集 gate**：Prompt 改动必须过评估集（RAGAS / TruLens / DeepEval）· 详见 [ai-workloads/rag-evaluation](../ai-workloads/rag-evaluation.md)
- **灰度**：Prompt 新版先 5% 流量 · 监控质量 + token 成本

## 2. Schema Evolution 流程

### 2.1 变更分类

| 变更类型 | 例子 | 兼容性 | 处理流程 |
|---|---|---|---|
| **Additive**（加字段）| 加 nullable 列 · 加新表 | ✅ 向后兼容 | 直接发 · 下游自动 ignore |
| **Lenient Additive**（加 required 列）| 加 NOT NULL 列 · 带默认值 | ⚠️ 只对新数据要求 | 必须有 default · 否则历史数据破 |
| **Destructive**（删 / 改 type）| 删列 · 改列类型（narrowing）| ❌ 不兼容 | Breaking change 流程（§2.2） |
| **Semantic**（改语义）| `amount` 单位从分变成元 | ❌ 最危险 · schema 不变语义变 | 必须**加新列**（`amount_cents`）· 不改旧列 |

### 2.2 Breaking Change 流程

按 Data Contract（详见 [ml-infra/data-quality-for-ml §2 Data Contract](../ml-infra/data-quality-for-ml.md)）·**破坏性变更标准流程**：

```
1. 提前 30 天通知下游（Slack / 邮件 / 工单）
2. 新旧版本并存期（双写新旧列 · 或新旧表）
3. 下游逐个切过去
4. 全部切完 · 旧版本弃用（先标 deprecated · 后删）
5. 记录变更（ADR / CHANGELOG / Data Contract 版本升）
```

**不要**：
- 偷偷删列（下游炸）
- 偷偷改语义（下游数据错）
- 通知期不够（下游没时间迁）

### 2.3 Iceberg / Paimon 的 Schema Evolution 支持

湖表格式本身对 schema 演化友好（列 ID 机制）· 但**语义变更**不能靠表格式解决：

- **加列 / 删列 / 改列名**：Iceberg / Paimon 原生支持（见 [lakehouse/schema-evolution](../lakehouse/schema-evolution.md)）
- **改类型**（int → bigint）：部分支持（widening OK · narrowing 不支持）
- **改语义**：表格式无法检测 · 必须**加新列** + 流程管控

## 3. 发布策略

### 3.1 灰度发布（Canary / Progressive Delivery）

数据 / ML / AI 的灰度：

| 场景 | 灰度方式 |
|---|---|
| **dbt model 改动** | Shadow 表 + 对比 · 切换 view |
| **ML 模型新版** | Alias champion/challenger 流量切分（见 [ml-infra/model-serving](../ml-infra/model-serving.md)）|
| **LLM Prompt 改** | 5% → 25% → 50% → 100% · 看质量 + 成本 |
| **数据源切换** | 双写 → 双读对比 → 切读 → 停旧写 |

**自动回滚触发**：业务 KPI 下降 / 错误率上升 / 延迟退化 / fairness gap 扩大。

### 3.2 Blue / Green

适合**模型服务**和**API**：
- 蓝环境（现行）+ 绿环境（新版）· 流量瞬时切换
- 回滚：流量切回蓝
- 代价：双倍资源（短暂）

### 3.3 Feature Flag（2024-2026 主流实践）

**"变更即发布 · 启用独立控制"**：

- **LaunchDarkly / Unleash / Flagsmith** · Feature Flag 商业 + OSS
- 代码部署但功能**默认关闭** · 通过 flag 打开
- 某租户 / 某用户先开
- 出问题 · flag 关 · 不回滚代码

**数据场景的 Feature Flag**：
- 新的 ML 模型版本先对 5% 用户开
- Agent 的新 Tool 对内部用户先试
- LLM 新 Prompt 先对某租户打开

## 4. 回滚机制

### 4.1 数据回滚

- **Iceberg / Paimon Time Travel**：`CALL rollback_to_snapshot('t', SNAPSHOT_ID)`
- 前提：snapshot 未被 `expire_snapshots` 清掉
- 保留 30+ 天 snapshot 给关键表
- 详见 [disaster-recovery](disaster-recovery.md) §误操作

### 4.2 ML 模型回滚

```python
# MLflow 2.9+ alias 切换 · 秒级回滚
client.set_registered_model_alias(
    name="model_name", alias="champion", version=PREVIOUS_VERSION
)
# serving 侧热加载或蓝绿 · 详见 ml-infra/model-serving §Rollback runbook
```

### 4.3 AI 应用回滚

- **Prompt 回滚**：Registry 里切换到上一版本
- **RAG 索引回滚**：保留旧索引 · alias 切换
- **Agent 流量回滚**：路由到旧版

### 4.4 MTTR 目标

| 场景 | 目标 MTTR |
|---|---|
| P0 数据事故 | < 1 小时 |
| ML 模型回滚 | < 5 分钟 |
| AI Prompt 回滚 | < 1 分钟 |
| Schema 错误回滚 | < 15 分钟（Iceberg rollback） |

## 5. Feature Flag 深度用法

### 5.1 数据平台常见 Flag

- **新 ML 模型开启**（per-user / per-tenant）
- **新 Agent Tool 启用**（内部先试）
- **新 LLM 模型路由**（LLM Gateway 侧）
- **新 Data Pipeline 启用**（双栈过渡）
- **实验性功能**（beta 用户）

### 5.2 Flag 治理

**过期 Flag 清理是大坑**：
- Flag 用完要及时删（不然代码路径膨胀）
- 每季度 Flag review
- **Flag 债务**（Flag 超过 6 月未删 · 需处理）

## 6. 最小可用清单

团队上线变更管理至少要：

- [ ] PR 触发 CI（dbt slim CI / 代码测试）
- [ ] 数据质量 gate（关键模型有 dbt tests）
- [ ] Schema 变更走 review（不允许偷偷改）
- [ ] Breaking change 有 notice 流程
- [ ] ML 模型有 Alias + Shadow + Canary
- [ ] 关键表 snapshot 保留 30+ 天
- [ ] Feature Flag 用在高风险变更
- [ ] 每次生产发布有回滚 runbook

## 7. 陷阱 · 反模式

- **PR 不跑 CI · 人眼 review** · 质量靠运气
- **Schema 偷偷加 required 列** · 下游写入失败
- **Breaking change 没通知** · 下游团队爆
- **ML 模型直接替换 champion · 无 Shadow** · 坏模型上线
- **Feature Flag 从不清理** · 代码分支爆炸
- **回滚 runbook 只在个别脑子里** · 事故时没人会
- **变更没 changelog** · 3 月后不知道做过什么

## 8. 和其他章节

- [migration-playbook](migration-playbook.md) · 跨系统迁移
- [incident-management](incident-management.md) · 变更引起事故的响应
- [production-checklist](production-checklist.md) · 上线前变更准备
- [data-governance](data-governance.md) · Data Contract 治理
- [ml-infra/data-quality-for-ml](../ml-infra/data-quality-for-ml.md) · Data Contract canonical
- [ml-infra/model-registry](../ml-infra/model-registry.md) · 模型版本管理
- [ml-infra/model-serving](../ml-infra/model-serving.md) · Shadow/Canary/Rollback
- [lakehouse/schema-evolution](../lakehouse/schema-evolution.md) · 湖表 schema 演化
- [ai-workloads/prompt-management](../ai-workloads/prompt-management.md) · Prompt 版本管理

## 9. 延伸阅读

- *Database Reliability Engineering*（Campbell / Majors）
- *Designing Data-Intensive Applications* · Ch 4 Encoding and Evolution
- dbt Continuous Integration · <https://docs.getdbt.com/docs/deploy/continuous-integration>
- LaunchDarkly · *Feature Management* 博客系列
- Data Contracts · Andrew Jones 博客 + 书
