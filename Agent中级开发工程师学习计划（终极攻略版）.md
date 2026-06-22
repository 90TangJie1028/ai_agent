# Agent中级开发工程师学习计划（终极攻略版）

**版本日期**：2026-06-22（已结合招聘市场调研优化，详见 [Agent岗位招聘需求调研与技能对标分析.md](./Agent岗位招聘需求调研与技能对标分析.md)）  
**适配对象**：10年以上开发经验，想在4-5个月内转向 Agent/RAG/LLM 应用工程，并达到“能独立设计、实现、评测、部署一个中等复杂 Agent 系统”的水平。  
**每日投入**：4小时。  
**总周期**：18周。  
**最终目标**：不是“学会几个框架”，而是成为能把大模型能力做成可靠软件系统的人。

---

## 1. 总判断

你最好的路线不是按初学者方式补一堆 AI 概念，而是利用已有多年工程经验，直接切到 Agent 工程最有壁垒的部分：

1. **模型能力工程化**：把不稳定的模型输出变成可校验、可回滚、可观测的系统能力。
2. **RAG 可评测化**：不是“能问答”，而是能证明检索、引用、回答质量。
3. **工具调用安全化**：Agent 的价值来自能行动，风险也来自能行动。
4. **工作流状态化**：复杂任务必须有状态、暂停、恢复、审批、失败处理。
5. **作品集产品化**：面试时要展示一个完整系统，而不是一堆 notebook。

一句话路线：

> 用一个旗舰项目贯穿18周，边学边构建：模型网关 + RAG + 工具调用 + Agent 编排 + 评测 + 部署 + 面试表达。

---

## 2. 18周后的你应该长什么样

18周结束后，你应该能做到：

| 能力 | 合格标准 |
|---|---|
| LLM API 工程化 | 能封装多模型调用、结构化输出、重试、超时、限流、成本统计 |
| RAG 系统 | 能处理文档摄取、分块、索引、混合检索、重排、引用、拒答 |
| Agent 编排 | 能实现工具调用循环、状态管理、任务中断恢复、人工审批 |
| 评测体系 | 有固定测试集，能评估检索命中、回答正确性、幻觉、成本、延迟 |
| 安全控制 | 能防 prompt injection、工具越权、敏感信息泄漏、危险动作误执行 |
| 服务化部署 | 能用 FastAPI + Docker Compose 暴露服务并跑端到端测试 |
| 面试表达 | 能10分钟讲清系统架构、难点、指标、取舍和改进方向 |

目标岗位定位：

> Agent 应用工程师 / LLM 应用工程师 / RAG 工程师 / AI 后端工程师 / 智能体开发工程师。

不要把自己包装成“算法研究员”。你的强项应该是工程交付、系统设计和复杂问题落地。

**招聘市场关键词（2026 Q2）**：JD 高频且你应能写进简历的 —— LangChain、LangGraph、MCP、RAG、Function Calling、Skills、评测体系、Docker、多模型适配（含 DeepSeek/通义）。

---

## 3. 推荐技术栈

### 主栈

| 层级 | 推荐 | 原因 |
|---|---|---|
| 语言 | Python（含 asyncio） | Agent/RAG 生态最完整，招聘匹配度最高 |
| Web API | FastAPI | 简洁、异步友好、文档自动生成；JD 出现频率极高 |
| 数据校验 | Pydantic + JSON Schema | 模型输出、工具参数、API DTO 全部结构化 |
| LLM 生态 | **LangChain + LangGraph** | LangChain 是 JD 硬性关键词；LangGraph 负责状态编排 |
| 模型 API | OpenAI Responses API / Agents SDK + 国内模型适配 | 新项目用 Responses/Agents SDK；国内投递需 DeepSeek/通义/智谱适配器 |
| 工具协议 | **MCP（Model Context Protocol）** | 2026 从加分项变为硬性筛选条件，必须会写 MCP Server |
| 编排 | LangGraph | 长任务、状态、human-in-the-loop、Checkpointer 恢复 |
| RAG | LlamaIndex + LangChain Retriever | 文档摄取用 LlamaIndex；检索管线可与 LangChain LCEL 组合 |
| 向量库 | Chroma 起步，**pgvector**/Qdrant 进阶 | Chroma 快速开发；pgvector 更贴近国内 JD（Milvus/pgvector） |
| 低代码认知 | Dify / Coze（体验级） | 面试常问“为什么不用 Dify”；需能讲清 code-first vs 低代码取舍 |
| 缓存/队列 | Redis | 会话状态、任务队列、缓存都用得上 |
| 数据库 | PostgreSQL | 业务数据、评测结果、trace 元数据 |
| 观测 | OpenTelemetry + LangSmith/Langfuse 二选一 | 能追踪模型、工具、耗时、成本、失败原因 |
| 评测 | pytest + golden dataset + RAGAs（可选） | Agent 项目没有回归评测就不可靠 |
| 部署 | Docker Compose | 对作品集和中级面试足够；K8s 面试讲概念即可 |
| 提效工具 | Cursor / Copilot | 2026 JD 开始显性要求 AI Coding 工具使用能力 |

### 框架取舍

- **OpenAI Responses API**：适合单次模型调用、结构化输出、工具调用。
- **OpenAI Agents SDK**：适合你用 OpenAI 生态做 code-first agent、handoff、工具、审批、trace。
- **LangGraph**：适合复杂状态机、长任务、恢复、人工审批、多步骤工作流。
- **LlamaIndex**：适合 RAG、文档索引、检索评测。
- **CrewAI**：了解即可。它适合快速组织 crews/flows，但不要把18周主线押在“多 Agent 团队很炫”上。

最优组合建议（已对齐招聘市场）：

> Python + FastAPI + Pydantic + **LangChain + LangGraph** + OpenAI Responses/Agents SDK + **MCP** + LlamaIndex + PostgreSQL/pgvector + Redis + Docker Compose + Langfuse。

**简历技术关键词串**（ATS 友好）：

```text
Python | FastAPI | LangChain | LangGraph | LlamaIndex | RAG | Agent | MCP | 
Function Calling | Pydantic | PostgreSQL | pgvector | Redis | Docker | 
Langfuse | Prompt Engineering | Structured Output | DeepSeek
```

---

## 4. 旗舰项目：AI Research & Execution Agent

你需要一个足够通用、足够高级、足够好讲的项目。最推荐做：

> **AI Research & Execution Agent：面向知识工作和工程任务的研究执行 Agent 平台。**

它不是普通聊天机器人，而是一个能“检索资料、形成计划、调用工具、执行任务、生成报告、接受人工审批、保留评测记录”的 Agent 系统。

### 项目功能

| 模块 | 功能 |
|---|---|
| Knowledge Base | 上传 Markdown/PDF/网页/代码文本，建立可引用知识库 |
| Research Agent | 根据问题检索资料、交叉验证、输出带引用研究报告 |
| Task Planner | 把用户目标拆成步骤、依赖、风险和验收标准 |
| Tool Executor | 调用搜索、读取文件、计算、HTTP API、SQL 查询、代码运行等工具 |
| MCP Server | 将 kb/agent 能力以 MCP 标准协议暴露，支持动态工具发现 |
| Skills Registry | 工具/技能模块化注册、版本化、Schema 文档化（对标字节/联想 JD） |
| Human Approval | 写文件、发请求、执行命令、修改数据前必须人工确认 |
| Evaluation Center | 固定评测集、检索指标、回答指标、工具调用指标、成本延迟 |
| Trace Dashboard | 展示每次任务的模型调用、工具调用、token、耗时、费用、失败原因 |
| API/CLI/Web Demo | 至少提供 API 和 CLI，Web 做轻量演示即可 |

### 为什么这个项目最适合你

- 覆盖 Agent 工程核心能力，不是单点 demo。
- 不绑定某个行业，面试时适配范围广。
- 可以自然展示工程经验：API、状态、权限、测试、部署、观测。
- 可以逐步扩展，不会被业务细节拖死。
- 可以用公开数据构建，不涉及隐私或公司资料。

### 最小可行版本

必须包含这些命令或接口：

```text
kb.ingest      导入文档
kb.search      检索知识库
agent.ask      带引用问答
agent.plan     目标拆解和执行计划
agent.run      执行安全工具链
agent.report   生成 Markdown 报告
eval.run       跑回归评测
trace.show     查看一次任务轨迹
```

---

## 5. 每天4小时怎么用

每天固定节奏：

| 时间 | 做什么 | 产出 |
|---|---|---|
| 30分钟 | 看官方文档/论文/源码 | 5条笔记 + 1个可落地动作 |
| 120分钟 | 编码主任务 | 可运行代码 |
| 45分钟 | 测试、评测、调试 | 测试结果或评测表 |
| 30分钟 | 写文档 | README、ADR、复盘、博客草稿 |
| 15分钟 | 明天计划 | 明天第一个动作 |

每日必须留下一个产物：

- commit
- 测试结果
- 评测报告
- README 更新
- 架构图
- demo 截图
- 博客段落

只看不写，不算完成。

---

## 6. 18周路线图

### 第1-2周：模型工程底座

目标：把模型当成外部不可靠服务来封装。

| 周次 | 任务 | 交付物 | 验收 |
|---|---|---|---|
| 第1周 | Model Gateway | `ModelGateway`、模型适配器、超时、重试、限流、成本统计 | 20次调用可记录模型、token、耗时、费用、错误 |
| 第2周 | Structured Output + Tools | Pydantic schema、工具注册器、参数校验、错误修复；**加 DeepSeek/通义适配器** | 工具参数错误能捕获；至少 2 个国内外模型可切换 |

必须掌握：

- JSON mode 和 Structured Outputs 的区别。
- function calling 和普通结构化响应的区别。
- token 预算、上下文裁剪、失败重试、幂等性。

### 第3-5周：RAG 可评测系统

目标：做一个能证明质量的 RAG，不是简单向量检索。

| 周次 | 任务 | 交付物 | 验收 |
|---|---|---|---|
| 第3周 | 文档摄取 | Markdown/PDF/网页导入、chunk、metadata、索引；**LangChain LCEL 管线** | 每个答案能定位到原始来源 |
| 第4周 | 检索增强 | hybrid search、rerank、引用、拒答 | 50题评测集能跑完整流程 |
| 第5周 | RAG 评测 | hit@k、MRR、faithfulness、answer relevancy、成本延迟 | 改分块/模型/重排后能量化对比 |

硬规则：

- 没引用的回答不算合格。
- 不能回答时要拒答。
- 所有优化都用评测集证明。

### 第6-8周：Agent 核心

目标：从“问答系统”升级到“能行动的系统”。

| 周次 | 任务 | 交付物 | 验收 |
|---|---|---|---|
| 第6周 | 手写 Agent Loop | ReAct loop、tool call、observation、max steps、失败退出 | 能清楚解释每一步状态流转 |
| 第7周 | LangGraph / Agents SDK 编排 | 状态图、**Checkpointer 持久化**、**记忆模块**、流式输出、中断恢复 | 长任务中断后可恢复；能区分工作/短期/长期记忆 |
| 第8周 | MCP + Skills + Safety | **MCP Server 开发**、Skills 注册、工具权限、人工审批、prompt injection 测试 | MCP 工具可被外部 Client 发现；高风险工具不能被模型直接执行 |

重点：

- 单 Agent 先做到可靠，再谈多 Agent。
- Agent 是模型 + 上下文 + 工具 + 状态 + 中间件，不只是 prompt。
- 工具越强，权限越要严格。

### 第9-12周：旗舰项目 MVP

目标：完成 AI Research & Execution Agent 的可演示闭环。

| 周次 | 任务 | 交付物 | 验收 |
|---|---|---|---|
| 第9周 | 项目架构 | PRD、架构图、数据流、权限表、API 草案 | 陌生人能看懂项目目标和模块 |
| 第10周 | Knowledge Base + Research Agent | 文档导入、检索、带引用研究报告 | 输入主题后能生成可信报告 |
| 第11周 | Planner + Executor | 任务拆解、工具执行、审批、trace | 能执行一个多步骤任务并记录轨迹 |
| 第12周 | API/CLI Demo | FastAPI、CLI、Docker Compose、端到端脚本；**可选 Dify 对比实验** | 一条命令启动，一条命令跑 demo；能讲 code-first vs Dify 取舍 |

MVP 演示场景建议：

1. 导入一组技术文档，问一个需要综合多来源的问题。
2. 让 Agent 生成一份调研报告，并标出引用。
3. 让 Agent 拆解一个工程任务，生成步骤和风险。
4. 让 Agent 调用安全工具执行部分步骤。
5. 高风险动作触发人工审批。
6. 展示 trace 和评测结果。

### 第13-15周：生产级补强

目标：让项目看起来像中级工程师交付，而不是玩具。

| 周次 | 任务 | 交付物 | 验收 |
|---|---|---|---|
| 第13周 | 回归评测 | 100条 golden dataset、CI smoke test、失败样例库 | 每次提交都能跑核心回归 |
| 第14周 | 成本、延迟、观测 | trace、日志、成本预算、缓存、超时、降级 | 任意一次失败能定位原因 |
| 第15周 | 安全与部署 | prompt injection 测试、权限策略、Docker Compose、部署文档 | 危险工具调用必须审批或拒绝 |

这一阶段最重要的成果：

- 一份评测报告。
- 一份安全测试报告。
- 一份性能/成本优化记录。
- 一个可复现部署环境。

### 第16-18周：作品集和求职

目标：把项目变成面试官能快速理解的证据。

| 周次 | 任务 | 交付物 | 验收 |
|---|---|---|---|
| 第16周 | 作品集 | README、架构图、演示视频、博客2篇 | 10分钟内能看懂项目价值 |
| 第17周 | 面试准备 | 简历、项目讲稿、30道问答、模拟面试 | 能讲清技术取舍和指标 |
| 第18周 | 投递复盘 | 公司清单、投递记录、面试问题库 | 每次面试后更新材料 |

---

## 7. 项目目录建议

```text
ai-research-execution-agent/
  apps/
    api/                 FastAPI 服务
    cli/                 CLI 入口
    web/                 可选轻量演示页
  packages/
    model_gateway/       模型调用、结构化输出、成本统计
    tools/               工具注册、权限、参数校验
    mcp_server/          MCP 协议暴露、工具发现、鉴权
    skills/              Skills 注册、版本、Schema 文档
    rag/                 文档摄取、索引、检索、引用
    agent_runtime/       状态、编排、审批、中断恢复
    evaluation/          golden dataset、评测指标、报告
    observability/       trace、日志、成本、错误
  datasets/
    raw/
    processed/
    golden/
  docs/
    architecture.md
    eval_report.md
    security_report.md
    api.md
    demo_script.md
  docker-compose.yml
  README.md
```

---

## 8. 验收指标

### RAG 指标

| 指标 | 合格线 |
|---|---|
| hit@5 | >= 80% |
| 引用可追踪率 | >= 95% |
| 拒答正确率 | >= 80% |
| faithfulness | 用 LLM judge + 人工抽检 |
| 回答延迟 | 常规问题 P95 <= 8s |

### Agent 指标

| 指标 | 合格线 |
|---|---|
| 工具选择准确率 | >= 85% |
| 工具参数校验覆盖率 | 100% |
| 高风险动作审批覆盖率 | 100% |
| 任务失败可解释率 | >= 90% |
| trace 完整率 | 100% |

### 工程指标

| 指标 | 合格线 |
|---|---|
| 单元测试 | 核心模块覆盖 |
| 端到端 demo | 一条命令可跑 |
| Docker 启动 | 一条命令可启动核心服务 |
| README | 陌生人可复现 |
| CI | smoke test + eval subset |

---

## 9. 你必须避开的坑

1. **不要做三个项目**：做深一个旗舰项目，比做浅三个 demo 更有价值。
2. **不要迷信多 Agent**：多数场景一个可靠 Agent + 明确工具 + 状态机就够。
3. **不要只写 prompt**：prompt 不是系统，评测、状态、工具、权限才是壁垒。
4. **不要无评测优化**：没有 baseline 和 dataset，优化全是感觉。
5. **不要过度做前端**：中级 Agent 岗位更看重后端、编排、RAG、评测、部署。
6. **不要绑定单框架**：面试讲“为什么选”，而不是“我只会这个”。
7. **不要让 Agent 直接执行危险动作**：写文件、执行命令、发请求、改数据库都要审批。

---

## 10. 面试叙事模板

### 简历项目描述

```text
AI Research & Execution Agent

设计并实现一个面向知识工作和工程任务的 Agent 平台，支持文档知识库、带引用研究问答、任务规划、工具调用、MCP 标准协议接入、Skills 模块化注册、人工审批、执行追踪和回归评测。系统使用 Python/FastAPI/Pydantic 构建多模型网关（OpenAI + DeepSeek）和工具运行时，结合 LangChain/LlamaIndex 实现 RAG 摄取与检索评测，使用 LangGraph 管理多步骤任务状态、Checkpointer 中断恢复和 human-in-the-loop 审批。构建100条 golden dataset 覆盖检索、回答、工具调用和安全拒答场景，并记录 token、成本、延迟和失败原因。
```

### 10分钟项目讲法

1. **背景**：普通聊天机器人不能可靠完成多步骤知识工作。
2. **目标**：做一个能检索、计划、执行、审批、评测的 Agent 平台。
3. **架构**：模型网关、RAG、工具系统、Agent runtime、评测中心、观测系统。
4. **难点**：幻觉、工具误调用、上下文过长、成本、长任务恢复、安全边界。
5. **方案**：结构化输出、引用校验、golden dataset、human approval、trace。
6. **结果**：展示检索指标、工具准确率、成本延迟、失败案例。
7. **取舍**：为什么先单 Agent，为什么不做复杂前端，为什么不用全自动。

---

## 11. 每周复盘模板

```md
## 第N周复盘

### 本周交付
- 

### 本周指标
- RAG：
- Agent：
- 成本：
- 延迟：
- 测试：

### 最大问题
- 

### 下周只做一件最重要的事
- 

### 面试素材沉淀
- 
```

---

## 12. 最小成功版本

如果18周中途时间不够，最低也要完成：

1. 一个可运行的 Agent 项目。
2. 一个带引用的 RAG 系统。
3. 一个工具调用和人工审批闭环。
4. 一套50-100条评测集。
5. 一个 Docker Compose 启动环境。
6. 一个完整 README。
7. 一个10分钟演示视频。
8. 一套项目面试讲稿。

这8项比“我学过10个框架”更值钱。

---

## 13. 官方资料索引

- OpenAI Agents SDK：https://developers.openai.com/api/docs/guides/agents
- OpenAI Responses API migration：https://developers.openai.com/api/docs/guides/migrate-to-responses
- OpenAI Structured Outputs：https://developers.openai.com/api/docs/guides/structured-outputs
- OpenAI Tools：https://developers.openai.com/api/docs/guides/tools
- LangGraph Overview：https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph Workflows and Agents：https://docs.langchain.com/oss/python/langgraph/workflows-agents
- LangGraph Human-in-the-loop：https://docs.langchain.com/oss/python/langchain/human-in-the-loop
- LlamaIndex Agents：https://developers.llamaindex.ai/python/framework/module_guides/deploying/agents/
- LlamaIndex VectorStoreIndex：https://developers.llamaindex.ai/python/framework/module_guides/indexing/vector_store_index/
- CrewAI Documentation：https://docs.crewai.com/
- CrewAI Quickstart / Flows：https://docs.crewai.com/en/quickstart
- MCP 官方文档：https://modelcontextprotocol.io/
- LangChain 文档：https://docs.langchain.com/
- Dify 文档：https://docs.dify.ai/
- RAGAs 评测：https://docs.ragas.io/

---

## 14. 招聘市场对标补丁（2026-06 新增）

> 完整调研数据见 [Agent岗位招聘需求调研与技能对标分析.md](./Agent岗位招聘需求调研与技能对标分析.md)

### 14.1 必须新增的 4 项（原计划的 P0/P1 缺口）

| 项 | 为什么 | 怎么补 | 插入位置 |
|---|---|---|---|
| **MCP** | 2026 JD 从加分变硬性；字节/联想/腾讯均提及 | 为旗舰项目写 MCP Server，暴露 kb.search / agent.run 等工具 | 第 8 周 |
| **LangChain 显性使用** | 大量 JD 要求“2 年 LangChain 经验” | RAG 管线用 LCEL；简历和 README 写清 LangChain 组件 | 第 3 周起 |
| **国内模型适配** | 国内公司普遍要求 GPT + 国产模型 | ModelGateway 加 DeepSeek、通义或智谱 | 第 1–2 周 |
| **记忆系统** | JD 高频：会话管理、上下文、长期记忆 | LangGraph Checkpointer + 向量长期记忆 | 第 7 周 |

### 14.2 建议了解的 3 项（P2，不拖主线）

1. **Dify / Coze**：花 2 天搭一个同款 RAG Bot，写 ADR 对比“何时 code-first、何时低代码”。  
2. **GraphRAG**：读概念 + 了解多跳推理场景，面试能答“向量 RAG vs 图谱 RAG”。  
3. **K8s 概念**：面试能讲 Deployment/Service/Ingress，18 周不强制实操。

### 14.3 面试加分的“踩坑故事”清单

准备以下真实案例（来自你旗舰项目的 badcase 库）：

- Agent 工具死循环 → 你如何加 max steps + 循环检测 + 熔断  
- RAG 检索不准 → 你如何调分块/混合检索/rerank 并用量化指标证明  
- MCP 工具描述被注入 → 你如何审计工具 metadata + 权限最小化  
- 成本失控 → 你如何加模型路由、缓存、Token 预算  
- 长任务中断 → 你如何用 Checkpointer 恢复状态  

### 14.4 投递策略速查

| 优先投 | 谨慎投 |
|---|---|
| Agent 应用工程师、智能体开发、LLM 应用工程师 | 大模型算法工程师（训练/微调/paper） |
| RAG 工程师、AI 后端工程师 | 要求 2 年+ 商业 LangChain + 985 算法背景 |
| Agent 平台工程师（若有 MCP + 评测 + 工具治理） | 纯 AIGC 生图/生视频算法岗 |

---

## 15. 最终攻略

你最该追求的不是“18周学完 Agent”，而是：

> 18周做出一个能被真实工程团队理解、运行、评测、复盘的 Agent 系统。

最强路径是：

1. 第1个月：模型网关 + 多模型适配 + RAG + 评测。
2. 第2个月：Agent loop + MCP/Skills + 状态/记忆 + 审批。
3. 第3个月：旗舰项目 MVP。
4. 第4个月：评测、观测、安全、部署。
5. 最后2周：作品集、简历、面试表达。

最终判断标准很简单：

> 面试官问“你怎么保证 Agent 可靠？”你能拿出代码、trace、评测集、失败样例、安全策略和部署环境，而不是只讲 prompt 技巧。

