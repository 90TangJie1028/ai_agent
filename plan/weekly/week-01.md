# 第 1 周 · Model Gateway（P1）

**日期**：2026-06-22（一）~ 06-28（日）  
**项目目录**：`coding/projects/01-model-gateway`  
**周验收**：`python -m model_gateway.cli bench --n 20` 输出完整统计报告

---

## D1 · 周一 06-22 · Lab-00 环境与 monorepo 骨架

| 时段 | 分钟 | 任务 | 产出位置 |
|:---|:---:|:---|:---|
| 学习 | 30 | 阅读 [OpenAI API Quickstart](https://platform.openai.com/docs/quickstart)；记 5 条笔记 | `notes/concepts/00-开发环境.md` |
| 编码 | 120 | 创建 `coding/` 目录树；`labs/00-setup`；根目录 `requirements.txt`；虚拟环境 | `coding/labs/00-setup/` |
| 测试 | 45 | 写 `test_env.py`：import openai、load_dotenv 通过 | `coding/labs/00-setup/tests/` |
| 文档 | 30 | 更新根 `README.md` 目录说明；P1 项目 README 草稿 | `coding/projects/01-model-gateway/README.md` |
| 计划 | 15 | 明日：创建 `ModelGateway` 空类 | 打卡表 D2 |

**编码清单**：
- [ ] `coding/projects/01-model-gateway/src/model_gateway/__init__.py`
- [ ] `coding/shared/requirements-base.txt`（openai, pydantic, python-dotenv, httpx）
- [ ] `.env` 从 `.env.example` 复制

**今日验收**：`pytest coding/labs/00-setup` 全绿；git commit

---

## D2 · 周二 06-23 · Lab-01 + Gateway 最小调用

| 时段 | 分钟 | 任务 | 产出位置 |
|:---|:---:|:---|:---|
| 学习 | 30 | Responses API vs Chat Completions 区别；记笔记 | `notes/concepts/01-LLM-API基础.md` |
| 编码 | 90 | `labs/01-hello-llm/main.py` 单次调用 | `coding/labs/01-hello-llm/` |
| 编码 | 30 | `ModelGateway.chat()` + `OpenAIAdapter` 初版 | `src/model_gateway/gateway.py` |
| 测试 | 45 | 集成测试：真实 API 调用 1 次（mock 可选） | `tests/test_gateway_smoke.py` |
| 文档 | 30 | Lab-01 README；笔记补 token 字段说明 | |
| 计划 | 15 | 明日：加重试装饰器 | |

**今日验收**：`python coding/labs/01-hello-llm/main.py` 有输出；`ModelGateway` 能 chat

---

## D3 · 周三 06-24 · 超时与重试

| 时段 | 分钟 | 任务 | 产出位置 |
|:---|:---:|:---|:---|
| 学习 | 30 | 指数退避、幂等性、可重试 HTTP 状态码（429/5xx） | `notes/concepts/02-重试与超时.md` |
| 编码 | 120 | `retry.py`：`@with_retry`；`gateway` 集成 timeout | `src/model_gateway/retry.py` |
| 测试 | 45 | 单元测试：mock 429 重试 3 次；超时抛 `TimeoutError` | `tests/test_retry.py` |
| 文档 | 30 | ADR：`001-retry-policy.md` | `notes/adr/001-retry-policy.md` |
| 计划 | 15 | 明日：令牌桶限流 | |

**今日验收**：重试测试全绿

---

## D4 · 周四 06-25 · 限流与并发

| 时段 | 分钟 | 任务 | 产出位置 |
|:---|:---:|:---|:---|
| 学习 | 30 | asyncio、`Semaphore`、令牌桶算法 | `notes/concepts/03-限流.md` |
| 编码 | 120 | `ratelimit.py`；`async_chat` + 并发 10 路 | `src/model_gateway/ratelimit.py` |
| 测试 | 45 | 压测脚本：10 并发不超 QPS 上限 | `tests/test_ratelimit.py` |
| 文档 | 30 | metrics 字段设计草案 | `src/model_gateway/metrics.py` 注释 |
| 计划 | 15 | 明日：实现 metrics 统计 | |

**今日验收**：10 并发无异常；超限请求被排队或拒绝

---

## D5 · 周五 06-26 · Token / 费用 / 耗时

| 时段 | 分钟 | 任务 | 产出位置 |
|:---|:---:|:---|:---|
| 学习 | 30 | 各模型 pricing 表；usage 响应字段 | 笔记补充 |
| 编码 | 120 | `metrics.py`：`CallRecord`；`GatewayResult` 含 cost/latency | `src/model_gateway/metrics.py` |
| 测试 | 45 | 单次调用断言 `record.tokens > 0` | `tests/test_metrics.py` |
| 文档 | 30 | pricing 配置 `config/pricing.yaml` | |
| 计划 | 15 | 明日：bench 脚本 | |

**今日验收**：每次 chat 返回结构化 `CallRecord`

---

## D6 · 周六 06-27 · 集成 bench + 错误场景

| 时段 | 分钟 | 任务 | 产出位置 |
|:---|:---:|:---|:---|
| 学习 | 30 | 结构化日志（JSON log）最佳实践 | |
| 编码 | 90 | `cli.py bench --n 20`；汇总 JSON/表格报告 | `src/model_gateway/cli.py` |
| 编码 | 30 | 错误场景：无效 key、空 prompt 处理 | |
| 测试 | 45 | 跑满 20 次；故意 2 次错误入报告 | `reports/week01-bench.json` |
| 文档 | 30 | P1 README 安装与运行章节 | |
| 计划 | 15 | 明日：周复盘 | |

**今日验收**：`bench --n 20` 报告含成功/失败/总 token/总费用

---

## D7 · 周日 06-28 · 周复盘

| 时段 | 分钟 | 任务 | 产出位置 |
|:---|:---:|:---|:---|
| 学习 | 30 | 浏览第 2 周计划；Pydantic v2 文档导读 | |
| 编码 | 60 | 修 bench 遗留 bug；代码整理 | |
| 测试 | 45 | 全量 pytest；覆盖率扫一眼 | |
| 文档 | 90 | `notes/weekly/week-01-复盘.md`；`notes/projects/P1-进度.md` | |
| 计划 | 15 | 周一：Pydantic 输出模型 | |

**周验收打勾**：
- [ ] 20 次调用统计完整
- [ ] 超时/重试/限流有测试
- [ ] git tag `p1-w01`
