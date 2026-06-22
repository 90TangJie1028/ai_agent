# Coding 目录

所有可运行代码放这里：**labs**（小时级实验）→ **projects**（由小到大的练习项目）。

## 项目进度

| 代号 | 目录 | 周期 | 状态 |
|:---|:---|:---|:---:|
| Lab-00 | [labs/00-setup](./labs/00-setup) | D1 | ⬜ |
| Lab-01 | [labs/01-hello-llm](./labs/01-hello-llm) | D2 | ⬜ |
| P1 | [projects/01-model-gateway](./projects/01-model-gateway) | W1–2 | ⬜ |
| P2 | [projects/02-mini-rag](./projects/02-mini-rag) | W3–5 | ⬜ |
| P3 | [projects/03-react-agent](./projects/03-react-agent) | W6 | ⬜ |
| P4 | [projects/04-langgraph-agent](./projects/04-langgraph-agent) | W7 | ⬜ |
| P5 | [projects/05-mcp-server](./projects/05-mcp-server) | W8 | ⬜ |
| P6 | [projects/06-research-agent](./projects/06-research-agent) | W9–15 | ⬜ |

规划详情 → [plan/练习项目路线图.md](../plan/练习项目路线图.md)

## 快速开始

```powershell
cd e:\work\ai_agent
python -m venv .venv
.venv\Scripts\activate
pip install -r coding/shared/requirements-base.txt
```

## 目录约定

```text
coding/
  shared/              # 共用依赖与工具
  labs/                # 小实验，不追求工程完整
  projects/
    01-model-gateway/  # 每个项目独立 src/ tests/ README
    ...
```

每个项目内：

```text
projects/0X-name/
  README.md
  pyproject.toml 或 requirements.txt
  src/
  tests/
  data/           # 样例数据（小文件可入库）
```
