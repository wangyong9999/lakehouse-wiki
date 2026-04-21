---
title: LLM Observability · Trace / Cost / Prompt 版本 / 事故归因
type: system
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: OTel GenAI semantic conventions（2026-Q1 experimental · stable 待定）· Langfuse 3.x · LangSmith · Phoenix（Arize）· Helicone · OpenLLMetry · 2024-2026 生态
tags: [ai, llm, observability, tracing, langfuse, langsmith, phoenix, opentelemetry]
aliases: [LLM Tracing, LLM Monitoring, GenAI Observability]
status: stable
---

# LLM Observability · 生产 AI 的观测契约

!!! tip "一句话定位"
    **生产 AI 没有 observability 就是盲飞**。一次请求里 chunk → embed → retrieve → rerank → tool call → LLM → guardrails 各花了多久？哪步爆成本？哪个 prompt / 哪个 tool / 哪个模型版本引入了回归？这些问题**散在 Gateway log / RAG eval / Agent trace 里** · 本页把它们**立成统一观测契约**。

!!! abstract "TL;DR"
    - **四维契约**：**Trace**（每步完整调用链）· **Cost**（按 user / team / feature 归因）· **Latency**（TTFT / 段级 / p95-p99）· **Version**（prompt / model / tool schema 版本追踪）
    - **OTel GenAI semantic conventions**：2026-Q1 仍 **experimental** · 未 stable · 但已是事实参考 · 建议预先接入
    - **2026 主流工具**：**Langfuse**（开源 MIT · API-first）· **LangSmith**（LangChain 原生 · 闭源 SaaS）· **Phoenix / Arize**（开源 · OTel 原生 · LlamaIndex 友好）· **Helicone**（Drop-in proxy）· **OpenLLMetry**（Traceloop · 多框架集成）
    - **集成模式**：**Gateway 注入**（对应用无侵入）· **SDK 手工埋点**（Agent 框架原生）· **OTel auto-instrumentation**（行业标准路径）
    - **生产纪律**：采样（100% trace 贵）· PII 脱敏 · 数据留存期 · 事故归因模板
    - **和 [LLM Gateway](llm-gateway.md) 分工**：Gateway 是"**数据产生**" · Observability 是"**trace 汇聚 + 分析 + 告警**"

!!! warning "本页边界"
    - **LLM Gateway 自带的基础监控**（request count / error rate / cost agg）→ 看 [llm-gateway](llm-gateway.md)
    - **RAG 质量评估**（Groundedness / Context Relevance 等）→ 看 [rag-evaluation](rag-evaluation.md)
    - **Agent 任务评估**（SWE-bench / τ-bench / Task Success Rate）→ 看 [agent-patterns](agent-patterns.md)
    - **通用 Infra 监控**（Prometheus / 告警规则 / 链路追踪基础）→ 看 `ops/observability`
    - **本页专注**：LLM 语义的 trace 契约 + 事故归因 + prompt / model 版本追踪

## 1. 业务痛点 · 不做 observability 会发生什么

### 典型生产事故排查

**场景**：某天客服机器人**answer relevance** 突然下降 20%（用户投诉飙升）。

**无 observability**：
- 日志只有"LLM 返回了 X"
- 不知道是 retrieval 出问题 · Rerank 换模型 · 还是 prompt 昨天改了
- **调试耗时 2-3 天** · 工程师像考古
- 中间损失 · 品牌声誉 · 可能回滚错版本继续出错

**有 observability**：
```
1. Dashboard 看到 answer_relevance p50 昨晚 22:00 掉
2. 按时间线查 trace · 发现 22:00 有 prompt 部署（prompt_version v12→v13）
3. 对比两版 trace · v13 context precision 低 15% · retrieval 正常 · 仅 prompt 变化
4. 回滚 v13 · 监控恢复
5. 全程 < 10 分钟
```

**真实对比**：同等团队 · 有 / 无 obs 事故 MTTR 相差 **5-10 倍**（经验值 · 依团队 / 事故类型变化极大）。

### LLM 独特挑战（不能只套传统 APM）

| 传统 APM | LLM 场景增量 |
|---|---|
| HTTP method / status | Prompt 内容 · 响应 · token 用量 |
| 延迟 | **TTFT**（Time to First Token）· 总生成时长 · 段级（retrieve / rerank / LLM）|
| 错误码 | Hallucination · Groundedness · refusal · jailbreak detected |
| QPS / error rate | Cost per request · model / prompt / tool 版本 · Cache hit rate |
| Service mesh | **Agent 多步骤 trace 树** · tool call 嵌套 · 多 agent 消息传递 |

## 2. 四维观测契约

### 维度 1 · Trace（调用链）

一次 LLM 请求是**一棵 span 树**：

```
Root span · user_query
 ├─ retrieve_docs（embed + vector search + ACL filter）
 │   ├─ embedding（model=bge-large-zh · 15ms）
 │   ├─ vector_search（lancedb · top_k=50 · 120ms）
 │   └─ rerank（bge-reranker-v2 · top_k=10 · 85ms）
 ├─ build_prompt（prompt_version=v13 · tokens_in=2150）
 ├─ llm_call（model=gpt-4o-2024-11-20 · tokens_out=280 · 1.4s）
 │   ├─ first_token_latency=520ms
 │   ├─ tool_call: query_sales_tool（parent span）
 │   │   └─ sql_execute（380ms）
 │   └─ second llm_call（post-tool · 680ms）
 └─ output_guardrails（llama_guard_3 · 90ms）
```

**契约要求**（每个 span 至少带）：
- `gen_ai.operation.name`（chat / embedding / rerank / tool）
- `gen_ai.request.model` / `gen_ai.response.model`
- `gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens`
- `gen_ai.request.temperature` · 其他 request params
- `gen_ai.prompt_version`（如有）
- 用户 identity（脱敏后）· feature name · tenant

### 维度 2 · Cost（归因）

```
维度         典型聚合
────────────────────────────
user_id      每用户月度成本 · 异常检测
team / dept  部门 budget 监控
feature      哪个功能最烧钱（chat / code-review / summarize）
model        model mix · 贵 vs 便宜占比
cache_layer  semantic cache hit 省多少 · prompt cache 省多少
```

- **必须按 token 精确计算**（不是请求数 × avg）
- 按 input / output / cached 分列（价格不同）
- **Anthropic prompt cache** 和 **OpenAI prompt cache** 的 cached tokens 折扣要单独算

### 维度 3 · Latency（分段）

```
total_latency = queue + prep + retrieve + rerank + prompt_build + llm_prefill + llm_generate + guardrails + post
```

每段 p50 / p95 / p99 · 任何一段漂移都要抓住：
- **TTFT** 是用户感知最强指标
- **prefill vs decode** 分开（prefill 受 prompt 长度影响 · decode 受生成长度影响）
- Tool call 嵌套的端到端延迟

### 维度 4 · Version（追踪变更归因）

**最容易被忽视但事故归因最关键**：

| 版本维度 | 抓住什么 |
|---|---|
| **prompt_version** | 哪版 prompt 在跑 · 全量 vs A/B · 何时部署 |
| **model_version** | `gpt-4o-2024-11-20` vs `gpt-4o-2024-08-06` · 不同行为 |
| **tool_schema_version** | Agent tool 定义改了 · LLM 响应可能退化 |
| **retrieval_index_version** | 索引重建 · embedding 模型换 · 召回会变 |
| **guardrails_policy_version** | 策略改动导致 false positive 上升 |

**生产纪律**：任何一个版本变更 · 自动 diff 前后 trace 的关键指标（answer_relevance / groundedness / avg_latency / cost）。

## 3. OpenTelemetry GenAI Semantic Conventions

**2026-Q1 状态 · experimental**（非 stable · 仍在演进 · 建议 dual-emission 过渡）· 但**已是事实参考**。

### 覆盖面（4 信号）

- **Events**：GenAI 输入输出事件（prompt 内容 · response 内容）
- **Metrics**：GenAI 操作指标（token 用量 · latency · error rate）
- **Model spans**：模型操作（LLM 调用）
- **Agent spans**：Agent 框架操作（决策 · tool call · memory）

### 关键属性（示例）

```python
span.set_attributes({
    "gen_ai.system": "openai",                     # provider
    "gen_ai.operation.name": "chat",               # chat / embedding / rerank / text_completion
    "gen_ai.request.model": "gpt-4o-2024-11-20",
    "gen_ai.response.model": "gpt-4o-2024-11-20",
    "gen_ai.request.temperature": 0.2,
    "gen_ai.request.max_tokens": 500,
    "gen_ai.usage.input_tokens": 2150,
    "gen_ai.usage.output_tokens": 280,
    "gen_ai.response.finish_reasons": ["stop"],
})
```

### 过渡策略（稳定前的 dual-emission）

```bash
# 让 SDK 同时发出 legacy 和 GenAI 属性 · 升级平滑
export OTEL_SEMCONV_STABILITY_OPT_IN="gen_ai_latest_experimental"
```

### 实践意义

- **锁定厂商风险降低**：换观测工具时 · trace 格式兼容
- **跨框架统一**：LangChain · LlamaIndex · 自研 · 都走 OTel 就不用各写一套
- **批判**：2026-Q1 **仍不 stable** · 生产采用要有 fallback 计划 · API 可能有 breaking change

## 4. 2026 主流工具对比

| 工具 | 形态 | 开源 | OTel 兼容 | 特色 | 适合 |
|---|---|---|---|---|---|
| **Langfuse** | 自托管 Web + SDK（Python/TS）| ✅ MIT | ✅（2024+ 深度）| API-first · 功能最全 · 自托管无限 | 小-中-大团队 · 数据主权要求 |
| **LangSmith** | 闭源 SaaS（自托管 Enterprise 付费）| ❌ | ⚠️ 部分 | LangChain 原生集成最深 | LangChain 栈重度用户 |
| **Phoenix (Arize)** | 自托管 · 商业云版本 | ✅ | ✅ **原生 OTel** | LlamaIndex 友好 · OTel 优先 · 需 k8s + Postgres | OTel 标准化诉求 · LlamaIndex 栈 |
| **Helicone** | Drop-in proxy · 商业 + 开源内核 | 部分 | ⚠️ | 改 `base_url` 即可接入 · 监控强 | 快速起步 · 不想改代码 |
| **OpenLLMetry** | 开源 SDK（Traceloop）| ✅ | ✅ 完整 | OTel-native · 多框架 auto-instrument | 多框架混用 · OTel 栈 |
| **Braintrust** | 商业 SaaS | ❌ | - | Eval 和 obs 一体 | 评估驱动的团队 |
| **Datadog LLM Obs** | 商业 SaaS | ❌ | ✅ | 和 Datadog APM 打通 | 已用 DD 的企业 |
| **New Relic AI Monitoring** | 商业 SaaS | ❌ | ✅ | 和 NR 打通 | 已用 NR 的企业 |

### 选型决策

- **开源 + 数据主权 + 功能全** → **Langfuse**
- **OTel 优先 + LlamaIndex** → **Phoenix**
- **LangChain 深度栈 + 不介意闭源** → **LangSmith**
- **最快起步 + 不改代码** → **Helicone**
- **多框架混合 + OTel 原生** → **OpenLLMetry**
- **已有 Datadog / New Relic** → 直接用对方的 LLM 模块
- **评估和 obs 一起** → Braintrust

## 5. 集成模式

### 模式 1 · Gateway 注入（零侵入）

```
    业务代码
       │
       ↓
[LLM Gateway] ──注入 trace/metrics──> Langfuse / Phoenix
       │
       ↓
    LLM Provider
```

- **优点**：业务代码不动 · Gateway 统一管观测
- **缺点**：Gateway 之前的步骤（retrieval / rerank）拿不到 · 只能从 Gateway 那一刻开始
- **工具**：LiteLLM + Langfuse callback 是典型组合

### 模式 2 · SDK 手工埋点

```python
from langfuse import observe, Langfuse

langfuse = Langfuse()

@observe()
def rag_answer(query: str):
    docs = retrieve(query)           # 自动成一个 span
    reranked = rerank(query, docs)   # 另一个 span
    prompt = build_prompt(query, reranked)
    response = llm_call(prompt)      # 包装成 span
    return response
```

- **优点**：控制最细 · 自定义 attributes 随意
- **缺点**：代码侵入 · 每个调用点都要手工加

### 模式 3 · OTel auto-instrumentation（推荐生产）

```python
# OpenLLMetry 或 Phoenix auto-instrument
from traceloop.sdk import Traceloop
Traceloop.init(app_name="my-ai-app")

# OpenAI / Anthropic / LangChain / LlamaIndex 调用 · 自动生成 GenAI spans
```

- **优点**：零代码入侵 · 符合 OTel 标准 · 多框架通吃
- **缺点**：自定义属性仍需手工加
- **2026 生产推荐路径**

### 模式 4 · Agent 框架原生

LangGraph / CrewAI / LangChain 内建 tracing hooks · 直接对接 LangSmith / Langfuse：

```python
from langgraph.graph import StateGraph
from langfuse.callback import CallbackHandler

graph = StateGraph(...)
result = graph.invoke(
    state,
    config={"callbacks": [CallbackHandler()]},
)
```

## 6. 事故归因 · 生产模板

### 典型问答事故 · 5 问排查法

```
事故："客服答非所问变多"
1. 什么时候开始？→ 看 answer_relevance metric 时间线
2. 相关变更？→ 查 prompt_version / model_version / retrieval_index_version 的部署时间戳
3. 哪一步退化？→ 分解 trace · retrieve / rerank / prompt / LLM 各看 p50
4. 能复现？→ 用当时的 prompt + 数据 replay
5. 回滚谁？→ 找到退化变更 · rollback + incident review
```

### 必备告警

- **Cost budget burn rate** · 按天 / 按 user / 按 feature
- **p95 latency 上涨 > 30%** · 分段告警
- **Error rate 上涨** · LLM 429 / 5xx / tool failure
- **Guardrails false positive 率**（被挡的正常请求比例）
- **Hit rate 下降**（Semantic Cache / Prompt Cache）
- **Groundedness / Answer Relevance 周期评估退化**（见 [rag-evaluation](rag-evaluation.md)）

## 7. 生产纪律

### 采样策略

- **100% trace 太贵**（LLM 请求 log 量大 · 带 prompt / response）
- **分层采样**：
  - 错误 / 慢请求 100%
  - 生产 5-10%
  - staging / 开发 100%
- **Cost-based**：贵请求（> N tokens）100% · 便宜请求采样

### PII 脱敏

- Prompt / response 含用户数据 · 落盘前必须脱敏
- Microsoft Presidio 做 PII 检测 · 写入 trace 前替换
- Trace 保留期策略：generally 14-30 天 · 合规场景按规范

### 数据量

- 典型 1000 LLM req/day · trace + prompt/response 数据约 **100MB-1GB/day**
- 高流量（10k+）· 需要**冷数据到对象存储** · 热数据 Postgres

### 成本

| 方案 | 月成本（10k req/day · 中等 trace）|
|---|---|
| Langfuse 自托管 | ~$50-200（infra 成本） |
| LangSmith 云 | ~$300+ |
| Phoenix 自托管 | ~$100-300 |
| Datadog LLM Obs | ~$500+（依 DD billing）|
| Helicone 云 | ~$100-500 |

（依流量 / 数据量 / 保留期变化极大 · 自测准）

## 8. 陷阱与反模式

- **只看 LLM 调用 · 不看 retrieval / rerank** · 错过早期环节的退化
- **trace 不含 prompt_version** · 事故归因基本无望
- **不分离 TTFT vs total** · 用户感知是 TTFT · total 够用但体验差
- **token 用量误算** · 忽略 prompt cache / semantic cache · 成本高估
- **PII 裸落盘** · GDPR / HIPAA 违规 · 审计过不了
- **100% trace**（小流量可以 · 大流量账单爆 + 存储爆）
- **无 version diff 告警** · prompt 一改全崩 · 事后才发现
- **Obs 工具锁定** · 没走 OTel · 换工具重写所有埋点
- **Agent 深度嵌套 span 没建好** · Agent trace 看不出决策路径 · 排查失败
- **把 evaluation 和 observability 混为一谈** · Obs 是"发生了什么" · Eval 是"质量怎么样" · 两事都要

## 9. 横向对比 · 延伸阅读

- [LLM Gateway](llm-gateway.md) —— 是 obs 的数据产生端
- [RAG 评估](rag-evaluation.md) —— 离线 / 在线质量评估（vs obs 的实时追踪）
- [Agent Patterns](agent-patterns.md) —— Agent trace 嵌套设计
- [Prompt 管理](prompt-management.md) —— prompt_version 来源
- [Semantic Cache](semantic-cache.md) —— Cache hit 是关键 obs metric

### 权威阅读

- **[OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)**
- **[OTel GenAI Spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/)** · **[Agent Spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/)** · **[Metrics](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-metrics/)**
- **[Langfuse 官方](https://langfuse.com/)** · **[GitHub](https://github.com/langfuse/langfuse)**
- **[LangSmith](https://smith.langchain.com/)**
- **[Arize Phoenix](https://phoenix.arize.com/)** · **[GitHub](https://github.com/Arize-ai/phoenix)**
- **[Helicone](https://www.helicone.ai/)**
- **[OpenLLMetry (Traceloop)](https://github.com/traceloop/openllmetry)**
- **[Datadog LLM Observability](https://www.datadoghq.com/product/llm-observability/)**
- **[Braintrust](https://www.braintrust.dev/)**

## 相关

- [LLM Gateway](llm-gateway.md) · [Prompt 管理](prompt-management.md) · [RAG 评估](rag-evaluation.md) · [Agent Patterns](agent-patterns.md) · [Semantic Cache](semantic-cache.md)
