---
title: 编排系统概览
applies_to: "2024-2026 主流"
type: concept
depth: 进阶
level: A
last_reviewed: 2026-04-20
prerequisites: []
tags: [pipelines, orchestration, airflow, dagster]
related: [streaming-ingestion, embedding-pipelines]
systems: [airflow, dagster, prefect, flyte, temporal]
status: stable
---

# 编排系统概览

!!! tip "一句话理解"
    把一组"任务 + 依赖 + 时间表"变成**可调度、可重跑、可观测**的数据管线。Airflow 是事实标准；Dagster / Prefect / Flyte / Temporal 各有亮点。湖仓场景里**选一个足够**，不要混用多个。

!!! abstract "TL;DR"
    - **Airflow**：大而全、生态无敌、运维重
    - **Dagster**：Asset-centric 模型与湖仓最贴合
    - **Prefect**：开发体验好、Python 原生
    - **Flyte / Argo Workflows**：ML / K8s 原生
    - **Temporal**：流程编排（workflow），和数据管线略不同定位
    - **选型基于三维度**：**现有技术栈**（Spark/Flink 栈偏 Airflow · K8s 原生偏 Argo）· **ML 比例**（ML 重选 Dagster / Flyte 的 asset / type 模型）· **团队 Python 成熟度**（Prefect 上手最快）

## 为什么要编排系统

湖仓里一条"简单"管线是：

```
每日 02:00：
  1. 上游业务库 CDC 同步完毕 → 触发
  2. Spark 跑 DWD 层作业
  3. 成功后跑 DWS 层
  4. 跑数据质量检查
  5. 失败则 Slack 告警、成功则刷物化视图
  6. 记 run id + 版本到 Catalog
```

自己 cron + shell 维护 = 灾难。编排系统解决：

- **DAG 表达**（任务依赖）
- **重试 / 失败告警**
- **回填**（补跑某天）
- **观测**（每次 run 的状态、时长、日志）
- **资源管理**（限并发、限队列）

## 主流选手

### Airflow（大而全的事实标准）

```python
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

with DAG("daily_dwd", schedule="0 2 * * *") as dag:
    ods_to_dwd = SparkSubmitOperator(
        task_id="ods_to_dwd",
        application="s3://jobs/dwd_build.py",
    )
    dwd_to_dws = SparkSubmitOperator(
        task_id="dwd_to_dws",
        application="s3://jobs/dws_build.py",
    )
    ods_to_dwd >> dwd_to_dws
```

**优点**：
- 生态最全（Spark / Flink / dbt / 云厂商 Operator 几百个）
- 运维稳定、文档丰富
- 社区大

**缺点**：
- Web UI 重、学习曲线陡
- Task 模型不直接表达"数据资产"
- 调度器 / 执行器 / DB 多组件运维
- 升级版本容易出坑

**适合**：中大型团队、已有 Spark / Hadoop 栈、不想冒险。

### Dagster（Asset-centric）

```python
from dagster import asset, AssetIn

@asset
def raw_orders(context):
    return spark.read.table("ods.orders")

@asset(ins={"orders": AssetIn("raw_orders")})
def dwd_orders(orders):
    return orders.filter("status = 'valid'")
```

**核心差异**：Dagster 的一等公民是**资产（Asset）**，不是任务（Task）。湖仓里每张表就是一个 Asset，Asset 之间的依赖 = 数据血缘。

**优点**：
- 资产模型天然贴合湖仓
- 自带物化追踪 + 血缘
- 开发体验好（本地跑、typed I/O）
- 和 dbt 集成深

**缺点**：
- 社区比 Airflow 小
- Task-centric 思维的团队要转变

**适合**：数据平台团队、dbt 重度用户、ML 管线。

### Prefect

**优点**：Python 原生、装饰器 API 最轻；云托管版省心。
**缺点**：生态不如 Airflow 广。

### Flyte / Argo Workflows

**优点**：K8s 原生、ML 训练管线友好、版本化。
**缺点**：对纯数据 ETL 重度场景略重。

### Temporal

**定位不同**：面向**业务流程编排**（订单状态流转、长事务），不是纯数据管线。湖仓里少见，除非业务流程里嵌数据作业。

## 推荐选择矩阵

| 团队画像 | 首选 | 备选 |
| --- | --- | --- |
| 大型数据平台，已有 Spark / Flink | **Airflow** | Dagster |
| 数据 + dbt 重度，追求资产模型 | **Dagster** | Prefect |
| ML / 训练管线为主 | **Flyte** | Dagster |
| K8s 原生、轻量 | **Argo Workflows** | Prefect |
| 小团队、Python 快速迭代 | **Prefect** | Dagster |

## 在湖仓场景的几件通用最佳实践

### 1. 作业幂等

同一 run 重跑产出相同结果。靠：
- 按 partition 覆盖而不是追加
- 利用 Iceberg `REPLACE PARTITION` / `MERGE INTO`
- 写入带 `run_id` 标注

### 2. 作业版本化

每次作业代码要能追溯到 git commit + 作业参数快照。编排系统都支持 `Variables` / `Configs` 版本。

### 3. 告警只告"值得告的"

- 失败 —— 必告
- 延迟 > SLA —— 必告
- 数据量异常 —— 必告
- "成功"不要告

### 4. 回填策略 · 批 vs 流 的编排职责矩阵

**核心原则**：**批作业编排系统管 · 流作业流引擎管**——两类回填手段不同 · 不能混用。

| 维度 | 批作业（DWD/DWS 每日构建） | 流作业（Flink CDC / Kafka 入湖） |
|---|---|---|
| **谁管生命周期** | 编排系统（Airflow / Dagster）| 流引擎（Flink · Spark Streaming）|
| **回填机制** | 编排系统按 `partition_date` / `run_id` 重跑 | **流引擎 savepoint 回退 + source offset 重置**（见 [pipeline-resilience · Backfill](pipeline-resilience.md)）|
| **错误做法** | 把批作业拆成 cron | 用编排系统"重跑"流作业——**产生双写**（原作业 + 回填作业并行）· 常见事故源 |
| **限并发** | Airflow `max_active_runs`（其他系统有等价参数）| 流作业本身单实例 · 无需额外限流 |

### 5. 和 Catalog 集成

每次作业成功：
- 更新 Catalog 里目标表的 `last_refreshed_ts`
- 触发下游 MV 刷新
- 写入血缘事件（OpenLineage）

## 反模式

- **一个 DAG 做所有事** —— 巨大 DAG 维护噩梦；按域拆
- **用编排系统跑流式作业** —— 流式作业靠流式引擎自己管（Flink / Spark Streaming），编排只负责启停
- **不做幂等** —— 重跑产生重复
- **告警全发钉钉群** —— 钉钉群被告警淹没 = 没人看
- **多个编排系统并存** —— 债务指数增长

## 相关

- [Kafka 到湖](kafka-ingestion.md)
- [Bulk Loading](bulk-loading.md)
- [Embedding 流水线](../ml-infra/embedding-pipelines.md)
- [可观测性](../ops/observability.md)
- [数据治理](../ops/data-governance.md)

## 延伸阅读

- Airflow docs: <https://airflow.apache.org/docs/>
- Dagster: <https://dagster.io/>
- *Fundamentals of Data Engineering*（第 2-3 章编排部分）
- Prefect: <https://www.prefect.io/> · Flyte: <https://flyte.org/> · Argo Workflows: <https://argoproj.github.io/workflows/> · Temporal: <https://temporal.io/>
