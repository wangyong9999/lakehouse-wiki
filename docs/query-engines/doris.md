---
title: Apache Doris · MPP OLAP 数据库
type: system
depth: 资深
level: A
last_reviewed: 2026-04-20
applies_to: Apache Doris 3.0+ (2025) · 2.1 LTS · 存算分离模式 2.0+
tags: [query-engine, olap, mpp, mpp-database]
category: query-engine
repo: https://github.com/apache/doris
license: Apache-2.0
status: stable
---

# Apache Doris

!!! tip "一句话定位 · 独立 MPP OLAP 数据库 · 湖仓融合方向强"
    **MPP 分析型数据库**——和 ClickHouse / StarRocks 同属"自带存储的 OLAP DB"层 · 不是纯查询引擎。向量化执行 + Pipeline 执行模型 + Iceberg/Hudi/Paimon 直读。和 [StarRocks](starrocks.md) **同源**（都源自百度 Palo），定位、架构、能力高度重合；**2024-2026 在湖仓融合方向投入大**，中国社区活跃。

!!! info "向量化 ≠ 向量检索 · 和 retrieval/ 章节的边界"
    Doris **2.1+（2024）** 加了**向量索引 + 相似度检索**能力。区分同前：

    - **"向量化执行"** = SIMD + Pipeline 执行引擎 · 本页性能基础
    - **"向量检索"** = ANN 相似度 · 2024+ 延伸能力 · 详见 [多模检索](../retrieval/index.md)

    定位同 StarRocks · BI 数据表附带向量做混合查询合适；纯向量走专业向量库。

## 它解决什么 · Doris 的独立判断框架

**不只是"StarRocks 同源"** · Doris 作为独立产品的判断要点：

- **Apache 顶级项目治理**（StarRocks 是 Linux Foundation + 商业公司 StarRocks Inc.）· 更符合"纯社区"偏好
- **湖仓融合 2024-2026 重点投入**：Iceberg / Hudi / Paimon 三家表格式读支持持续完善 · 存算分离模式（Compute Node 直读对象存储）2024+ 实用化
- **国内社区深耕**：飞轮 / 百度等商业参与方让中文生态 / 文档 / 案例积累厚；中国场景选型**常见默认选项**
- **MPP + OLAP DB 能力矩阵**和 StarRocks 高度重合：高并发 OLAP + 多表 join + MV + 向量化

**真正的独立亮点**：

- **存算分离** 2.0+ 成熟度追赶（对公有云部署友好）
- **Unique Key 表模型** 的 upsert 场景优化
- **异步 MV 跨内外部表** · 支持把 Iceberg 外表 + 内表 join 后物化

### 湖仓直读 vs 加速副本 · 和 StarRocks 同构

| 维度 | 直读外表（Catalog） | 加速副本（Internal + 异步 MV）|
|---|---|---|
| **延迟** | 秒级 | 毫秒到亚秒 |
| **MV 刷新** | 无刷新概念（直读）| 异步 MV 跨 Catalog 刷新 |
| **成熟度** | Iceberg 2024-2025 补齐 · Paimon 和 Hudi 仍在演进 | 内部表 + MV 成熟 |
| **推荐用途** | 低频探索 · 冷数据 | 仪表盘 · BI 热路径 |

定位判断**同 StarRocks**：**热路径走内表 + MV 加速 · 冷路径走外表直读**；直读外表当仪表盘主路径会失望。

## 架构

- **FE（Frontend）** + **BE（Backend）** 架构（与 StarRocks 同构）
- 存算一体（Internal Table）+ 存算分离（Compute Node 直读湖表）
- 向量化执行 + Pipeline 执行模型

## 对湖仓的关键能力

- 内部表：明细 / 主键 / 聚合 / Unique 多种模型
- 外部表 / Catalog：Hive / Iceberg / Hudi / Paimon / JDBC
- **Asynchronous Materialized View** —— 跨内部表 + 外部表
- **存算分离模式**：数据在对象存储，计算节点弹性伸缩

## 和 StarRocks 怎么选

两者非常相近，在实战差异：

| 维度 | StarRocks | Doris |
| --- | --- | --- |
| **开源治理** | Linux Foundation（原 StarRocks Inc.）| Apache 顶级 |
| **向量化深度** | 内部重写更彻底，benchmark 略优 | 持续追平 |
| **湖仓集成（Iceberg / Paimon）** | 较早，成熟 | 近年快速补齐 |
| **社区生态** | 全球更活跃，国际案例多 | 中国社区深厚 |
| **企业背书** | StarRocks Inc. 商业公司 | 飞轮、百度、选手多 |

**没有"绝对更好"**。建议：

- 已有选型的继续跟进
- 新项目两者都 POC 一轮，看自家负载

## 什么时候选

- 需要 MPP + 湖仓融合
- 中国内需求 / 社区支持偏好
- 想要 Apache 社区治理（Doris）

## 陷阱

- **版本差异**：两者的 roadmap 非一致，某些特性名字相同含义不同
- **生态二选一成本低但运维分流** —— 两套都用成本更高，建议选一个
- **存算分离模式**还相对新，生产案例积累中

## 相关

- [StarRocks](starrocks.md) —— 主要对比对象
- [Trino](trino.md) / [ClickHouse](clickhouse.md) —— 其他 OLAP 选项
- 场景：[BI on Lake](../scenarios/bi-on-lake.md)

## 延伸阅读

- Apache Doris docs: <https://doris.apache.org/>
- *A Deep Comparison: Apache Doris vs StarRocks* —— 社区多篇对比文
