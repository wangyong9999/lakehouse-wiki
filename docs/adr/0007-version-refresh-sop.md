---
title: 0007 版本刷新 SOP · known_versions.yml + version_scan.py + 季度刷新
tags: [adr, decision, governance]
type: adr
status: accepted
date: 2026-04-21
deciders: [wangyong9999]
---

# 0007. 版本刷新 SOP

## 背景

2026-Q2 对抗评审发现 · wiki 中 **frontmatter `applies_to` 字段系统性滞后**：

- Trino 450+ 实际应 480+（滞后 ≥ 9 个月）
- ClickHouse 25.x 实际应 26.3+（滞后 ≥ 3 个月）
- Spark 3.5 实际应 3.5.8 LTS + 4.1（滞后 ≥ 4 个月）
- 其他 Flink / StarRocks / DuckDB / Nessie / Unity Catalog OSS 同样滞后

自动脚本 `scripts/version_scan.py` 首次运行发现 **47 处 stale 引用**。

根源：没有机制让作者知道"什么时候该刷新 applies_to"。信息源在外部（产品 release page）· 表达在内部（wiki frontmatter）· 同步永远手工。

## 决策

采用"**静态表 + 季度扫描 + 非阻断 CI**"三件套。

### 单一事实源

`scripts/known_versions.yml` · 是 wiki 对"各产品当前稳定版"的**共识**。

格式：

```yaml
products:
  <ProductName>:
    aliases: [...]            # applies_to 中可能出现的其他写法
    latest: "X.Y.Z"            # 当前稳定版本
    lts: "X.Y.Z"               # (可选) 当前 LTS
    release_date: "YYYY-MM-DD" # 发布日期
    source: https://...        # 验证来源（release page）
    note: "..."                # (可选) 升级提醒 / 已知问题
```

### 季度扫描 + 刷新节奏

- **每季度第一周** · 手工根据 `source` 链接检查所有产品 · 更新 `known_versions.yml`
- `scripts/version_scan.py` 自动报告 stale `applies_to` 字段
- 对照报告批量 commit 刷新 `applies_to`（单次 commit · 打 tag `B1-refresh-YYYY-Q<N>`）

### CI 集成

`.github/workflows/quality.yml` 有 `version-scan` job · `continue-on-error: true` · **不阻断构建**·只做告警。

理由：阻断 CI 会让"产品发新版→所有 wiki PR 挂"——这不是合理的 quality gate。版本是漂移信号 · 不是 bug。

### 人工验证原则

agent 报告的版本也可能 hallucinate（S22 已观察到 2 例）。引入新事实前必须：

1. WebSearch 验证
2. 或直接访问产品 release page（known_versions.yml 的 `source`）
3. 怀疑时标记"无法验证"而非猜测

## 依据

### 为什么静态表而不是实时 API 拉取

- **确定性**：CI 不依赖外部 HTTP · 不因产品 release page 挂而挂
- **审计**：每次 known_versions.yml 变更都有 commit 记录
- **多级版本**：latest + lts + release_date + note 需求难被单一 REST API 满足
- **产品差异**：GitHub releases / 产品博客 / ASF announce · 每家不一样 · 统一抓取器复杂度高

### 为什么季度而非月度

- 产品大多 monthly-patch / quarterly-minor · quarterly 节奏能抓到稳定版
- 每月会让刷新噪音 > 信号 · 读者反而麻木
- 季度够快：3 个月内的滞后还在大多数企业可接受范围

### 为什么 CI 非阻断

- 阻断 = 版本发布日起所有文档 PR 挂 · 不合理
- 非阻断 = 每次 CI 都可见提醒 · 信号持续 · 行动留给作者

## 后果

**正面**：

- 自动发现 stale · 不再靠偶然对抗评审
- 所有 applies_to 刷新有单一流程 · 作者不需逐产品查官网
- known_versions.yml 本身是团队对产品现状的"快照"·对新人有价值

**负面**：

- 季度 known_versions.yml 维护是固定成本（~30min / 季度）
- 产品与 alias 遗漏会造成漏报（需要对抗评审补位）
- `applies_to` 格式风格多样化时 scanner 的正则可能漏抓 · 需维护

**后续**：

- 2026-Q3 首次季度刷新 · 验证流程
- 若发现 scanner 假阳性 > 20% · 扩大 scanner 启发式（带 ` · ` delimiter 的多产品段）
- 增加产品时同步加入 known_versions.yml

## 相关

- `scripts/known_versions.yml` · 静态事实源
- `scripts/version_scan.py` · 扫描器
- `.github/workflows/quality.yml` · CI 集成
- ADR [0006](0006-chapter-structure-dimensions.md) 章节结构 · applies_to 约定的必要性
- ADR [0008](0008-adversarial-review-sop.md) 对抗评审 · 补位 scanner 漏抓
