---
title: 调度 / Orchestration 横比 · Airflow / Dagster / Prefect / DolphinScheduler
type: comparison
depth: 进阶
tags: [comparison, orchestration, airflow, dagster, prefect]
related: [modern-data-stack]
status: stable
last_reviewed: 2026-04-22
---

# 调度 / Orchestration 横比

!!! tip "一句话回答"
    **Airflow** 是生态最广的老牌选择，**Dagster** 是"数据资产为中心"的现代派，**Prefect** 是 Python-first 的轻量派，**DolphinScheduler** 是国产开源代表。对新项目 **Dagster > Airflow > Prefect**；老项目多数还是 **Airflow**。

!!! abstract "TL;DR"
    - **Airflow**：老牌 · 生态最广 · DAG 为中心 · 相对陈旧 UX
    - **Dagster**：现代 · 资产为中心 · 类型安全 · **新项目首选**
    - **Prefect**：Python 原生 · 简洁 · 支持动态 workflow
    - **DolphinScheduler**：Apache 开源 · 可视化 · 国产生态
    - **SaaS**：Astronomer（Airflow）· Prefect Cloud · Dagster Cloud

## 1. 调度系统解决什么

### 核心需求

- **依赖管理**：A 完成才能跑 B
- **调度触发**：定时 / 事件 / 外部
- **失败处理**：重试 / 告警 / 降级
- **可观测性**：UI / 日志 / 监控
- **参数化**：同一 workflow 跑不同参数
- **Backfill**：补跑历史数据
- **资源调度**：控制并发 / Pool

### 不要混淆的概念

- **ETL 工具**（Fivetran / Airbyte）≠ Orchestrator
- **dbt** 做 SQL 转换 ≠ Orchestrator
- **K8s CronJob** 是最简单的定时，不算 Orchestrator

Orchestrator 是**上层协调**：调 dbt、调 Spark、调 Fivetran、监控结果。

---

## 2. 四家深度

### Apache Airflow

**出身**：Airbnb 2014 开源 → Apache 顶级项目。

**核心概念**：**DAG + Task + Operator + Sensor**

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG("etl", start_date=datetime(2024,1,1), schedule="@daily") as dag:
    extract = PythonOperator(task_id="extract", python_callable=extract_fn)
    transform = PythonOperator(task_id="transform", python_callable=transform_fn)
    extract >> transform
```

**优**：
- 生态最广（Provider packages 覆盖几乎所有数据源）
- 社区大、文档多
- Apache 背书、稳定
- 商业支持：Astronomer / AWS MWAA / GCP Cloud Composer

**劣**：
- **UX 相对陈旧**
- **动态 DAG 支持弱**（需要 TaskFlow API）
- **资产概念弱**（仅任务）
- Python 版本升级慢

**适合**：已有 Airflow、生态依赖重、团队熟练。

### Dagster

**出身**：Elementl 2018+ 开源（现 Dagster Labs）。

**核心理念**：**数据资产（Software-Defined Asset）为中心**。

```python
import dagster as dg

@dg.asset
def raw_orders() -> pl.DataFrame:
    return pl.read_parquet("s3://lake/orders/")

@dg.asset
def orders_cleaned(raw_orders: pl.DataFrame) -> pl.DataFrame:
    return raw_orders.filter(pl.col("status") == "completed")

@dg.asset
def orders_aggregated(orders_cleaned: pl.DataFrame) -> pl.DataFrame:
    return orders_cleaned.group_by("region").sum()
```

**差异化**：
- 每个 "asset" 表示**一个数据产物**（表 / 文件 / 模型）
- **依赖关系从资产中推导**，而非显式 DAG
- **类型化 IO**
- **Partition 天然支持**（按日期 / 按租户）
- 内置 **软删除 Sensors, 资产 Lineage, 质量检查**

**优**：
- 现代化 UX（UI 最好）
- **Asset-centric** 对数据团队更自然
- 与 dbt / Snowflake / Databricks 深度集成
- 类型安全
- 快速成长的社区

**劣**：
- 生态比 Airflow 小（但在快速补齐）
- 迁移成本（和 Airflow 概念不完全对应）

**适合**：**新项目 · 数据团队 · 资产为中心的工作流**。

### Prefect

**出身**：Prefect Technologies 2018 开源。

**核心理念**：**Python-first + 动态 workflow**。

```python
from prefect import flow, task

@task
def extract(): ...

@task
def transform(x): ...

@flow
def etl():
    data = extract()
    for chunk in split(data):
        transform.submit(chunk)
```

**优**：
- Python 原生（无 DSL）
- **动态 workflow**：flow 里可以 if/for/while
- 托管 Prefect Cloud 体验好
- 轻量

**劣**：
- 生态比 Airflow / Dagster 小
- 大规模企业使用案例少

**适合**：Python 数据工程师、中小团队、动态 workflow 需求。

### Apache DolphinScheduler

**出身**：易观 2017 开源 → Apache 顶级项目。

**核心**：**可视化拖拽 + 分布式 + 高可用**。

**优**：
- **UI 可视化**强（国产产品的强项）
- 支持多种任务类型（Shell / Python / Spark / Flink / DataX）
- 中文社区活跃
- 分布式架构（Master + Worker 高可用）

**劣**：
- 海外生态薄
- Code-first 体验比 Airflow / Dagster 弱

**适合**：国内团队、重可视化、非 Python 为主。

---

## 3. 能力矩阵

| 能力 | Airflow | Dagster | Prefect | DolphinScheduler |
|---|---|---|---|---|
| DAG 定义 | Python | Asset-based Python | Python | UI + Script |
| 动态 workflow | 弱 | 中 | **强** | 弱 |
| 资产血缘 | 弱 | **强** | 中 | 弱 |
| 类型安全 | ❌ | ✅ | ✅ | ❌ |
| UI | 老旧 | **最好** | 现代 | 可视化强 |
| 社区 | 最大 | 中快速涨 | 中 | 国内大 |
| 商业托管 | Astronomer / AWS MWAA / GCP CC | Dagster+ | Prefect Cloud | 各家云厂 |
| K8s-native | 要额外组件 | ✅ | ✅ | 要配 |
| dbt 集成 | 有 provider | **原生深度** | 有 | 有 |
| Spark / Flink | 有 operator | ✅ | ✅ | ✅ |
| 学习曲线 | 中 | 中 | 低 | 低 |

---

## 4. 选型决策

### 按项目阶段

| 阶段 | 推荐 |
|---|---|
| **新项目 · 2024+** | **Dagster** |
| **已有 Airflow 栈** | 继续 Airflow（迁移成本 > 收益）|
| **小团队 / 快速起步** | Prefect 或 Dagster |
| **国内企业 · 可视化重** | DolphinScheduler |
| **数据资产为中心** | Dagster |
| **大量遗留 Oozie / Hive** | DolphinScheduler 或 Airflow |

### 按功能需求

| 需求 | 推荐 |
|---|---|
| 资产血缘 | **Dagster** |
| 动态 workflow（运行时生成 DAG）| **Prefect** |
| 最大生态 / 最多 Provider | **Airflow** |
| 国产化 / 可视化 UI | **DolphinScheduler** |
| K8s 原生 | Dagster / Prefect |

---

## 5. 和 dbt 的协作

dbt 是 T（SQL 转换），Orchestrator 是"什么时候跑 dbt、dbt 跑完做什么"。

### Airflow + dbt

```python
from airflow_dbt_python.operators.dbt import DbtRunOperator

dbt_run = DbtRunOperator(task_id="dbt_run", project_dir="/dbt", profiles_dir="/dbt")
```

或用 **Cosmos**（Astronomer 出品）自动把 dbt models 展开成 Airflow tasks。

### Dagster + dbt

```python
from dagster_dbt import DbtCliResource, dbt_assets

@dbt_assets(manifest="target/manifest.json")
def my_dbt_assets(context, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
```

每个 dbt model 自动成为一个 Dagster asset，血缘自然打通。**这是 Dagster 最亮的集成**。

---

## 6. 部署 / 运营

### 自建

| 方案 | 典型规格 |
|---|---|
| Airflow on K8s (KubernetesExecutor) | Scheduler + Worker + Postgres |
| Dagster on K8s | Daemon + Webserver + DB |
| Prefect on K8s | Server + Agent + DB |

### SaaS

| 产品 | 特点 |
|---|---|
| **Astronomer** | Airflow 最大托管商 |
| **Dagster+** | Dagster 官方 |
| **Prefect Cloud** | Prefect 官方 |
| **AWS MWAA** | AWS 托管 Airflow |
| **GCP Cloud Composer** | GCP 托管 Airflow |

### 成本参考（中型团队，50 DAG）

| 方案 | 月成本 |
|---|---|
| 自建 | $500-2000（EC2） + 工程师维护 |
| Astronomer | $2000-10000 |
| AWS MWAA | $500-3000 |

---

## 7. 陷阱 · 通用

- **把 Orchestrator 当 ETL 工具**：调度器不该内置复杂 T 逻辑
- **DAG 跑得太细**：每个 SQL 一个 task，Airflow 调度开销比任务还贵
- **Airflow 老版本**：Airflow 1.x 到 2.x / 3.x 升级痛苦，尽早规划
- **Dagster 当 Airflow 用**：没利用 asset-based 核心特性
- **无测试**：DAG 代码没单测 / 集成测试
- **没 SLA 告警**：关键表 4 小时没更新才发现
- **Mocking 不够**：本地跑不起来、只能上线后发现问题

---

## 8. 延伸阅读

- **[Airflow 官方](https://airflow.apache.org/)** · **[Dagster 官方](https://dagster.io/)** · **[Prefect 官方](https://www.prefect.io/)** · **[DolphinScheduler](https://dolphinscheduler.apache.org/)**
- **[*Data Pipelines Pocket Reference* (O'Reilly)](https://www.oreilly.com/library/view/data-pipelines-pocket/9781492087823/)**
- **[Astronomer Academy](https://academy.astronomer.io/)** —— Airflow 学习
- **[Dagster University](https://courses.dagster.io/)** —— 免费课
- Benn Stancil / dbt 社区博客（Orchestration 对比）

## 相关

- [Modern Data Stack](../modern-data-stack.md) —— Orchestration 是其中一环
- [Kafka Ingestion](../pipelines/kafka-ingestion.md) · [Bulk Loading](../pipelines/bulk-loading.md)
- [编排系统概览](../pipelines/orchestration.md)
