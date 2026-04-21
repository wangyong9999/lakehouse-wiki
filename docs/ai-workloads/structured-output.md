---
title: Structured Output · JSON / Schema / Function Calling
type: concept
depth: 资深
level: A
last_reviewed: 2026-04-21
applies_to: OpenAI Structured Outputs (2024-08+) · Anthropic Tool Use · Gemini JSON mode · Instructor · Outlines · Marvin · 2024-2026
tags: [ai, llm, json-mode, function-calling, structured-output, pydantic]
aliases: [JSON Mode, Function Calling, Tool Use]
status: stable
---

# Structured Output · LLM 结构化输出

!!! tip "一句话定位"
    **让 LLM 稳定输出机器可读的结构**（JSON / Schema / Function Calling / Tool Use）。生产 AI app 必备——**没有结构化输出就没有 Agent · 没有 tool use · 没有和其他系统集成**。核心区分：**Schema-guaranteed**（API 层保证）vs **Prompt-based**（靠模型自觉）· 2024-08 起前者成主流。

!!! abstract "TL;DR"
    - **核心范式**：JSON mode（弱约束）· Structured Outputs / Response Schema（强约束）· Function Calling / Tool Use（参数结构化）
    - **OpenAI 2024-08 Structured Outputs** 是分水岭：**100% 符合 JSON Schema**（之前靠 prompt + 重试）
    - **Anthropic / Gemini** 跟进 · **开源模型** 靠 Outlines / Instructor / SGLang CFSM 补齐
    - **Instructor**（Pydantic + 重试）· **Outlines**（grammar / regex 约束生成）· **Marvin** · **LangChain parsers** 是 4 条工程化路径
    - **和 Agent 的关系**：Function Calling 是"参数结构化"· Agent tool 的 schema 就用这个机制
    - **陷阱**：JSON mode ≠ schema · 嵌套对象 token 爆 · 流式结构化需特殊处理 · 开源模型 schema 遵守率差异大

!!! info "边界"
    本页是 canonical "LLM 结构化输出"· [Agent Patterns](agent-patterns.md) 用它做 tool schema · [RAG](rag.md) 用它做引用格式 · [Guardrails](guardrails.md) 用它做输入 / 输出 validation。

## 1. 业务痛点 · 为什么不能靠 prompt + parse

### 朴素方法的问题

```python
prompt = "返回 JSON: {\"name\": ..., \"age\": ...}"
response = llm.generate(prompt)
data = json.loads(response)  # ❌ 经常崩
```

失败模式：
- **非 JSON**（有解释文本前缀："Sure, here is..."）
- **JSON 但不合 schema**（多字段 · 少字段 · 类型错）
- **格式偏差**（单引号 · trailing comma · markdown 代码块包裹）
- **嵌套结构不完整**

生产统计：朴素 prompt 的 JSON 合法率 **70-90%** · 合 schema 率更低。上游 parse 失败率 5-30% · 不可接受。

### 需求演进

- **2022-2023**：prompt + parse + 重试 · 工程脏
- **2023**：OpenAI Function Calling 引入 · 参数级结构化
- **2024-08**：**OpenAI Structured Outputs GA** · **100% schema 符合保证**（API 层面）· 分水岭
- **2024-2025**：Anthropic Tool Use（含 input schema） · Gemini JSON mode 跟进
- **2025-2026**：开源（Outlines · SGLang CFSM · vLLM guided decoding）补齐

## 2. 四种机制 · 约束强度递增

### 机制 1 · Prompt-based JSON（最弱）

```python
prompt = "返回 JSON · 字段 name (str) · age (int) · 只返回 JSON 不要其他"
# 靠模型"自觉"
```

- **无硬约束** · 模型可偏离
- **需要重试** / fallback parse
- 适用 · 小规模 · 简单 schema · 容错高

### 机制 2 · JSON Mode（弱约束）

OpenAI `response_format = {"type": "json_object"}` · Anthropic / Gemini 有类似。

```python
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    response_format={"type": "json_object"},
)
# 保证是合法 JSON · 但字段 / 类型仍靠 prompt
```

- **保证**：输出是**合法 JSON**（可被 json.loads）
- **不保证**：字段 / 类型符合你的预期
- 适用：自由 JSON 结构 · 或配合 prompt 约束

### 机制 3 · Structured Outputs / Response Schema（强约束）

OpenAI 2024-08 GA · Anthropic 2024 跟进。

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
    email: str | None = None

response = openai.chat.completions.create(
    model="gpt-4o-2024-08-06+",
    messages=[...],
    response_format=Person,  # 自动转 JSON Schema
)
person = response.choices[0].message.parsed  # Pydantic 对象
```

- **100% 符合 JSON Schema**（API 层面 · 通过约束生成实现）
- **生产推荐** · 主流工程选项
- 模型：OpenAI `gpt-4o-2024-08-06+` / Anthropic 2024+ 主流 / Gemini 1.5+

### 机制 4 · Function Calling / Tool Use（参数结构化）

```python
tools = [{
    "type": "function",
    "function": {
        "name": "query_sales",
        "description": "Query sales data",
        "parameters": {
            "type": "object",
            "properties": {
                "region": {"type": "string", "enum": ["north", "south", "east", "west"]},
                "date_range": {"type": "string", "format": "date"},
            },
            "required": ["region", "date_range"],
        }
    }
}]

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    tools=tools,
    tool_choice="auto",  # or "required" / specific tool
)
```

- **本质**：Structured Outputs 的特例 · schema 定义了 tool 调用的参数
- **Agent 的核心**：每个 tool 一个 schema · LLM 按 schema 填参数
- **跨 LLM 差异**：OpenAI / Anthropic / Gemini / 开源模型 tool use 格式略异 · LLM Gateway 或 LangChain 做适配

## 3. 开源 / 跨模型工程化

**OpenAI Structured Outputs 只在 OpenAI 模型** · 用其他模型时 · 以下库补齐：

### Instructor · Pydantic + 重试

```python
import instructor
from openai import OpenAI

client = instructor.from_openai(OpenAI())

class Person(BaseModel):
    name: str
    age: int

person = client.chat.completions.create(
    model="gpt-4o",
    response_model=Person,
    max_retries=3,
    messages=[...],
)
```

- **Pydantic 优先** · 响应自动转 Pydantic 对象
- **重试**：schema validation 失败自动重试 · 把错误反馈给模型
- **广度**：支持 OpenAI / Anthropic / Gemini / Ollama / Together / Groq 等多家
- 2026 最常用工程化库之一

### Outlines · Grammar / Regex 约束生成

```python
import outlines

model = outlines.models.transformers("meta-llama/Llama-3.3-8B-Instruct")

generator = outlines.generate.json(model, Person)
person = generator("Generate a person: ")
# 或
generator = outlines.generate.regex(model, r"\d{4}-\d{2}-\d{2}")
date = generator("Return a date: ")
```

- **底层修改生成 logits** · 强制约束输出符合 grammar / regex / JSON schema
- **本地模型** · vLLM / Transformers / llama.cpp backends
- **不需要重试** · 生成层保证
- 2024-2026 开源模型结构化首选

### SGLang Compressed FSM（高性能）

- SGLang 0.4+ 的**结构化输出 6.4× 吞吐**来自 CFSM 压缩状态机
- 生产部署的**最快开源路径**（详见 [LLM Inference](llm-inference.md)）

### Marvin · AI-first functions

```python
import marvin

@marvin.fn
def extract_person(text: str) -> Person:
    """从文本中抽取人物信息"""

person = extract_person("John is 30 years old")
```

- **装饰器风格** · 感觉像普通函数
- 轻量 · 适合快速原型

### LangChain Output Parsers

- `PydanticOutputParser` · `StructuredOutputParser` · `ResponseSchema` 等
- **问题**：底层多用 prompt + parse 路径 · 可靠性不如 Instructor / Outlines
- 作为大 LangChain 栈一部分 · 独立用价值一般

## 4. 选型决策

| 场景 | 推荐 |
|---|---|
| OpenAI 模型 · 简单 schema | **OpenAI Structured Outputs**（原生） |
| Anthropic / Gemini | 原生 Tool Use / Response Schema |
| 多家 LLM 切换 | **Instructor**（统一 API） |
| 开源模型本地跑 | **Outlines** 或 **SGLang CFSM** |
| Agent tool 参数 | Function Calling / Tool Use（机制 4） |
| 快速原型 · 函数感 | **Marvin** |
| 已在 LangChain 栈 | LangChain parser（但首选 Instructor）|

## 5. 生产模式

### 重试 + Validation

```python
from pydantic import ValidationError

for attempt in range(3):
    response = llm.generate(...)
    try:
        parsed = Schema.model_validate_json(response)
        break
    except ValidationError as e:
        # 把错误反馈回 prompt · 让 LLM 修正
        prompt += f"\n\nPrevious error: {e}. Retry."
```

- Instructor 原生做这个 · 不用自己写
- **max_retries 默认 3** · 超过则 fallback

### Fallback 链

```
Structured Outputs（强约束）
  ↓ 失败 / 模型不支持
JSON mode + schema in prompt
  ↓ 失败
Prompt-based + retry
  ↓ 失败
Fallback 模板 / 人工
```

### 部分 valid 处理

```python
# 有些字段能 parse · 有些不行
try:
    data = Schema.model_validate(raw)
except ValidationError as e:
    # 收集成功字段 · 只重试失败字段
    ...
```

### 流式结构化

- 传统：等完整响应再 parse · 用户感知慢
- 流式：边生成边增量 parse
  - OpenAI Structured Outputs 支持 streaming（`response.parsed` 逐步填）
  - Instructor 有 `stream=True` · 返回 partial Pydantic
  - 开源：Outlines 的 streaming 模式 · Partial JSON parsing
- 适用：长响应 · 列表 / 表格增量展示

### Token 预算

- 嵌套对象 · 字段名冗长 → **schema 本身吃 token**（tool schema 5 个 tool × 100 tokens = 500）
- 工具：压缩 description · 避免冗余嵌套
- OpenAI 的 Prompt Caching 能缓存工具定义（详见 [Semantic Cache](semantic-cache.md)）

## 6. 和 Agent / RAG / Guardrails 的联动

### Agent 侧（Tool Schema）

Agent 的 tool 声明 · 就是 structured output 的一种：

```python
@tool
def query_sales(region: Literal["north", "south"], date_range: date):
    """Query sales."""
    ...
```

框架（LangChain / LangGraph / Instructor）自动转 JSON Schema。

### RAG 侧（引用格式）

```python
class Answer(BaseModel):
    text: str
    citations: list[Citation]

class Citation(BaseModel):
    source_id: str
    quote: str
```

让 RAG 答案自带结构化引用 · 比 prompt "请带引用 [n]" 可靠得多。

### Guardrails 侧

- Guardrails AI 本身**围绕 schema validation 构建**
- Input guardrails 检查"用户输入符合 expected schema"
- Output guardrails 检查"LLM 输出符合 policy schema"（含"不能包含 PII"这种 meta-schema）

## 7. 陷阱与反模式

- **把 JSON mode 当 Schema 约束** · JSON mode 只保证"合法 JSON"· 字段 / 类型靠模型自觉 · 想要 schema 用 Structured Outputs
- **嵌套 schema 太深** · token 爆 · parse 慢 · 生产一般限 3 层以内
- **字段描述不写** · LLM 不知道每个字段是干嘛 · 必须 `Field(description="...")`
- **枚举用字符串不用 enum** · `type: string` 比 `enum: [north, south, east, west]` 更易写错 · 永远 enum
- **忽视模型差异** · Llama 8B 的 schema 遵守率 < GPT-4o · benchmark 自家数据 · 必要时用 Outlines 强制约束
- **流式不处理 partial** · 流式场景 parse 整段 · 用户等不到
- **无 fallback** · Schema 约束 API 挂了 → 整个 app 挂 · 必须有 prompt-based fallback
- **Function Calling 错用**：把"需要流式文本的功能"塞进 function call · function call 不流式 · 拆开
- **Schema 变更没版本化** · schema 改了 · 旧数据不 validate · 要 schema migration 机制
- **滥用 Function Calling 做简单分类**：LLM 直接输出 `{"category": "X"}` 比 function call 更轻 · 简单任务用机制 3 不用 4

## 8. 横向对比 · 延伸阅读

- [Agent Patterns](agent-patterns.md) —— Function Calling 是 tool schema 的特例
- [MCP](mcp.md) —— Tool schema 标准化的跨 host 协议
- [RAG](rag.md) —— Structured output 做引用格式
- [Guardrails](guardrails.md) —— Schema validation 作为 guardrails 落地
- [LLM Inference](llm-inference.md) —— SGLang Compressed FSM 结构化输出

### 权威阅读

- **[OpenAI Structured Outputs 文档](https://platform.openai.com/docs/guides/structured-outputs)** · **[2024-08 GA 博客](https://openai.com/index/introducing-structured-outputs-in-the-api/)**
- **[Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)**
- **[Google Gemini JSON mode](https://ai.google.dev/gemini-api/docs/json-mode)**
- **[Instructor 官方](https://python.useinstructor.com/)**
- **[Outlines · dottxt](https://dottxt-ai.github.io/outlines/)** · **[GitHub](https://github.com/dottxt-ai/outlines)**
- **[SGLang 结构化输出文档](https://docs.sglang.io/advanced_features/structured_outputs.html)**
- **[Marvin](https://www.askmarvin.ai/)**

## 相关

- [Agent Patterns](agent-patterns.md) · [MCP](mcp.md) · [RAG](rag.md) · [Guardrails](guardrails.md) · [LLM Inference](llm-inference.md)
- [Prompt 管理](prompt-management.md) —— schema 也是 prompt 资产
