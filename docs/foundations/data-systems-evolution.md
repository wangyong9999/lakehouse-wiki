---
title: 三代数据系统演进史 · Database → Data Warehouse → Lakehouse
type: concept
depth: 进阶
level: S
applies_to: 历史梳理（1970s-2025）
tags: [foundations, history, evolution]
aliases: [数据系统简史, Data Systems Evolution]
related: [lake-table, oltp-vs-olap, modern-data-stack]
status: stable
---

# 三代数据系统演进史

!!! tip "一句话理解"
    数据系统 50 年史 = **每一代都在解决上一代的天花板**。关系数据库（1970s）解决应用系统的结构化存储；数据仓库（1990s）解决 OLAP 分析；数据湖（2010s）解决半/非结构化；**湖仓（Lakehouse, 2020+）**融合批 + 流 + AI + BI 一体。看懂这条线，就看懂"为什么今天的架构长这样"。

!!! abstract "TL;DR"
    - 1970s 关系数据库：Codd 关系模型，ACID，面向 OLTP
    - 1990s 数据仓库：Kimball / Inmon，星型建模，批量 ETL，昂贵专有
    - 2006 Hadoop 时代：开源 MPP 处理非结构化、规模大但慢
    - 2012 大数据分叉：数仓专有（Snowflake / Redshift）· 开源湖（Hive/Spark）
    - 2018+ 湖仓融合：Delta / Iceberg / Hudi / Paimon + 计算存储分离
    - 2023+ AI-native 湖仓：多模 + 向量 + LLM + Agent 原生支持

## 1. 1970s · 关系数据库的胜利

### 时代背景

在 Codd 1970 年论文前，数据存储是**应用特异性**的：银行交易有自己的文件格式、航空预定有自己的 B-tree、库存管理有自己的 ISAM。

每个应用都要重新发明：
- 存储结构
- 索引算法
- 并发控制
- 查询语言

### Codd 的革命（1970）

E.F. Codd 的 *"A Relational Model of Data for Large Shared Data Banks"* 提出：
- **数据 = 关系（Relation, 一张表）**
- **操作 = 关系代数**（select/project/join/...）
- **完整性 = 约束**

这三件让**数据模型从物理解耦成逻辑**——SQL 语法一次定义、不同引擎实现。

### 标志产品

- **System R**（IBM 1974）· **Ingres**（UC Berkeley 1974）
- **Oracle**（1977）· **DB2**（1983）
- **PostgreSQL**（1986，Ingres 后继）· **MySQL**（1995）

### 核心特征

- **OLTP 优化**：点查询、事务、ACID
- **行存布局**：一行紧凑存一起
- **B-tree 主力索引**
- **单机 / 主备**

### 天花板

- **大规模分析慢**：OLTP 结构扫全表太慢
- **数据量受限**：单机 GB-TB
- **跨系统分析难**：每个业务系统自己一套 DB

## 2. 1990s · 数据仓库的崛起

### 为什么需要

企业 CIO：
- 销售在 Oracle、库存在 DB2、CRM 在自研 → 报表要跨 3 个系统
- OLTP 系统白天被业务吃饱，晚上跑分析扛不住
- 历史数据归档靠磁带，分析不了

### 数仓的发明（Inmon 1992 · Kimball 1996）

**Bill Inmon**（"数仓之父"）：*Building the Data Warehouse*
- 企业级数据汇聚
- 三范式建模
- 独立于操作型系统

**Ralph Kimball**：*The Data Warehouse Toolkit*
- 星型 / 雪花模型
- 事实表 + 维度表
- ETL 流水线

### 标志产品

- **Teradata**（1979，开创者）
- **Oracle Exadata** / **Sybase IQ** / **Netezza**
- **Microsoft SQL Server Analysis Services**

### 核心特征

- **列式存储**（Sybase IQ 1996 年首创）
- **MPP 架构**（大规模并行处理）
- **专用硬件**（Exadata / Netezza ASIC）
- **批量 ETL**（T+1 为主）

### 天花板

- **昂贵**：Exadata 一个 rack 百万美元起
- **垂直扩展**：加机器加磁盘都贵
- **非结构化数据不收**：日志 / 图像 / JSON 进不了
- **专有封闭**：数据搬出来很痛

## 3. 2006+ · Hadoop 与大数据时代

### Google 的三篇神论文（2003-2006）

1. **GFS (2003)** · *The Google File System* → HDFS
2. **MapReduce (2004)** · *Simplified Data Processing* → MR 编程模型
3. **Bigtable (2006)** · *A Distributed Storage System* → HBase

### 开源实现

- **Hadoop**（2006 起步，Yahoo / Cloudera 推动）
- **Hive**（Facebook 2008）—— SQL on HDFS
- **Spark**（Berkeley 2014 毕业到 Apache）—— 内存 MR

### 核心特征

- **水平扩展**：加普通机器加磁盘
- **廉价存储**（HDFS 本地盘）
- **半结构化友好**：JSON / Avro / Parquet
- **开源生态**：Spark / Kafka / Flink / Presto

### 天花板

- **慢**：MapReduce 批跑几小时
- **ACID 弱**：Hive 表的 schema 演化破数据
- **小文件问题**：HDFS NameNode 瓶颈
- **运维复杂**：Hadoop 集群一堆组件

## 4. 2012+ · 云数仓崛起 · 与开源湖分叉

### 专有云数仓走红

- **Amazon Redshift**（2012）—— 基于 ParAccel
- **Snowflake**（2014 GA）—— **计算存储分离 + 按需付费**的标杆
- **Google BigQuery**（2011，基于 Dremel）

**Snowflake 的关键创新**：
- 存算分离（S3 存、EC2 算）
- 自动 concurrency scaling
- 零运维
- 按秒计费

**用户体验**革命性提升——但**封闭 + 贵 + 数据锁定**。

### 开源大数据继续进化

- **Spark** 取代 MapReduce 成主力
- **Trino/Presto** 做交互式 SQL
- **Kafka** 成为事件流标准
- **Hive** 逐渐被 Spark SQL 替代

### 数据湖概念诞生

James Dixon（2010）提出 "Data Lake"：
- 存**原始数据**（不先 ETL）
- Schema-on-read（读时解析）
- 支持任意格式

### 天花板

- **Swamp 风险**：没治理的湖变沼泽
- **无 ACID**：Hive 表并发写打架
- **性能不如专有数仓**：BigQuery / Snowflake 更快
- **治理缺失**：权限 / 血缘 / 质量全弱

## 5. 2018+ · 湖仓的融合

### 关键发明

**Delta Lake**（Databricks 2019）· **Apache Iceberg**（Netflix 2018）· **Apache Hudi**（Uber 2017）· **Apache Paimon**（阿里 2023 毕业）

共同创新：
- **ACID on Object Store**：CAS + Snapshot
- **Schema Evolution**：列 ID 不破历史
- **Time Travel**：Snapshot 是一等公民
- **Streaming + Batch**：统一底座

### 标志论文

**Armbrust et al., *Lakehouse: A New Generation of Open Platforms* (CIDR 2021)**

核心观点：
- 数仓的优势（SQL 性能、治理）
- 数据湖的优势（开放格式、廉价存储、多引擎）
- **湖仓 = 两者合一**

### Lakehouse 的架构突破

```
专有数仓（2010s）              湖仓（2020s+）
──────────────────            ───────────────
SQL                          SQL + Python + ML
Proprietary format            Parquet / ORC / Lance (open)
Vendor storage               Object Store (S3/GCS/OSS)
Closed Catalog               Open Catalog (REST / Unity / Nessie)
Single engine                Multi-engine (Spark / Trino / Flink / DuckDB)
Data + Compute coupled       Compute-Storage Separation
Expensive                    Commodity
```

### 标志产品

| 公司 | 2010s 时代 | 2020s+ 主线 |
|---|---|---|
| Databricks | Spark 云 | Lakehouse Platform |
| Snowflake | 云数仓 | + Iceberg REST Catalog |
| AWS | Redshift + EMR | S3 + Glue + Athena + Redshift Spectrum |
| Google | BigQuery | + BigLake + Iceberg |
| 阿里 | MaxCompute | Paimon + MC |
| 字节 | ByteHouse | ByteLake |

## 6. 2023+ · AI-Native Lakehouse

### 新的驱动力

- **大模型爆发**（ChatGPT 2022.11）
- **向量检索规模化**（Milvus / Pinecone 亿级）
- **多模数据**（图 / 文 / 音 / 视频）
- **Agent 架构**（2024+）

### 湖仓的新职责

```
之前：BI + ML 训练
现在：BI + ML + RAG + 推荐 + 多模 + Agent
```

**一份数据多引擎多 workload 消费**——这是湖仓的终极形态。

### 新关键能力

| 能力 | 贡献者 |
|---|---|
| **向量索引下沉到湖** | Iceberg Puffin · Lance format |
| **多模 schema** | 结构化 + blob URI + 向量 + 标签共存 |
| **Catalog 升级治理平面** | Unity / Polaris / Nessie |
| **MCP / Agent 协议** | Anthropic MCP（2024.11）|
| **AI-first 查询** | Text-to-SQL · AI Function（ai_classify / ai_extract）|
| **Flink + Paimon 流一体** | 准实时 ML 特征 |

### 代表新架构

```
原始数据源（CDC / 日志 / 外部 / IoT / 多模）
          ↓
Flink + Paimon （实时入湖）
          ↓
Iceberg / Paimon （湖底座）
          ↓
    ┌────┴────┐
    ↓         ↓
统一 Catalog   向量索引
(Unity)      (Lance / Puffin)
    │
    ├─→ Spark / Trino（BI + 训练）
    ├─→ Flink（实时）
    ├─→ DuckDB / pyiceberg（探索）
    ├─→ ML Serving（推荐 / RAG）
    └─→ LLM / Agent（RAG / MCP）
```

## 7. 从 50 年看规律

### 规律 1 · 每一代解决上一代的"扩展性天花板"

- DB：单机 → 分布式
- DW：昂贵专有 → 通用硬件 + 开源
- Lake：治理弱 → 湖仓 ACID
- Lakehouse：BI 为主 → AI 一等公民

### 规律 2 · 存储计算分离是长期方向

- 1970s：磁盘紧邻 CPU
- 1990s 数仓：专用存储阵列
- 2012+ Snowflake：**S3 + EC2 首次分离成功**
- 今天：所有湖仓都用对象存储

### 规律 3 · 协议化压缩"技术栈爆炸"

- SQL 标准化（1986 SQL-86）
- Parquet / ORC 成为列式标准
- **Iceberg REST Catalog**（2024）成为 Catalog 标准
- **Arrow / Flight / ADBC** 成为内存交换标准
- **MCP**（2024）成为 Agent + Tool 标准

## 8. 给团队的启示

- **不要盲信新词**：每代都有 hype；看清核心是"解决了上一代的哪个天花板"
- **架构选择要看 10 年**：选一个开放协议（Iceberg / Parquet）比选一个商业产品更安全
- **BI + AI 一体化是趋势**：别按"BI 团队用 BI 栈、AI 团队用 AI 栈"割裂
- **规模感与成本要算明白**：小团队用 Snowflake 省心、大团队开源成本低 10×

## 相关

- [湖表](../lakehouse/lake-table.md) · [Iceberg](../lakehouse/iceberg.md) · [Paimon](../lakehouse/paimon.md)
- [Modern Data Stack](modern-data-stack.md)
- [一体化架构](../unified/index.md) · [业务场景全景](../scenarios/business-scenarios.md)

## 延伸阅读

- **[Codd 1970 原论文](https://dl.acm.org/doi/10.1145/362384.362685)**
- **[Armbrust et al., *Lakehouse* (CIDR 2021)](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)**
- **[Google GFS / MapReduce / Bigtable papers](https://research.google/pubs/)**
- *Designing Data-Intensive Applications*（Kleppmann 2017）—— 系统性总结
- *The Data Warehouse Toolkit*（Kimball 2013）—— 数仓建模圣经
- *Data Mesh* (Zhamak Dehghani 2022)
