---
title: 数据合规 · GDPR / HIPAA / PDPA / 个保法 / 跨境
type: concept
depth: 资深
level: A
applies_to: GDPR · HIPAA · PDPA · 个保法 · CCPA · SOC2 · 2024-2025
tags: [ops, compliance, governance, privacy]
aliases: [Compliance, Data Privacy]
related: [data-governance, security-permissions, ai-governance]
status: stable
---

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

## 4. AI 合规叠加

详见 [AI 治理](../frontier/ai-governance.md)。

核心：
- LLM 训练数据 **来源合规**
- Prompt / Output 的**审计与过滤**
- **EU AI Act** 分级

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
- [AI 治理](../frontier/ai-governance.md)
- [TCO 与定价模型](tco-model.md)
