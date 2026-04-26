---
title: 参考资料 · ML 平台 / MLOps
type: reference
status: stable
tags: [reference, references, ml-infra]
description: MLOps 生命周期 / Feature Store / Model Serving / 数据质量 经典
last_reviewed: 2026-04-25
---

# 参考资料 · ML 平台 / MLOps

## MLOps 框架与成熟度

- **[Google MLOps: Continuous delivery and automation pipelines in machine learning](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)** _(2020+, official-doc)_ —— 三级 maturity model (Manual / Pipeline Automation / CI/CD)。**与本 wiki ml-infra 章节"数据→模型生命周期→训练基建"组织部分对齐**（components: Data validation / Feature stores / ML metadata / Pipeline orchestration / Model registries / Monitoring）。
- **[Hidden Technical Debt in Machine Learning Systems](https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)** _(2015, paper - Google)_ —— ML 系统技术债经典论文，证明 "ML 代码只占系统 5%"。
- **[Continuous Delivery for Machine Learning (CD4ML)](https://martinfowler.com/articles/cd4ml.html)** _(2019, blog - Martin Fowler)_ —— ML CI/CD 实践。

## Feature Store

- **[Uber - Meet Michelangelo: Uber's Machine Learning Platform](https://www.uber.com/blog/michelangelo-machine-learning-platform/)** _(2017, blog)_ —— Feature Store 鼻祖博客。**工业验证**。
- **[Feast Documentation](https://docs.feast.dev/)** _(official-doc)_ —— Feast 是开源 Feature Store 事实标准。
- **[The Feature Store Architecture](https://www.tecton.ai/blog/feature-store-architecture/)** _(blog - Tecton)_ —— **厂商主张**（Tecton）但架构详尽。
- **[Hopsworks - Feature Store Capabilities](https://www.hopsworks.ai/post/feature-store-the-missing-data-layer-in-ml-pipelines)** _(blog)_ —— Hopsworks 视角的 FS。

## Model Serving

- **[KServe Documentation](https://kserve.github.io/website/)** _(official-doc)_ —— Kubernetes ML serving 标准。
- **[Ray Serve](https://docs.ray.io/en/latest/serve/index.html)** _(official-doc)_ —— Ray 生态 serving。
- **[NVIDIA Triton Inference Server](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/)** _(official-doc)_ —— GPU serving 标准。
- **[BentoML](https://docs.bentoml.com/)** _(official-doc)_ —— Python-first serving framework。

## LLM Inference

- **[vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention](https://blog.vllm.ai/2023/06/20/vllm.html)** _(2023, blog)_ —— PagedAttention 论文级博客。
- **[FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/abs/2205.14135)** _(2022, paper)_ —— FlashAttention v1 论文。
- **[SGLang: Efficient Execution of Structured Language Model Programs](https://arxiv.org/abs/2312.07104)** _(2023, paper)_ —— SGLang 结构化 LLM 执行。
- **[Speculative Decoding](https://arxiv.org/abs/2211.17192)** _(2022, paper - Google)_ —— 推测解码加速推理。

## 训练编排 + GPU

- **[Ray Train Documentation](https://docs.ray.io/en/latest/train/train.html)** _(official-doc)_ —— 分布式训练。
- **[Kubeflow Documentation](https://www.kubeflow.org/docs/)** _(official-doc)_ —— K8s ML 平台。
- **[NVIDIA - Multi-Instance GPU (MIG)](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/)** _(official-doc)_ —— GPU 切片调度。

## 实验跟踪 / Model Registry

- **[MLflow Documentation](https://mlflow.org/docs/latest/)** _(official-doc)_ —— Tracking / Projects / Models / Registry。
- **[Weights & Biases](https://docs.wandb.ai/)** _(official-doc)_ —— 商业 + 免费版本。
- **[Neptune.ai](https://docs.neptune.ai/)** _(official-doc)_ —— 实验跟踪。

## 数据质量与监控

- **[Great Expectations Documentation](https://docs.greatexpectations.io/docs/)** _(official-doc)_ —— 数据质量框架。
- **[WhyLabs - WhyLogs](https://docs.whylabs.ai/)** _(official-doc)_ —— ML 数据 / 模型监控。
- **[Evidently AI](https://docs.evidentlyai.com/)** _(official-doc)_ —— Drift detection。

## 综述与教科书

- **[Designing Machine Learning Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/)** _(2022, book - Chip Huyen)_ —— ML 系统设计经典。
- **[Machine Learning Engineering for Production](https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops)** _(course - Andrew Ng)_ —— MLOps 课程。
- **[Made With ML](https://madewithml.com/)** _(blog/course - Goku Mohandas)_ —— MLOps 实战。

---

**待补**：2025-2026 LLMOps 框架；Agent ops；Distributed inference 最新工程方案
