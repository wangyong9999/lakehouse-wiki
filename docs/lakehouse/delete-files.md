---
title: Delete Files（行级删除）
type: concept
level: A
depth: 资深
last_reviewed: 2026-04-18
applies_to: Iceberg v2 (position/equality) · v3 (Deletion Vector) · Delta 4.0+ · Paimon 1.4+ · Hudi 1.0.2+
tags: [lakehouse, row-level-delete]
aliases: [Row-level Delete, Deletion Vectors]
related: [lake-table, streaming-upsert-cdc, compaction, puffin, snapshot]
systems: [iceberg, paimon, hudi, delta]
status: stable
---

# Delete Files（行级删除）

!!! tip "一句话理解"
    在**不重写数据文件**的前提下，用独立的小文件标记"哪些行被删除"。这让湖表支持**低成本的高频 update/delete**，代价是读时要合并，所以必须配合 [Compaction](compaction.md)。**2024-2025 各家都在往 Deletion Vector 形态收敛**。

!!! abstract "TL;DR"
    - **三代演进**：Position Delete File → Equality Delete File（v2）→ Deletion Vector（v3 / Delta 3+）
    - **DV 是 per-data-file 的 Roaring bitmap**——比 position delete 文件更紧凑、读更快
    - **Iceberg v3 的 DV 存在 Puffin 里**（`deletion-vector-v1` blob）；Delta DV 存 `_delta_log` sidecar
    - **Equality Delete 需 sequence number** 保证新老删除的应用顺序
    - **MoR 必配 compaction**——否则 delete 文件堆积查询会越来越慢

## 1. 为什么需要它

早期湖表只能 append + 整文件重写。对于 GDPR 删除、CDC upsert 这类场景，每次重写 GB 级数据文件成本太高。解决思路：**写一个小文件说"这个 base 文件里第几行失效了"**——读时 reader 合并生效。

## 2. 两种粒度（v2 做法）

### Position Delete

记录"在哪个 data file 的第几行失效"：

```
data_file_a.parquet, row=42
data_file_a.parquet, row=87
data_file_b.parquet, row=3
```

- **精确**：直接按 row position 过滤
- **快**：读时按 position set 跳过
- **代价**：writer 必须追踪 row 位置（写入复杂度高）

### Equality Delete

记录"这几个列=什么值的行失效了"：

```
user_id = 12345
order_id = 98765
```

- **灵活**：CDC 场景下 writer 不需知道 row position，写入 key 即可
- **慢**：读时要对每批 row 做值比较
- **需要 sequence number 保证顺序**（见下段）

Iceberg v2 spec 原生支持这两种；Hudi / Paimon / Delta 各有等价物。

## 3. Sequence Number · Equality Delete 的正确性基石

Equality delete 可能出现一种微妙错误：**一个老的 delete 文件"删掉"一个新的 insert**。例如：

```
commit 10: INSERT user_id=123
commit 11: DELETE WHERE user_id=123     ← 写 equality delete "user_id=123"
commit 12: INSERT user_id=123           ← 又写进来（新行）
```

如果 reader 不加区分地把 commit 11 的 equality delete 应用到 commit 12 的新行，就会错误地把新行删掉。

**解法**：每个 snapshot 有 **`sequence-number`**（v2 spec 引入）。规则是：

> **Equality delete（sequence-number = D）只应用于 sequence-number 严格小于 D 的 data file**

按 Iceberg v2 spec：equality delete 对**同一个或后续 snapshot** 写入的 data file **不生效**。所以上例：

- commit 10 的 data file（seq=10）< commit 11 的 delete（seq=11）→ 被删 ✓
- commit 12 的 data file（seq=12）> commit 11 的 delete（seq=11）→ 不被删 ✓

这是湖表并发正确性的关键不变量，在 [Snapshot](snapshot.md) 的 `sequence-number` 字段上体现。

## 4. Deletion Vector · 跨格式的共同方向

DV 不是 Delta 独有——**Delta 3+、Iceberg v3、Paimon 0.9+ 都采用**。本质是 per-data-file 的 **Roaring bitmap**：

```
data_file_a.parquet → DV = Roaring bitmap(42, 87)
```

- **紧凑**：Roaring bitmap 对稀疏 bitmap 有极好的压缩
- **读快**：直接按 bitmap 做 row skip，比 position delete file 少一层间接
- **和 Puffin 整合**：Iceberg v3 把 DV 作为 `deletion-vector-v1` blob 存在 Puffin 里

### v2 Position Delete vs v3 Deletion Vector

| 维度 | v2 Position Delete File | v3 Deletion Vector |
|---|---|---|
| 存储形式 | 独立 Parquet 文件（列：`file_path`, `pos`） | Puffin blob（Roaring bitmap）|
| 定位单位 | 每个 delete 是一条 `(file, pos)` 记录 | 每个 data file 一个 bitmap |
| 读侧合并成本 | 中（构造 position set + 过滤） | 低（直接位图 skip） |
| 写侧成本 | 追加新 delete 文件 | 重写该 data file 的 DV |
| 小文件问题 | delete 文件数量易爆 | DV 文件数量等于被删 data file 数 |
| 消费生态 | v2 reader | v3 reader |

**过渡期**：v2 表 + v2 reader 继续用 position delete；新表用 v3 + DV；跨版本读写要版本协商。v3 DV 是 [Iceberg v3 整体能力演进](iceberg.md) 的一部分——配套还有 Row Lineage / Variant / Geometry 等新特性（见 Iceberg 页"v3 spec 演进"段）。

### 跨格式 DV 实现矩阵 · Iceberg v3 / Delta 3+ / Paimon 0.9+

三家 DV 的位图本体都是 **Roaring bitmap**；但载体、开启方式、读侧融合机制都不同：

| 维度 | Iceberg v3 DV | Delta 3+ DV | Paimon 0.9+ DV |
|---|---|---|---|
| **载体** | Puffin 文件的 `deletion-vector-v1` blob | `_delta_log/` 下的 sidecar（`.deletion-vector-<uuid>.bin`）| 独立 DV 文件（`dv-*.bin`）+ manifest 引用 |
| **开启** | `format-version = 3` 后默认 | `delta.enableDeletionVectors = true` | `deletion-vectors.enabled = true`（建表/ALTER）|
| **被什么引用** | Manifest entry + Puffin blob | commit JSON 里 `add/remove` action 的 `deletionVector` 字段 | Paimon manifest 里 DV 条目（类似 data file 条目） |
| **压缩** | Puffin blob 支持 per-blob 压缩 | 原始字节 | 原始字节 |
| **对 MoR 的替代** | 替代 v2 position-delete file | 替代"重写文件" | 替代 log 文件合并（DV mode） |
| **读路径融合** | reader 按 Manifest 找 DV Puffin blob → 过滤 | reader 按 `_delta_log` 找 sidecar → 过滤 | reader 按 manifest 找 DV → 过滤 |
| **跨引擎兼容** | v3-aware reader 都支持（Spark 4.0 最完整）| Delta reader 3.0+ | Paimon 0.9+ 所有 reader |

**共同原理**：**避免 "重写大数据文件" 或 "堆积 delete 文件" 两个极端**，用 per-file 紧凑位图做行级 skip。

**对读者的选择启示**：

- 三家都在 DV 路径上了 → **这是 2026 行级删除的既定方向**
- 载体差异决定**跨格式互操作时 delete 语义需要翻译**（Apache XTable 的关键工作之一）
- 和 [Puffin](puffin.md) + [Iceberg](iceberg.md) 的"v3 spec 演进"段对照阅读，能看清 Iceberg 把 DV 标准化成 blob 的架构意图

## 5. Iceberg Delete File 的使用姿势

```
metadata.json → manifest-list → manifest
                                   ├── data_file_a (user 1..1000)
                                   ├── data_file_b
                                   └── delete_file_x (position: a:42, a:87, b:3)
                                   └── puffin_file_y (DV for a / b) [v3]
```

Reader 读 `data_file_a` 时，同时加载引用它的 delete file / DV，把对应 row 过滤掉。

## 6. MoR 读路径伪代码

读一个被删除过的 data file 时：

```python
def read_data_file(data_file, ref_delete_files, ref_dv_blobs):
    # 1. 收集应用于 data_file 的 delete 载体
    #    equality delete 的 seq 必须 > data_file.seq 才生效（spec 规则）
    #    position delete / DV 通常直接绑定到具体 data file，无 seq 歧义
    deletes_to_apply = [
        d for d in ref_delete_files + ref_dv_blobs
        if d.applies_to(data_file)
           and (d.type != 'equality-delete' or d.sequence_number > data_file.sequence_number)
    ]

    # 2. 构造"被删除 row position"的位图
    deleted_positions = RoaringBitmap()
    for d in deletes_to_apply:
        if d.type == 'position-delete':
            for row in d.positions():
                if row.file == data_file.path:
                    deleted_positions.add(row.pos)
        elif d.type == 'deletion-vector':
            deleted_positions.or_inplace(d.bitmap)
        elif d.type == 'equality-delete':
            # 需要对 data file 扫一遍做比较
            for (pos, row) in data_file.scan():
                if d.matches(row):
                    deleted_positions.add(pos)

    # 3. 读 data file 时跳过被删 position
    for (pos, row) in data_file.scan():
        if pos not in deleted_positions:
            yield row
```

关键点：
- **equality delete** 读时要扫 data file 做值比较（最慢）
- **position delete / DV** 读时直接按 position 跳过（快）
- **sequence number 过滤**保证并发正确性

## 7. 和 CoW / MoR 的关系

- **CoW** 不需要 delete 文件 —— 每次 update/delete 直接重写 base data file
- **MoR** 核心依赖 delete 文件 —— 不重写、只追加 delta
- 所以"**MoR → 写快读慢 → 需要频繁 compaction → 用 delete 文件承担成本**"这条链是内在一致的

## 8. 运维要点

- **delete / DV 数必须监控**：长到一定量就要合并
- **合并触发器**：通常 `delete 行数 / base 行数 > 30%` 或 `delete 文件数 > 50` 或 `DV 文件数 > 数据文件数 × 0.5`
- **合并命令**：Iceberg `CALL system.rewrite_position_delete_files` + `rewrite_data_files`；Delta `OPTIMIZE`（自动合 DV）；Paimon `full-compaction`；Hudi `run_compaction`
- **GDPR / 合规删除**：法规要求"物理可验证删除"时，要做 CoW 或强制 compaction（让 delete 真的变成 data file 的重写）
- **读时缓存**：对频繁被读的 data file，其 delete file / DV 应在查询引擎侧缓存
- **跨版本互操作**：v2 reader 读 v3 表（用 DV）会失败 —— 升级 reader 前先做兼容评估

## 9. 陷阱

- **delete 文件没配 compaction** → 几周后查询合并成本线性爆炸
- **同一 row 多次 equality delete** → 正确但浪费（合并时会去重）
- **并发 writer 不走 sequence number** → 老 delete 误删新 insert（见 §3）
- **误以为 DV 是 Delta 独有** → Iceberg v3、Paimon 都有对应机制
- **v3 DV 迁移时 reader 没升级** → 读失败或误读
- **把 delete 文件当"记录删除历史"** → 它是当前视图的补丁，不是审计日志

## 10. 相关

- [Compaction](compaction.md) —— 消化 delete 文件的核心手段
- [Streaming Upsert / CDC](streaming-upsert-cdc.md) —— delete 文件的主要生产场景
- [Puffin](puffin.md) —— Iceberg v3 DV 的载体
- [Snapshot](snapshot.md) —— sequence number 的定义页
- [Apache Iceberg](iceberg.md) · [Delta Lake](delta-lake.md)

## 11. 延伸阅读

- **[Iceberg spec · Delete Files (v2)](https://iceberg.apache.org/spec/#delete-files)**
- **[Iceberg spec · Deletion Vectors (v3)](https://iceberg.apache.org/spec/#version-3)**
- **[Delta Deletion Vectors](https://docs.delta.io/latest/delta-deletion-vectors.html)**
- **[Paimon Deletion Vectors mode](https://paimon.apache.org/docs/master/primary-key-table/deletion-vectors/)**
- *Efficient Row-Level Deletion in Apache Iceberg* —— 社区讨论
