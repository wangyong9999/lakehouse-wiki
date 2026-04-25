# Multimodal Lakehouse Handbook

多模一体化湖仓 · 面向 AI 与 BI 负载的工程手册。

面向数据湖上**多模检索 + 多模分析**的团队知识库。当前 143 页，覆盖从存储底座到检索 + AI + BI 的完整工程主题。

## 在线访问

<https://wangyong9999.github.io/lakehouse-wiki/>

## 本地预览

```bash
pip install -r requirements.txt
mkdocs serve
```

然后打开 <http://127.0.0.1:8000/>

## 反馈与贡献

- 发现错误 / 过时 / 坏链接 → 走 [Issue 模板](https://github.com/wangyong9999/lakehouse-wiki/issues/new/choose) 或直接 PR
- 内容更新以事件驱动为主（新论文 / 新工具 / 厂商变更 / 生产事故 / 季度自检）
- 写作规范见 [贡献指南](docs/contributing.md)

## 内容组织

| 目录 | 内容 |
| --- | --- |
| `foundations/` | 存储、文件格式、计算、分布式、一致性、谓词下推 |
| `lakehouse/` | 湖表、Snapshot、Manifest、Schema & Partition Evolution、Compaction、Delete Files 等 |
| `catalog/` | Hive / REST / Nessie / Unity / Polaris / Gravitino |
| `query-engines/` | Trino / Spark / Flink / DuckDB / StarRocks / ClickHouse / Doris |
| `pipelines/` | 入湖、多模预处理（图/视/音/文档）、编排 |
| `retrieval/` | 向量数据库、ANN、Hybrid、Rerank、Embedding、多模对齐、评估 |
| `ai-workloads/` | RAG、Agent、Prompt、Feature Store、微调数据准备 |
| `ml-infra/` | Model Registry、Serving、Training、GPU 调度 |
| `bi-workloads/` | OLAP 建模、物化视图、查询加速 |
| `unified/` | 湖 + 向量融合、多模建模、统一 Catalog、跨模态查询、案例 |
| `ops/` | 可观测性、性能、成本、安全、治理、迁移、排障 |
| `frontier/` | 论文笔记、Benchmark |
| `compare/` | 横向对比（7 套选型决策） |
| `scenarios/` | 端到端场景（BI on Lake、RAG、多模检索、流式入湖 等） |
| `learning-paths/` | 4 条时间脚手架：一周 / 一月 AI / 一月 BI / 一季度 |
| `roles/` | 按角色阅读清单（数据 / ML / 平台 / BI） |
| `cheatsheets/` | 一页式参数速查 |
| `adr/` | 团队技术决策记录 |

## License

内容采用 [CC BY 4.0](LICENSE)。
