# AI Agent 学习仓库

18 周 Agent 中级工程师学习 — 计划、代码、笔记分离管理。

## 目录结构

```text
ai_agent/
├── plan/                 # 学习计划（每日/每周/每月）
│   ├── README.md         # 计划总入口
│   ├── 18周总路线图.md
│   ├── 练习项目路线图.md
│   ├── daily/            # 打卡索引 + 日记模板
│   ├── weekly/           # week-01 ~ week-18 每日 4h 拆分
│   └── monthly/          # 第1月 ~ 第5月
├── coding/               # 全部代码
│   ├── labs/             # Lab-00, Lab-01 小实验
│   └── projects/         # P1~P6 由小到大
├── notes/                # 笔记、复盘、面试素材
├── Agent中级开发工程师学习计划（终极攻略版）.md
└── Agent岗位招聘需求调研与技能对标分析.md
```

## 今天怎么学（Day 2）

1. 打开 **[plan/weekly/week-01.md](plan/weekly/week-01.md)** — 按 D2 四时段执行  
2. 代码：**`coding/labs/01-hello-llm`** + **`coding/projects/01-model-gateway`**  
3. 笔记：**[notes/concepts/01-LLM-API基础.md](notes/concepts/01-LLM-API基础.md)**  
4. 学完在 **[plan/daily/打卡索引.md](plan/daily/打卡索引.md)** D2 打勾  

## 练习项目路线

```text
Lab-00/01 → P1 Gateway → P2 RAG → P3 ReAct → P4 LangGraph → P5 MCP → P6 旗舰
```

详情 → [plan/练习项目路线图.md](plan/练习项目路线图.md)

## 快速开始

```powershell
cd e:\work\ai_agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env    # 填入 DEEPSEEK_API_KEY
pytest coding/labs/00-setup/tests
```

**默认模型**：DeepSeek（国内可直接调用）。OpenAI 暂不依赖，原理相通，后续有时间再接入。

## 当前进度

**第 1 周 · D2** — Hello LLM + Gateway（2026-06-23）
