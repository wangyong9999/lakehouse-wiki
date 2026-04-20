---
title: 压缩与编码
type: concept
depth: 进阶
prerequisites: [parquet, columnar-vs-row]
tags: [foundations, compression, encoding, parquet, orc]
related: [parquet, orc, columnar-vs-row, vectorized-execution]
applies_to: Parquet / ORC / Lance / 通用列式
last_reviewed: 2026-04-18
status: stable
---

# 压缩与编码

!!! tip "一句话理解"
    "为什么列式能快 10 倍、空间省 5 倍" —— 答案不在"列式"本身，而在**列式让数据重复 / 有序，从而让轻量级编码（RLE / Dict / Bit-pack）能压得极狠**，然后再叠一层通用压缩（Zstd / Snappy）。两层协作才是真正的收益。

!!! abstract "TL;DR"
    - **两层架构**：先**编码**（RLE · Dictionary · Bit-pack · Delta）→ 再**压缩**（Zstd · Snappy · LZ4）
    - **编码比压缩更关键**：低基数列 Dictionary + RLE 能把 1GB 压到 10MB，通用压缩再优化也就 2-3×
    - **Snappy vs Zstd**：Snappy 极快但压缩率一般；**Zstd 是 2020+ 的默认建议**，压缩率高且解压够快
    - **选型口诀**：BI 查询主导 → Zstd；写吞吐主导 → Snappy / LZ4；归档 → Zstd-19 / gzip
    - **和向量化执行的关系**：字典编码 + Bit-packing 让 CPU 直接在压缩数据上 SIMD 处理（"延迟解码"）

## 1. 为什么分两层

原始数据 → 编码 → 压缩 → 磁盘 / 对象存储。

**编码**针对数据规律（重复 / 有序 / 低基数），**压缩**针对字节流的熵。两者叠加：

```
原始 10GB
  → 编码（Dict + RLE + Bit-pack）→ 800MB
    → 压缩（Zstd）→ 200MB
```

如果只有压缩没有编码：10GB → 4GB。如果只有编码没有压缩：10GB → 800MB。两者结合才能到 200MB。

---

## 2. 编码技术（Encoding）

### 2.1 Dictionary Encoding（字典编码）

**适用**：低基数列（distinct 数 << 行数）——国家、状态、性别、设备类型。

```
原始： ["CN","US","CN","CN","US","CN","JP",...]   1M 行
字典：  {0:"CN", 1:"US", 2:"JP"}
编码：  [0, 1, 0, 0, 1, 0, 2, ...]   → 每值 2 bit 即可
```

**效果**：字符串列从几 MB 压到几 KB 很常见。**几乎所有列式格式默认开启**，阈值通常是"字典 ≤ 某大小（如 Parquet 默认 1MB）"。

**陷阱**：
- 高基数列（user_id、uuid）字典比原始还大 → Parquet / ORC 会自动退回 plain encoding
- 字典本身要放进 Row Group metadata → 每个 Row Group 独立字典（跨 RG 不共享）

### 2.2 RLE · Run-Length Encoding（游程编码）

**适用**：连续重复值（排序后或天然重复，如时间分区后的日期列、枚举值）。

```
原始： [CN,CN,CN,CN,CN,US,US,US,JP,JP,...]
RLE ： [(CN,5), (US,3), (JP,2), ...]
```

**效果**：**配合排序/聚簇**后 RLE 极其有效（这就是为什么 Iceberg / Delta 都建议"高基数列排序存储"）。

### 2.3 Bit-Packing

**适用**：整数列取值范围小。

```
原始 int32（32 bit） 值 0-7：[0,3,1,7,2,5,...]
Bit-pack（3 bit 足够）：     [000,011,001,111,010,101,...]
```

**效果**：Dictionary 编码后的整数 index 几乎都很小 → Bit-pack 又省 4-10×。Parquet / ORC 都原生叠这一层。

### 2.4 Delta Encoding

**适用**：单调递增 / 近似递增（时间戳、自增 ID）。

```
原始： [1700000001, 1700000003, 1700000005, 1700000007, ...]
Delta：1700000001, [2, 2, 2, ...]（base + deltas）
```

**效果**：时间戳列配合 Delta + Bit-pack，压缩率常到 50-100×。

### 2.5 其他

- **Delta-of-Delta**：二阶差分，对时序指标更狠（InfluxDB / Prometheus TSDB 用得多）
- **FOR** (Frame of Reference)：批内减去最小值再 Bit-pack
- **Byte Stream Split** (Parquet v2)：浮点列拆字节后分别压缩

---

## 3. 压缩算法（Compression）

### 3.1 速查

| 算法 | 压缩率 | 压缩速度 | 解压速度 | 典型用途 |
|---|---|---|---|---|
| **Zstd** | ★★★★ | ★★★ | ★★★★ | **默认推荐**（2020+）· 湖仓主流 |
| **Zstd-19 / max** | ★★★★★ | ★ | ★★★★ | 冷数据 / 归档 |
| **Snappy** | ★★ | ★★★★★ | ★★★★★ | 老 Hadoop 默认 · 写密集 |
| **LZ4** | ★★ | ★★★★★ | ★★★★★ | 低延迟流场景 · 日志 |
| **Gzip** | ★★★ | ★★ | ★★ | 跨语言兼容 · 老系统 |
| **Brotli** | ★★★★ | ★★ | ★★★ | Web / 静态资源 |
| **LZO** | ★★ | ★★★★ | ★★★★ | 老系统 · 专利限制已过 |
| **无压缩** | — | ★★★★★ | ★★★★★ | 已压缩的 binary（图像 / Parquet of Parquet） |

### 3.2 Zstd：2020+ 的主流推荐

**Zstd（Facebook 2016）的优势**：
- 压缩率接近 Gzip，但解压速度接近 Snappy
- **level 可调**（1-22），同一算法一套参数覆盖从"实时流"到"冷归档"
- **在"新建湖表"场景**越来越多系统的推荐默认——Iceberg 的 `write.parquet.compression-codec` 默认已是 `zstd`；Delta / ClickHouse 的新建表也普遍切换到 Zstd
- **但不是所有库的现行默认**：PyArrow `write_table` 仍默认 `snappy`；ORC / Paimon / 旧 Parquet 客户端很多也还是 Snappy / ZLIB。写入端真正用什么，取决于**客户端库默认 + 显式参数**，不是 Parquet/ORC 文件 spec（spec 不规定默认压缩）

**level 建议**：
- **Zstd-1 到 -3**：写密集（Kafka → 湖 CDC 流，写吞吐 > 压缩率）
- **Zstd-3 到 -9**：通用（大多数湖表的默认区间）
- **Zstd-15 到 -22**：冷归档 / 日常 Compaction 后的归档层（压缩率优先）

### 3.3 Snappy 仍然有用的场景

- 写吞吐极敏感（Kafka in-flight / 流 Sink）
- CPU 受限环境（边缘 / 嵌入式）
- 老 Hadoop / Hive 生态（历史默认）

### 3.4 不要用的

- **Gzip on 列式**：压缩慢、解压慢，几乎总被 Zstd 全面碾压
- **Bzip2**：更慢，无场景优势
- **无压缩** on 文本列：除非已经是压缩过的 binary

---

## 4. 和列式格式的对应

| 格式 | Encoding 层 | 常见 Compression（spec 不规定默认） |
|---|---|---|
| **Parquet v1 / v2** | Dictionary · RLE · Bit-pack · Delta · Delta-of-Delta（v2 增 Byte Stream Split · Delta Length Byte Array）| 客户端库决定：PyArrow 默认 Snappy；Iceberg / Delta 的写入默认多为 Zstd；可显式选 |
| **ORC** | 同上 + FOR · 紧致字典 | ZLIB（历史默认）· Zstd（推荐新建表切换）· Snappy |
| **Lance** | Dictionary · Bit-pack · Byte Stream Split | Zstd / LZ4（可配） |

**关键**：格式自动选编码（根据统计），**开发者基本只选 compression 算法 + level**。

```python
# PyArrow 写 Parquet 的常见配置
import pyarrow.parquet as pq
pq.write_table(
    table,
    'events.parquet',
    compression='zstd',            # 默认推荐
    compression_level=3,           # 1-22, 默认 3
    use_dictionary=True,           # 默认 True，低基数列自动字典
    write_statistics=True,         # 默认 True，min/max + bloom（可选）
    data_page_version='2.0',       # 开 byte_stream_split 等新编码
)
```

---

## 5. 和向量化执行的协同

**关键洞察**：现代查询引擎（DuckDB · Velox · Polars · StarRocks）能**在压缩数据上直接做向量化计算**——Dictionary 编码的数据不解成字符串，直接在 int index 上 SIMD 过滤。

```
WHERE country = 'CN'
  → 查字典：'CN' → 0
  → 在 bit-packed index 列 SIMD 比较 == 0
  → 延迟解码：只对匹配的行解字典（或连字典都不解）
```

这就是为什么"Dictionary + Bit-pack" 能让 OLAP 在低基数列上快几十倍。

---

## 6. 选型决策

| 场景 | Compression | Level |
|---|---|---|
| **通用湖仓（BI + AI 混合）** | Zstd | 3-6 |
| **写密集 CDC / 流入湖** | Zstd 或 Snappy | 1-3 |
| **冷归档 / 法规保留** | Zstd 或 Gzip | 15-22 |
| **边缘 / CPU 紧缺** | Snappy / LZ4 | — |
| **需要 Hive 老生态读** | Snappy | — |

**Row Group / Stripe 大小**同样影响性能（太小 overhead 大、太大 pushdown 粒度差），默认 128MB-512MB 是安全起点。

---

## 7. 陷阱

- **所有列一样压**：JSON / 日志 string 列收益大；已压过的 binary（图像 bytes）再压反而变大 + 慢 → 标记 `compression=uncompressed`
- **Row Group 太小**：编码字典 / 统计 overhead 变大，压缩率反而降
- **只看 ratio 不看 CPU**：Zstd-22 压缩率比 -3 好 5%，但写慢 10×，读也可能变慢
- **忘了 bloom filter 独立开关**：Parquet / ORC 的 bloom 是额外成本，高基数列才有用
- **Gzip 当默认**：老惯性，基本都应该切 Zstd

---

## 8. 延伸阅读

- **[Zstd 官方基准](https://facebook.github.io/zstd/)** · **[Zstd 论文 / 白皮书](https://facebook.github.io/zstd/zstd_manual.html)**
- **[Parquet 编码规范](https://github.com/apache/parquet-format/blob/master/Encodings.md)** —— 每种 encoding 的二进制细节
- **[Apache ORC 规范](https://orc.apache.org/specification/ORCv1/)** · 编码章节
- **[*Integrating Compression and Execution in Column-Oriented DBMS*](https://people.cs.umass.edu/~dbae/arvindcompression.pdf)** (Abadi et al., SIGMOD 2006) —— "在压缩数据上直接计算"的奠基论文
- **[DuckDB · Lightweight Compression](https://duckdb.org/2022/10/28/lightweight-compression.html)** —— 工程博客：为什么 Dict + RLE + Bit-pack 比 Zstd 更关键

## 相关

- [Parquet](parquet.md) · [ORC](orc.md) · [Lance Format](lance-format.md)
- [列式 vs 行式](columnar-vs-row.md) · [向量化执行](../query-engines/vectorized-execution.md) · [谓词下推](../query-engines/predicate-pushdown.md)
