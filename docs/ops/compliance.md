---
title: 数据合规 · GDPR · EU AI Act · HIPAA · 个保法 · 生成式 AI 法规
type: concept
depth: 资深
level: S
last_reviewed: 2026-04-21
applies_to: GDPR · HIPAA · PDPA · 个保法 · CCPA · SOC2 · EU AI Act (2024-08 生效) · NIST AI RMF · 中国《生成式 AI 服务管理办法》(2023-07) · 2024-2026 实践
tags: [ops, compliance, governance, privacy, eu-ai-act, ai-compliance]
aliases: [Compliance, Data Privacy, AI Compliance]
related: [data-governance, security-permissions, ai-governance, model-registry]
status: stable
---

!!! warning "章节分工声明"
    - **本页**：合规法规的**工程实施视角**（具体要求 · 技术对应 · 落地清单）· 含 §4 AI 合规（EU AI Act · NIST AI RMF · 中国生成式 AI 管理办法）
    - **Guardrails 技术层 + Red Teaming 方法** → [ai-workloads/guardrails](../ai-workloads/guardrails.md)
    - **Model Card / 模型许可工程实施** → [ml-infra/model-registry](../ml-infra/model-registry.md) §合规 artifact

# 数据合规

!!! tip "一句话理解"
    **湖仓承载的数据几乎都受法律约束**。GDPR（欧盟）· HIPAA（美医疗）· PDPA（新加坡等亚洲）· 中国《个人信息保护法 / 数据安全法》· CCPA（加州）—— 各地立法要求不同但核心一致：**知情 · 最小化 · 可删除 · 可追溯 · 跨境受限**。工程化的合规护栏是**"数据产品"**的基础能力。

!!! abstract "TL;DR"
    - **GDPR 三大核心**：Right to access · Right to be forgotten · Consent
    - **HIPAA**（医疗美国）：PHI（protected health information）严控
    - **中国**：数据本地化 + 个人信息出境安全评估
    - **湖上工程手段**：分类标签 + 行级过滤 + 删除流程 + 审计日志 + 加密
    - **跨境**：Schrems II 判决后，欧美数据流动按 Standard Contractual Clauses
    - **SOC 2 / ISO 27001**：商业客户几乎都要求

## 1. 主要法规速览

### GDPR（欧盟，2018 年生效）

**全球最严格、影响最广**。核心权利：

| 权利 | 含义 |
|---|---|
| **Right to access** | 用户可要求获取其全部数据 |
| **Right to be forgotten** | 用户可要求彻底删除 |
| **Right to rectification** | 更正错误数据 |
| **Right to data portability** | 导出结构化数据 |
| **Consent** | 数据处理前同意 |
| **Data breach notification** | 72 小时内告知 |

**处罚**：最高全球营业额 4% 或 2000 万欧元。

**典型事故**：
- Meta 被罚 13 亿欧元（2023，数据跨境）
- Amazon 被罚 7.46 亿欧元（2021）

### HIPAA（美国医疗）

**PHI (Protected Health Information)** 必须严格保护：
- 姓名、地址、日期（除年份）
- 医保号、病历号、账户号
- 生物识别数据
- 任何可识别患者的信息

**覆盖实体**：医院、诊所、保险、服务商。**BAA**（Business Associate Agreement）是云使用的前提。

### PDPA 系列（新加坡 / 泰国等亚洲）

类似 GDPR 但**略轻**。各国略有差异。

### 中国《个人信息保护法》+ 《数据安全法》

2021 生效。关键：

- **个人信息分类**：一般 / 敏感（如生物识别、医疗、金融、14 岁以下未成年人）
- **处理原则**：**合法、正当、必要**
- **敏感个人信息**需"单独同意"
- **跨境传输**：需要安全评估（CAC 审批）或认证
- **关键信息基础设施**（CII）数据本地化

### CCPA（加州）

类似 GDPR 简化版。2023 扩展为 CPRA，新增 sensitive PI 分类。

### SOC 2

**安全 / 可用性 / 保密性 / 处理完整性 / 隐私**五大 Trust Principle。
不是法律，是商业客户采购门槛。

## 2. 湖仓层面的合规工程

### 基础护栏清单

- [ ] **数据分类标签**（Tag by sensitivity）
- [ ] **访问控制**（RBAC / ABAC / 行级 / 列级）
- [ ] **加密**（传输 TLS + 存储 SSE）
- [ ] **审计日志**（谁何时访问了什么）
- [ ] **PII 识别与脱敏**
- [ ] **删除流程**（GDPR 被遗忘权）
- [ ] **跨境传输控制**
- [ ] **数据保留期**（过期自动销毁）
- [ ] **Consent 记录**
- [ ] **DPIA**（高风险处理的影响评估）

### 实现 1 · 数据分类

```sql
-- Iceberg 表属性
ALTER TABLE prod.sales.orders SET TBLPROPERTIES (
  'data.classification' = 'confidential',
  'data.contains_pii' = 'true',
  'data.retention_days' = '2555',   -- 7 年
  'data.owner' = 'sales_team'
);

-- 列级标签（部分 Catalog 支持，如 Unity / Polaris）
ALTER TABLE prod.sales.orders ALTER COLUMN email 
  SET TAGS ('pii', 'sensitive');
ALTER TABLE prod.sales.orders ALTER COLUMN phone 
  SET TAGS ('pii', 'sensitive');
```

### 实现 2 · 行级安全

```sql
-- Unity Catalog 行级过滤函数
CREATE FUNCTION row_filter_by_tenant(tenant_id STRING)
  RETURNS BOOLEAN
  RETURN tenant_id = current_user_tenant();

ALTER TABLE prod.sales.orders
  SET ROW FILTER row_filter_by_tenant ON (tenant_id);
```

### 实现 3 · 列级脱敏（动态视图）

```sql
CREATE VIEW prod.sales.orders_masked AS
SELECT
  order_id,
  CASE WHEN is_member('pii_access') THEN email 
       ELSE regexp_replace(email, '(?<=.).*(?=@)', '***') 
       END AS email,
  CASE WHEN is_member('finance') THEN amount ELSE NULL END AS amount
FROM prod.sales.orders;
```

### 实现 4 · GDPR 被遗忘权（Right to be Forgotten）

```sql
-- Iceberg v2 Row-Level Delete
DELETE FROM prod.sales.orders WHERE user_id = 'U-12345';

-- 后续 vacuum 物理删除数据文件
CALL system.remove_orphan_files('prod.sales.orders', older_than => now() - INTERVAL 30 DAYS);

-- 向量库也需删除
lancedb_table.delete("user_id = 'U-12345'")
```

**关键**：不只是"标记删除"，**还要物理从磁盘删除**（GDPR 要求）。

**对 Iceberg**：删除写到 Delete File → 下次 compaction 物理合并 → expire_snapshots 后物理清除。

### 实现 5 · 加密

**两类**：

| 类型 | 做法 |
|---|---|
| **In-Transit** | HTTPS / TLS 1.2+ · 集群内 mTLS |
| **At-Rest** | S3 SSE（AES-256）· KMS 密钥 · **Client-side encryption**（Iceberg 支持） |
| **Column-level** | 敏感列单独密钥（Iceberg 支持）|

### 实现 6 · 审计日志

```sql
-- Audit log 作为 Iceberg 表
CREATE TABLE audit.access_log (
  event_ts TIMESTAMP,
  user_id  STRING,
  operation STRING,      -- SELECT / INSERT / DELETE / SHARE / ...
  catalog  STRING,
  schema   STRING,
  table    STRING,
  columns  ARRAY<STRING>,
  row_count BIGINT,
  query_text STRING,
  client_ip STRING,
  success  BOOLEAN
) USING iceberg
PARTITIONED BY (days(event_ts));
```

所有引擎（Trino / Spark / DuckDB 通过 Catalog）查询 → 写入 audit。

## 3. 跨境传输

### 欧美之间（Schrems II 后）

2020 Schrems II 判决让 Privacy Shield 无效。目前方案：

1. **Standard Contractual Clauses (SCC)**：合同承诺 GDPR 级别保护
2. **Transfer Impact Assessment (TIA)**：评估目的地法律风险
3. **Supplementary measures**（加密 / 假名化）

**实务**：
- Anthropic、OpenAI 的欧洲客户，数据在 EU-hosted instances
- AWS / GCP 提供 EU region + data residency 承诺

### 中国出境

需要：
- **CAC 安全评估**（大规模 / 敏感数据）
- **个人信息保护认证**（中等规模）
- **标准合同**（小规模）

工程手段：
- 关键数据**本地化**（中国业务用中国区域）
- Cross-region 流动**经审批路径**
- **数据分级** + **出境清单** 管理

## 4. AI 合规叠加（2024-2026 重点）

AI 法规**2024-2026 爆发** · 本节详细讲工程影响。Red Teaming 方法论和 Guardrails 工具见 [ai-workloads/guardrails](../ai-workloads/guardrails.md) §7。

### 4.1 EU AI Act（2024-08 生效 · 2026-08 全量执行）

**全球最严格的 AI 法规**。核心是**风险分级**：

| 风险级 | 定义 | 工程要求 |
|---|---|---|
| **Unacceptable Risk** | 社会评分 · 实时生物识别执法 · 操纵人类行为 | **禁止** |
| **High Risk** | 招聘 · 信贷 · 执法 · 教育 · 医疗决策 · 关键基础设施 | **严格监管**（见下方详细） |
| **Limited Risk** | 聊天机器人 · 深度伪造 | **透明度要求**（告知用户是 AI） |
| **Minimal Risk** | 游戏 AI · 垃圾邮件过滤 | 无特殊要求 |

**High Risk 系统工程要求**（对数据平台影响最大）：

1. **Risk Management System** · 系统化风险识别 / 评估 / 缓解流程
2. **Data Governance** · 训练 / 验证 / 测试数据的质量 + 偏见检查
3. **Technical Documentation**（必须有 **Model Card** + 训练数据描述）· 见 [ml-infra/model-registry](../ml-infra/model-registry.md) §合规 artifact
4. **Record-Keeping** · 自动日志保存 · 用于事后审计
5. **Transparency** · 使用者理解系统输出
6. **Human Oversight** · HITL · 人可以停掉 / 审核
7. **Accuracy · Robustness · Cybersecurity**

**处罚**：最高 **3500 万欧元或全球营业额 7%**（更严 GDPR）。

### 4.2 NIST AI Risk Management Framework（AI RMF · 2023）

**美国联邦层面的 AI 风险管理框架**（非法律但政府采购要求）：

**AI RMF 四功能**：
- **Govern** · 组织治理 AI 风险
- **Map** · 识别 AI 使用场景和风险
- **Measure** · 测量风险（准确性 · 偏见 · 鲁棒性 · 可解释性 · 隐私）
- **Manage** · 优先级排序 · 分配资源 · 缓解

**工程对应**：Model Card + 自动评估 + Fairness subgroup 监控 + 文档。

### 4.3 中国《生成式 AI 服务管理办法》（2023-07 生效）

**中国针对生成式 AI 的专门法规**：

核心要求：
- **备案** · 提供服务需向网信办备案
- **数据合规** · 训练数据来源合法 · 不侵犯知识产权
- **内容安全** · 输出不得生成违法有害内容
- **用户标识** · 生成内容明示为 AI 生成
- **个人信息** · 不得非法处理个人信息
- **未成年人保护** · 防沉迷

**工程对应**：
- 内容过滤（见 [ai-workloads/guardrails](../ai-workloads/guardrails.md)）
- 输出水印 / 标识
- 训练数据来源审计
- 用户行为日志保存

**更宽**：还有《互联网信息服务算法推荐管理规定》（2022）· 《互联网信息服务深度合成管理规定》（2023）· 《生成式 AI 服务管理办法》（2023）· 三者组合。

### 4.4 AI 供应链合规（2024-2026 新话题）

**模型 License 合规**是 AI 供应链核心问题：

- **Llama 3 Community License**：**7 亿 MAU 上限**（超限要单独谈）· 不得训练竞品 LLM
- **Gemma Terms**：相对宽松但有使用政策
- **Mistral**（开源系列）：Apache 2.0 · 商用友好
- **Qwen / DeepSeek / Baichuan** · 各版本不同

**工程对应**：
- Model Registry 强制 license 元数据（见 [ml-infra/model-registry](../ml-infra/model-registry.md)）
- Fine-tuned 模型**继承 base license 限制**
- 自动扫描（MAU 接近限制告警）

### 4.5 AI 系统的典型合规清单

对应 EU AI Act High Risk 系统 · 工程 checklist：

- [ ] Model Card 完整（预期用途 / 限制 / 训练数据）
- [ ] Fairness subgroup 监控（demographic parity / equal opportunity）
- [ ] Drift 监控 + 告警
- [ ] Human-in-the-loop 机制（高风险决策可人工 override）
- [ ] 审计日志（模型输入输出完整留存 ≥ 3 年）
- [ ] 透明度（用户知道这是 AI 决策）
- [ ] Red Teaming 报告（安全测试）
- [ ] 训练数据来源合规证明
- [ ] 数据删除权（GDPR 的 Right to be forgotten · 叠加 AI 场景）
- [ ] Unlearning 策略（虽然技术不成熟 · 合规期待）

## 5. SOC 2 落地要点

企业客户最常要求。**Type II** 审计（6-12 月期）是真正有价值的。

五个 Trust Principle：

| | 核心控制 |
|---|---|
| **Security** | 访问控制、加密、漏洞管理 |
| **Availability** | SLO、DR、Backup |
| **Confidentiality** | 分类、加密、NDA |
| **Processing Integrity** | 数据质量、自动化测试 |
| **Privacy** | Consent、访问请求、删除流程 |

**工具**：Vanta · Drata · SecureFrame（商业合规平台）帮做 SOC 2。

## 6. 合规与工程冲突的平衡

### 常见冲突

| 合规要求 | 工程影响 |
|---|---|
| 数据最小化 | 想留一切数据做分析 |
| 删除权 | 历史 snapshot 难处理 |
| 跨境限制 | 云成本多 region 部署 |
| 审计日志保留 | 存储成本 |
| 加密 | 延迟 + 运维 |

### 平衡原则

- **分级**：不是所有数据都要最高合规，按分类区分
- **尽量自动化**：手动合规成本爆
- **影响评估**：重大变更走 **DPIA**
- **合规工具链一次投入**：省却每个项目重复做

## 7. 陷阱

- **"我们没欧洲用户"**：但 B 端客户有 → 传染合规要求
- **Audit log 不保留**：事故发生后查不到原因 → 监管重罚
- **Iceberg 旧 snapshot 含被删数据**：`expire_snapshots` 必须跑
- **向量库没删除**：LanceDB / Milvus 里用户 embedding 还在
- **日志里 PII 明文**：自己违法
- **Cross-region 自动同步不加审批**：数据悄悄出境
- **加密密钥管理差**：KMS 配错权限 → 密钥泄露 = 全部数据泄露
- **Consent 没记录**：监管查同意证据拿不出
- **SOC 2 纸面合规**：证书有但实际控制缺失 → 真审计挂

## 8. 延伸阅读

- **[GDPR 官方全文](https://gdpr.eu/)** · **[HIPAA 官方](https://www.hhs.gov/hipaa/)**
- **[中国个保法](https://www.gov.cn/xinwen/2021-08/20/content_5632486.htm)** · **[数据安全法](https://www.gov.cn/xinwen/2021-06/11/content_5616919.htm)**
- **[NIST Privacy Framework](https://www.nist.gov/privacy-framework)**
- **[AICPA SOC 2 指南](https://www.aicpa.org/resources/landing/soc-2)**
- **[Schrems II 判决](https://edpb.europa.eu/sme-data-protection-guide/international-data-transfers)**
- *Privacy Engineering: A Dataflow and Ontological Approach*（Cranor, 2022）
- *The Privacy Engineer's Manifesto*（Dennedy et al.）

## 相关

- [数据治理](data-governance.md) · [安全与权限](security-permissions.md) · [多租户](multi-tenancy.md)
- [ai-workloads/guardrails](../ai-workloads/guardrails.md) · Guardrails 工程 + §7 Red Teaming 方法
- [TCO 与定价模型](tco-model.md)
