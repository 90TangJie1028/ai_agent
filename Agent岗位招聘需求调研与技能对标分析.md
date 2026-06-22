# Agent 岗位招聘需求调研与技能对标分析

**版本日期**：2026-06-22  
**调研范围**：Boss 直聘、智联招聘、猎聘、大厂官方 JD；辅以掘金/CSDN 等对 50+ 真实 JD 的二次分析  
**对标文档**：[Agent中级开发工程师学习计划（终极攻略版）.md](./Agent中级开发工程师学习计划（终极攻略版）.md)  
**目标读者**：有 10 年+ 工程经验、计划 4–5 个月转向 Agent/LLM 应用工程的中级开发者

---

## 1. 调研方法与样本说明

### 1.1 数据来源

| 来源 | 样本类型 | 参考价值 |
|---|---|---|
| 智联招聘 | 联想教育、中创智维、蓬勃科技、保利和润等 Agent 岗 JD 原文 | 中型公司、交付型岗位，技能描述完整 |
| 猎聘 | 腾讯 PCG、字节 Coze/开发者服务/AI for Science、湃方科技等 | 大厂与高薪岗，工程化要求最高 |
| Boss 直聘 | 通过掘金数据分析文章间接采样（50+ JD） | 关键词频率、岗位趋势 |
| 行业分析 | CSDN《2026 大厂 Agent 面试风向标》、AgentGuide 招聘分析 | 面试考点与 JD 趋势交叉验证 |

### 1.2 岗位名称归一化

招聘市场上的名称很杂，本报告统一归为以下四类：

| 类型 | 常见 JD 标题 | 占比体感 | 与你学习计划的匹配度 |
|---|---|---|---|
| **A. Agent 应用工程师** | AI Agent 开发工程师、智能体开发工程师、大模型应用工程师 | ~45% | ★★★★★ 主目标 |
| **B. Agent 平台工程师** | Agent 平台工程师、AI 应用平台开发、Dify 二次开发 | ~25% | ★★★★☆ 你的旗舰项目可向上靠 |
| **C. 全栈 Agent 工程师** | AI 全栈工程师、Python 全栈（Agent 方向） | ~20% | ★★★☆☆ 需补轻量前端 |
| **D. 算法偏重型** | 大模型算法工程师（含 Agent）、AI 算法开发 | ~10% | ★★☆☆☆ 非主路线，慎投 |

**结论**：你的原计划定位（Agent 应用工程师 / LLM 应用工程师）与市场需求主体一致，方向正确。需要补的是 **MCP、LangChain 生态显性覆盖、低代码平台认知、国内大模型适配** 等 JD 高频但原计划偏弱的项。

---

## 2. 技能需求频率矩阵（过滤后）

以下按 **出现频率** 和 **面试权重** 综合排序，★ 为必备，☆ 为加分。

### 2.1 编程与后端基础

| 技能 | 频率 | 典型 JD 表述 | 原计划覆盖 | 缺口 |
|---|---|---|---|---|
| **Python** | ★★★★★ | 精通 Python，扎实软件工程基础 | ✅ 主语言 | 补 asyncio 异步编程实战 |
| **FastAPI** | ★★★★☆ | RESTful API、异步服务 | ✅ 已列 | 无 |
| Django/Flask | ★★★☆☆ | 熟悉其一即可 | ⚠️ 未列 | 了解即可，不必深学 |
| **Pydantic / JSON Schema** | ★★★★☆ | 工具参数 Schema、结构化输出 | ✅ 已列 | 无 |
| Go/Java 第二语言 | ★★★☆☆ | 大厂/平台岗常见 | ❌ 未列 | 非 18 周主线，简历可写“可快速适配” |
| 微服务 / 高并发 | ★★★★☆ | 3–5 年经验岗标配 | ⚠️ 弱 | 旗舰项目加队列/限流即可 |
| 消息队列 Kafka/RabbitMQ | ★★★☆☆ | 异步长任务、Agent 平台岗 | ❌ 未列 | 第 13–14 周可选加 Redis Stream 或 Celery |

### 2.2 Agent 核心能力

| 技能 | 频率 | 典型 JD 表述 | 原计划覆盖 | 缺口 |
|---|---|---|---|---|
| **ReAct / Agent Loop** | ★★★★★ | 手写或理解 Think-Act-Observe | ✅ 第 6 周 | 无 |
| **Function Calling / Tool Use** | ★★★★★ | 工具注册、参数校验、执行器 | ✅ 已列 | 无 |
| **MCP（模型上下文协议）** | ★★★★★↑ | 2026 从加分项变硬性条件 | ❌ **重大缺口** | **必须新增专项** |
| **LangGraph** | ★★★★★ | 状态机、中断恢复、DAG 编排 | ✅ 已列 | 无 |
| **LangChain** | ★★★★★ | 生态组件、LCEL、Chain | ⚠️ 仅间接 | **需显性列入主栈** |
| Plan-and-Execute | ★★★★☆ | 任务拆解、规划执行 | ✅ 项目含 Planner | 面试要能画图讲 |
| **记忆系统** | ★★★★☆ | 短期/长期记忆、上下文管理 | ⚠️ 弱 | 需补 Memory 模块 |
| Multi-Agent | ★★★★☆ | AutoGen/CrewAI/多 Agent 协作 | ⚠️ CrewAI 了解即可 | 补“何时不用多 Agent”案例 |
| **Skills 规范** | ★★★★☆↑ | 字节/联想等 2026 新热点 | ❌ 未列 | 与 MCP 一起学习 |
| A2A 协议 | ★★★☆☆ | Agent 间协作 | ❌ 未列 | 了解概念即可 |
| Dify / Coze | ★★★★☆ | 低代码平台、快速交付 | ❌ 未列 | 1 周体验级覆盖 |
| AutoGen | ★★★☆☆ | 多 Agent 对话协作 | ❌ 未列 | 文档级了解 |

### 2.3 RAG 与知识库

| 技能 | 频率 | 典型 JD 表述 | 原计划覆盖 | 缺口 |
|---|---|---|---|---|
| **RAG 全流程** | ★★★★★ | 摄取、分块、索引、检索、生成 | ✅ 第 3–5 周 | 无 |
| **混合检索 + Rerank** | ★★★★★ | BM25+向量、重排序 | ✅ 已列 | 无 |
| **引用溯源 / 拒答** | ★★★★☆ | 企业级可信问答 | ✅ 已列 | 无 |
| 向量库 Milvus/Qdrant/pgvector | ★★★★☆ | 至少熟练一种 | ✅ Chroma 起步 | 建议 MVP 阶段切 pgvector |
| ES 混合检索 | ★★★☆☆ | Milvus+ES 双路 | ❌ 未列 | 简历可写“了解 ES 混合检索方案” |
| GraphRAG / 知识图谱 | ★★★☆☆ | 多跳推理、复杂关联 | ❌ 未列 | 了解概念 + 1 个 demo 阅读 |
| 评测 RAGAs/DeepEval | ★★★★☆ | 离线评测、指标驱动优化 | ✅ golden dataset | 可引入 RAGAs 库 |
| ACL/RBAC 权限过滤 | ★★★☆☆ | 企业知识库 | ⚠️ 弱 | 旗舰项目加文档级权限即可 |

### 2.4 模型与 Prompt

| 技能 | 频率 | 典型 JD 表述 | 原计划覆盖 | 缺口 |
|---|---|---|---|---|
| **Prompt Engineering** | ★★★★★ | CoT、Few-shot、模板化 | ⚠️ 分散 | 集中 2–3 天整理 Prompt 库 |
| **多模型接入与路由** | ★★★★☆ | GPT/Claude/DeepSeek/通义/文心 | ⚠️ 偏 OpenAI | **加国内模型适配器** |
| Structured Output | ★★★★☆ | JSON Schema 约束输出 | ✅ 第 2 周 | 无 |
| Embedding 选型与调优 | ★★★★☆ | 维度、中英文、领域适配 | ⚠️ 弱 | RAG 周补充对比实验 |
| 模型微调 LoRA/PEFT | ★★★☆☆ | 算法偏重型岗 | ❌ 未列 | 非主线，知道原理即可 |
| vLLM / 私有化部署 | ★★★☆☆ | 推理优化、本地部署 | ❌ 未列 | 了解 Ollama/vLLM 概念 |

### 2.5 工程化与运维

| 技能 | 频率 | 典型 JD 表述 | 原计划覆盖 | 缺口 |
|---|---|---|---|---|
| **Docker / Docker Compose** | ★★★★★ | 容器化部署 | ✅ 已列 | 无 |
| **评测与可观测** | ★★★★★ | Tracing、成本、成功率 | ✅ LangSmith/Langfuse | 无 |
| Kubernetes | ★★★★☆ | 3–5 年平台岗 | ❌ 未列 | 面试了解概念，不纳入 18 周主线 |
| CI/CD + 回归测试 | ★★★★☆ | smoke test、eval subset | ✅ 第 13 周 | 无 |
| 熔断/降级/限流/幂等 | ★★★★☆ | 生产级 Agent 平台 | ✅ Model Gateway | 无 |
| Redis | ★★★★☆ | 缓存、会话、队列 | ✅ 已列 | 无 |
| PostgreSQL | ★★★★☆ | 业务数据 + pgvector | ✅ 已列 | 无 |
| **AI Coding 工具** | ★★★★☆↑ | Cursor/Copilot 提效 | ❌ 未列 | 日常开发默认使用即可 |

### 2.6 软技能与简历信号

| 信号 | 频率 | 说明 |
|---|---|---|
| **0→1 完整项目** | ★★★★★ | 能演示、能讲架构、有 GitHub |
| **量化指标** | ★★★★★ | 检索命中率、工具成功率、P95 延迟、成本 |
| **行业落地经验** | ★★★★☆ | 金融/制造/政务/教育等垂直场景 |
| 开源贡献 | ★★★☆☆ | 加分但非必须 |
| 英语读写 | ★★★☆☆ | 外企/全球化团队岗 |
| 全栈（React/Vue） | ★★★☆☆ | 部分岗要求轻量管理后台 |

---

## 3. 典型 JD 原文摘要（代表性样本）

### 3.1 大厂应用型 — 腾讯 PCG Agent 工程师（猎聘，30–60k）

**核心要求摘录**：
- Go/Python 高并发 Agent 服务、工作流引擎、队列消费
- LangChain/LangGraph/LlamaIndex/AutoGen/Eino/Dify/Coze 至少一种
- Function Calling、Tool Use、**MCP**、ReAct、Plan-and-Execute、**Skills**
- 单测、CI/CD、可观测性（日志、Trace、Metrics）
- 有完整 Agent 落地项目，可附 Demo/GitHub

**对你的启示**：大厂不只看框架名称，看 **工程化全套**。你的 18 周计划在评测、trace、CI 上与大厂方向一致；需补 **MCP + Skills**。

### 3.2 大厂平台型 — 字节跳动开发者服务 Agent 研发（猎聘，30–60k）

**核心要求摘录**：
- 模型接入、Agent 开发、RAG 优化、**MCP 及工具开发**
- 评估系统、上下文工程
- 从 0–1 搭建 Agent 应用经验
- 服务化、异步、高可用、监控容灾

**对你的启示**：字节系特别强调 **MCP、工具生态、评估系统**，与“测试开发-开发者 AI”岗一样，把 Agent 可靠性当硬指标。

### 3.3 交付型中型公司 — 联想教育 AI Agent 工程师（智联，25–35k）

**核心要求摘录**：
- LangChain/LangGraph、DAG/状态机、多 Agent、会话与长任务
- **Skills 注册**、MCP、工具 Schema、租户隔离、鉴权、幂等/重试/限流/熔断
- 企业级 RAG：混合检索 Milvus+ES、重排、引用溯源、ACL
- 全栈 Python+React、K8s/Docker、离线评测 + 线上指标
- 解决幻觉、死循环、上下文丢失等行业共性问题

**对你的启示**：这是与你目标最贴近的 JD 之一。你的旗舰项目模块划分与这份 JD **高度同构**，补齐 MCP/Skills/混合检索即可直接对标。

### 3.4 行业集成型 — 中创智维 AI 大模型应用及 Agent 工程师（智联）

**核心要求摘录**：
- 至少 2 年 LangChain 经验，LangGraph/langFlow
- RAG 全流程、向量数据库、与行业业务融合
- 系统运维、客户系统集成
- 学历/年限门槛较高（985/3 年+）

**对你的启示**：集成型公司看重 **LangChain 生态熟练度 + 行业话术**。面试时要能把你的旗舰项目翻译成“某行业知识工作台”。

### 3.5 创业型 — 蓬勃科技 AI Agent 开发工程师（智联）

**核心要求摘录**：
- 5 年+ 后端，2 年+ Agent 商业化经验
- LangChain/LlamaIndex、LangGraph 状态机
- Milvus/Chroma、GPT/文心/通义等多模型
- Docker/K8s、Kafka/RabbitMQ、Dify 二次开发加分

**对你的启示**：创业公司对 **商业化交付、多模型、消息队列** 敏感。你的项目应展示“可卖给客户”的完整度。

---

## 4. 2026 面试高频考点（JD 之外但决定通过率）

来自大厂面试面经归纳，以下问题在 JD 里常常只写一行，但面试会深挖：

| 考点 | 面试官真正想听的 | 你的准备动作 |
|---|---|---|
| Agent vs Chatbot | 自主决策 + 工具行动闭环 | 用旗舰项目 1 分钟版回答 |
| Agentic Loop | Think→Act→Observe，消息格式 | 第 6 周手写 loop 时画序列图 |
| 工具死循环 | 三层防御：工具层/推理层/规划层 | 第 8 周安全周写进代码 |
| MCP vs Function Calling | 动态发现、Server-First、可复用资产 | **新增 MCP 专项** |
| RAG 检索差怎么办 | 分块、混合检索、rerank、query 改写 | 第 4–5 周留 badcase 库 |
| 记忆方案 | 工作/短期/长期记忆，检索式 vs 权重式 | 第 7 周 LangGraph 加 Memory |
| 多 Agent 何时用 | 子任务隔离 vs 需要通信 | 准备“为什么单 Agent”论据 |
| 成本优化 | 模型路由、缓存、Token 预算、KV cache | 第 14 周观测周 |
| Prompt Injection | MCP Context Poisoning、工具描述审计 | 第 8/15 周安全报告 |

---

## 5. 与原学习计划的差距分析

### 5.1 原计划做对了什么（与市场需求高度一致）

1. **工程化优先，非算法研究** — 与 80%+ JD 方向一致  
2. **旗舰项目贯穿** — 对标“0→1 完整系统”硬要求  
3. **RAG 可评测化** — 企业级 JD 反复强调离线评测  
4. **LangGraph 状态编排** — 2026 最热框架之一  
5. **安全与人工审批** — 大厂面试高频  
6. **trace + 成本 + 部署** — 平台型 JD 标配  

### 5.2 必须补充的缺口（按优先级）

| 优先级 | 缺口 | 建议动作 | 建议插入周次 |
|---|---|---|---|
| **P0** | MCP 协议与 Server 开发 | 为旗舰项目加 MCP Server，暴露 kb/agent 工具 | 第 7–8 周 |
| **P0** | LangChain 生态显性覆盖 | 主栈表加入 LangChain；用 LCEL 做 RAG 管线 | 第 3 周起 |
| **P1** | 国内大模型适配 | ModelGateway 加 DeepSeek/通义/智谱适配器 | 第 1–2 周 |
| **P1** | 记忆系统 | LangGraph Checkpointer + 长期记忆检索 | 第 7 周 |
| **P1** | Skills 规范 | 工具模块化注册，版本化，文档化 | 第 8 周 |
| **P2** | Dify/Coze 体验 | 2 天搭建同款 RAG/Agent，写对比 ADR | 第 12 周末 |
| **P2** | pgvector 生产化 | MVP 阶段从 Chroma 迁 pgvector | 第 10 周 |
| **P2** | AI Coding 工具 | 日常用 Cursor，简历写提效实践 | 全程 |
| **P3** | GraphRAG 了解 | 读 1 篇论文 + LlamaIndex GraphRAG 文档 | 第 5 周末 |
| **P3** | 轻量 React 管理台 | 可选：对话页 + trace 查看 | 第 12 周 |

### 5.3 不建议纳入 18 周主线的项

| 技能 | 原因 |
|---|---|
| PyTorch 深度学习 / 模型训练 | JD 里算法岗才硬要求；应用岗“了解即可” |
| Kubernetes 深度实战 | 中型岗 Docker Compose 够用；K8s 面试讲概念 |
| 前端重型开发 | 多数 Agent 岗后端权重 70%+；轻量 demo 即可 |
| 多 Agent 炫技 | 市场要“可靠单 Agent”，不是“八个 Agent 开会” |

---

## 6. 岗位投递策略（结合调研）

### 6.1 优先投递

- AI Agent 开发工程师 / 智能体开发工程师 / 大模型应用工程师  
- RAG 工程师 / LLM 应用工程师 / AI 后端工程师  
- Agent 平台工程师（若旗舰项目含 MCP + 评测 + 多租户雏形）

### 6.2 谨慎投递

- 明确要求 2 年+ LangChain 商业经验、985 算法背景  
- 大模型算法工程师（需训练/微调/paper）  
- 纯 AIGC 生图/生视频算法岗（技能栈偏离）

### 6.3 简历关键词建议（ATS 友好）

```
Python | FastAPI | LangChain | LangGraph | LlamaIndex | RAG | Agent | 
Function Calling | MCP | Tool Use | Pydantic | PostgreSQL | pgvector | 
Redis | Docker | OpenTelemetry | Langfuse | Prompt Engineering | 
Structured Output | Human-in-the-loop | Evaluation | DeepSeek | 通义千问
```

### 6.4 薪资带宽参考（2026 Q2，仅供参考）

| 城市/类型 | 经验要求 | 月薪带宽 |
|---|---|---|
| 北京/上海 大厂 | 3–5 年 | 30–60k × 15 薪 |
| 一线中型公司 | 3–5 年 | 20–35k |
| 二线/交付型 | 2–4 年 | 15–25k |
| 创业早期 | 不限 | 面议，股权占比大 |

你有 10 年+ 工程经验，简历应突出 **系统设计与交付**，弱化“转岗学习”，强化“用工程方法构建 Agent 系统”。

---

## 7. 技能对标总表（一页纸）

```
市场需求                    你的原计划          优化后
─────────────────────────────────────────────────────────
Python/FastAPI              ✅                  ✅
LangChain 生态              ⚠️ 弱              ✅ 显性纳入
LangGraph                   ✅                  ✅
OpenAI Agents SDK           ✅                  ✅
LlamaIndex/RAG              ✅                  ✅
MCP                         ❌                  ✅ 新增
Skills                      ❌                  ✅ 新增
Function Calling            ✅                  ✅
记忆/Checkpointer           ⚠️ 弱              ✅ 加强
多模型(含国内)              ⚠️ 弱              ✅ 加强
Dify/Coze 认知              ❌                  ✅ 体验级
评测体系                    ✅                  ✅
安全/HITL                   ✅                  ✅
Docker Compose              ✅                  ✅
K8s                         ❌                  📖 概念级
全栈 React                  ❌                  ⭕ 可选
微调/训练                   ❌                  📖 了解即可
```

---

## 8. 参考链接

| 资源 | 链接 |
|---|---|
| 腾讯 PCG Agent 工程师 JD | https://www.liepin.com/job/1982715501.shtml |
| 字节 Coze Agent 开发 JD | https://www.liepin.com/job/1983380283.shtml |
| 字节开发者服务 Agent JD | https://www.liepin.com/job/1983380379.shtml |
| 字节 AI for Science Agent 平台 JD | https://www.liepin.com/job/1983540379.shtml |
| 联想教育 Agent 工程师 JD | https://www.zhaopin.com/jobdetail/CC840683300J40856094311.htm |
| 中创智维 Agent 工程师 JD | https://www.zhaopin.com/jobdetail/CC272222130J40712519014.htm |
| 蓬勃科技 Agent 工程师 JD | https://www.zhaopin.com/jobdetail/CCL1328897090J40847638001.htm |
| 2026 大厂 Agent 面试风向标 | https://blog.csdn.net/2301_80239908/article/details/161399535 |
| MCP 官方文档 | https://modelcontextprotocol.io/ |
| Dify 文档 | https://docs.dify.ai/ |
| LangChain 文档 | https://docs.langchain.com/ |

---

## 9. 结论

1. **方向正确**：你的原计划与 2026 年 Agent 应用工程师主流 JD 同向，工程化、评测、安全是正确壁垒。  
2. **最大缺口是 MCP**：已从“加分项”变为多个大厂/中型公司的硬性或半硬性要求，必须纳入学习主线。  
3. **LangChain 要显性出现**：很多 JD 写“2 年 LangChain 经验”，仅学 LangGraph 不够，需在简历和项目中体现 LangChain 生态使用。  
4. **国内大模型适配是差异化**：纯 OpenAI 栈在国内投递面窄，ModelGateway 加 1–2 个国内模型很实用。  
5. **面试考系统不考名词**：准备好死循环防御、检索优化、MCP 架构、成本/trace 四张王牌即可覆盖大部分技术面。

> 下一步：参见更新后的 [Agent中级开发工程师学习计划（终极攻略版）.md](./Agent中级开发工程师学习计划（终极攻略版）.md) 第 15 节「招聘市场对标补丁」。
