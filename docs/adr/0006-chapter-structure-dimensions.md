---
title: 0006 章节结构与维度划分 · 多维并存 + canonical source 原则
type: adr
status: accepted
date: 2026-04-21
deciders: [wangyong9999]
---

# 0006. 章节结构与维度划分

## 背景

wiki 到 2026-Q2 有 22 个顶级章节 · 约 42k 行。章节组织同时沿四个维度展开：

- **技术栈维度** · `lakehouse/` `retrieval/` `query-engines/` `catalog/` `ai-workloads/` `bi-workloads/` `ml-infra/` `pipelines/` · 按"它是什么技术"分
- **角色维度** · `roles/` `learning-paths/` · 按"你是谁"分
- **业务场景维度** · `scenarios/` · 按"你要做什么"分
- **工程实践维度** · `ops/` `foundations/` · 按"怎么稳定运转"分

参考 / 辅助区：`compare/` `unified/` `cases/` `frontier/` `tutorials/` `cheatsheets/` `adr/` `_templates/`。

2026-Q2 对抗评审发现四个症状 ——
1. `scenarios/` 的页面常与机制章（`bi-workloads/` `ai-workloads/` `lakehouse/`）内容重叠，版本 / 数字漂移
2. 同一概念（MV · Text-to-SQL · RAG）出现在 ≥ 2 个章节，没声明哪个是 canonical
3. 新增内容时不知道"该放哪章"——扩容成本随章节数平方上升
4. 每页 metadata 和导航入口质量不一

外部类比：Diátaxis（tutorial / how-to / reference / explanation）本身就是多维度 · 多入口本身不是 bug。

## 决策

**维度并存是特性 · 不是 bug。治理点在 canonical source + signposting · 不在"合并维度"。**

### 章节归属规则

- **机制 / 原理类** → 技术栈维度（`lakehouse/` `retrieval/` `query-engines/` etc.）· 是唯一 canonical
- **端到端业务** → `scenarios/` · 必须 link 到机制 canonical · **不再独立描述机制**
- **横向对比** → `compare/` · 选型决策树为主 · 不复述单产品
- **角色阅读清单** → `roles/` + `learning-paths/` · 只聚合不新写
- **工程实践** → `ops/` · 通用治理（备份 / SLO / 成本 / 安全 / 性能调优）
- **跨章节组合视角**（真·不属单章的架构组合 / 选型决策 / 团队路线主张）→ `unified/` · **极严格**· 每次新增必须验证"5 个以上单章都无法单独承载"才放这里（2026-Q2 S29 重整后 unified/ 从 10 页精简到 3 页 · 案例页外迁到 `cases/` · 选型页外迁到对应技术栈章）
- **工业案例参考**（Netflix / LinkedIn / Uber 等工业数据平台公开资料）→ `cases/` · reference 性质 · 不讲机制 · 讲"别人怎么做"
- **前沿 / 实验性** → `frontier/` · 定期回顾 · 成熟后下沉主章（迁移 ADR 写明）

### canonical source 约定

每个**核心概念**在 wiki 中只有一个 canonical 页。其他地方提到该概念时：

- 用 markdown link 指向 canonical
- 不再重复描述机制 · 不再重复版本表 · 不再重复 benchmark 数字
- 如果必须概述 · 明确标注"详见 `<chapter>/<page>.md`"并控制在 1-2 段

canonical 归属优先级：**技术栈章 > 对比章 > 场景章**。例如：
- 物化视图 canonical = `bi-workloads/materialized-view.md`（BI 视角的原理 · 不是 `lakehouse/`）
- RAG canonical = `ai-workloads/rag.md`（不是 `scenarios/rag-on-lake.md`）
- Iceberg V3 canonical = `lakehouse/iceberg.md`（不是 `frontier/`）

### signposting 要求

非 canonical 页面顶部显式横幅 · 格式示意（不是真 link · 写作时替换为实际路径）：

```markdown
!!! info "本页是场景视角"
    机制深挖见 [<机制章路径>](../<chapter>/<page>.md)
```

## 依据

### 为什么不合并维度

多维是读者真实需求的映射 · 强制单维会让某个读者群失去入口。Diátaxis / Microsoft Learn / AWS Well-Architected Framework 都是多维组织 · 这不是我们独有的问题。

### 为什么不"场景即机制简版"

scenarios 的价值应当是**"把多个机制编排成一个业务方案"**·而不是"又一遍描述这些机制"。2026-Q2 评审已证明 scenarios 滑向后者 · 治理方式是**强制 link + 瘦身** · 不是取消 scenarios。

### 为什么不按英文社区"Reference / Guide / Tutorial" 三段分

我们的读者画像（数据湖 + BI + AI 三合一）跨 Diátaxis 四象限 · 按象限拆反而切碎技术脉络。多维现状更贴合读者搜索路径。

## 后果

**正面**：

- 明确了新增内容的归属判断流程 · 扩容不再焦虑
- canonical source 约定让跨章 drift 有了治理抓手
- scenarios 章定位清晰化 · 后续可按此瘦身

**负面**：

- canonical 约定需要写作纪律 · 作者每次写新页要主动查 canonical
- signposting 横幅要一次补齐（约 20 处）
- 新概念的 canonical 归属偶有争议

**后续**：

- 写 B5 `scenarios/` 瘦身清单 · 在该章每页加横幅
- 写 hook 检查 canonical 约定（detect "同一概念在多章有 2+ 节深描述"）—— 下一个 ADR
- 建立"新内容归属决策 5 问"写入 contributing.md

## 相关

- ADR [0007](0007-version-refresh-sop.md) 版本刷新 SOP · 保证 canonical 不漂移
- ADR [0008](0008-adversarial-review-sop.md) 对抗评审 SOP · 周期性检查 canonical 遵守
- [scenarios/index.md](../scenarios/index.md) · 本 ADR 的首要影响面
