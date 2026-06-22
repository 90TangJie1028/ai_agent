# P1：Model Gateway

**周期**：第 1–2 周  
**目标**：多模型统一网关 — 超时、重试、限流、成本统计、工具调用

## 周计划

- [week-01](../../plan/weekly/week-01.md)
- [week-02](../../plan/weekly/week-02.md)

## 目标结构

```text
src/model_gateway/
  gateway.py
  adapters/       # openai, deepseek, dashscope
  retry.py
  ratelimit.py
  metrics.py
  schemas.py
  tools/registry.py
  cli.py
tests/
```

## 验收命令（W1 末）

```powershell
cd coding/projects/01-model-gateway
pip install -e ".[dev]"
python -m model_gateway.cli bench --n 20
```

## 验收命令（W2 末）

```powershell
python -m model_gateway.cli chat --model deepseek "你好"
python -m model_gateway.cli tools calc "1+2*3"
```

## 面试 Elevator Pitch

> 我把大模型封装成不可靠外部服务：统一网关支持多模型路由、指数退避重试、令牌桶限流，每次调用记录 token 与费用，工具调用带 Pydantic 参数校验。
