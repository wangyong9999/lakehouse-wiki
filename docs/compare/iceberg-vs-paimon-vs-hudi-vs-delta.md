---
title: Iceberg vs Paimon vs Hudi vs Delta · 四大湖表格式选型
type: comparison
depth: 资深
level: A
last_reviewed: 2026-04-18
applies_to: Iceberg 1.10+/v3 稳定 · Paimon 1.4+ · Hudi 1.0.2+ · Delta 4.0+
tags: [comparison, lakehouse, table-format]
subjects: [iceberg, paimon, hudi, delta-lake]
status: stable
---

# Iceberg vs Paimon vs Hudi vs Delta

!!! tip "读完能回答的选型问题"
    四大湖表格式，我在 **BI 为主 / 流式 upsert 为主 / Databricks 生态 / 多引擎开放** 四种场景下到底该选哪个？**2024-2025 年生态格局有重大变化**（Databricks 收购 Tabular、Paimon Apache 毕业、Uniform 生态），需要重新审视。

!!! abstract "TL;DR"
    - **Iceberg** = 多引擎中立 · REST Catalog 生态成熟 · 2024+ 事实上的"行业通用协议"
    - **Paimon** = Flink + 流式 upsert 原生 · 2023 Apache 毕业 · 国内生态活跃
    - **Hudi** = Spark 生态 + Incremental Query 历史强 · Uber 规模化验证 · 新项目采用放缓
    - **Delta Lake** = Databricks 深度集成 · Uniform 向 Iceberg 靠拢 · 2024 收购 Tabular 是关键信号
    - **2026 主流共识**：**新项目优先 Iceberg** + 流场景配 Paimon；已有栈渐进演化

## 对比维度总表

| 维度 | Iceberg | Paimon | Hudi | Delta |
|---|---|---|---|---|
| **主要生态** | 多引擎中立 | Flink 中心 | Spark 中心 | Databricks 中心 |
| **批分析** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **流式 upsert** | ⭐⭐⭐（v2 delete file）| ⭐⭐⭐⭐⭐（LSM 原生）| ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **CDC / Changelog** | 增量读（snapshot diff）| **原生 4 种 changelog producer** | Incremental Query | CDF（Change Data Feed）|
| **架构思路** | Manifest + Snapshot | LSM + Manifest | Timeline + CoW/MoR | 事务日志 + checkpoint |
| **Schema Evolution** | ⭐⭐⭐⭐⭐（列 ID）| ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Row-Level Delete** | v2 Position + Equality · v3 Deletion Vector | Delete File | CoW 重写 / MoR log | v3+ Deletion Vectors |
| **Catalog 生态** | **最多**（HMS/REST/Nessie/Unity/Polaris/Glue）| Flink / Hive / REST | Hive / Glue | Databricks UC / HMS |
| **多引擎开放** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐（Flink/Spark/Trino OK）| ⭐⭐⭐ | ⭐⭐⭐（Uniform 改善中）|
| **社区治理** | Apache · Netflix/Apple/LinkedIn 共治 | Apache · 阿里主导 | Apache · Onehouse 主推 | LF AI · **Databricks 单一主导** |
| **AI / 多模扩展** | 高（Puffin + Lance 融合）| 中（LSM 适合流）| 中 | 高（Databricks 生态）|
| **商业化主推** | Tabular（**2024.06 被 Databricks 收购**）· Snowflake · AWS | 阿里 / Ververica / 国内云厂 | Onehouse | Databricks |
| **2025+ 活跃度** | 🔥🔥🔥 极活跃 | 🔥🔥 快速发展 | 🔥 相对放缓 | 🔥🔥 受 Uniform 推动 |

## 2024-2025 重大事件

### 1. Databricks 收购 Tabular（2024.06）

- Ryan Blue（Iceberg 创始人）+ Daniel Weeks + Jason Reid 团队整体加入 Databricks
- **信号**：Databricks 承诺长期支持 Iceberg、推动 Delta + Iceberg 协议融合
- **影响**：独立 Iceberg 托管生态缺一块；但 Iceberg 开源协议**被更大力量推动**
- **Uniform 进一步发展**：Delta 表可被 Iceberg 读取器识别

### 2. Paimon Apache 顶级项目毕业（2024.03）

- 从 Flink 子项目独立
- 国内大厂（阿里、字节、腾讯）深度投入
- 2024 下半年 1.0 GA
- **流批一体 + 高频 upsert** 场景渐成首选

### 3. Iceberg v3 spec 推进（2024-2025）

- Deletion Vectors · Row Lineage · Multi-Table Transaction · Geo / Variant 类型
- 2025 Q2 预计社区投票
- **和 Delta v4 的协议融合**是长期趋势
- 详见 [Iceberg v3 · spec 演进与采用](../lakehouse/iceberg-v3.md)

### 4. Hudi 相对降速

- 仍然稳定、Uber 规模生产
- 但新项目采用率**被 Iceberg / Paimon 稀释**
- Onehouse 商业化聚焦"多表格兼容层"而非单推 Hudi

---

## 每位选手的关键差异

### Iceberg（2024+ 行业通用协议）

**定位演进**：从"Netflix 内部工具"（2018）→"Apache 顶级"（2020）→**"行业通用表格式协议"**（2024+）。

**核心优势**：
- **协议中立**：REST Catalog 把"表是什么"标准化
- **多 Catalog 选项**：HMS / REST / Nessie / Polaris / Unity / Glue
- **v3 spec** 带来 Deletion Vector + Multi-Table Transaction + Row Lineage
- **Puffin** 为向量 / sketch 扩展预留口子
- **被所有主流商业厂商拥抱**：Snowflake Polaris · Databricks（收购 Tabular）· AWS Glue · Google BigLake

**边界**：
- 流式 upsert 不如 Paimon 原生
- v3 尚未稳定，生产采用要谨慎

### Paimon（流一体原生 · 国内生态首选）

**定位演进**：从 Flink Table Store（2022）→ Apache 顶级（2024）。

**核心优势**：
- **LSM on Object Store** 天然支持高频 upsert
- **4 种 Changelog Producer**（`input`/`lookup`/`full-compaction`/`none`）给下游流处理灵活度
- **流批一体**：同一表 Flink 流 + Trino 批查
- **阿里 / 字节 / 腾讯** 深度投入，国内生态活跃

**边界**：
- 社区以 Flink 为中心（Spark / Trino 支持成熟但不如 Iceberg）
- 相对 Iceberg **生态广度仍有差距**
- Catalog 生态主要还是 Hive / REST（Unity / Polaris 集成相对弱）

### Hudi（Spark 生态老将）

**定位演进**：从 Uber 2017 开源 → 2020 Apache 顶级 → 2024 相对"成熟稳定期"。

**核心优势**：
- **三种查询类型**（Snapshot / Read-Optimized / **Incremental**）
- **Record-level Index**（1.0+）加速主键定位
- **CoW / MoR 双模** 灵活
- **Uber 规模化验证**（PB 级生产）

**边界**：
- **新项目采用率放缓**，被 Iceberg + Paimon 蚕食
- **Multi-Writer 需外部 lock**（ZK / DynamoDB）—— 不如 Iceberg CAS 优雅
- **多引擎支持**：Trino / Flink 不如 Spark 完整
- Onehouse 也承认"多表格兼容"比单押 Hudi 更务实

### Delta Lake（Databricks 深度 · Uniform 拥抱 Iceberg）

**定位演进**：Databricks 2019 开源 → LF AI 托管 → **2024 收购 Tabular 后**深度拥抱 Iceberg。

**核心优势**：
- **Databricks Runtime + Photon** 最优性能
- **Unity Catalog** 深度集成（血缘 / 治理完整）
- **Deletion Vectors + Liquid Clustering** 工业级成熟
- **Uniform**：一张 Delta 表可被 Iceberg 客户端读

**边界**：
- **Databricks 生态外相对弱**（开源 Spark 的 Delta 和 Databricks Runtime 有功能差距）
- **商业主导**：社区治理不如 Iceberg / Paimon 中立
- **长期问题**：Delta vs Iceberg 的协议融合未完成，未来可能"被收敛"到 Iceberg 主导

---

## 决策矩阵（2026 实务）

### 按场景选

| 场景 | 首选 | 备选 / 互补 |
|---|---|---|
| **新项目 BI + 多引擎** | **Iceberg** | — |
| **流式 CDC 入湖 + 准实时 BI** | **Paimon** | Iceberg v2 MoR |
| **流热表 + 批冷表** | **Paimon 热 + Iceberg 冷**（共 Catalog） | — |
| **已在 Databricks 深度栈** | **Delta** | 关注 Uniform 过渡 |
| **多云 / 跨厂商 · 避免锁定** | **Iceberg** | — |
| **已有 Hudi 生产** | 不强行换 · 下一代新表用 Iceberg / Paimon |
| **国内 + 流场景 + Flink 为主** | **Paimon** | — |
| **高频行级删除（合规 / GDPR）** | Iceberg v3 或 Delta v3+（Deletion Vectors） |
| **跨表原子事务** | Nessie / Iceberg v3 |

### 按团队现状选

| 现状 | 推荐 |
|---|---|
| 现在是 2026 · 新项目起步 · 云中立 | **Iceberg + Paimon** 组合 |
| 现在是 2026 · 新项目 · 全栈 Databricks | **Delta + Unity Catalog**（未来可切 Iceberg） |
| 现在是 2026 · 全栈 Snowflake | **Iceberg Tables** 原生 + **Polaris Catalog** |
| 已在 Hudi 生产（Uber / 字节等）| 继续 Hudi · 评估新表去 Iceberg 的 ROI |
| 老 Hive 栈 · 想升级 | 直接 **Iceberg**，不走 Hudi |

---

## 混用 / 迁移路径

### 常见混用模式

- **Iceberg + Paimon 双表** （国内互联网主流）：
  - 热 CDC 表：Paimon 主键表（分钟级新鲜度）
  - 冷历史表：Iceberg 追加（批分析 + 时间旅行）
  - 共享同一 Catalog（Nessie / REST / HMS 都可）

- **Delta + Iceberg 双读**（Databricks 用户拥抱开放）：
  - 用 Uniform 把 Delta 表暴露给 Iceberg 读者
  - 写仍用 Delta API、读可多引擎

### 迁移路径

| 起点 → 终点 | 难度 | 典型做法 |
|---|---|---|
| **Hive → Iceberg** | 低 | `CALL system.migrate('hive_table')` 零拷贝迁 |
| **Delta → Iceberg** | 中 | Uniform 双读（过渡）→ 完全切换（一次性）|
| **Hudi → Iceberg** | 中-高 | 通常一次性重写（不易双写）|
| **Parquet 裸文件 → Iceberg** | 低 | `CREATE TABLE ... AS SELECT` 或 migrate |

### 不推荐的路径

- **Iceberg → 任何其他**：反潮流；通常没动力
- **多格式**在同一业务混用（无分层）：运维噩梦

---

## 性能对比（公开 benchmark 参考）

!!! warning "数据来源"
    以下数字来自各家公开 benchmark（**各有立场**）。自家业务 POC 才是真相。

### 批查询性能（TPC-DS 100，相对比）

- Iceberg · Delta · Hudi（CoW）· Paimon（批模式）**在纯批查询场景差异不大**（10% 以内）
- Databricks Runtime 的 Photon 给 Delta 额外加成 2-5×（但那是引擎优化不是格式优势）

### 流式 upsert 吞吐

- Paimon（LSM）：单作业 **10k-100k rows/s**
- Hudi MoR：单作业 **10k-50k rows/s**
- Iceberg MoR：较新但赶上中
- Delta CoW：upsert 不是长项

### 小文件 / Compaction 开销

- 所有系统都需要定期 compaction
- Paimon 的 LSM 机制**内建分层合并**，自动化好
- Iceberg / Delta 需要额外 compaction 作业

---

## 现实检视 · 2026 视角

### 协议融合趋势

- **Iceberg 实际上正在成为事实标准**，Delta / Hudi / Paimon 都在某种程度"兼容 Iceberg"
- **Uniform** 让 Delta 用户可渐进迁移
- Paimon 有独立发展轨迹（LSM 路线），**不完全融合** Iceberg，但保持互操作

### 商业博弈

- Databricks 收购 Tabular 后，**Delta + Iceberg 的商业战争**基本结束——Databricks 同时押两边
- Snowflake Polaris + Open Catalog 继续推 Iceberg 标准化
- 国内阿里 / 字节推 Paimon（差异化路线）

### 对团队的务实建议

1. **2026 新项目 · 优先 Iceberg**（不论云 / 国内 / 国外）
2. **流场景重的加 Paimon**（Iceberg 流能力 v3 后才真补齐）
3. **已有 Delta 栈别急着换**，用 Uniform 做过渡
4. **已有 Hudi 栈别急着换**，新项目让新表去 Iceberg
5. **关注 Iceberg v3 进度**，2026-2027 可能是"大版本切换"节点

### 警惕的坑

- **盲信"某格式 3× 快过另一个"**：benchmark 立场强烈
- **追求"全栈 Delta"或"全栈 Iceberg"**：混用合理有理由
- **换格式的迁移成本经常被低估**：通常 PB 级 1-3 季度
- **Catalog 决定多引擎**：选 Catalog 比选表格式还重要（REST vs Unity vs Polaris）

---

## 相关

- 各系统深度页：[Iceberg](../lakehouse/iceberg.md) · [Paimon](../lakehouse/paimon.md) · [Hudi](../lakehouse/hudi.md) · [Delta](../lakehouse/delta-lake.md)
- [DB 存储引擎 vs 湖表](db-engine-vs-lake-table.md) · [Catalog 全景对比](catalog-landscape.md)
- [Iceberg v3 · spec 演进与采用](../lakehouse/iceberg-v3.md) —— 下一代
- [Lakehouse 厂商与开源生态格局](../vendor-landscape.md) —— 商业视角

## 延伸阅读

- **[Apache Iceberg 官方](https://iceberg.apache.org/)** · **[Paimon 官方](https://paimon.apache.org/)** · **[Hudi 官方](https://hudi.apache.org/)** · **[Delta 官方](https://delta.io/)**
- **[Databricks 收购 Tabular 博客](https://www.databricks.com/blog/databricks-tabular)**
- **[Snowflake Polaris 发布](https://www.snowflake.com/en/blog/introducing-polaris-catalog/)**
- **[Onehouse 多格式对比](https://www.onehouse.ai/blog)**（注意：Onehouse 主推 Hudi）
- **[Uniform docs (Databricks)](https://docs.databricks.com/en/delta/uniform.html)**
- *The Open Lakehouse Format Comparison*（各家独立测评，2024-2025 多篇更新）
