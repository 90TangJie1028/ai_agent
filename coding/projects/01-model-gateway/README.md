# P1：Model Gateway

**周期**：第 1–2 周  
**目标**：多模型统一网关 — 超时、重试、限流、成本统计、工具调用  
**默认主模型**：DeepSeek（国内环境）

## 周计划

- [week-01](../../plan/weekly/week-01.md)
- [week-02](../../plan/weekly/week-02.md)

## 目标结构

```text
src/model_gateway/
  gateway.py
  config.py
  adapters/
    deepseek.py       # 主模型
    moonshot.py       # Kimi 备模型
    openai_compat.py  # 通用 OpenAI 兼容实现
    openai_provider.py
  retry.py
  ratelimit.py
  metrics.py
  schemas.py
  tools/registry.py
  tools/calculator.py
  cli.py                 # chat / providers / bench / tools calc
tests/
```

## 安装与运行

```powershell
# 仓库根目录
cd e:\work\ai_agent
.\.venv\Scripts\Activate.ps1

# 可编辑安装 P1（含 dev 依赖）
cd coding\projects\01-model-gateway
pip install -e ".[dev]"
```

复制仓库根目录 `.env.example` → `.env`，至少填入：

```env
DEEPSEEK_API_KEY=你的key
DEFAULT_PROVIDER=deepseek
DEFAULT_MODEL=deepseek-chat

# 双模型（D12）
MOONSHOT_API_KEY=你的key
MOONSHOT_MODEL=kimi-k2.6
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `python -m model_gateway.cli providers` | 列出已配置 provider |
| `python -m model_gateway.cli chat "你好"` | 单次对话（默认 deepseek，无 Key 时可用 mock） |
| `python -m model_gateway.cli tools calc "123 * 456" --provider mock` | 计算器 FC 闭环（离线） |
| `python -m model_gateway.cli tools calc "123 * 456"` | 计算器 FC（默认 provider，需 Key） |
| `python -m model_gateway.cli bench --n 20` | 离线 bench（默认 mock） |
| `python -m model_gateway.cli bench --n 20 --provider deepseek` | 真实 API bench |
| `pytest` | 单元测试（不联网） |
| `pytest -m integration` | 集成测试（需 Key） |

bench 报告默认写入 `reports/week01-bench.json`，终端同步打印汇总表。

## 验收命令（W1 末）

```powershell
cd coding/projects/01-model-gateway
pip install -e ".[dev]"
python -m model_gateway.cli providers
python -m model_gateway.cli chat "你好"
python -m model_gateway.cli bench --n 20
```

## 验收命令（W2 末）

```powershell
python -m model_gateway.cli chat --provider moonshot "你好"
python -m model_gateway.cli tools calc "1+2*3"
pytest -m integration   # 有 Key 时手动跑真实调用
```

## 面试 Elevator Pitch

> 我把大模型封装成不可靠外部服务：默认 DeepSeek，可切换 Kimi/通义/OpenAI；统一网关支持重试、限流，每次调用记录 token 与费用，工具调用带 Pydantic 参数校验。
