# Agent中级开发工程师学习计划（高效终局版）

**版本日期**：2026-07-17  
**调研依据**：[Agent岗位招聘需求调研与技能对标分析.md](./Agent岗位招聘需求调研与技能对标分析.md)（同日更新）  
**适配对象**：10 年+ 工程经验，4–5 个月转向 Agent/RAG/LLM **应用工程**，目标是独立设计、实现、评测、部署一个中等复杂 Agent 系统。  
**每日投入**：4 小时（建议 5×4h/周，周末可加 1 次复盘，不另开新主题）。  
**总周期**：18 周（约 360 小时）。  
**效率原则**：时间最贵 —— 只学招聘会筛、面试会挖、作品集能证明的东西；其余一律砍掉或降级为「面试能答一句」。

---

## 0. 一句话总纲

> **用一个旗舰项目贯穿全程：模型网关 → 可评测 RAG → 可靠 Agent（状态/审批/MCP）→ 观测与回归评测 → 可演示作品集。**  
> 市场买的是「能把不稳定模型做成可靠软件」的人，不是「会十个框架名词」的人。

你已有工程底座（API、状态、权限、测试、部署）。转型的正确姿势是 **能力叠加**，不是从零当算法生。

仓库内项目骨架已对齐本计划：`coding/projects/01-model-gateway` … `06-research-agent`。按周推进，不要另起炉灶。

---



## 1. 2026-07 市场研判（决定学什么）



### 1.1 岗位真相


| 判断       | 依据                                              |
| -------- | ----------------------------------------------- |
| 主投岗位     | Agent 应用 / 智能体开发 / LLM 应用 / RAG / AI 后端         |
| 不投岗位     | 大模型训练/微调算法、纯 AIGC 生图视频、要求顶会一作的 Research         |
| 市场缺什么人   | 能上线、能限流熔断、能控成本、能评测回归、能权限审计的人                    |
| 市场不缺什么人  | 只会调 API、只会写 Prompt、只会 notebook demo 的人          |
| Prompt 岗 | 独立「提示词工程师」明显萎缩，被 Agent + Context Engineering 吸收 |




### 1.2 技能优先级矩阵（按投入产出排序）

评分：招聘出现率 × 面试深挖度 × 作品集可证明度。只按 **P0/P1 排日程**；P2 塞缝；P3 不占主线。


| 优先级    | 技能                                              | 学到什么程度                   | 为何是这个优先级                           |
| ------ | ----------------------------------------------- | ------------------------ | ---------------------------------- |
| **P0** | Python + asyncio + FastAPI + Pydantic           | 能独立交付服务                  | 几乎所有应用岗硬门槛                         |
| **P0** | 多模型网关（超时/重试/限流/成本/结构化输出/工具调用）                   | 自研一层薄封装                  | 面试「工程化」第一印象；国内要 DeepSeek/通义        |
| **P0** | RAG：摄取→分块→混合检索→rerank→引用→拒答→评测集                 | 可量化对比优化                  | 企业岗最高频业务能力                         |
| **P0** | Agent Loop（先手写再上 LangGraph）                     | 能讲清状态机与失败退出              | 面试必手撕/必画图                          |
| **P0** | LangGraph：状态、Checkpointer、HITL、中断恢复             | 主编排框架做深                  | 2026 生产编排事实标准之一                    |
| **P0** | MCP Server：工具发现、Schema、鉴权边界                     | 至少一个可被 Client 调用的 Server | JD 从加分变硬性/半硬性                      |
| **P0** | 评测 + Trace（golden set + Langfuse/LangSmith 二选一） | 回归可跑、失败可定位               | 中高级岗差异化核心；Applied AI = reliability |
| **P0** | 安全：审批、越权、injection、工具输出截断                       | 有测试报告                    | 大厂高频追问                             |
| **P1** | Context Engineering（上下文预算、工具描述、记忆分层）            | 能讲体系，不只「写 prompt」        | 正在替代空泛 Prompt Engineering 叙事       |
| **P1** | LangChain 生态「显性使用」                              | LCEL/组件出现在 README 与简历    | 大量 JD 写 LangChain；不必精通全部模块         |
| **P1** | 记忆：工作/短期/长期（向量）                                 | Checkpointer + 简单长期记忆    | JD 高频                              |
| **P1** | Skills 注册（工具模块化/版本/Schema 文档）                   | 自研 registry 即可           | 字节/联想等 JD 热点；名称可对标                 |
| **P1** | 轻量多 Agent（supervisor + 2 specialist）            | 1 个 demo，能讲「何时不用」        | JD 出现率上升，但深度要求仍次于可靠单 Agent         |
| **P1** | 成本工程：模型路由、缓存、动态工具子集                             | 有数字前后对比                  | 生产岗必问                              |
| **P2** | Dify/Coze                                       | 2 天体验 + 1 篇 ADR          | 面试常问「为何不用低代码」                      |
| **P2** | Agentic RAG（query 改写/多步检索）                      | RAG 周加一小段实验              | 部分 JD 写高级 RAG                      |
| **P2** | GraphRAG / 知识图谱                                 | 概念 + 能对比向量 RAG           | 加分，非主线                             |
| **P2** | Claude Agent SDK / OpenAI Agents SDK            | 各扫半天，对照 LangGraph        | 一等公民 SDK 上升；不换主线                   |
| **P2** | A2A 协议                                          | 概念级                      | 平台岗偶见，应用岗非硬门槛                      |
| **P3** | K8s 实操 / 重前端 / 微调 LoRA / AutoGen 深挖 / CrewAI 主线 | 不学或只了解名词                 | ROI 低或偏离目标岗                        |




### 1.3 明确不学（保护你的 360 小时）

1. **不训练模型、不做 LoRA 主线** —— 算法岗才硬要。
2. **不并行精通 4 个框架** —— 主栈锁定见 §3；CrewAI/AutoGen 只了解。
3. **不做三个无关项目** —— 一个旗舰 + 前期模块并入旗舰。
4. **不重做复杂前端** —— CLI + FastAPI + 轻量 Web 即可。
5. **不追每周新框架** —— 协议（MCP）和工程能力（评测/状态/安全）比 logo 保值。
6. **不为「2 年 LangChain」焦虑重学两年** —— 用系统年限 + 深度项目 + 显性关键词对冲（见 §10）。



### 1.4 简历必须能写进 ATS 的关键词串

```text
Python | FastAPI | Pydantic | LangChain | LangGraph | RAG | Agentic RAG |
Agent | MCP | Function Calling | Context Engineering | Structured Output |
Human-in-the-loop | Checkpointer | pgvector | PostgreSQL | Redis | Docker |
Langfuse | Evaluation | Trajectory Eval | DeepSeek | 通义
```

---



## 2. 18 周后的合格画像


| 能力    | 合格标准（可演示）                             |
| ----- | ------------------------------------- |
| 模型工程  | 多模型切换；结构化输出；工具参数校验；成本/延迟可统计           |
| RAG   | 带引用问答 + 拒答；50–100 题评测；改分块/检索能量化对比     |
| Agent | 手写 loop 能讲清；LangGraph 可中断恢复；高风险动作必须审批 |
| MCP   | 外部 Client 能发现并调用至少 2 个工具              |
| 评测    | golden set + 工具轨迹断言 + CI smoke        |
| 观测    | 任意失败能从 trace 定位到模型/工具/检索哪一步           |
| 表达    | 10 分钟讲清架构、难点、指标、取舍                    |


目标包装：**Agent 应用工程师**，不是算法研究员。

---



## 3. 最高效技术栈（锁定，少即是多）



### 3.1 主栈（只深挖这些）


| 层级    | 选型                                           | 纪律                                                 |
| ----- | -------------------------------------------- | -------------------------------------------------- |
| 语言    | Python + asyncio                             | 主语言；第二语言简历写「可快速适配」即可                               |
| API   | FastAPI + Pydantic                           | DTO / 工具参数 / 模型输出统一 Schema                         |
| 编排    | **LangGraph**                                | 唯一深度编排框架                                           |
| 生态关键词 | **LangChain**（LCEL / Retriever 等组件）          | 为 JD 显性覆盖；不追求学全                                    |
| RAG   | **二选一做深**：LlamaIndex 摄取 **或** LangChain 检索管线 | 禁止两边都「学一半」；推荐：摄取偏 LlamaIndex，编排与 Agent 偏 LangGraph |
| 模型    | OpenAI 兼容 API + **DeepSeek 主** + 通义/智谱任一备    | 国内投递必需                                             |
| 协议    | **MCP**（官方 Python SDK）                       | 必须写 Server，不只读概念                                   |
| 向量库   | Chroma 起步 → **pgvector** 进阶                  | 贴近国内 JD；Milvus 面试了解即可                              |
| 观测    | **Langfuse**（优先，可自托管）或 LangSmith             | 二选一做深                                              |
| 评测    | pytest + 自建 golden +（可选）RAGAs                | 轨迹断言手写，不依赖玄学                                       |
| 部署    | Docker Compose                               | K8s 只准备概念回答                                        |
| 提效    | Cursor                                       | 简历可写 AI Coding 日常交付                                |




### 3.2 框架取舍（面试原话级别）


| 工具                            | 用途             | 你的立场                  |
| ----------------------------- | -------------- | --------------------- |
| LangGraph                     | 长任务、状态、HITL、恢复 | **主**                 |
| LangChain                     | 组件与 JD 关键词     | **辅，显性使用**            |
| LlamaIndex                    | 文档摄取与索引        | **RAG 层用，不负责编排**      |
| OpenAI Responses / Agents SDK | 对照与单厂商快速原型     | 了解，不双主线               |
| Claude Agent SDK              | 海外/一等公民 SDK 叙事 | 半日扫文档                 |
| CrewAI / AutoGen              | 多 Agent 快速组织   | 了解；AutoGen 已偏维护态，勿押主线 |
| Dify / Coze                   | 低代码对照          | 2 天体验                 |


最优组合（写进 README）：

> Python + FastAPI + Pydantic + LangGraph + LangChain（组件）+ MCP + LlamaIndex（摄取）+ PostgreSQL/pgvector + Redis + Docker Compose + Langfuse + DeepSeek

---



## 4. 旗舰项目：AI Research & Execution Agent

> 面向知识工作的研究执行 Agent：检索 → 计划 → 工具执行 → 审批 → 报告 → 评测 → Trace。

这不是聊天机器人，而是面试官能一眼看出的 **系统**。

### 4.1 模块与招聘对标


| 模块                | 功能                     | 对标 JD 词          |
| ----------------- | ---------------------- | ---------------- |
| Knowledge Base    | Markdown/PDF/网页摄取、引用检索 | RAG、向量库          |
| Research Agent    | 带引用研究报告、拒答             | Agentic RAG、可信问答 |
| Task Planner      | 步骤、依赖、风险、验收标准          | Plan-and-Execute |
| Tool Executor     | 搜索/文件/HTTP/SQL 等       | Function Calling |
| MCP Server        | 标准协议暴露工具               | MCP              |
| Skills Registry   | 工具注册、版本、Schema 文档      | Skills           |
| Human Approval    | 写文件/发请求/改数据前确认         | HITL、安全          |
| Evaluation Center | 检索/回答/工具轨迹/安全用例        | Eval、回归          |
| Trace             | token、成本、耗时、失败原因       | 可观测、Langfuse     |
| API/CLI           | 可演示入口                  | 工程交付             |




### 4.2 最小命令集（MVP 验收）

```text
kb.ingest / kb.search
agent.ask / agent.plan / agent.run / agent.report
eval.run / trace.show
```



### 4.3 与仓库项目映射


| 周次    | 仓库项目                 | 说明          |
| ----- | -------------------- | ----------- |
| 1–2   | `01-model-gateway`   | 网关底座        |
| 3–5   | `02-mini-rag`        | 可评测 RAG     |
| 6     | `03-react-agent`     | 手写 loop     |
| 7     | `04-langgraph-agent` | 状态/记忆/恢复    |
| 8     | `05-mcp-server`      | MCP + 安全底线  |
| 9–15  | `06-research-agent`  | 模块合并为旗舰     |
| 16–18 | 作品集与求职               | 文档/视频/简历/投递 |


前期模块 **以库形式并入** 旗舰，避免三个独立 demo。

---



## 5. 每天 4 小时怎么用（含缓冲）


| 时间     | 做什么                   | 产出             |
| ------ | --------------------- | -------------- |
| 25 分钟  | 官方文档/源码（只读与今日任务相关的）   | ≤5 条笔记 + 1 个动作 |
| 110 分钟 | 编码主任务                 | 可运行代码          |
| 40 分钟  | 测试 / 评测 / 调试          | 测试或评测结果        |
| 25 分钟  | 文档（README / ADR / 复盘） | 可给陌生人看的说明      |
| 20 分钟  | **缓冲**（排错、补环境、重跑失败用例） | 不欠技术债过夜        |
| 10 分钟  | 写下明天第一个动作             | 明天开工零摩擦        |


规则：

- 每天至少 1 个可验证产物：commit / 测试结果 / 评测表 / README 更新。  
- **只看不写 = 未完成。**  
- 当天主任务超时时，砍「多学一个库」，不砍测试。

---



## 6. 18 周路线图（高效版）



### 阶段 A · 第 1–2 周：模型工程底座（P1）

**目标**：把模型当不可靠外部服务封装。


| 周次  | 任务                                     | 交付物                                                                         | 验收                            |
| --- | -------------------------------------- | --------------------------------------------------------------------------- | ----------------------------- |
| 1   | Model Gateway                          | 适配器、超时、重试、限流、成本统计                                                           | 20 次调用可记录模型/token/耗时/费用/错误    |
| 2   | Structured Output + Tools + Context 基础 | Pydantic schema、工具注册、参数修复；DeepSeek + 另一国内模型；**Context 预算与工具描述规范** 写进 README | ≥2 模型可切换；坏参数可捕获；工具描述有「最小必要」原则 |


必须能讲清：JSON mode vs Structured Outputs；function calling vs 普通结构化响应；幂等与重试。

### 阶段 B · 第 3–5 周：可评测 RAG（P2）

**目标**：证明质量，不是「能问答」。


| 周次  | 任务     | 交付物                                                            | 验收               |
| --- | ------ | -------------------------------------------------------------- | ---------------- |
| 3   | 摄取与索引  | 文档导入、chunk、metadata；LangChain 组件或 LlamaIndex 摄取（按 §3 选定）       | 答案可定位原文          |
| 4   | 检索增强   | hybrid + rerank + 引用 + 拒答；**可选 1 天 Agentic RAG**（query 改写后再检索） | 50 题跑通全流程        |
| 5   | RAG 评测 | hit@k、MRR、引用率、拒答、成本延迟；留 badcase 库                              | 任意改动能对比 baseline |


硬规则：无引用不合格；不能答要拒答；优化必须有评测数字。

### 阶段 C · 第 6–8 周：Agent 核心（P3–P5）

**目标**：从问答到「能行动且可控」。


| 周次  | 任务            | 交付物                                                      | 验收                     |
| --- | ------------- | -------------------------------------------------------- | ---------------------- |
| 6   | 手写 Agent Loop | ReAct、max steps、重复动作检测、失败退出                              | 能画序列图讲解每步              |
| 7   | LangGraph     | 状态图、Checkpointer、短/长期记忆、流式、中断恢复                          | 长任务可恢复；记忆分层能讲清         |
| 8   | MCP + 安全底线    | MCP Server（kb.search / agent.run 等）；权限；人工审批；injection 用例 | Client 可发现工具；高风险不可直接执行 |


**第 8 周纪律（防爆炸）**：本周 **不做** Skills 文档大全、不做多 Agent。Skills 注册并入第 11 周；多 Agent 放第 12 周轻量版。

### 阶段 D · 第 9–12 周：旗舰 MVP（P6）

**目标**：一条命令可演示的闭环。


| 周次  | 任务                              | 交付物                                                           | 验收                               |
| --- | ------------------------------- | ------------------------------------------------------------- | -------------------------------- |
| 9   | 架构冻结                            | PRD、架构图、权限表、API 草案、数据流                                        | 陌生人 10 分钟看懂目标                    |
| 10  | KB + Research                   | 导入、检索、带引用报告；向量库切 **pgvector**                                 | 综合多来源问题可答                        |
| 11  | Planner + Executor + Skills     | 多步执行、审批、trace；Skills 注册表                                      | 完整轨迹可回放                          |
| 12  | API/CLI + 可选轻量多 Agent + Dify 对照 | FastAPI、CLI、Compose、e2e；supervisor+2 角色 demo（可选）；Dify 2 天 ADR | `docker compose up` + 一条 demo 脚本 |


MVP 演示脚本（固定这 6 步）：

1. 导入文档 → 综合问答带引用
2. 生成调研报告
3. 拆解工程任务
4. 执行安全工具链
5. 触发人工审批
6. 展示 trace + 评测摘要



### 阶段 E · 第 13–15 周：生产级补强


| 周次  | 任务           | 交付物                                      | 验收              |
| --- | ------------ | ---------------------------------------- | --------------- |
| 13  | 回归评测         | 100 条 golden（含 **工具轨迹断言**、安全拒答）；CI smoke | 每次提交可跑核心子集      |
| 14  | 成本 / 延迟 / 观测 | 路由、缓存、Token 预算、降级、Langfuse               | 任意失败可定位；有成本前后对比 |
| 15  | 安全与部署        | injection 报告、权限策略、Compose、部署文档           | 危险动作 100% 审批或拒绝 |




### 阶段 F · 第 16–18 周：作品集与求职（3 周，不是 2 周）


| 周次  | 任务   | 交付物                               | 验收        |
| --- | ---- | --------------------------------- | --------- |
| 16  | 作品集  | README、架构图、5–10 分钟演示视频、技术博客 1–2 篇 | 10 分钟看懂价值 |
| 17  | 面试弹药 | 简历、项目讲稿、30 题问答、模拟面试               | 能量化讲指标与取舍 |
| 18  | 投递复盘 | 公司清单、投递表、面试题库迭代                   | 每次面试后更新材料 |


---



## 7. 项目目录建议（旗舰合并后）

```text
ai-research-execution-agent/
  apps/api|cli|web
  packages/
    model_gateway/
    tools/ + skills/
    mcp_server/
    rag/
    agent_runtime/
    evaluation/
    observability/
  datasets/raw|processed|golden
  docs/architecture|eval_report|security_report|demo_script
  docker-compose.yml
  README.md
```

---



## 8. 验收指标（可答辩，不虚高）

指标都绑定 **你的 golden set**；简历写「在自建 N 题集上相对 baseline 的提升」，避免绝对百分比不可复现。

### RAG（相对自建 baseline）


| 指标           | 目标                        |
| ------------ | ------------------------- |
| hit@5        | 相对朴素向量检索明显提升（记录绝对数 + Δ）   |
| 引用可追踪率       | ≥ 95%                     |
| 拒答正确率        | ≥ 80%（该拒则拒）               |
| faithfulness | LLM-judge + 人工抽检 ≥ 20 条/轮 |
| P95 延迟       | 常规问题有测量值；优化有前后对比          |




### Agent


| 指标        | 目标            |
| --------- | ------------- |
| 工具选择准确率   | ≥ 85%（评测集内）   |
| 工具参数校验    | 100% 走 Schema |
| 高风险审批覆盖   | 100%          |
| 轨迹断言通过率   | 核心场景 ≥ 90%    |
| trace 完整率 | 100%          |




### 工程


| 指标       | 目标                  |
| -------- | ------------------- |
| 单元测试     | 核心模块有测              |
| e2e demo | 一条命令                |
| Compose  | 一条命令起核心服务           |
| CI       | smoke + eval subset |


---



## 9. 必须避开的坑

1. 三个浅 demo < 一个深旗舰。
2. 多 Agent 炫技 < 可靠单 Agent + 说清何时拆。
3. 只调 prompt < 评测、状态、权限、trace。
4. 无 baseline 的「感觉优化」。
5. 重前端轻后端。
6. 绑定单框架不会讲取舍。
7. Agent 直接执行危险动作。
8. **并行学五个框架导致每个都浅** —— 这是 18 周最大时间杀手。

---



## 10. 面试与简历（10 年经验特供）



### 10.1 年限话术（对冲「2 年 LangChain」）

不要写「转岗学员」。写：

> N 年软件工程经验，近 X 个月主导设计并实现生产级 Agent/RAG 系统（多模型网关、可评测检索、LangGraph 状态编排、MCP 工具层、HITL 与回归评测）。擅长将非确定性模型输出约束为可观测、可回滚的服务能力。

项目描述里 **堆 JD 关键词 + 量化指标**，用深度对冲「框架工龄」。

### 10.2 简历项目段落（可直接改数字）

```text
AI Research & Execution Agent

设计并实现面向知识工作的 Agent 平台：文档知识库、带引用研究问答、任务规划、
工具调用、MCP 协议接入、Skills 模块化注册、人工审批、执行追踪与回归评测。
使用 Python/FastAPI/Pydantic 构建多模型网关（DeepSeek + OpenAI 兼容），
结合 LangChain 组件与 LlamaIndex 完成 RAG 摄取与检索评测，使用 LangGraph
管理多步骤状态、Checkpointer 恢复与 human-in-the-loop。建设 golden dataset
覆盖检索、回答、工具轨迹与安全拒答，并记录 token/成本/延迟与失败原因。
```



### 10.3 10 分钟讲法

1. 背景：聊天机器人完不成多步知识工作
2. 目标：检索→计划→执行→审批→评测
3. 架构：网关 / RAG / 工具·MCP / runtime / eval / trace
4. 难点：幻觉、死循环、上下文膨胀、成本、恢复、安全
5. 方案：结构化输出、引用校验、轨迹评测、HITL、Checkpointer
6. 结果：指标 + badcase
7. 取舍：为何单 Agent 为主、为何 code-first 而非纯 Dify



### 10.4 面试必答五张牌（每张对应你项目里的真实故事）

1. Agent 死循环：max steps + 重复动作检测 + 熔断
2. RAG 不准：分块/混合/rerank + 评测数字
3. MCP vs Function Calling：动态发现、Server 资产化、权限边界
4. 成本：路由、缓存、工具子集、Token 预算
5. 长任务中断：Checkpointer 恢复



### 10.5 投递策略


| 优先投                        | 谨慎投                                   |
| -------------------------- | ------------------------------------- |
| Agent/智能体/LLM 应用/RAG/AI 后端 | 训练微调算法、顶会导向 Research                  |
| 要求 MCP + 评测 + 工具治理的平台岗     | 「2 年商业 LangChain + 985 算法」硬筛且无项目对标空间时 |


---



## 11. 每周复盘模板

```md
## 第N周复盘

### 本周交付
- 

### 本周指标（相对 baseline）
- RAG：
- Agent/轨迹：
- 成本/延迟：
- 测试：

### 砍掉了什么（防止范围膨胀）
- 

### 下周唯一最重要的事
- 

### 面试素材（1 个踩坑故事）
- 
```

---



## 12. 最小成功版本（时间不够时的止损线）

若中途只能保 8 项，按此顺序砍：

1. 可运行 Agent（含工具 + 审批）
2. 带引用 RAG
3. 50–100 条评测（含轨迹）
4. MCP Server 至少一个
5. Docker Compose
6. 完整 README + 架构图
7. 10 分钟演示视频
8. 面试讲稿

这 8 项 > 「学过 10 个框架」。

---



## 13. 官方资料索引（精读清单，拒绝信息过载）

**主读（按周用到再打开）：**

- OpenAI Structured Outputs / Tools / Responses：[https://developers.openai.com/api/docs/](https://developers.openai.com/api/docs/)  
- LangGraph Overview + HITL：[https://docs.langchain.com/oss/python/langgraph/overview](https://docs.langchain.com/oss/python/langgraph/overview)  
- LangChain：[https://docs.langchain.com/](https://docs.langchain.com/)  
- LlamaIndex：[https://developers.llamaindex.ai/](https://developers.llamaindex.ai/)  
- MCP：[https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)  
- Langfuse：[https://langfuse.com/docs](https://langfuse.com/docs)  
- RAGAs（可选）：[https://docs.ragas.io/](https://docs.ragas.io/)

**对照扫（各 ≤0.5 天）：**

- OpenAI Agents SDK、Claude Agent SDK、Dify 文档、CrewAI Quickstart

**面试题库（第 16–17 周集中用）：** 自建「30 题」为主；外部题库只用来查漏，不替代项目故事。

---



## 14. 与旧版计划的差异（你在省下的时间）


| 旧版问题                                     | 本版处理                                     |
| ---------------------------------------- | ---------------------------------------- |
| LangChain + LlamaIndex + Agents SDK 并行深挖 | 编排只深 LangGraph；RAG 二选一做深；SDK 对照          |
| 第 8 周 MCP+Skills+安全过载                    | Skills 挪到第 11 周；第 8 周只保 MCP+审批+injection |
| 「最后 2 周」与 16–18 周矛盾                      | 明确求职阶段 **3 周**                           |
| §14 补丁与正文重复                              | 市场结论并入 §1，不再「缺口补丁」体                      |
| 多 Agent 一刀切反对                            | 主线单 Agent；第 12 周轻量 supervisor 演示         |
| 缺 Context Engineering / 轨迹评测             | 第 2 周与第 13 周纳入主验收                        |
| 绝对 hit@5≥80% 易虚高                         | 改为相对 baseline + 可复现数据集                   |


---



## 15. 最终判断标准

你最该追求的不是「18 周学完 Agent」，而是：

> **面试官问「你怎么保证 Agent 可靠？」——你能掏出代码、trace、评测集、失败样例、安全策略和部署环境。**

月度节奏：

1. **第 1 月**：网关 + 多模型 + 可评测 RAG
2. **第 2 月**：手写 loop + LangGraph + MCP/安全
3. **第 3 月**：旗舰 MVP（含 Skills、可选轻量多 Agent）
4. **第 4 月**：评测加深、成本观测、安全部署
5. **最后 3 周**：作品集、简历、面试与投递

执行口令：

> **每周只完成路线图上最重要的一件可演示事；其余全部砍。**

