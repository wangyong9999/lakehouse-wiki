---
title: 0001 选择 MkDocs Material 作为 Wiki 框架
type: adr
status: accepted
date: 2026-04-17
deciders: [wangyong9999]
---

# 0001. 选择 MkDocs Material 作为 Wiki 框架

## 背景

团队需要一个系统化、可协作维护、新人友好的知识库，覆盖"多模一体化湖仓 + AI/BI 负载"全部知识面。候选方案：

1. GitHub 原生 Wiki（`.wiki.git`）
2. Docs-as-Code（MkDocs Material / Docusaurus / Starlight / VitePress / mdBook）
3. 自托管 Wiki 应用（Outline / Wiki.js / BookStack）
4. 自研 Web 应用

## 决策

采用 **MkDocs Material + GitHub 公开仓库 + GitHub Pages** 组合。

- 框架：MkDocs Material（>= 9.5）
- 源：公开仓库作为单一事实源
- 部署：GitHub Pages（Actions artifact 路径），公开免费
- 内容：Markdown + YAML frontmatter

## 依据

- **贡献者全是工程师**：Markdown + PR 工作流的门槛等于零；富文本 Wiki 反而增加摩擦
- **技术准确性敏感**：PR review + CODEOWNERS 分域自动指派比 Wiki 的"直接 Edit"可靠得多
- **CI 质量门禁**：markdownlint、`mkdocs build --strict`、lychee 都能卡在 PR 前；Wiki 无法触发 Actions
- **生态一致性**：团队日常接触的 OSS（Iceberg、Paimon、LanceDB、Milvus、Nessie）大多采用 docs-as-code，迁移心智成本最低
- **AI 二次消费**：Markdown + frontmatter 天然适合被内部 RAG bot 消费，未来无缝集成
- **可迁移性**：纯 Markdown + 配置文件，将来迁到任何其他静态站框架成本都很低

### 为什么不是 Docusaurus

Docusaurus 偏"产品站 + 版本化发布 + 博客"，对于一个偏"概念百科 + 团队知识库"的诉求来说功能冗余、写作体验偏重。MkDocs Material 的 Markdown + 配置体验更轻、搜索更即时、国际化更简单。

### 为什么不是 GitHub 原生 Wiki

- 不支持 PR，无法走 review
- 不能触发 Actions，无法做质量门禁
- 模板能力弱，无法强制"概念页必须有统一结构"
- 主题与扩展能力几乎为零

### 为什么不是自托管 Wiki（Outline/Wiki.js）

- 需要额外运维（数据库、备份、升级）
- 内容绑定到应用，未来迁移困难
- 不天然支持 Git-style review

### 为什么不是自研

- 知识库不是团队业务，投入产出比最差

## 后果

**正面**：

- 新人 onboarding 友好（学习路径 + 即时搜索 + 清爽阅读）
- 贡献门槛低，审查机制完善
- 运维成本极低（GitHub Pages 免费且免维护）

**负面**：

- 国内访问 GitHub Pages 偶有速度问题 → 后续叠加 Cloudflare Pages 镜像（另行 ADR）
- Markdown 对非工程师贡献者仍有门槛（但本 Wiki 贡献者主体是工程师，影响小）
- 富交互（如可编辑架构图）需要额外插件支持

**后续**：

- 搭建骨架与 CI（本 ADR 同期执行）
- 建立 6 类页面模板
- Phase 3 冷启动种子内容
- 若半年内出现国内访问瓶颈，新开 ADR 引入 Cloudflare Pages 镜像

## 相关

- 未来相关：ADR-0002（Cloudflare Pages 镜像）、ADR-0003（Algolia DocSearch 接入）
