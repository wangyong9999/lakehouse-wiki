---
title: Agent Patterns · 模式 + 框架 + Memory + Multi-agent
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: LangGraph 0.2+ · Microsoft Agent Framework (AutoGen + SK 合并) · OpenAI Agents SDK · Claude Agent SDK · Google ADK · CrewAI · 2024-2026
tags: [ai, agent, llm, langgraph, autogen, claude-sdk]
status: stable
---

# Agent Patterns · 机制 + 框架 + Memory + Multi-agent

!!! tip "一句话定位"
    **Agent = LLM + Tools + 控制循环 + 状态 / 记忆**。从 ReAct（2022）到 2026 Agent 框架战 · Agent 是"LLM 应用层最复杂也最不成熟"的话题。本页讲 **通用机制** · [Agents on Lakehouse](agents-on-lakehouse.md) 讲湖仓专属 tool 设计 · [scenarios/agentic-workflows](../scenarios/agentic-workflows.md) 讲业务编排。

!!! abstract "TL;DR"
    - **5 大控制循环模式**：ReAct · Reflexion · Plan-and-Execute · Tree of Thoughts · StateGraph（显式图）
    - **4 类 Memory**：Short-term（context）· Long-term（vector/KV store）· Episodic（事件时序）· Procedural（技能沉淀）
    - **Multi-agent 3 种编排**：Supervisor · Swarm · Hierarchical
    - **2026 框架战**：**LangGraph**（生产就绪最高 · 图结构 + checkpoint）· **Microsoft Agent Framework**（AutoGen + SK 2026 合并）· **OpenAI Agents SDK**（替代 Swarm · 专用 OpenAI 栈）· **Claude Agent SDK**（专用 Anthropic · 安全优先）· **Google ADK** · **CrewAI**（快速原型）
    - **核心工具协议**：[MCP](mcp.md) · 跨 host 的 tool 标准（2025 起事实标准）
    - **评估基准**：SWE-bench · τ-bench · WebArena · AgentBench · GAIA
    - **不成熟真相**：90% agent 可靠性问题来自 LLM 规划 / 理解 · 不是框架 · 不是工具 · 不是 prompt

!!! warning "本章定位"
    本页讲**通用 Agent 机制 + 框架对比**（canonical）· **不讲 RAG**（见 [RAG](rag.md)）· **不讲 MCP 协议细节**（见 [MCP](mcp.md)）· **不讲湖仓 Agent tool 设计**（见 [Agents on Lakehouse](agents-on-lakehouse.md)）· **不讲业务场景**（见 [scenarios/agentic-workflows](../scenarios/agentic-workflows.md)）。

## 1. 业务痛点 · Agent 为何不成熟却最火

### 从 ReAct 到 2026

- **2022 · ReAct** 论文（Yao et al.）提出 "Reasoning + Acting" 交替范式 · 奠定 agent 基础
- **2023 · LangChain Agents** 把 ReAct 工程化 · 一度爆火但局限明显
- **2024 · Multi-agent + Planner-Executor** 成熟 · AutoGen / CrewAI / LangGraph 各立山头
- **2025 · 大厂入场**：OpenAI Swarm（实验）→ Agents SDK（2025 GA）· Anthropic Claude Code SDK → Claude Agent SDK（2025 改名）· Google ADK（2025）
- **2026 · 合并 + 收敛**：Microsoft 合并 AutoGen + Semantic Kernel 为 Agent Framework · 生态向少数框架汇聚

### 为何"最火"

- LLM 规划能力逼近人类 · Agent 是利用这种能力的原生形态
- RAG 解信息接入 · Agent 解**自动化执行**
- 企业 SOP / 工单 / 运维 / 研究 都可能被 Agent 重塑

### 为何"不成熟"

- LLM 规划在**多步** / **长序列** 场景退化明显（GAIA benchmark 2025 最强模型 < 40% 通过率）
- **错误累积** · 10 步任务任何一步错 agent 偏轨
- 评估**极难**（多路径成功 / 多维度指标）
- **成本**：多步 agent 的 token 成本是单轮 LLM 的 10-100×

## 2. 5 大控制循环模式

!!! info "稳定路径 vs 演进跟踪"
    **2026 生产默认路径**：**StateGraph（显式图 · LangGraph）+ Function Calling + 窄 tools + HITL approval**。这是最可控、最可观测、最好恢复的路径。

    其他模式按场景取舍 · 不要一上来全用：
    - ✅ **ReAct** · 单场景 Agent 入门 · 适合 3 步以内
    - ✅ **Plan-and-Execute** · 多步任务 · planner 用强模型 / executor 用轻模型
    - 🟡 **Reflexion** · 可重试场景（编码 / 数学）· 非可重试场景不适合
    - 🟡 **Tree of Thoughts** · 搜索 / 推理重 · 代价明显 · 多数场景不划算

### 模式 1 · ReAct（Reason + Act · 2022）

```
Thought: 我需要查销售数据
Action: query_sales("华北 Q4")
Observation: [表格]
Thought: 有数据 · 算增长率
Action: ...
Thought: 够了
Answer: 增长 23%
```

- **优点**：简单 · 透明 · 无需特殊训练
- **缺点**：长任务错误积累 · LLM 自由度太大容易偏

### 模式 2 · Plan-and-Execute（2023）

```
步骤 1 · Plan：LLM 一次列出所有步骤
步骤 2 · Execute：逐步执行 · 每步简单 LLM + 工具
步骤 3 · Replan：若中途失败 · 重新规划
```

- **优点**：推理和执行分离 · planner 可用强模型 · executor 用轻模型（省 token）
- **缺点**：计划质量依赖 planner · 长任务 replan 开销大

### 模式 3 · Reflexion（自反思 · 2023）

- Agent 执行后 · **另一个 LLM 实例评估**结果
- 发现错误 → 生成 "reflection memory" 添加到 prompt
- 下次尝试带教训
- **适合**：任务可反复尝试的场景（编码 / 数学）

### 模式 4 · Tree of Thoughts（ToT · 2023）

- 问题空间建成树 · 每个节点是一个中间推理状态
- **BFS / DFS 搜索** · 每步多个候选 · 评估选择
- **适合**：推理重的任务（博弈 / 数学）· 代价高

### 模式 5 · StateGraph（显式状态图 · 2024 LangGraph 主推）

```python
# LangGraph StateGraph
graph = StateGraph(AgentState)
graph.add_node("planner", plan_node)
graph.add_node("researcher", research_node)
graph.add_node("writer", write_node)
graph.add_edge("planner", "researcher")
graph.add_conditional_edges(
    "researcher",
    lambda state: "writer" if state.enough_info else "researcher",
)
```

- **优点**：显式控制流 · 无 LLM 盲决策 · 可 checkpoint 恢复
- **缺点**：开发者要写图 · 失去 "agent 自主性"
- **2026 主流生产路径**：显式图 > 纯 LLM 循环

### 5 模式选型

| 任务类型 | 推荐模式 |
|---|---|
| **简单 ≤ 3 步 · 低风险** | ReAct |
| **多步 · 有明确子任务** | Plan-and-Execute |
| **可迭代重试（编码 / 数学）** | Reflexion |
| **推理 / 搜索重** | ToT |
| **生产 · 可靠性优先** | StateGraph（显式图）+ LangGraph |

## 3. Memory 机制

### Short-term · Context Window

- 就是 LLM 当前的 context
- 2025-2026 典型 100k-1M tokens
- **核心痛点**：**Lost in the Middle** · 长 context 信息被忽略
- **工程**：重要信息放 context 前或后 · prompt caching 减成本

### Long-term · Vector / KV Store

- **Vector store**（LanceDB / Milvus / Qdrant）存历史对话 · 任务经验 · 检索时召回
- **KV store**（Redis / Postgres）存结构化 memory（用户偏好 · 任务状态）
- 召回策略：语义相似度 + recency decay + 重要性分

### Episodic · 事件时序

- Agent 执行过的 **任务序列**（"上周二我帮用户 X 查过销售数据"）
- 结构化存储（JSONL / time-series DB）
- 用于"历史追溯" + "学习模式"

### Procedural · 技能 / Workflow 沉淀

- Agent 成功完成的任务模板沉淀 · 下次类似任务直接调用
- 类似 **skill library** 或 **prompt template 积累**
- 早期实验性 · 2025-2026 代表：Voyager（MineCraft agent）· AutoGen 的 workflow 复用

### Memory 工程陷阱

- **无限堆积**：memory 越多召回质量反降（噪音）· 必须淘汰 / 总结
- **一致性问题**：agent 改了偏好 · old memory 冲突 · 需冲突解决
- **跨 agent 共享**：memory 属于 agent 还是用户？权限边界

## 4. Multi-agent 模式

### Supervisor（中心化）

```
        Supervisor (LLM)
          ├─ Researcher
          ├─ Coder
          └─ Writer
```

- 中心 agent 分派任务给专家 agent
- **优点**：控制流清晰 · 易调试
- **缺点**：supervisor 成瓶颈 · 多轮 orchestration 成本高
- **典型框架**：LangGraph · AutoGen · CrewAI（Hierarchical Process）

### Swarm（去中心化 · 对话式）

```
Agent A ↔ Agent B ↔ Agent C
     所有 agent 可直接对话 · 动态路由
```

- 无中心 · agent 之间直接通信（message passing）
- **优点**：灵活 · 涌现行为
- **缺点**：不可预测 · 死循环风险
- **典型框架**：原 OpenAI Swarm（实验）· AutoGen GroupChat · CrewAI Hierarchical

### Hierarchical（分层）

```
Senior Agent
  ├─ Mid Agent 1
  │   ├─ Junior A
  │   └─ Junior B
  └─ Mid Agent 2
```

- 多层 supervisor / sub-team
- **适合**：大型任务分解
- **典型**：CrewAI Hierarchical Process · AutoGen 嵌套

### 选择

- **生产 · 确定性要求高** → Supervisor + StateGraph
- **研究 · 涌现行为** → Swarm
- **大任务 · 分工明确** → Hierarchical

## 5. Human-in-the-Loop（HITL）

**生产 Agent 几乎必须**：

| 模式 | 场景 |
|---|---|
| **Approval** · 执行前确认 | 破坏性操作（写数据 · 发邮件 · 调 API）|
| **Intervention** · 中途暂停 | 用户可打断 · 补充信息 · 纠偏 |
| **Correction** · 事后纠正 | Agent 失败后用户教 agent · 记入 memory |
| **Review** · 批处理审阅 | Agent 完成 N 个任务后批量过一遍 |

- **LangGraph 原生支持** checkpoint + human input · 生产路径
- **AutoGen UserProxyAgent** 可配 input_mode
- **Claude Agent SDK** 有 hook 机制

## 6. 2026 Agent 框架战

### 📊 主流框架对比（2026-Q2）

| 框架 | 模型依赖 | 架构特色 | 状态持久化 | 生产就绪度 | 适用 |
|---|---|---|---|---|---|
| **LangGraph** | 模型中立 | **StateGraph** · checkpoint · 时间旅行 · LangSmith 追踪 | 原生（含 time travel）| **最高** | 复杂工作流 · 生产优先 |
| **Microsoft Agent Framework** | 模型中立 | AutoGen + Semantic Kernel **2026 合并** · 多语言（.NET / Python）| 会话历史 · 可扩展 | 高 | 微软生态 · 企业 |
| **OpenAI Agents SDK** | OpenAI only | **替代 Swarm（2025 GA）** · 内建 tracing + guardrails | Context variables（默认临时）| 高 | 快速原型 · OpenAI 栈 |
| **Claude Agent SDK** | Claude only | 安全优先 · 深度集成 MCP · Extended Thinking | 通过 MCP servers | 高 | Anthropic 栈 · 安全敏感 |
| **Google ADK** | 模型中立 | 2025 发布 · 4 种语言 SDK · GCP 集成 | — | 中 | GCP 生态 |
| **CrewAI** | 模型中立 | **Role-based** · 快速原型 · 显式协作 | 任务历史 | 中 | 快 idea → prototype · 据报道比 LangGraph 快 40% |
| **AutoGen (0.2 / 原)** | 模型中立 | GroupChat · Multi-agent · 已合并为 MS Agent Framework | 会话历史（in-memory）| 中 | 存量项目 · 2026 向合并后产品过渡 |
| **LlamaIndex Agents** | 模型中立 | 检索优先 · workflow + FunctionAgent | 有 | 中 | RAG 重 agent |

### 选型决策（2026-Q2）

- **新项目 · 生产优先** → **LangGraph**
- **多 agent 协作中心** → **CrewAI**（快起来）或 **LangGraph**（可控）
- **工作流复杂 · 需要 checkpoint / time travel** → **LangGraph**
- **最快 prototype** → **OpenAI Agents SDK**（锁 OpenAI）或 **CrewAI**（中立）
- **Anthropic 栈 · 安全敏感** → **Claude Agent SDK**
- **微软 / .NET 栈** → **Microsoft Agent Framework**
- **GCP 栈** → **Google ADK**

## 7. Agent 评估

比 RAG 评估难得多 · 多步骤 · 多路径 · 多维度。

### 核心指标

| 指标 | 含义 |
|---|---|
| **Task Success Rate** | 最终结果是否正确（人工或 LLM judge）|
| **Tool Call Accuracy** | 每步调用工具是否合理 |
| **Step Efficiency** | 平均几步完成（越少越好）|
| **Cost per Task** | Token + tool 执行总成本 |
| **Replan Rate** | 中途重新规划比例（高意味 planner 差）|
| **Hallucination Rate** | 编造不存在的 tool / 参数 / 结果 |

### 2026 主流 Benchmark

| Benchmark | 特色 | SOTA（2026-Q2 估）|
|---|---|---|
| **SWE-bench**（代码修复）| GitHub Issue → PR patch · Verified 子集 | ~60-70% |
| **τ-bench**（客服模拟）| Airline / Retail 客服场景 · 工具使用 + 多轮 | ~50-60% |
| **WebArena**（网页操作）| 5 类网站任务 · 点击 / 表单 / 导航 | ~35-45% |
| **AgentBench**（综合）| 8 类任务 · 游戏 / 家务 / 编程 / web 等 | 一般 30-50% |
| **GAIA**（通用助手）| 真实助手任务 · 3 难度 Level | 最强 < 40%（依然远低人类）|

**关键认知**：SOTA 模型在**真实通用任务** benchmark 上仍远低于人类 · 2026 agent 仍在"可演示 · 难托管"阶段。

## 8. 执行契约 · 幂等 / 补偿 / 恢复 / 审计 / 回放

**Agent 比 RAG 难得多的地方不是"控制循环"而是"执行语义"**。Agent 调用外部副作用 · 副作用失败 · 长任务中断 · 写操作 · 这些都是**可靠系统**必修课 · 不是"Agent 模式"层面的事。

### 8.1 幂等性（Idempotency）

Agent 重试时不能重复副作用：

```python
@tool(idempotent=True)
def send_email(to: str, subject: str, body: str, idempotency_key: str):
    """发邮件。idempotency_key 用 (user_id, task_id, step_id) 组合 · 同 key 重发无效果。"""
    if email_log.exists(idempotency_key):
        return email_log.get(idempotency_key)  # 幂等返回
    result = email_api.send(...)
    email_log.write(idempotency_key, result)
    return result
```

- **写操作 tool 必须幂等** · retry / replan 时重入安全
- idempotency_key 由 agent framework 传 · 不要让 LLM 编

### 8.2 副作用补偿（Compensation · Saga 模式）

Agent 多步骤中失败 · **已做的副作用需要逆转**（类似分布式事务的 Saga）：

```
步骤 1 · create_customer → 成功
步骤 2 · create_order → 成功
步骤 3 · charge_payment → 失败
↓
补偿链（逆序）：
  3 compensate: void_reservation
  2 compensate: cancel_order
  1 compensate: delete_customer（或标记 abandoned）
```

- 每个写 tool 有对应的 **compensate tool**
- Agent framework（LangGraph / Temporal）可支持 saga 模式
- **不适合强事务场景** · 更适合"最终一致 + 可逆"

### 8.3 长任务恢复（Resumability）

Agent 跑到一半挂了怎么办？

```python
# LangGraph 原生 checkpoint
graph = workflow.compile(checkpointer=PostgresSaver(...))

config = {"configurable": {"thread_id": "task-42"}}

# 首次调用
try:
    result = graph.invoke(initial_state, config=config)
except Exception:
    # 崩了 · thread 42 的 state 已持久化

# 恢复
resumed = graph.invoke(None, config=config)  # None → 从 checkpoint 继续
```

- **LangGraph / Temporal / Restate** 支持 checkpoint + resume
- 自建：每步后 atomic persist state + step number
- 恢复时**从最近 checkpoint 重入**（不是从头）

### 8.4 写操作审批（Deep HITL）

通用 HITL 在 §5 讲过 · 执行契约角度更严：

```
写操作触发 · Agent 生成 action plan
↓
store pending_action to queue
↓
notify human reviewer
↓
  approve → execute
  reject → abort + notify user
  edit   → execute edited version
  timeout → default (abort or escalate)
```

- **approval 必须异步** · 不能阻塞 agent 循环
- 有**超时策略**（批准 / 拒绝 / 升级）
- 审批记录入**审计表**

### 8.5 多步审计（Step-level Audit Trail）

```
┌─────────────────────────────────────────────────┐
│ audit_trail(task_id)                              │
├─────────────────────────────────────────────────┤
│ step_id  | tool       | args    | result | user │
│ 1        | query_db   | {...}   | [...]  | u42  │
│ 2        | compute    | {...}   | {...}  | u42  │
│ 3        | send_email | {...}   | ok     | u42  │
│ 4 (approval) reviewer=u7, decision=approve       │
│ 5        | delete_row | {...}   | ok     | u42  │
└─────────────────────────────────────────────────┘
```

- 每个 step 记录 tool / args / result / user / timestamp
- 事故复盘 / 审计 / 合规基础
- 关联 [LLM Observability](llm-observability.md) 的 trace · 一体化

### 8.6 回放（Deterministic Replay）

出事故后 · 用**当时的状态 + 当时的 LLM 响应**重演：

```python
# 生产环境每步 persist：LLM response · tool results · state delta
# 事后 replay
replay_state = load_state_at(task_id, step=3)
next_decision = load_llm_response_at(task_id, step=4)  # 用原 response 不重调 LLM
# 继续走 · 精确复现
```

- **LLM 调用不确定** · 生产要**persist 实际 response**（不是只 prompt）
- 回放用于**事故分析** / **对抗测试** / **审计**
- Temporal / Restate 的 **workflow replay** 是此模式最成熟实现

### 8.7 执行契约清单（生产 Agent 必过）

```
☐ 所有写 tool 标记 idempotent + 带 idempotency_key
☐ 关键写 tool 有 compensate pair
☐ 长任务（> 1 min）走 checkpoint + resume
☐ 写操作走 HITL approval 队列 · 有超时策略
☐ 每步 step-level audit · 关联 trace
☐ 生产 persist LLM raw response · 支持回放
☐ 事故 playbook：如何查 audit · 如何 replay · 如何回滚副作用
```

## 9. 陷阱与反模式

- **Tool 太多 > 10**：LLM 选不准 · 必须分组 / 分 server / 分 agent
- **Tool 描述模糊**：LLM 选工具靠 description · 写清楚 + 给例子
- **不限步数**：Agent 无限循环 · **必须设 max_iterations**
- **不限 token**：多步 agent 成本爆 · 每步累计 · 必须预算控制
- **权限过大**：Agent 用管理员 credential 跑 · 失误 → 数据灾难 · 必须最小权限 + sandbox
- **无 checkpoint**：长任务中途挂 → 从头再来 · **LangGraph 原生支持 · 用起来**
- **不做 HITL**：破坏性操作裸奔 · 必须 approval
- **忽视 prompt injection**：Tool 返回的数据可能含"忽略上述规则..." · input/output 都要过 guardrails
- **一上来多 agent**：单 agent 搞不定 · 多 agent 更搞不定 · 先单 agent + 好 tool · 再加多 agent
- **只看演示不看评估**：demo 完美 · 生产 40% 失败率 · **必须 benchmark 自家任务**
- **框架锁定早**：框架迭代快 · 生产 agent 抽象层 · 不要 API 贴死

## 10. 横向对比 · 延伸阅读

- [MCP](mcp.md) —— Agent 的 tool 协议 · 跨 host 标准
- [Agents on Lakehouse](agents-on-lakehouse.md) —— 湖仓专属 tool 设计
- [RAG](rag.md) —— Agent 常见能力之一（Agentic RAG）
- [Structured Output](structured-output.md) —— Agent tool 的输入输出
- [LLM Gateway](llm-gateway.md) · [Guardrails](guardrails.md) · [LLM Inference](llm-inference.md) —— 支撑层
- [scenarios/agentic-workflows](../scenarios/agentic-workflows.md) —— 业务场景编排

### 权威阅读

- **[*ReAct: Synergizing Reasoning and Acting* (Yao et al., 2022)](https://arxiv.org/abs/2210.03629)** —— 原论文
- **[*Reflexion* (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366)** · **[*Tree of Thoughts* (Yao et al., 2023)](https://arxiv.org/abs/2305.10601)**
- **[LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)**
- **[Microsoft Agent Framework](https://github.com/microsoft/agent-framework)**（AutoGen + SK 合并）
- **[OpenAI Agents SDK](https://platform.openai.com/docs/guides/agents-sdk)**
- **[Anthropic Claude Agent SDK](https://docs.anthropic.com/en/docs/agents)**
- **[Google ADK](https://google.github.io/adk-docs/)**
- **[CrewAI 官方](https://docs.crewai.com/)**
- **[SWE-bench](https://www.swebench.com/)** · **[GAIA benchmark](https://huggingface.co/papers/2311.12983)** · **[τ-bench](https://github.com/sierra-research/tau-bench)**
- **Anthropic [*Building Effective Agents*](https://www.anthropic.com/engineering/building-effective-agents)**（2024-12 · 工程最佳实践）

## 相关

- [MCP](mcp.md) · [Agents on Lakehouse](agents-on-lakehouse.md) · [Structured Output](structured-output.md) · [RAG](rag.md) · [Guardrails](guardrails.md)
- [scenarios/agentic-workflows](../scenarios/agentic-workflows.md)（业务场景）
