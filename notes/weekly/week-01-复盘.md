# 第 1 周复盘 · 2026-06-28

## 本周交付

| 天 | 主题 | 核心产出 |
|:---|:---|:---|
| D1 | 环境 | `.venv`、Lab-00 pytest 绿 |
| D2 | 最小调用 | `ModelGateway.chat()`、`DeepSeekAdapter`、mock smoke |
| D3 | 超时重试 | `retry.py`、`@with_retry`、ADR-001 |
| D4 | 限流并发 | `TokenBucket`、`async_chat_batch`、Semaphore |
| D5 | 观测 | `CallRecord`、`MetricsCollector`、`pricing.yaml` |
| D6 | bench | `bench.py`、CLI `bench --n 20`、MockAdapter 错误注入 |
| D7 | 周复盘 | 本文档、`P1-进度.md`、README 安装章节 |

**架构一句话**：Gateway 把不可靠 LLM API 包成可观测的同步/异步入口；单次出口是 `GatewayResult(record + content)`，批量汇总走 `MetricsCollector`。

## 本周指标

| 项 | 值 |
|:---|:---|
| ModelGateway 调用（bench mock） | 20 次，18 成功 / 2 失败 |
| bench 成功率（mock） | 90.0% |
| bench 成功率（deepseek，D6 实测） | 95.0%（19/20，空 prompt 被 API 接受） |
| 单元测试 | **37/37 绿**（含 lab-00-setup 6 项） |
| 模块数 | gateway + 4 adapter + retry + ratelimit + metrics + bench + cli |

## 最大问题

1. **错误场景与真实 API 不一致**：bench 用「空 prompt」作失败注入，DeepSeek 仍返回 success；真实失败要靠无效 model。下周工具调用也会遇到「你以为会 ValidationError，模型却胡编参数」——不能假设 provider 行为一致。
2. **测试分层未完全落地**：`integration` marker 已注册，但 D7 前有个 `@pytest.mark.abc` 笔误（已删）；未装 `pytest-cov`，覆盖率只能肉眼扫。
3. **W2 目标结构大半未建**：`schemas.py`、`tools/registry.py`、moonshot 路由仍为空壳或缺失——W1 只完成「可靠调用 + 观测」底座。

## 下周最重要一件事

**Pydantic 结构化输出**：`ChatRequest` / `StructuredAnswer` + `gateway.chat_structured()`，把模型自由文本收成可校验对象。这是 W2 所有工具调用的前置。

## 面试素材

> W1 我把 LLM 当不可靠外部服务：重试扛 429/5xx，令牌桶 + Semaphore 控 QPS/并发，每次调用落 `CallRecord`（token、latency、cost、error_type）。bench 不是压测 QPS，是把 D3–D5 串成观测闭环——失败也进账本，success_rate 才有意义。DeepSeek 空 prompt 仍 success 说明：**失败路径必须按 provider 实测设计，不能靠假设。**

## 周验收

- [x] bench --n 20 报告完整（summary + records + meta JSON）
- [x] 超时/重试/限流有测试（test_retry 4、test_ratelimit 6、test_metrics 等）
- [x] git tag `p1-w01`（已 push）
