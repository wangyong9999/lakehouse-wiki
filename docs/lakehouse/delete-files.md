---
title: Delete Files（行级删除）
type: concept
tags: [lakehouse, row-level-delete]
aliases: [Row-level Delete, Deletion Vectors]
related: [lake-table, streaming-upsert-cdc, compaction]
systems: [iceberg, paimon, hudi, delta]
status: stable
---

# Delete Files（行级删除）

!!! tip "一句话理解"
    在**不重写数据文件**的前提下，用独立的小文件标记"哪些行被删除"。这让湖表支持**低成本的高频 update/delete**，代价是读时要合并，所以必须配合 [Compaction](compaction.md)。

## 为什么需要它

早期湖表只能 append + 整文件重写。对于 GDPR 删除、CDC upsert 这类场景，每次重写 GB 级数据文件成本太高。解决思路：**写一个小文件说"这个 base 文件里第几行失效了"**——读时 reader 合并生效。

## 两种粒度

### Position Delete

记录"在哪个 data file 的第几行失效"：

```
data_file_a.parquet,row=42
data_file_a.parquet,row=87
data_file_b.parquet,row=3
```

- **精确**：直接按 row position 过滤
- **快**：读时按 position set 跳过
- **需要知道 row 位置**：写入者必须追踪

### Equality Delete

记录"这几个列=什么值的行失效了"：

```
user_id = 12345
order_id = 98765
```

- **灵活**：CDC 场景下 writer 不需知道 row position，写入 key 即可
- **慢**：读时要对每个 row 做值比较
- **常配合 sequence number** 使用以保证顺序正确

Iceberg v2 spec 原生支持这两种；Hudi / Paimon / Delta 各有等价物（Deletion Vectors 等）。

## Iceberg Delete File 的使用姿势

```
metadata.json → manifest-list → manifest
                                   ├── data_file_a (包含 user 1..1000)
                                   ├── data_file_b
                                   └── delete_file_x (position: a:42, a:87, b:3)
```

Reader 读 `data_file_a` 时，同时加载引用它的 delete file，把 row 42/87 过滤掉。

## Deletion Vectors —— 跨格式的共同方向

DV 不是 Delta 独有——Delta（v3+）、Iceberg（v3）、Paimon（0.9+）都采用了类似机制。本质是 per-data-file 的**位图**（Roaring bitmap）：

```
data_file_a.parquet → DV = bitmap(42, 87)
```

优点是读时直接按 bitmap 跳过，比 position delete 文件还快；缺点是 metadata 粒度更细，小文件问题更严重。

**Iceberg v3 的 DV 存在 Puffin 里**（`deletion-vector-v1` blob type），取代 v2 的独立 position-delete file。Delta DV 存 `_delta_log` + sidecar；Paimon 内置 DV 模式。未来湖表行级删除会逐步统一到 DV 形态。

## 和 CoW / MoR 的关系

- **CoW** 不需要 delete 文件 —— 每次 update/delete 直接重写 base
- **MoR** 核心依赖 delete 文件 —— 不重写，只追加 delta
- 所以"**MoR → 写快读慢 → 需要频繁 compaction → 用 delete 文件承担成本**"这条链是内在一致的

## 运维要点

- **delete 文件数必须监控**：长到一定量就要合并
- **合并时机**：通常是 `delta / base > 30%` 或 `delete 文件数 > 50`
- **GDPR / 合规删除**：用户数据删除法规要求"物理可验证"时，要做 CoW 或强制 compaction
- **读时缓存**：对频繁被读的 data file，delete file 应在查询引擎侧缓存

## 相关

- [Compaction](compaction.md) —— 消化 delete 文件的核心手段
- [Streaming Upsert / CDC](streaming-upsert-cdc.md) —— delete 文件的主要生产场景
- [Apache Iceberg](iceberg.md)

## 延伸阅读

- Iceberg spec v2 - Delete Files: <https://iceberg.apache.org/spec/#delete-files>
- Delta Lake Deletion Vectors: <https://docs.delta.io/latest/delta-deletion-vectors.html>
- *Efficient Row-Level Deletion in Apache Iceberg* —— 社区讨论
