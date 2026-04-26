---
title: LLM Gateway · 统一的模型代理层
type: system
depth: 资深
level: A
last_reviewed: 2026-04-18
applies_to: LiteLLM 1.x · Portkey · Helicone · OpenRouter · 2024-2026 生态
tags: [ml-infra, llm, gateway, router]
aliases: [LLM Proxy, LLM Router]
related: [rag, mcp, llm-inference]
systems: [litellm, portkey, helicone, openrouter, vllm]
status: stable
---

# LLM Gateway · 统一模型代理层

!!! tip "一句话理解"
    **LLM 版的 API Gateway**。统一不同厂商（OpenAI / Anthropic / Google / 开源 vLLM）的调用接口，集中做**限流 / 重试 / 缓存 / 成本监控 / 路由 / 灰度**。**当 LLM 调用多于单源、且规模成本可观时，Gateway 价值明显**；**单模型单用例早期阶段可以不上**。

!!! abstract "TL;DR"
    - **核心价值**：统一协议 + 限流 + 成本监控 + 重试 / fallback + 灰度
    - **开源主流**：**LiteLLM**（最全，100+ 模型适配）· **LangSmith Proxy**
    - **商业主流**：**Portkey**（全栈）· **Helicone**（监控强）· **OpenRouter**（模型聚合）
    - **自建**：Nginx/Envoy + 自研插件（大厂做法）
    - **成熟度**：2024 快速成熟，成为 AI Infra 标配
    - **对标**：相当于 API 侧的 Kong / Apollo / Zuul，但面向 LLM 特性优化

## 1. 业务痛点 · 没 Gateway 的 AI 服务

### 典型问题

直接让业务代码调 OpenAI SDK 会踩坑：

| 痛点 | 症状 |
|---|---|
| **成本失控** | 某 bug 一晚烧 $5k、没人知道 |
| **限流来临无预警** | OpenAI 429 直接业务崩 |
| **模型升级要改所有代码** | GPT-4 → GPT-4o 改 N 处 |
| **多模型对比成本高** | Claude / GPT / Gemini 要各自代码 |
| **无缓存** | 相同 query 反复调 LLM |
| **无审计** | 出问题查不到哪个 request |
| **灰度发布难** | 新模型全量 or 改代码 |

### Gateway 的价值

**一处治理、多处消费**：

```
    业务代码
       │
       ↓ OpenAI-compatible API
┌─────────────────────┐
│   LLM Gateway       │  统一：限流 / 重试 / 缓存 / 路由 / 审计 / 成本
└─────────┬───────────┘
          │
    ┌─────┼──────┬─────────┬──────────┐
    ↓     ↓      ↓         ↓          ↓
  OpenAI Claude Gemini vLLM(自建) Groq / Together
```

## 2. 核心能力

### 1 · 协议统一

OpenAI 协议基本成了**事实标准**。Gateway 把各家 API 统一映射：

```python
# 不管后端是谁，调用方式一样
from openai import OpenAI
client = OpenAI(base_url="https://gateway.corp/v1", api_key="gateway-key")
client.chat.completions.create(
    model="claude-3-5-sonnet",   # Gateway 路由到 Anthropic
    messages=[...]
)
# 或
client.chat.completions.create(
    model="llama-70b-internal",  # Gateway 路由到内部 vLLM
    messages=[...]
)
```

### 2 · 限流 / 配额

- 按 user / team / model 限 TPM (tokens per minute) / RPM (requests per minute)
- 防止某 bug 把所有配额用光
- 按优先级队列

### 3 · 重试 / Fallback

```yaml
primary: gpt-4o
fallback:
  - claude-3-5-sonnet     # 主挂了用这个
  - llama-70b-internal
retry:
  max_attempts: 3
  backoff: exponential
```

主模型限流或挂 → **自动切备用**，业务无感。

### 4 · 缓存（语义缓存）

- 相同 prompt → 直接返回缓存答案
- **Semantic Cache**：prompt 语义相似度匹配（见 [Semantic Cache](../ai-workloads/semantic-cache.md)）
- 典型命中率 10-30%，节省显著

### 5 · 成本监控

- 每 request 记录 model / tokens_in / tokens_out / cost
- 按 team / endpoint / user 聚合
- 月度 burn rate 告警

### 6 · 路由策略

| 策略 | 用法 |
|---|---|
| **Latency-based** | 延迟最低路由 |
| **Cost-based** | 预算紧时路由便宜模型 |
| **Model-tier**: | 简单任务小模型、复杂大模型 |
| **Geo**: | 用户地理位置选就近 |
| **Canary** | 1% 流量到新模型 |

### 7 · 审计与观测

- 所有 request 记录
- PII 脱敏
- 慢 request 追踪

### 8 · Prompt 注入防护（Guardrails 集成）

- 统一接入 Llama Guard / Lakera 等
- Input / Output 双向过滤

## 3. 主流产品对比

### LiteLLM（开源首选）

**定位**：Python 库 + Proxy Server。

**核心**：
- **100+ 模型适配**（OpenAI / Anthropic / Google / Cohere / 开源 / ...）
- 自部署 Proxy Server（FastAPI + Docker）
- SQLite / Postgres 存日志
- 已有 Load Balance / Fallback / Budget 等

**优**：
- **完全开源**（BSD）
- 社区活跃，模型适配最快
- 简单自部署

**劣**：
- UI 相对简单
- 大规模部署要自己调优

### Portkey（商业全栈）

**定位**：LLM Gateway 商业 SaaS。

**核心**：
- 全托管 API
- 专业的监控 dashboard
- Prompt 版本管理
- Canary / A/B 一键

**优**：
- 企业级功能完整
- 运维外包

**劣**：
- 闭源、锁定
- 按量付费

### Helicone（监控优势）

**定位**：侧重 LLM **可观测性**的 Proxy。

**核心**：
- Drop-in 替换（一行改 base_url）
- 详细的 Dashboard（成本 / 延迟 / Token 分析）
- 有开源 + 云版本

**优**：
- 监控最深入
- 开源可自部署

**劣**：
- 路由 / Fallback 弱于 LiteLLM / Portkey

### OpenRouter（模型聚合）

**定位**："100+ 模型一个 API"。

**核心**：
- 统一 API 调 200+ LLM
- 按 token 付费 + 无月费
- 非"Gateway"严格意义——**更像 marketplace**

**用法**：
- 快速对比模型
- 个人开发者试水

### 企业自建（大厂）

Uber / 字节 / 阿里等**内部自建 Gateway**：
- Nginx / Envoy + Lua / Go 插件
- 深度集成内部权限 / 审计
- 成本比商业低但需平台团队

## 4. 能力矩阵

| 能力 | LiteLLM | Portkey | Helicone | OpenRouter | 自建 |
|---|---|---|---|---|---|
| 开源 | ✅ BSD | ❌ | 部分 | ❌ | - |
| 协议统一 | ✅ | ✅ | ✅ | ✅ | 按需 |
| 限流 / 配额 | ✅ | ✅ 强 | ⚠️ | ⚠️ | 自建强 |
| Fallback | ✅ | ✅ | ⚠️ | ❌ | 自建 |
| Semantic Cache | ⚠️ 插件 | ✅ | ⚠️ | ❌ | 自建 |
| 监控 Dashboard | 基础 | 强 | **最强** | 基础 | 自建 |
| Prompt Version | ❌ | ✅ | ❌ | ❌ | 自建 |
| Guardrails 集成 | 插件 | ✅ | 插件 | ❌ | 自建 |
| 自部署 | ✅ | ❌（商业托管）| ✅ | ❌ | 完全自控 |
| 企业级 RBAC | ⚠️ | ✅ | 部分 | ❌ | 自建 |

## 5. 工程落地

### 典型部署（LiteLLM）

```bash
# docker-compose
version: "3"
services:
  litellm:
    image: ghcr.io/berriai/litellm:latest
    ports:
      - "4000:4000"
    environment:
      LITELLM_MASTER_KEY: "sk-corp-master"
      DATABASE_URL: "postgresql://user:pass@postgres/litellm"
    volumes:
      - ./config.yaml:/app/config.yaml
    command: --config /app/config.yaml
  postgres:
    image: postgres:15
```

### config.yaml

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
      rpm: 500
  
  - model_name: claude-3-5-sonnet
    litellm_params:
      model: anthropic/claude-3-5-sonnet
      api_key: os.environ/ANTHROPIC_API_KEY
      rpm: 300

  - model_name: llama-70b
    litellm_params:
      model: openai/meta-llama/Llama-3-70B-Instruct
      api_base: https://vllm.internal:8000/v1
      api_key: "internal"

router_settings:
  routing_strategy: least-busy
  fallbacks:
    - gpt-4o:
        - claude-3-5-sonnet
        - llama-70b

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: os.environ/DATABASE_URL

litellm_settings:
  success_callback: ["langfuse"]
  cache: True
  cache_params:
    type: "redis"
    host: "redis.internal"
```

### 业务代码调用

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://litellm.internal:4000/v1",
    api_key="sk-team-data-science"  # Gateway 签发的 team key
)

response = client.chat.completions.create(
    model="gpt-4o",  # Gateway 路由
    messages=[{"role": "user", "content": "..."}],
)
```

### 关键配置建议

- **Master Key** + **Team Key** 分层（每 team 独立 budget）
- **日志异步**落 Postgres / ClickHouse
- **Redis 缓存**高频 query
- **Langfuse / Helicone**  做监控联动

## 6. 性能数字

### 典型 Gateway 开销

| 维度 | Overhead |
|---|---|
| 网络跳数 | +1（业务 → Gateway → LLM） |
| 延迟增加 | p50 +5-20ms · p99 +50-100ms |
| 吞吐 | 单 LiteLLM 实例 500-2000 QPS |
| 缓存命中率（典型） | 10-30% |

### 成本节省（实际案例）

- **某 AI 公司 2024**（匿名 case study）：LiteLLM + Semantic Cache → 节省 ~15% LLM 账单 `[来源未验证 · 无公开 postmortem]`
- **某 SaaS**（匿名）：Smart Routing（简单任务走小模型）→ 节省 30%+ `[来源未验证]`
- **读者提醒**：节省比例严重依赖业务 query 分布（重复率）· 不要直接套用 · 必须自测

## 7. 现实检视 · 2026 视角

### 已成熟可上

- **LiteLLM**：开源生产可用，多数 AI 团队标配
- **Portkey / Helicone**：中小团队商业方案成熟
- **核心能力**：限流 / 重试 / 成本 / 审计 —— 这 4 件事没人再争议

### 仍在演进

- **Semantic Cache 命中率**：取决于业务特性，10-50% 都有可能
- **Guardrails 集成**：各家做法不同，还没成熟协议
- **Prompt Caching**（Anthropic 原生 / OpenAI 2024）**和 Gateway 缓存怎么协同**还在探索
- **Agent 场景的 Gateway**（多轮 tool call）还没标准化

### 争议与选择

- **LiteLLM 的稳定性**：2024 年后稳定性显著提升（breaking change 从月度降到季度 · 数千家企业生产运行）· 仍建议**固定主版本**并关注 release note
- **商业 vs 自建**：团队 < 100 工程师用商业更省心
- **LLM Router smart routing**：简单任务小模型看起来省钱，**但 routing 本身也耗资源** + 质量波动
- **MCP 的出现**对 Gateway 冲击：两者关注点不同，**不冲突甚至互补**

## 8. 陷阱与反模式

- **无 Gateway 直连 OpenAI**：出问题（配额 / 成本 / 事故）追悔莫及
- **Gateway 不限流**：一个 team bug 打死全公司 LLM 配额
- **Master Key 到处分发**：用 team key 分发
- **Logs 同步落 DB**：高 QPS 时 DB 压力大 → 异步 + 批量
- **缓存 Key 粒度错**：带 timestamp / random 字段 → 命中率近 0
- **Fallback 链太长**：5 级 fallback → 延迟失控
- **不监控 Budget**：月底账单惊喜
- **Gateway 单点**：自建要 **HA**（至少 3 副本）

## 9. 延伸阅读

- **[LiteLLM 文档](https://docs.litellm.ai/)** · **[GitHub](https://github.com/BerriAI/litellm)**
- **[Portkey](https://portkey.ai/)** · **[Helicone](https://www.helicone.ai/)** · **[OpenRouter](https://openrouter.ai/)**
- **[Langfuse](https://langfuse.com/)** —— 配合 Gateway 做 Observability
- **[Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)**
- **[OpenAI Prompt Caching](https://platform.openai.com/docs/guides/prompt-caching)**

## 相关

- [Semantic Cache](../ai-workloads/semantic-cache.md) · [RAG](../ai-workloads/rag.md)
- [MCP](../ai-workloads/mcp.md) —— 和 Gateway 关注点不同但互补
- [LLM Inference](../ai-workloads/llm-inference.md) —— Gateway 后端是这个
- [LLM Observability](../ai-workloads/llm-observability.md) —— Gateway 是观测数据产生端
- [Guardrails](../ai-workloads/guardrails.md) —— Gateway 是 Guardrails 落地点
- [AI App Authorization](../ai-workloads/authorization.md) —— Gateway 做 identity 流转的一站

