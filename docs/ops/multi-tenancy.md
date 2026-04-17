---
title: 多租户隔离
type: concept
depth: 资深
prerequisites: [security-permissions, unified-catalog-strategy]
tags: [ops, multi-tenancy, isolation]
related: [security-permissions, data-governance, cost-optimization]
systems: [iceberg, unity-catalog, kubernetes]
status: stable
---

# 多租户隔离

!!! tip "一句话理解"
    **多个业务团队共享同一个湖仓底座**时，要隔离的不只是"数据看不到"，还有**命名空间、计算资源、成本核算、故障爆炸半径**。每一层隔离强度不同，整体取舍就是"成本 vs 强度"的权衡。

!!! abstract "TL;DR"
    - **5 层隔离**：命名空间 / 权限 / 存储 / 计算 / 成本
    - 硬隔离（独立集群）最强但贵；软隔离（Queue / Resource Group）廉价但可能互相影响
    - **Catalog 是多租户的锚点**：命名空间 → 权限 → 资源池都绑它
    - 一个团队的坏作业**绝不能**让另一个团队的 BI 仪表盘挂掉（爆炸半径）
    - 成本公平分摊比"只算用量"更重要 → show-back / charge-back

## 什么要隔离

| 层 | 租户之间需要隔离 | 风险举例 |
| --- | --- | --- |
| 命名空间 | 表名、向量库 collection、模型名 | 命名冲突 |
| 权限 | 谁能读写哪些资产 | 越权访问 |
| 存储 | 数据物理路径、桶、加密 | 误删他人数据 |
| 计算 | CPU / 内存 / GPU | 一租户打爆集群 |
| 成本 | 账单归属 | 某租户白嫖 |

## 层 1 · 命名空间隔离

**Catalog 层的基本手段**。

Iceberg / Unity / Nessie 都支持多级命名：

```
catalog
  └── <tenant>          ← 租户域
       └── <schema>
            └── table / vector_collection / model
```

**实操建议**：

- 租户名即 Catalog 的一级目录（`finance.*` / `marketing.*`）
- 命名规范写进 `contributing.md` 强制遵守
- 禁止在 `shared.*` 下随意开表（只允许平台团队审批）

## 层 2 · 权限隔离

详见 [安全与权限](security-permissions.md)。多租户场景的关键：

- **租户 group** 作为一等公民：RBAC 主体不是个人，是角色
- **行级 policy**：同一张宽表里按 `tenant_id` 过滤，跨租户透明
- **列级 Mask**：某些敏感列对跨租户只显示 `***`
- **Service Principal**：租户的服务账号（ETL 作业、API 服务），权限按最小化颁发
- **Credential vending**：对象存储凭证由 Catalog **短时**颁发（15 分钟 TTL），绝不下发长期 AWS Key

## 层 3 · 存储隔离

三种强度：

### 弱：同 bucket 不同 prefix

```
s3://warehouse/
  ├── finance/
  └── marketing/
```

- 依赖权限（IAM + Catalog）
- 运维简单
- **风险**：IAM 误配会跨 prefix 露出

### 中：不同 bucket

```
s3://lake-finance/
s3://lake-marketing/
```

- bucket 级独立 IAM
- 跨 bucket 访问必须显式授权
- 推荐**中大团队**的默认

### 强：不同账号 / 子组织

- AWS Organizations / GCP Projects / 阿里云子账号
- 网络层也隔离
- 审计、合规要求极严时采用

## 层 4 · 计算隔离

### 查询引擎 (Trino / Spark / Flink)

**Resource Group**（Trino）/ **Queue**（Spark YARN/K8s）：

```
resource-groups.json:
  root:
    finance:
      hardConcurrencyLimit: 20
      softMemoryLimit: 40%
    marketing:
      hardConcurrencyLimit: 20
      softMemoryLimit: 40%
    exploration:  # 低优先级
      hardConcurrencyLimit: 5
      softMemoryLimit: 20%
      schedulingWeight: 1
```

**软隔离**：共享集群，配额约束。成本低，但调度器挂了互相影响。

**硬隔离**：每个租户独立集群。强但贵（运维 × N）。

**实操建议**：

- 每个租户**一个 Resource Group** 作为起点
- P0 业务可以额外**独立集群**（如财报月封装）
- 探索 / Notebook 走**共享低优先级池**

### GPU 隔离（AI 负载）

见 [GPU 调度](../ml-infra/gpu-scheduling.md)：
- MIG（NVIDIA A100+）做硬切分
- MPS 做软并发
- Volcano / Kubernetes 做队列

## 层 5 · 成本核算

**show-back / charge-back**：

- **Show-back**：只告知租户用了多少，不收费。培养意识
- **Charge-back**：真实转账，激励优化

关键数据来源：

- 对象存储 inventory 报告（按 prefix / tag 聚合）
- 查询引擎日志（`query_id + user + cpu_time + bytes_scanned`）
- K8s 资源用量（CPU·h + GPU·h × 单价）

写成月度 dashboard，每个租户对自己账单可见。

## 爆炸半径（Blast Radius）

真正的多租户考验 = **一个租户出问题，其他租户是否受影响**：

| 事件 | 良好设计下应该 | 反例 |
| --- | --- | --- |
| 租户 A 提交爆内存的查询 | A 的 Resource Group OOM，其他租户无感 | 共享 JVM 崩溃，全部租户查询失败 |
| 租户 A 的 ETL 写入错误 | 只污染 A 的 schema | 写到共享表 |
| 租户 A 把 API Key 泄露 | A 范围内的凭证可轮换，其他无影响 | 长期 root key 共享 |
| 租户 A 发起 DDoS 级查询 | Coordinator throttle | 全集群卡死 |

**定期演练**：故意提交一个"坏查询"，验证其他租户无感。

## 成熟路径

| 阶段 | 代表做法 |
| --- | --- |
| **初创** | 单 bucket 多 prefix + Catalog 权限 + Resource Group |
| **中期** | 多 bucket + Service Principal + show-back |
| **规模化** | 多账号 / 多 Catalog + charge-back + 独立 P0 集群 |
| **企业级** | 跨区域 / 数据驻留 + 合规隔离 + 审计分租户 |

不要**跳级**——初期多 bucket 多账号是过度工程。

## 反模式

- **所有人都是 admin 角色** → 出事的时候谁改的都找不到
- **长期 AWS root key 下发给开发者** → 合规炸弹
- **单一 Catalog 不分命名空间** → 长期拆分极贵
- **硬隔离但无 charge-back** → 成本失控
- **软隔离但无 Resource Group** → 互相影响

## 相关

- [安全与权限](security-permissions.md) —— 权限隔离的基础
- [数据治理](data-governance.md) —— 治理视角
- [成本优化](cost-optimization.md) —— charge-back 基础
- [统一 Catalog 策略](../unified/unified-catalog-strategy.md) —— Catalog 作为锚点

## 延伸阅读

- Unity Catalog Multi-tenancy docs
- Trino Resource Group 配置
- AWS "Data Mesh" 多账号架构参考
- *Data Mesh*（Zhamak Dehghani）——按域划分的组织模式与多租户天然契合
