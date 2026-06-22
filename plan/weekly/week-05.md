# 第 5 周 · RAG 评测（P2 完结）

**日期**：2026-07-20 ~ 07-26  
**周验收**：hit@5 ≥ 80%；有评测报告 markdown

---

## D29 · 周一 · hit@k / MRR

| 编码 120m | `eval/metrics.py`：hit@5, MRR |
| 测试 45m | 50 题跑分 baseline |

## D30 · 周二 · faithfulness / relevancy

| 学习 30m | RAGAs 或 LLM-as-judge |
| 编码 120m | `eval/judge.py` 抽样 10 题 |

## D31 · 周三 · 分块 A/B

| 编码 120m | 256 vs 512 chunk 对比实验 |
| 文档 30m | 实验表格入报告 |

## D32 · 周四 · rerank A/B + 成本

| 编码 120m | 开/关 rerank；记录延迟与 token |

## D33 · 周五 · eval CLI

| 编码 120m | `cli eval`；输出 `reports/rag-eval.md` |

## D34 · 周六 · badcase 库

| 编码 90m | `eval/badcases.md` ≥10 条失败样例分析 |
| 文档 30m | `notes/projects/P2-总结.md` |

## D35 · 周日 · P2 收尾

| 测试 | 全量 pytest；tag `p2-v0.1.0` |
| 文档 | `week-05-复盘.md` |
