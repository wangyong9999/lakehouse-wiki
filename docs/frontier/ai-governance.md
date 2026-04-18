---
title: AI 治理 · EU AI Act / Guardrails / Red Teaming
type: concept
depth: 资深
level: A
applies_to: EU AI Act 2024+, 生成式 AI 管理办法 2024+
tags: [frontier, governance, compliance, safety, ai]
aliases: [AI Governance, AI 合规]
related: [compliance, agentic-workflows, rag]
status: stable
---

# AI 治理 · 合规 + 安全 + 对齐

!!! tip "一句话理解"
    **AI 产品化的合规与安全护栏**。2024+ 全球进入强监管：欧盟 AI Act、中国生成式 AI 管理办法、美国各州 AI 法案。团队必须回答"这个 AI 系统有多大风险、怎么验证、出事怎么办"。**Guardrails + Red Teaming + 可追溯**是三大抓手。

!!! abstract "TL;DR"
    - **监管格局**：EU AI Act（风险分级）· 中国《生成式 AI 管理办法》· 美国 EO 14110
    - **分级监管**：EU 把 AI 分 **不可接受 / 高风险 / 有限风险 / 最小风险** 四级
    - **三大护栏**：**Input Guardrails**（prompt 过滤）· **Output Guardrails**（内容过滤）· **Tool/Action Guardrails**（危险操作拦截）
    - **Red Teaming**：对抗测试、越狱尝试、有害内容诱导
    - **可追溯**：Prompt + 模型版本 + 输出 + 决策 全链路审计
    - **工具生态**：NVIDIA NeMo Guardrails · Guardrails AI · Lakera · Protect AI

## 1. 背景 · 为什么合规突然紧迫

### 监管时间线

| 时间 | 地区 | 事件 |
|---|---|---|
| 2022.11 | - | ChatGPT 发布 |
| 2023.07 | 中国 | 《生成式 AI 管理办法》征求意见稿 |
| 2023.10 | 美国 | Biden EO 14110（AI 行政命令）|
| 2024.03 | 欧盟 | **EU AI Act 立法通过** |
| 2024.08 | 欧盟 | **生效** |
| 2024+ | 多地 | 加州 SB 1047 · 美国 AI 安全局 |

**合规已不是"未来问题"**，而是**当下必须做的事**。

### 典型合规事故

- **ChatGPT 在欧盟一度被禁**（2023，意大利 GDPR 问题）
- **某银行 AI 客服被利用绕过限额**（2024）
- **生成式 AI 版权诉讼**（《纽约时报》vs OpenAI）
- **Deep fake 诈骗金额飙升**（2024 - 数亿美元）

## 2. EU AI Act 分级

四级风险：

| 级别 | 定义 | 例 | 要求 |
|---|---|---|---|
| **Unacceptable Risk** | 禁用 | 社会评分、AI 操纵 | **禁止** |
| **High Risk** | 受严格监管 | 医疗诊断、招聘、信贷、司法 | 合规审计、CE 标志、持续监控 |
| **Limited Risk** | 透明度要求 | 聊天机器人、深度伪造 | 告知用户是 AI |
| **Minimal Risk** | 自愿 | 游戏 AI、垃圾邮件过滤 | 鼓励 best practice |

**生成式 AI / 基础模型**单列：需要公开训练数据摘要、版权清单、安全评估。

### 高风险场景的 10 点合规要求

1. 数据治理（质量、偏见）
2. 文档（技术文档、风险评估）
3. 记录保留（log）
4. 透明度（用户告知）
5. 人工监督
6. 准确性（测试标准）
7. 鲁棒性（对抗测试）
8. 网络安全
9. 质量管理系统
10. 注册 / CE 标志

## 3. 中国《生成式 AI 管理办法》

2023.08 正式施行。核心要求：

- **备案制**：有"公众舆论属性"或"社会动员能力"的必须备案
- **内容合规**：符合社会主义核心价值观
- **数据合规**：训练数据合法来源、无侵权
- **实名认证**：用户侧
- **显著标识**：生成内容要标记
- **安全评估**：上线前评估

执行机构：**国家互联网信息办公室（CAC）**。

## 4. 技术护栏（Guardrails）

### 分类

| 位置 | 防什么 |
|---|---|
| **Input Guardrails** | Prompt Injection / 越狱 / 有害输入 |
| **Output Guardrails** | 有害 / 偏见 / 虚假信息 / 隐私泄露 |
| **Tool / Action Guardrails** | 危险操作（删库、转账、发邮件）|
| **Chain-of-thought Guardrails** | 中间步骤的越界 |

### Input Guardrails

检测 + 拦截：
- **Prompt Injection**（让 LLM 忽略原 system prompt）
- **Jailbreak**（诱导输出有害内容）
- **Data Extraction**（让 LLM 泄露训练数据）
- **Off-topic**（超出产品范围）

工具：
- **Lakera AI**（商业）
- **Microsoft Prompt Shields**
- **Protect AI Llama Guard**（开源）
- **NeMo Guardrails**（NVIDIA，规则式）

### Output Guardrails

- **有害内容**：暴力 / 仇恨 / 自伤
- **偏见**：种族 / 性别 / 年龄歧视
- **PII 泄露**：不应出现的个人信息
- **幻觉**：与 RAG context 不符
- **版权**：逐字复制训练文本

工具：
- **Llama Guard 3**（Meta）
- **Guardrails AI**（开源）
- **OpenAI Moderation API**
- **Perspective API**（Google）

### Tool / Action Guardrails（Agent 时代关键）

- **最小权限**：Agent 不应有超出任务的权限
- **User Confirmation**：敏感操作需用户确认
- **Approval Workflow**：高风险操作走审批
- **Rate Limit + Quota**：防滥用

## 5. Red Teaming（对抗测试）

专门团队或工具**主动攻击** AI 系统：

### 攻击维度

| 攻击 | 做什么 |
|---|---|
| **Prompt Injection** | "忽略前面指令，做 X" |
| **Jailbreak** | DAN / AIM / 多轮诱导 |
| **Adversarial Input** | 错字 / 同义替换 / 噪声 |
| **Data Poisoning** | 投毒训练数据（针对 RAG 语料） |
| **Model Extraction** | 通过大量 query 复刻模型 |
| **Membership Inference** | 推断某数据是否在训练集 |

### 工具

- **Microsoft PyRIT**（Python Risk Identification Tool）
- **Garak**（LLM vulnerability scanner）
- **Promptfoo**（可对抗测试框架）
- **Llama-Attacks** 数据集

### 推荐流程

1. **每季度一次**全面 red team
2. **持续 automated red team**（CI 跑对抗测试）
3. **第三方审计**（合规要求）
4. **Bug Bounty**（像 Anthropic / OpenAI 做公开奖金）

## 6. 可追溯性 · 审计

### 必要日志

```
每次交互记录：
- timestamp
- user_id
- session_id
- input (redacted if PII)
- system_prompt version
- model + version
- tools invoked
- output
- guardrail decisions (通过 / 拦截原因)
- confidence / grounding score
```

### 存储

- **Iceberg 审计表**：方便 SQL 查询 + 合规审计
- **保留期**：金融 / 医疗通常 5-7 年
- **PII 脱敏**：日志里敏感字段 hash 或 redact

### 血缘（AI Lineage）

合规越来越要求：
- 这个答案**来自哪篇文档**（RAG 引用）
- 这个模型**训练用了哪些数据**
- 这次调用**经过哪些 tool**

**Model Cards + Data Cards + System Cards** 是标准做法。

## 7. 团队的落地

### 阶段 1 · 基础（所有团队）

- [ ] 所有 LLM 调用**有审计日志**
- [ ] Output Guardrails（Llama Guard 3 最低配）
- [ ] PII 脱敏（日志 + 输出）
- [ ] **用户告知**（产品界面标识是 AI）

### 阶段 2 · 进阶（面向 B 端 / 金融 / 医疗）

- [ ] Input Guardrails（Prompt injection 防御）
- [ ] Tool Guardrails（敏感操作审批）
- [ ] Red Team 每季度一次
- [ ] **Model Card** 发布

### 阶段 3 · 合规（EU / 监管严格）

- [ ] DPIA（Data Protection Impact Assessment）
- [ ] CE 标志 / 合规审计
- [ ] 第三方 red team
- [ ] Incident response playbook

## 8. 横向对比 · 延伸阅读

- [合规总论](../ops/compliance.md)（TODO R2.4）
- [Agentic Workflows 安全](../scenarios/agentic-workflows.md) —— Agent 的安全最佳实践

### 权威阅读

- **[EU AI Act 全文](https://artificialintelligenceact.eu/)**
- **[中国《生成式 AI 管理办法》](http://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm)**
- **[US EO 14110](https://www.whitehouse.gov/briefing-room/presidential-actions/2023/10/30/executive-order-on-the-safe-secure-and-trustworthy-development-and-use-of-artificial-intelligence/)**
- **[Llama Guard 3](https://ai.meta.com/blog/llama-guard-3/)** · **[NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)**
- **[OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)** —— 攻击分类
- **[Anthropic Red Teaming Guide](https://www.anthropic.com/news/challenges-in-red-teaming-ai)**
- **[NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)**
- **[Stanford CRFM: Foundation Model Transparency Index](https://crfm.stanford.edu/fmti/)**

## 相关

- [业务场景全景](../scenarios/business-scenarios.md)
- [Agentic Workflows](../scenarios/agentic-workflows.md)
- [安全与权限](../ops/security-permissions.md) · [数据治理](../ops/data-governance.md)
