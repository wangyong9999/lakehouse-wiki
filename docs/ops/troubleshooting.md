---
title: 故障排查手册 · 湖仓 + AI 全栈
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: Iceberg 1.6+ / v3 · Paimon 1.0+ · Spark 3.5+ · Trino 440+ · Flink 1.18+ · LanceDB · Milvus · UC / Polaris / Nessie · LLM 应用 · 2024-2026 实践
prerequisites: [observability, performance-tuning]
tags: [ops, troubleshooting, ai-troubleshooting, ml-troubleshooting, catalog]
aliases: [Troubleshooting, Debug Runbook]
related: [observability, performance-tuning, compaction, incident-management, disaster-recovery]
systems: [iceberg, paimon, spark, trino, flink, milvus, lancedb, unity-catalog, polaris, nessie]
status: stable
---

!!! warning "章节分工声明"
    - **本页**：**故障形状 + 排查树 + 修复姿势**（湖仓 + AI 全栈）
    - **事故响应流程 / SEV / Postmortem** → [incident-management](incident-management.md)
    - **观测指标 / Dashboard 设计** → [observability](observability.md)
    - **性能调优方法论** → [performance-tuning](performance-tuning.md)
    - **恢复 / DR** → [disaster-recovery](disaster-recovery.md)
    - 本页专注 **"看到这个现象怎么办"**——不讲流程、不讲治理、只讲 debug。

# 故障排查手册

!!! tip "一句话理解"
    生产湖仓 + AI 应用经常出的 **20 类问题** + 排查树 + 修复姿势。**出事时不慌**的唯一方法 = 提前见过这些形状。

!!! abstract "TL;DR"
    - 80% 的"查询慢"来自**数据布局 + 小文件 + delete files**
    - 80% 的"写挂"来自 **commit 冲突 + schema 漂移 + 外部 Catalog 问题**
    - 80% 的"数据对不上"来自 **CDC offset / snapshot 选错 / 时区**
    - 80% 的 **AI 应用异常** 来自 **模型版本漂移 / Embedding 不一致 / RAG 召回崩**
    - 80% 的 **GPU 训练炸** 来自 **OOM / 分布式通信 hang / checkpoint 坏**
    - **先看观测面板再动手** —— 观察 > 假设

## 组 1 · 湖仓查询 / 写入故障

### 问题 1：查询突然变慢

**检查顺序**：

1. EXPLAIN 看扫了多少字节 / 文件数
2. 如果文件数暴增 → 小文件未 compact，跑 `rewrite_data_files`
3. 如果扫描字节远超预期 → 谓词下推失效，检查 WHERE 是否有 UDF / CAST
4. 如果并发增加 → 引擎 resource group / queue 是否公平
5. 如果特定时间段慢 → 和 compaction / ETL 高峰冲突

**工具**：Trino Web UI / Spark History Server / Iceberg metadata tables (`table.files` / `table.snapshots`)

### 问题 2：Commit 冲突（concurrent modification）

**现象**：`ValidationException: Cannot commit, conflicting write`

**原因**：两个写作业对同一张表并发 commit，基于同一个 parent snapshot，只有一个成功。

**修复**：

- 写作业内置重试（Spark / Flink 默认有但次数有限）
- 不同作业**分不同分区写**（物理避免冲突）
- 批作业和流作业不要写同一张表（除非协调）
- 看 Catalog 是否正确实现 CAS

### 问题 3：小文件海啸

**现象**：某表查询慢、元数据 list 慢、S3 费用异常。

**检查**：

```sql
SELECT count(*) FROM my_table.files WHERE file_size_in_bytes < 16 * 1024 * 1024;
```

超过几千个 16MB 以下文件 = 需要治理。

**修复**：

- `rewrite_data_files` with target size
- Flink sink `sink.parallelism` + `bucket` 配合，控制并行度
- CDC 频率降低（增加 checkpoint interval）

### 问题 4：Delete file 积压

**现象**：MoR 表查询延迟缓慢上升。

**检查**：

```sql
SELECT count(*), sum(record_count) 
FROM my_table.delete_files;
```

和数据文件的比例如果 > 30%，该合了。

**修复**：

```sql
CALL system.rewrite_position_deletes('my_table');
CALL system.rewrite_data_files('my_table', strategy => 'sort');
```

### 问题 5：Schema 演化破坏下游

**现象**：下游作业报错 "column not found" 或类型不兼容。

**常见来源**：

- 上游偷偷 drop column
- 类型从 INT 改成 STRING
- 字段重命名且下游 hardcode 了名字

**预防**：

- CI 对 schema 变化做 **breaking change** 检测（见 [change-management](change-management.md) §Schema Evolution）
- 下游作业用 Iceberg 列 ID 引用
- 契约化（见 [ml-infra/data-quality-for-ml §Data Contract](../ml-infra/data-quality-for-ml.md)）

**应急**：回滚 Snapshot + 通知上游。

### 问题 6：Time Travel 不到

**现象**：`VERSION AS OF xxx` 报错 "Snapshot not found"。

**原因**：`expire_snapshots` 清了。

**修复**：

- 重要 snapshot 打 **tag**（带 RETAIN）
- 调整保留策略拉长
- 这次只能从备份恢复或重跑 ETL（见 [disaster-recovery](disaster-recovery.md) §灾难 1）

### 问题 7：CDC 延迟 / 数据丢

**现象**：Paimon 表落后上游分钟到小时级。

**检查**：

1. Flink CDC source offset lag
2. Kafka consumer group lag
3. Flink checkpoint interval
4. Sink 端小文件导致的 commit 慢

**修复**：

- 增加 Flink 并行度（但注意 Kafka partition 数上限）
- 调 checkpoint interval
- 加压 sink（多 writer 并行）

### 问题 8：对象存储 API 费用异常

**现象**：S3 LIST / GET 费用月增 3 倍。

**原因**（排列组合）：

- 小文件爆炸 → list 次数暴增
- 客户端轮询
- 跨区读取
- 某个作业高频 HEAD 同一批 key

**修复**：

- 聚合小文件
- 限流 bad-client
- 使用 inventory 报告统计访问模式

## 组 2 · Catalog 服务故障

### 问题 9：Catalog 服务慢 / 挂（通用）

**现象**：所有引擎查询超时，或 commit 卡死。

**检查**：

- Catalog 服务端 CPU / 内存
- 背后 RDBMS（HMS / UC 后端 Postgres / Polaris 后端）是否打爆
- 网络连通

**修复**：

- 读副本分流
- 连接池大小调优
- 重启 Catalog 服务（保留 Snapshot，重启后 self-heal）

### 问题 10：Unity Catalog / Polaris / Nessie 专项故障

**Unity Catalog**：

| 现象 | 可能原因 | 修复 |
|---|---|---|
| 403 `PERMISSION_DENIED` · 明明有权限 | UC 的 `USE CATALOG` / `USE SCHEMA` 三级权限没给全 | 检查 `SHOW GRANTS`，三层都要有 |
| `Credential vending failed` | STS 信任关系 / 角色边界未配 | 检查 UC Storage Credential 的 IAM trust policy |
| Databricks 外部客户端（Trino/Spark）报 Iceberg REST 401 | PAT 过期 / OAuth 配置错 | 轮换 token · 用 SP（Service Principal）不用个人 PAT |
| 外部表 `SYNC` 后 schema 不一致 | UC metadata 与底层 Iceberg metadata.json 漂移 | `REFRESH TABLE` + 检查 UC vs 文件层 snapshot |

**Apache Polaris**：

| 现象 | 可能原因 | 修复 |
|---|---|---|
| Iceberg REST `NoSuchNamespaceException` · 但实际存在 | Principal 的 Role 缺少 NAMESPACE 级权限 | grant 到 CATALOG_ADMIN 或对应 namespace role |
| 跨引擎写冲突频繁 | Polaris CAS 冲突窗口大 | 降低并发或按分区路由 |
| Credential vending 403 | storage config 的 trust relationship 未配 | 检查 `storageConfigInfo` 和云侧角色 |

**Nessie**：

| 现象 | 可能原因 | 修复 |
|---|---|---|
| Merge 失败 `Conflict` | 两分支对同一表做了不兼容变更 | merge strategy 选 `NORMAL` · 手动解决或 rebase |
| `ReferenceNotFoundException` | 分支 / tag 写错或被删 | `nessie branch list` 核对 · 从 commit hash 恢复 |
| Version Store（Postgres / RocksDB）慢 | store 过大未压缩 | `nessie-gc` 定期清理 · 或切到 JGit 后端 |
| 跨引擎 commit history 不一致 | 引擎未统一用 Nessie REST | 所有引擎走 Nessie catalog · 不要混用 HMS |

**HMS（遗留）**：

| 现象 | 可能原因 | 修复 |
|---|---|---|
| `MetaException` 大量抛出 | HMS backend RDBMS 锁表 | 检查长事务 · 调整 Derby/MySQL 连接池 |
| 分区元数据膨胀 | 分区数百万级 | 启用 HMS cache · 或迁移到 UC/Polaris |

**通用建议**：Catalog 级故障最致命——**数据在但查询全挂**。Catalog 必须有独立 DR，详见 [disaster-recovery §灾难 2](disaster-recovery.md)。

## 组 3 · AI 应用故障（2024-2026 新增）

!!! info "本组定位 · 故障形状 + 定位三步 + canonical 指针"
    每个问题只列 **典型现象 + 排查顺序 + 修复姿势** · 不展开机制 / 深度工具 —— **深度见各 canonical 页**（行内标注）。本组目的 = **生产事故发生时能快速定位到哪个 canonical 去查** · 不重复 ai-workloads/ · ml-infra/ · retrieval/ 章节的深度内容。

### 问题 11：LLM 调用延迟 / 超时

**现象**：应用端 p95 从 2s 涨到 15s · 或 504 超时率飙升。

**排查**：

1. **模型端**：OpenAI/Anthropic status page · 是否区域性降级？
2. **路由层**：LLM Gateway（LiteLLM / Portkey）是否过载？rate limit 是否触发？
3. **Prompt 膨胀**：最近 prompt token 数是否增长？（context 堆积 / RAG 召回文档变长）
4. **流式**：是否从 streaming 切到非 streaming（首 token 延迟不同）
5. **上下游依赖**：Tool calling 的外部 API 是否慢？

**修复**：

- 切到备用模型（claude-opus → claude-sonnet / GPT-4 → GPT-4-mini 降级）
- 启用 **Prompt Cache**（Anthropic 原生支持 · 省 token 又加速首 token）
- Context 裁剪 · 限制 RAG top-k
- Circuit breaker · 对慢 provider 自动熔断
- 详见 [ai-workloads/llm-gateway](../ai-workloads/llm-gateway.md)

### 问题 12：幻觉率突增 / 回答质量下降

**现象**：用户反馈答案胡编 · 评估集 faithfulness 从 0.85 掉到 0.60。

**排查**：

1. **模型版本漂移**：provider 是否悄悄升级 snapshot？（`gpt-4-turbo` 非 pinned · `claude-sonnet-4-5` 是否换了 minor 版本？）
2. **Prompt 改动**：最近是否改了 system prompt · 某个 few-shot example？
3. **RAG 召回质量**：检索到的 chunk 是否相关？（recall 指标）
4. **Embedding 不一致**：索引用的 embedding model vs 查询用的 embedding model 是否相同？
5. **Chunking 变化**：文档重新 chunk 了吗？chunk size / overlap 改过吗？

**修复**：

- **Pin 模型版本**：`gpt-4-turbo-2024-04-09` · `claude-sonnet-4-5-20260315` 明确版本
- 回滚最近 prompt 变更（Registry 切上一版本 · 详见 [ai-workloads/prompt-management](../ai-workloads/prompt-management.md)）
- RAG 侧跑 RAGAS / TruLens 看 faithfulness / answer_relevancy 分解
- 重建索引时固定 embedding 版本

### 问题 13：向量检索召回异常下降

**现象**：同一套 embedding，recall@10 从 0.85 掉到 0.70。

**排查**：

1. Embedding 模型版本有没有悄悄变？（OpenAI text-embedding-3 minor 版本 · 自建模型 checkpoint 被覆盖）
2. 向量索引重建策略 / 新 fragment 是否及时建索引？
3. 查询侧 `ef` / `nprobe` / `topk` 参数是否被改？
4. 数据分布是否发生漂移（新类别涌入 · 长尾数据比例变化）？
5. 是否有 filter pushdown 导致召回池变小？（metadata 过滤 + ANN 的交互）

**修复**：

- 固定 embedding model + version · 严格版本 pinning · 记 `embedding_version` 字段
- 监控 index lag（新数据到索引的延迟）
- 调整 ANN 参数：HNSW 的 `ef_search` 从 64 → 128 · IVF 的 `nprobe` 从 16 → 32
- Hybrid retrieval（BM25 + dense）补召回
- 详见 [retrieval/hnsw](../retrieval/hnsw.md) · [retrieval/ivf-pq](../retrieval/ivf-pq.md) · [retrieval/filter-aware-search](../retrieval/filter-aware-search.md)

### 问题 14：向量库 OOM / 崩溃

**Milvus**：

| 现象 | 原因 | 修复 |
|---|---|---|
| QueryNode OOM | 单 collection 太大 · mmap 未开 | 开启 `common.mmap.enabled` · 或拆 collection |
| 查询延迟尖刺 | Segment 合并中 | 低峰期手动 compact · 调 `compactionTrigger` |
| 插入阻塞 | Flush 慢 | 增加 DataNode · 检查对象存储延迟 |

**LanceDB**：

| 现象 | 原因 | 修复 |
|---|---|---|
| 查询慢 · 未使用索引 | Fragment 数过多无索引 | `create_index` · 或定期 `optimize` |
| Append 后查询漏数据 | 索引延迟 | 强制索引更新 · 或查询带 `use_index=false` 兜底 |

**Qdrant / Weaviate / Pinecone**：看厂商 dashboard · 常见是配额打满（vectors limit / QPS limit）。

### 问题 15：Agent 死循环 / 失控

**现象**：Agent 调用 tool 不停 · token 成本飙升 · 或卡在同一步反复。

**排查**：

1. **最大步数限制**：是否有 `max_iterations` / `max_steps`？
2. **Tool 调用历史**：最近 N 步是否在调同一个 tool 相同参数？（循环）
3. **Planner 质量**：LLM 是否误解了任务？prompt 是否清晰？
4. **Tool 错误处理**：tool 返回 error 是否被 agent 看到 · 是否在无脑重试？

**修复**：

- **硬限制**：`max_iterations=10` / `max_tokens_budget=50k` / `max_wall_time=5min`
- **重复检测**：同 tool+同参数连续 3 次 → 中止
- **Budget Guard**：token / 成本级的熔断
- **人工回退**：复杂任务降级到 human-in-the-loop
- 详见 [ai-workloads/agent-patterns](../ai-workloads/agent-patterns.md)

### 问题 16：Prompt 注入 / 越狱攻击

**现象**：用户输入触发了意料外的行为（泄露 system prompt · 绕过 guardrail · 调用不该调用的 tool）。

**排查**：

1. **Guardrail 是否启用**：Llama Guard / Prompt Shield / NeMo Guardrails
2. **输入清洗**：是否检测 "ignore previous instructions" 等模式
3. **权限边界**：Agent 是否有不该有的 tool 权限（写数据库 · 执行代码）
4. **日志**：是否记录了完整的 prompt + response 用于审计

**修复**：

- 启用 LLM 侧 guardrail + 输入/输出双层过滤
- Tool 权限最小化 · 高危操作二次确认
- System prompt 不放敏感信息（假设会泄露）
- 详见 [security-permissions](security-permissions.md) §AI 安全 · [compliance](compliance.md) §AI 合规

## 组 4 · ML 训练 / Serving 故障

!!! info "本组定位"
    同组 3 · 短概述 + 定位 + canonical 指针。深度见 [ml-infra/](../ml-infra/index.md) · 尤其 [training-orchestration](../ml-infra/training-orchestration.md) · [model-serving](../ml-infra/model-serving.md) · [gpu-scheduling](../ml-infra/gpu-scheduling.md)。

### 问题 17：GPU OOM / 训练崩溃

**现象**：`CUDA out of memory` · `NCCL error` · 训练 hang 住。

**GPU OOM 排查**：

1. **Batch size 过大**：gradient accumulation 替代
2. **Activation checkpointing 未开**：大模型必须开（trade compute for memory）
3. **Mixed precision 配置**：BF16 / FP16 正确吗？
4. **内存碎片**：`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`（PyTorch 2.1+）
5. **数据加载**：DataLoader `num_workers` 过大占内存
6. **Optimizer state**：Adam 的 optimizer state 是模型参数的 2-3 倍 · 考虑 ZeRO / FSDP

**分布式训练 hang 排查**：

| 现象 | 可能原因 | 定位 |
|---|---|---|
| 所有 rank 都停止日志 · 但进程没退出 | NCCL all-reduce 卡死 | `py-spy dump` 看栈 · `NCCL_DEBUG=INFO` 看通信 |
| 某个 rank 先挂 · 其他等 | OOM 或其他 rank 独有错误 | 查最早挂的 rank 日志 |
| Hang 在 checkpoint save | I/O 慢 · 对象存储限流 | 检查 S3 metrics · 用 async save |
| Loss NaN | 学习率过高 / 数据脏 / FP16 溢出 | 切回 FP32 验证 · 检查 input |

**修复工具**：`nvidia-smi` · `dcgm-exporter` · PyTorch Profiler · `nsys` · `rccl-tests`

**深度见** [ml-infra/gpu-scheduling](../ml-infra/gpu-scheduling.md) · [ml-infra/training-orchestration](../ml-infra/training-orchestration.md)。

### 问题 18：Checkpoint 坏 / 无法恢复

**现象**：从 checkpoint 恢复报 `state_dict` 不匹配 · 或文件损坏。

**排查**：

1. **模型结构变化**：代码改动导致 layer 名字变化（strict=False 可绕过但可能漏加载）
2. **文件损坏**：对象存储传输中断 · 没开 multipart complete 校验
3. **版本不兼容**：PyTorch 版本升级后格式变化
4. **Sharded checkpoint**：FSDP / DeepSpeed 的 shard 文件不全

**修复**：

- Checkpoint 写完后做 **checksum 校验**（S3 ETag · 或主动 MD5）
- 保留 **N 个历史 checkpoint**（不要只留 latest）
- 模型代码版本化 · checkpoint metadata 记 `torch_version` / `model_commit`
- 关键模型 · checkpoint 跨区复制

**深度见** [ml-infra/training-orchestration](../ml-infra/training-orchestration.md) · [ml-infra/model-registry](../ml-infra/model-registry.md)。

### 问题 19：训练集复现不了

**现象**：同样代码、同样模型、和一周前训的结果不一样。

**原因**：

- 训练集依赖的 Iceberg snapshot 被过期了（只有一个指针 latest，latest 变了）
- 模型代码依赖 LLM / Embedding API，API 模型升级
- Feature Store 的特征计算逻辑改了
- Random seed 未固定 · 或某库不受 seed 控制

**修复**：

- 训练集**物化成独立表 + Tag**（见 [scenarios/offline-training-pipeline](../scenarios/offline-training-pipeline.md)）
- 记 `dataset_snapshot_id` / `model_version` / `embedding_version` / `feature_view_version`
- 固定 `torch.manual_seed` + `numpy.random.seed` + `random.seed` + `CUBLAS_WORKSPACE_CONFIG`
- 详见 [ml-infra/experiment-tracking](../ml-infra/experiment-tracking.md) · [scenarios/offline-training-pipeline](../scenarios/offline-training-pipeline.md)

### 问题 20：模型 Serving 异常

**现象**：

- 延迟 p99 突然飙升
- 吞吐下降 · QPS 上不去
- 预测分布漂移（但输入看起来没变）

**排查**：

| 现象 | 可能原因 | 定位 |
|---|---|---|
| p99 尖刺 | GC pause · batch queue 积压 | Prometheus metrics `gc_pause_seconds` · queue depth |
| 吞吐退化 | 某新版模型计算量大 · GPU 利用率已满 | `nvidia-smi dmon` · 看 SM 利用率 |
| 冷启动慢 | 模型文件从对象存储拉取 | 本地 cache · 或 init container 预热 |
| 预测分布漂移 | 模型版本切了但未公告 | `model_version` 标签检查 · champion alias 指向 |
| Serving OOM | KV cache（LLM）无限增长 | vLLM `max_num_seqs` 限制 · 开启 PagedAttention |

**修复参考**：[ml-infra/model-serving §Rollback runbook](../ml-infra/model-serving.md)

## 组 5 · 权限与安全故障

### 问题 21：权限异常

**现象**：某用户本应能读 A 表却 403；另一用户应看不到 B 的 PII 却看到。

**排查**：

1. Catalog 层 ACL（`SHOW GRANTS ON TABLE A TO USER x`）
2. 存储层：STS token 权限是否限制到这张表
3. 行列级 policy 是否生效（`EXPLAIN` 看 filter 应用）
4. 身份上下文：OIDC 传的 group claim 是否正确
5. Credential vending 是否给了错误的 scope

**修复**：按 [security-permissions](security-permissions.md) 的四层防线排查，从上到下。

## 组 6 · Iceberg v3 新特性相关故障（2025-2026）

Iceberg v3（2025 发布）引入 Deletion Vectors、Row Lineage、Default Values、Variant Type 等新特性 · 和老引擎混用时常见故障：

| 现象 | 原因 | 修复 |
|---|---|---|
| 旧 Spark / Trino 读 v3 表报 `UnsupportedOperationException` | 引擎版本不支持 v3 | 升级到支持 v3 的版本（Spark 4.0+ · Trino 450+）· 或降级表到 v2 |
| Deletion Vector 读出数据和预期不符 | 写端用 DV · 读端按 positional deletes 解读 | 统一所有引擎到 DV 支持版本 · 或禁用 DV 写（`write.delete.mode=copy-on-write`） |
| Default value 列读出 NULL | 旧引擎未应用 default | 升级引擎 · 或显式 backfill 默认值 |
| Variant 类型查询失败 | 引擎不支持 Variant | 查询端 CAST 成 JSON string · 或等待引擎支持 |
| Row Lineage 字段丢失 | 中间写入引擎未保留 `_row_id` / `_last_updated_sequence_number` | 全链路用支持 v3 的引擎 |

**通用原则**：升 v3 前 · **全链路所有引擎版本对齐** · 先在测试表验证 · 再切生产。

## 通用原则

- **先看 dashboard 再动手**：不要凭感觉
- **别刻意 "快速修复"**：临时补丁变永久坑
- **改动留 ADR**：一年后你能回头知道为啥
- **事后复盘**：每次 P1 写 postmortem（见 [incident-management](incident-management.md) §Postmortem）
- **Runbook 化**：同一个故障出第 2 次 · 写进 runbook

## 相关

- [可观测性](observability.md)
- [性能调优](performance-tuning.md)
- [事故管理](incident-management.md)
- [灾难恢复](disaster-recovery.md)
- [变更管理](change-management.md)
- [Compaction](../lakehouse/compaction.md) · [Delete Files](../lakehouse/delete-files.md)
- [ml-infra/model-serving](../ml-infra/model-serving.md) · [ml-infra/experiment-tracking](../ml-infra/experiment-tracking.md)
- [ai-workloads/llm-gateway](../ai-workloads/llm-gateway.md) · [ai-workloads/agent-patterns](../ai-workloads/agent-patterns.md)

## 延伸阅读

- Iceberg Maintenance Guide · v3 Spec
- *Debugging Spark Applications*（各种博客）
- *The Site Reliability Workbook* (Google SRE) · Ch 12 Incident Response
- PyTorch Distributed Debugging Guide
- NVIDIA DCGM Documentation
- OpenAI / Anthropic Status Pages · 故障历史参考
