# 第 4 周 · 检索增强（P2）

**日期**：2026-07-13 ~ 07-19  
**周验收**：50 题评测集跑通；带引用回答 + 拒答

---

## D22 · 周一 · 向量检索 baseline

| 编码 120m | `retriever.py`：top-k 向量检索；`cli search "query"` |
| 测试 45m | 5 个手工 query 打印 top-3 chunk |

## D23 · 周二 · BM25 混合检索

| 学习 30m | hybrid search 原理；RRF 融合 |
| 编码 120m | `retriever.py` 加 BM25（rank_bm25 或 elasticsearch 轻量） |
| 测试 45m | 纯向量 vs 混合对比 10 query |

## D24 · 周三 · Reranker

| 编码 120m | `rerank.py`：cross-encoder 或 API rerank |
| 测试 45m | rerank 前后 top-1 变化记录 |

## D25 · 周四 · 引用回答格式

| 编码 120m | `qa.py`：prompt 强制 `[1][2]` 引用；后处理校验引用存在 |
| 测试 45m | 回答必含 source 字段 |

## D26 · 周五 · 拒答逻辑

| 编码 120m | 低相似度阈值拒答；「不知道」模板 |
| 测试 45m | 无关问题触发拒答 |

## D27 · 周六 · 50 题评测集 v1

| 编码 120m | `eval/dataset.jsonl` 50 条；`eval/runner.py` 骨架 |
| 文档 30m | 标注规范说明 |

## D28 · 周日 · 周复盘

| 文档 | `week-04-复盘.md` |
| 验收 | `cli ask` E2E 带引用
