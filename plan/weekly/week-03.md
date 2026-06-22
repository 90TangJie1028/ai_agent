# 第 3 周 · RAG 文档摄取（P2 启动）

**日期**：2026-07-06 ~ 07-12  
**项目目录**：`coding/projects/02-mini-rag`  
**周验收**：`ingest` 后每个 chunk 可追溯到源文件

---

## D15 · 周一 07-06 · P2 骨架 + Loader

| 学习 30m | LlamaIndex Document Loader；LangChain Document 概念 |
| 编码 120m | 初始化 P2；`loaders/markdown.py`、`loaders/pdf.py` |
| 测试 45m | 加载 `data/sample.md` 得 Document 列表 |
| 文档 30m | P2 README；准备 3 篇技术 MD 样例数据 |

## D16 · 周二 07-07 · 分块策略实验

| 学习 30m | chunk size / overlap 对检索影响 |
| 编码 120m | `chunking.py`：固定窗口 + 递归字符切分 |
| 测试 45m | 同文档 256/512/1024 三种 chunk 数量对比 |
| 文档 30m | `notes/concepts/05-文档分块.md` |

## D17 · 周三 07-08 · Embedding + Chroma

| 学习 30m | embedding 模型选型；Chroma 持久化 |
| 编码 120m | `index.py`：embed + upsert Chroma collection |
| 测试 45m | ingest 后 collection.count() > 0 |
| 文档 30m | metadata 设计：source, page, chunk_id |

## D18 · 周四 07-09 · LangChain LCEL 管线

| 学习 30m | LCEL `|` 管道；Runnable 接口 |
| 编码 120m | `pipeline/ingest_chain.py` 串联 load→split→embed→store |
| 测试 45m | 链式 ingest 与手写结果一致 |
| 文档 30m | `notes/frameworks/langchain-lcel.md` |

## D19 · 周五 07-10 · 来源溯源

| 学习 30m | parent document / chunk 映射 |
| 编码 120m | `traceability.py`：chunk_id → 文件路径+行号 |
| 测试 45m | 给定 chunk 能打印原文片段 |
| 文档 30m | 溯源 API 文档 |

## D20 · 周六 07-11 · CLI ingest

| 学习 30m | typer/click CLI 设计 |
| 编码 120m | `cli.py ingest <path>`；进度日志 |
| 测试 45m | CLI ingest `data/docs/` 全流程 |
| 文档 30m | 更新 P2 README 运行说明 |

## D21 · 周日 07-12 · 周复盘

| 文档 90m | `week-03-复盘.md`；`notes/projects/P2-进度.md` |
| 编码 60m | 修 ingest bug |
| 计划 | 周一：向量检索 baseline |

**周验收**：[ ] ingest CLI 可用 [ ] 溯源可查
