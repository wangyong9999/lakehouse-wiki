# Lakehouse + Multimodal Wiki

多模一体化湖仓知识库 · 支撑 AI + BI 负载 · 面向工程师的概念查找与系统入门。

## 在线访问

<https://wangyong9999.github.io/lakehouse-wiki/>

## 本地预览

```bash
pip install -r requirements.txt
mkdocs serve
```

然后打开 <http://127.0.0.1:8000/>

## 贡献

详见 [贡献指南](docs/contributing.md)。简而言之：

1. 开 Issue（用对应模板）或直接 fork
2. 按 `docs/_templates/` 下的对应模板新建页面
3. 开 PR，CI 绿 + review 合格后自动发布

## 内容组织

| 目录 | 内容 |
| --- | --- |
| `foundations/` | 存储、文件格式、计算、分布式等基础 |
| `lakehouse/` | 湖表、Snapshot、Manifest、Schema Evolution 等 |
| `catalog/` | Hive / REST / Nessie / Unity / Polaris |
| `query-engines/` | Trino、Spark、Flink、DuckDB、StarRocks |
| `retrieval/` | 向量数据库、ANN 索引、Hybrid Search |
| `ai-workloads/` | RAG、Feature Store、Embedding 流水线 |
| `bi-workloads/` | OLAP 建模、物化视图、查询加速 |
| `unified/` | 湖 + 向量一体化、多模数据建模 |
| `ops/` | 可观测性、成本优化、治理 |
| `frontier/` | 论文笔记、趋势 |
| `compare/` | 横向对比（对象 A vs 对象 B） |
| `scenarios/` | 端到端场景（BI on Lake、RAG on Lake …） |
| `learning-paths/` | 新人上手路径 |
| `adr/` | 团队技术决策记录 |

## License

内容采用 [CC BY 4.0](LICENSE)。
