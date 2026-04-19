---
title: 多模湖仓 · 向量 / 地理 / 半结构化 / 图 在湖表上的承载
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-19
applies_to: Iceberg v3, Paimon 1.0+, Lance v2, Vortex (LF AI Incubation), GeoParquet spec
tags: [lakehouse, multi-modal, vector, geography, variant, graph, ai]
aliases: [多模态湖表, Multi-modal Lakehouse]
related: [lake-table, iceberg, paimon, lance-format, puffin, vector-database]
systems: [iceberg, paimon, lance, milvus]
status: stable
---

# 多模湖仓 · 向量 / 地理 / 半结构化 / 图 在湖表上的承载

!!! tip "一句话理解"
    BI 时代的湖仓只需要处理"结构化行列"。**AI 时代的湖仓要同时承载向量（embedding）、地理（geo）、半结构化（JSON/Variant）、图（graph）四类非传统数据**——而且要和结构化列**共表、共事务、共快照**。这是 2024-2026 湖表最大一轮形态演进，也是当前最有启发空间的研究窗口。

!!! abstract "TL;DR"
    - **四个维度**：向量 / 地理 / 半结构化(Variant) / 图 —— 每个都对湖表有独立的 spec 演进
    - **存储载体**：Parquet（宽数据）· Lance（向量原生）· Vortex（新一代列存）· GeoParquet（地理）
    - **索引载体**：Puffin（Iceberg 侧车）· Lance 内嵌 IVF/HNSW · Metadata Table（Hudi）
    - **查询路径**：Trino / Spark / DuckDB + 专用向量 / 地理引擎协同
    - **Iceberg v3 是 2025-2026 主推动者**：Variant / Geometry / Geography 都进了 spec
    - **未收敛的问题**：向量索引 blob 协议、跨维联合查询、行列+向量共页

## 为什么湖上要做多模

### 业务层驱动

**AI + BI 融合的场景**把数据的边界扩展了：

- 电商：订单（结构化）+ 商品图片 embedding（向量）+ 门店 GPS（地理）+ 用户标签 JSON（半结构化）+ 社交关系（图）
- 医疗：病历（结构化）+ CT 切片 embedding（向量）+ 医院位置（地理）+ 基因结构（图）+ 问诊记录 JSON
- 风控：交易（结构化）+ 用户行为 embedding（向量）+ IP 地理 + 关系网络（图）

**传统做法**：每类数据一套存储（关系库 + 向量库 + PostGIS + MongoDB + Neo4j + ...）→ **六条 ETL 管道 + 六套权限 + 六个查询语言 + 六份备份**。团队疯掉。

### 湖上统一的两个诱惑

1. **存算分离下统一存储层**：都落对象存储 + 都靠 Catalog 联邦 + 都过 snapshot/事务 → 运维成本一份
2. **查询融合**：`SELECT order_id, vector_similarity(embedding, query_vec), ST_Distance(store_geo, user_geo) FROM unified_table` —— 单次查询跨四维

问题：**存储统一可行，索引和查询引擎还没完全统一**。这是 2026 窗口。

## 维度 1 · 向量 (Vector Embedding)

### 业务场景

文本 / 图像 / 视频 / 音频的 embedding 向量（通常 128 - 4096 维 float32）。RAG、相似搜索、推荐、异常检测。

### 存储载体的 2 条路径

**路径 A · 列式存储原生 array 字段**（Iceberg / Parquet）

```sql
CREATE TABLE docs (
  doc_id BIGINT,
  text STRING,
  embedding ARRAY<FLOAT>  -- 一行一个向量
) USING iceberg;
```

- ✅ 和结构化列**同表同事务**
- ✅ 所有 Iceberg 引擎都能读
- ❌ **Parquet 对 float array 不友好**：列存优化针对 primitive，不针对定长 array；读要反序列化整个 row group
- ❌ **无原生向量索引**：只能全表扫 + in-memory ANN

**路径 B · Lance Format**（见 [Lance Format](../foundations/lance-format.md)）

```python
import lance
dataset = lance.write_dataset(df, "s3://bucket/docs.lance")
dataset.create_index("embedding", index_type="IVF_PQ")
```

- ✅ **向量是一等公民**：列级编码针对高维向量优化（随机访问快 100+ ×）
- ✅ **内嵌 IVF_PQ / HNSW 索引**：无需 sidecar
- ✅ **Lance v2 (CIDR 2024) 证明**：混合 scan + random access 场景下显著优于 Parquet
- ❌ 生态还在追赶（Trino / Flink 连接器成熟度不如 Parquet）
- ❌ 作为"湖表层"还年轻，Catalog 集成待完善

**现实选择**：**数据量和查询量都大、向量主导** → Lance；**向量只是附属列、查询为主结构化过滤** → Iceberg + Parquet。

### 索引载体

| 方案 | 承载 | 成熟度 |
|---|---|---|
| **Lance 内嵌索引** | IVF_PQ / HNSW 在 Lance 文件内 | 成熟 |
| **Iceberg Puffin bloom-filter-v1** | spec PR 中 | proposal |
| **Iceberg Puffin HNSW proposal** | 社区提案 | 未接纳 |
| **外挂 Milvus / Qdrant** | Iceberg 表做 source of truth，向量库做索引 | 实务常见 |
| **Starrocks / Doris 向量索引** | 数据库内建 ANN | 非湖表方案 |

**2026 关键 open question**：**Iceberg 会接纳 HNSW blob 吗**？Databricks / Snowflake / Google 的取舍决定走向。如果接纳，湖表就原生支持 ANN；如不接纳，向量索引永远是外挂。

### 查询路径

```
SELECT doc_id, text, cosine(embedding, :q) AS score
FROM iceberg.docs
WHERE category = 'news'
ORDER BY score LIMIT 100
```

- **纯 Iceberg**：Trino / Spark 全表扫 + 排序（千万行级可行、亿级崩）
- **Lance**：Python/Rust 走 Lance 自家 query engine，ANN + 过滤 push-down
- **Iceberg + 外挂向量库**：Milvus / Qdrant 从 Iceberg 同步，查询走向量库

## 维度 2 · 地理 (Geography / Geometry)

### 业务场景

门店位置、骑手轨迹、物流路径、社交签到、气象 grid。

### 存储载体

**GeoParquet** 2021 年开源，2024 年成为**事实标准**：

- **列里存 WKB** (Well-Known Binary) 或 WKT（Text）
- 元数据里声明 **CRS**（坐标参考系，常见 EPSG:4326）
- 兼容 Parquet reader（不认识就当二进制读）

**Iceberg v3 Geometry / Geography 类型**（2025-06 ratified）：

- 类型系统原生支持（不再是 "ARRAY<BYTE>" 的 hack）
- 和 GeoParquet 对齐（直接复用 WKB 编码）
- **空间谓词 pushdown**：`ST_Intersects(geo, polygon)` 可以下到文件级

### 索引载体

| 方案 | 机制 | 成熟度 |
|---|---|---|
| **BBox 列 min/max** | Manifest 里记录 geometry 的 bbox | 基础 |
| **R-Tree in Puffin** | 社区 proposal | 未接纳 |
| **S2 / H3 cell 派生列** | 把 geo 派生成 cell ID，对 cell 建普通索引 | 实务常见 |

**实务建议**：派生 **H3 或 S2 cell** 作为普通 BIGINT 列 + 加 bucket partition，比等待 Puffin R-Tree 更快落地。

### 前沿参考

- **GeoLake** 研究（2023-2024）：Iceberg-based 地理湖表原型
- **Apache Sedona**（原 GeoSpark）：Spark 空间库，已支持 Iceberg
- **Overture Maps**：开源地图数据集，发布为 GeoParquet

## 维度 3 · 半结构化 · Variant

### 业务场景

日志、用户埋点、移动端事件、IoT 传感、API 响应存档——**schema 事先不知道**，事后要能过滤 / 聚合。

### Variant 类型 · 2024-2025 的大进展

**Variant 是 Apache Spark 4.0（2025）引入的新类型**，**Iceberg v3 吸收**（2025-06 ratified）：

- **高性能二进制编码**（不是 JSON 字符串）：保留类型信息，避免重复 parse
- **shredding**：高频访问的子字段被**物化成独立列**（`events.user_id` 经常查 → 提升为一等列）
- **统计 push-down**：对 shredded 字段可以做 min/max 剪枝

```sql
CREATE TABLE events (
  event_id BIGINT,
  ts TIMESTAMP,
  payload VARIANT  -- 半结构化
) USING iceberg;

SELECT payload:user_id::BIGINT, COUNT(*)
FROM events
WHERE payload:type = 'click'
GROUP BY 1;
```

### 存储载体的 3 种选择

| 方案 | 查询效率 | Schema 演化 | 成熟度 |
|---|---|---|---|
| **STRING 列存 JSON** | 慢（每次 parse）| 完全灵活 | 老做法 |
| **JSON 列（Parquet native）** | 中 | 灵活 | Parquet 1.14+ |
| **Variant（v3）** | 快（shredding） | 灵活 + 可物化 | **2026 主流** |
| **固定 schema（STRUCT）** | 最快 | 需要演化 | 用于稳定字段 |

### 对 AI 场景的启发

Variant 不只是"存 JSON"——它是**"schema 未定时保留原始数据 + 逐步发现稳定字段提升为列"**的基础设施。这和**特征工程的"探索→稳定"路径**天然匹配。

## 维度 4 · 图 (Graph)

### 业务场景

社交关系、风控网络、推荐协同过滤、供应链、知识图谱。

### 湖上图存储的现状：**弱**

这是**四维里最不成熟**的。主流做法：

1. **边表 + 点表**（双表）存 Iceberg / Paimon 里，**没有原生图索引**
2. **属性图 JSON** 塞 Variant 字段，查询时展开
3. **GraphAr**（Alibaba 2023 开源，进入 Apache 孵化 2024）：图数据的列式存储格式，和 Parquet / Iceberg 对齐

**GraphAr 的核心思路**：

- 点、边分 chunk 存列式文件
- 提供 "vertex/edge table" 抽象
- 兼容 Iceberg / LakeFS 作 Catalog
- PyG / DGL 可直接训练

### 索引载体：空缺

湖上图没有"图原生索引"的标准。实务：

- 训练场景：导到 PyG / DGL 内存 → 图神经网络
- OLAP 场景：边表做 hash join / SQL 的 `RECURSIVE CTE`
- 生产图查询：仍走 Neo4j / Nebula / TigerGraph 专用引擎

**2026 open question**：**图能否像向量一样进湖**？GraphAr 是方向，但还没形成像 GeoParquet 那样的事实标准。

## 跨维度交叉难题

### 难题 1 · 统一 Catalog + 多模权限

**Polaris / Unity / Gravitino** 都在做。但**向量、地理、Variant 的 RBAC 粒度**不同：

- 向量：可能要"屏蔽 embedding 但露 doc_id"
- 地理：可能要"只给粗粒度 cell 不给精确坐标"
- Variant：可能要"只给部分 JSON 字段"

**Column Masking / Row-Level Security** 需要从"列级"扩到"字段级 + geo-精度级 + 向量维度级"。2026 未解。

### 难题 2 · 跨维联合查询

```sql
-- 找出 1km 内 + embedding 相似度 > 0.8 + 属于同一社群 的商品
SELECT p.id, p.name
FROM products p
WHERE ST_Distance(p.location, :user_geo) < 1000
  AND cosine_sim(p.embedding, :user_embedding) > 0.8
  AND p.id IN (SELECT neighbor FROM graph WHERE user = :u);
```

**难点**：三个条件分别由地理索引 / 向量索引 / 图 hop 完成，但**优化器要能决定执行顺序**——先 ANN 还是先地理过滤？目前湖上还没统一 planner 能做这种选择性 (selectivity) 估算。

### 难题 3 · 行列 + 向量共页

Lance 把向量优化放进文件格式；Parquet 没有。**理想**：一种文件格式同时对"列式扫描" + "向量随机访问" + "半结构化嵌套" 都优。

**Vortex**（SpiralDB 2024 开源，**2025 捐献给 Linux Foundation AI & Data，Incubation 阶段**）：新一代列存格式，以**自适应级联编码 + 懒解压**为核心卖点——声称 100× 随机访问、10-20× scan、5× 写。如果社区生态能跟上，**会是 Parquet 继承者候选**。

## 前沿研究 · 2026 可关注

- **Lance v2** (CIDR 2024) —— ML workload 优先的列存
- **Vortex** (SpiralDB → LF AI & Data, 2024-2025) —— "Parquet 继承者"候选
- **GeoLake / GeoParquet** —— 地理湖表化
- **GraphAr** (Alibaba, 2023+) —— 图列存
- **Apache XTable** —— 跨格式互操作（三家湖表统一）
- **Polaris + Gravitino** —— 多 Catalog 联邦
- **Iceberg Variant + Shredding**（Spark/Snowflake/Databricks 2024-2025 联合推动）

## 创新启发窗口

从这页读完，**值得深入的几个方向**：

1. **把 embedding 表做成 Iceberg MV**——源表 CDC → 触发 embedding 刷新 → 写回 Iceberg → Milvus 作为外挂 ANN。这是**湖上 Feature Store 的现实路径**
2. **Variant + Shredding** 重新定义日志湖——原始日志全进 Variant，高频字段逐步物化。解决"先 schema 还是先数据"的哲学难题
3. **GeoParquet + Iceberg Geography** 的落地案例——Uber 交易、美团外卖、高德导航类业务的标准化湖仓
4. **多模 Catalog**（Polaris + Gravitino）的合流——RBAC / Schema Registry / 跨模块联邦
5. **Vortex 是否会替代 Parquet** —— 2026-2027 窗口，决定下一代湖表基底

这不是"未来学"——这是**现在就能挑一个方向做深的机会**。

## 和其他模块的边界

本页聚焦 **"湖表协议层"承载多模**——不重述产品维度的细节：

- 向量库产品对比（Milvus / LanceDB / Qdrant）走 [retrieval/向量数据库](../retrieval/vector-database.md)
- "湖 + 向量"组合的**架构模式**走 [unified/Lake + Vector 融合架构](../unified/lake-plus-vector.md)
- 向量检索算法/索引前沿走 [frontier/向量检索前沿](../frontier/vector-trends.md)
- Catalog 联邦（Polaris / Gravitino）走 [catalog/Apache Polaris](../catalog/polaris.md) · [catalog/Gravitino](../catalog/gravitino.md)
- Lance 作为**文件格式**走 [foundations/Lance Format](../foundations/lance-format.md)

## 相关

- [湖表](lake-table.md) —— 基础抽象
- [Apache Iceberg](iceberg.md) —— v3 是多模主推动者
- [Puffin](puffin.md) —— 索引侧车（向量未来承载）
- [Materialized View](materialized-view.md) —— Embedding MV 的基础设施

## 延伸阅读

- **Lance v2 · CIDR 2024** —— ML 工作负载列式格式
- **Vortex**: <https://github.com/vortex-data/vortex> (LF AI & Data Incubation)
- **GeoParquet spec**: <https://geoparquet.org/>
- **Iceberg Variant proposal**: Iceberg spec v3 Variant type
- **GraphAr**: <https://github.com/apache/incubator-graphar>
- **Apache XTable**: <https://github.com/apache/incubator-xtable>
- **Apache Polaris**: <https://github.com/apache/polaris>
- **Apache Sedona**: <https://sedona.apache.org/>
- **Apache Gravitino**: <https://gravitino.apache.org/>
