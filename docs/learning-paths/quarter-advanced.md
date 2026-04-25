---
title: 一季度资深路径
type: learning-path
tags: [learning-path, advanced]
audience: 已完成 1 月 AI 或 1 月 BI 路径、想成为一体化湖仓方向资深工程师的人
duration: 3 月
status: stable
last_reviewed: 2026-04-22
---

# 一季度资深路径

!!! tip "目标"
    季度结束时，你应该能**独立设计一个端到端的一体化湖仓方案**，并能有理有据解释每一步为什么选 X 不选 Y。你看本手册时不再是"学"，而是"给它补"。

## 前置

- 完成 [一周新人路径](week-1-newcomer.md)
- 完成 [一月 AI](month-1-ai-track.md) 或 [一月 BI](month-1-bi-track.md) 至少一条

## Month 1 · 存算与 Catalog 深入

### Week 1-2 · 存算底座

- [存算分离](../foundations/compute-storage-separation.md)
- [一致性模型](../foundations/consistency-models.md)
- [谓词下推](../query-engines/predicate-pushdown.md)
- [向量化执行](../query-engines/vectorized-execution.md)
- [Lance Format](../foundations/lance-format.md) —— 深度读
- 做：用 DuckDB 直连 S3 + Iceberg 跑 TPC-DS 10GB，看下推生效情况

### Week 3-4 · Catalog 治理平面

- 全部 Catalog 系统页 + [Catalog 全景对比](../compare/catalog-landscape.md)
- [统一 Catalog 策略](../catalog/strategy.md)
- [安全与权限](../ops/security-permissions.md)
- [数据治理](../ops/data-governance.md)
- [ADR-0004 Catalog 选型](../adr/0004-catalog-choice.md)
- 做：本地起 Polaris（或 Nessie）+ Spark + Trino，走一遍"注册表 → 查询 → 权限"

## Month 2 · 一体化架构 + 多模管线

### Week 5-6 · 一体化

- [Lake + Vector 融合架构](../unified/lake-plus-vector.md)
- [跨模态查询](../retrieval/cross-modal-queries.md)
- [Compute Pushdown](../query-engines/compute-pushdown.md)
- [案例拆解](../cases/studies.md)
- [多模数据建模](../unified/multimodal-data-modeling.md)
- 做：设计一张 `multimodal_assets` 表 schema（图+文+音），画出端到端架构图，写成 ADR 草稿

### Week 7-8 · 多模管线实操

- [图像管线](../pipelines/image-pipeline.md)
- [视频管线](../pipelines/video-pipeline.md)
- [音频管线](../pipelines/audio-pipeline.md)
- [文档管线](../pipelines/document-pipeline.md)
- [Embedding 流水线](../ml-infra/embedding-pipelines.md)
- 做：挑一种模态（如图像），端到端搭一条"原始 → embedding → 入湖 → 跨模态查询"

## Month 3 · ML 基础设施 + 生产化

### Week 9-10 · ML Infra

**推荐顺序**（先叙事总览 · 再数据底座 · 再训练 · 最后部署运维）：

1. [MLOps 生命周期](../ml-infra/mlops-lifecycle.md) —— 建立六环节全局
2. [Feature Store](../ml-infra/feature-store.md) —— 数据底座（PIT / 训推一致）
3. [训练编排](../ml-infra/training-orchestration.md) —— FSDP2 / torchtitan / DCP
4. [Model Registry](../ml-infra/model-registry.md) —— alias API / Model Card / 合规
5. [Model Serving](../ml-infra/model-serving.md) —— Inference Graph / Shadow / Canary / Rollback
6. [Model Monitoring](../ml-infra/model-monitoring.md) —— Drift / Auto-retrain 契约
7. [GPU 调度](../ml-infra/gpu-scheduling.md) —— 资源 + FinOps
8. [LLM Fine-tuning](../ml-infra/fine-tuning-data.md) —— LoRA / QLoRA / DPO 一体（LLM 应用方向必读）

- 做：把 Week 7-8 的 embedding 模型注册到 MLflow（alias champion）+ 用 Ray Serve 部署 + 配一条 drift 告警

### Week 11-12 · 生产化

- [可观测性](../ops/observability.md)
- [性能调优](../ops/performance-tuning.md)
- [成本优化](../ops/cost-optimization.md)
- [故障排查手册](../ops/troubleshooting.md)
- [迁移手册](../ops/migration-playbook.md)
- 做：为你 Month 2 搭的多模方案写一套监控 + 成本预算 + 容量规划

## 毕业成果

### 交付物

- [ ] 一份完整架构设计（图 + 表 + 权衡说明）
- [ ] 至少 2 条新 ADR 贡献到本手册
- [ ] 至少 1 篇 paper note 融入对应机制章的 §前沿进展 节
- [ ] 在本手册新增或深挖一个概念 / 系统 / 对比 / 场景页
- [ ] 做一次内部分享（1 小时），讲"我设计的一体化湖仓方案"

### 自测（能回答）

- [ ] 给你一个多模 AI 新场景，你能 1 小时画出合理架构
- [ ] 面对一个"BI + AI" 需求，你能说清什么时候选 Iceberg / Paimon / LanceDB / Milvus
- [ ] 能独立 debug 一个"查询突然慢了 10 倍"的问题
- [ ] 知道 GDPR 删除要求下，湖 + 向量 + 模型都要删什么
- [ ] 能评估一个新 OSS 项目值不值得引入（从架构契合度到运维成本）

## 下一步

- 写一条 **ADR** 推动团队技术选型
- **审团队 PR**（从消费者变成供应者）
- 关注至少 2 个上游项目的社区讨论（Iceberg / Paimon / LanceDB / Milvus）
