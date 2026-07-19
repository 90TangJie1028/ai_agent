# Agent 岗位招聘需求调研与技能对标分析

**版本日期**：2026-07-17（相对 2026-06-22 版的季度复盘）  
**调研范围**：猎聘/智联等公开 JD、海外 Applied AI / Agent 岗 JD、框架招聘统计（约 1100 条 agentic 岗位样本）、面试题库与后端转型路线（JavaGuide 等）交叉验证  
**对标文档**：[Agent中级开发工程师学习计划（终极攻略版）.md](./Agent中级开发工程师学习计划（终极攻略版）.md)  
**目标读者**：10 年+ 工程经验、4–5 个月转向 Agent/LLM **应用工程** 的开发者  
**核心问题**：时间最贵时，市场究竟为哪些技能付钱？哪些该学深、哪些该砍？

---

## 1. 执行摘要（先读这段再决定学什么）

### 1.1 三句结论

1. **赛道没变**：Agent 应用工程师 / LLM 应用工程师仍是主战场；训练/微调算法是另一条赛道，不要混投。  
2. **门槛变硬的是「生产可靠性」**：MCP、LangGraph 状态编排、可评测 RAG、观测与成本、HITL —— 不是又学一个新框架名。  
3. **最高 ROI 学习策略**：一个旗舰项目贯穿 + 先手写 Agent Loop 再上 LangGraph + MCP Server 必做 + golden set（含工具轨迹）必做；CrewAI/AutoGen/重前端/微调主线全部降级。

### 1.2 相对 2026-06 调研的变化

| 变化 | 方向 | 对学习计划的影响 |
|---|---|---|
| MCP | 加分 → 大量 JD 硬性/半硬性 | 保持 P0，强调「接企业系统」叙事 |
| Context Engineering | 从概念 → 独立岗与 JD 措辞 | 用它替代空泛「Prompt 优化」叙事 |
| Agentic RAG / 高级 RAG | JD 出现增多 | RAG 周加一小段，不另开阶段 |
| Agent 评测 | 从「有评测」→ 轨迹/工具序列/状态转移 | 第 13 周加 trajectory 断言 |
| 多 Agent | 出现率上升 | 轻量 supervisor demo，主线仍单 Agent |
| 一等公民 SDK（Claude/OpenAI Agents） | 上升 | 对照了解，不换 LangGraph 主线 |
| A2A | 课程/平台岗增多 | P2 概念级 |
| AutoGen | 招聘滞后、产品偏维护 | 了解即可，勿押主线 |
| AI Coding（Cursor 等） | 更多 JD 显性要求 | 日常使用即可写进简历 |
| 垂直场景（ChatBI/合同/差旅） | 增多 | 旗舰可加 1 个垂直切片，不换项目 |

### 1.3 给你个人的投产比判断

你有长期工程经验 → **不要从「AI 小白课程」重走**。市场真正缺的是：

> 能把非确定性模型输出，做成有权限、有状态、有评测、有成本账、出了问题能定位的服务的人。

这与你过往的 API / 稳定性 / 排障能力同构。缺的是 Agent/RAG/MCP 这一层的 **可证明作品**，不是再刷一年基础语法。

---

## 2. 调研方法与样本

| 来源类型 | 样本/材料 | 用途 |
|---|---|---|
| 国内 JD | 猎聘/智联：智能体应用开发、大模型应用、MCP/Skill、携程 Agent、资管 Agent、南昌/杭州等岗 | 关键词频率与职责表述 |
| 海外 JD / 角色定义 | Applied AI Engineer、Appian MCP 岗、Anthropic 系 Applied AI 能力描述 | 验证「评测=核心竞争力」 |
| 招聘统计 | agentic-engineering-jobs 对 1135 条岗位中框架共现分析（2026 春末采样窗） | 框架与 MCP 共现客观数据 |
| 面试题库 | 卡码笔记、面灵、博客园 Agent 面试梳理、大厂风向标类文章 | 校准「JD 一行、面试挖三层」的点 |
| 转型路线 | JavaGuide 后端→Agent（2026-06） | 工程背景转型节奏交叉验证 |
| 作品集建议 | Technovids 等 2026 AI Engineer Projects | 高信号项目形态 |

说明：公开招聘文案有水分（「精通一切」），本报告用 **多源交叉** —— 只把「JD + 面试题 + 框架招聘统计」同时出现的技能标为 P0。

---

## 3. 岗位地图：你该站哪一格

| 类型 | 常见标题 | 匹配度 | 策略 |
|---|---|---|---|
| **A. Agent 应用工程师** | AI Agent / 智能体开发 / 大模型应用 | ★★★★★ | **主投** |
| **B. RAG / LLM 应用** | RAG 工程师、知识库、AI 后端 | ★★★★★ | 主投；旗舰天然覆盖 |
| **C. Agent 平台** | MCP/Skill、工具平台、AI 中台 | ★★★★☆ | 旗舰含 MCP+评测+Skills 时可投 |
| **D. 全栈 Agent** | AI 全栈、轻前端 | ★★★☆☆ | 有 CLI/轻 Web 即可，不补重前端 |
| **E. 算法偏重** | 训练/微调/RL/顶会 | ★☆☆☆☆ | **不投**（除非你另有 paper 路径） |
| **F. Context Engineering** | 上下文/本体/语义层工程师 | ★★★☆☆ | 加分叙事；主项目偏 Agent 时作副线表达 |

北美市场另有 FDE / Applied AI / Agent Platform 等收敛岗位，共性仍是：**Python、工具调用、RAG、eval、MCP、生产可靠性**。薪资带与国内不可直接换算，但技能清单高度同构。

---

## 4. 技能需求频率矩阵（2026-07）

★ = 必备频率/面试权重；↑ = 相对 6 月上升。

### 4.1 编程与后端

| 技能 | 频率 | 原计划 | 结论 |
|---|---|---|---|
| Python（含 asyncio） | ★★★★★ | ✅ | 主语言锁定 |
| FastAPI / 同类 Web | ★★★★☆ | ✅ | 保持 |
| Pydantic / JSON Schema | ★★★★☆ | ✅ | 工具与结构化输出核心 |
| Go/Java 第二语言 | ★★★☆☆ | 弱 | 简历写可适配；18 周不深挖 |
| 高并发/队列/限流熔断 | ★★★★☆ | 网关可覆盖 | 用工程经验讲故事，项目里做够限流重试 |
| Redis / PostgreSQL | ★★★★☆ | ✅ | 保持；pgvector 优先于再学一个云向量库 |

### 4.2 Agent 核心

| 技能 | 频率 | 结论 |
|---|---|---|
| ReAct / 手写 Loop | ★★★★★ | P0；面试手撕 |
| Function Calling / Tool Use | ★★★★★ | P0 |
| **MCP** | ★★★★★↑ | **P0**；写 Server |
| **LangGraph** | ★★★★★ | P0；主编排 |
| **LangChain** | ★★★★★ | P0 级「显性使用」，非全模块精通 |
| 记忆 / Session / Checkpointer | ★★★★☆↑ | P1 |
| Plan-and-Execute | ★★★★☆ | 项目 Planner 覆盖 |
| Skills 抽象 | ★★★★☆↑ | P1；与 MCP 一起讲 |
| Multi-Agent | ★★★★☆↑ | P1 轻量 demo；主线单 Agent |
| Context Engineering | ★★★★☆↑ | P1；叙事升级 |
| Dify/Coze | ★★★☆☆ | P2 体验 |
| AutoGen / CrewAI | ★★★☆☆ | P3 了解；勿主线 |
| A2A | ★★☆☆☆↑ | P2 概念 |

### 4.3 RAG

| 技能 | 频率 | 结论 |
|---|---|---|
| RAG 全流程 | ★★★★★ | P0 |
| 混合检索 + Rerank | ★★★★★ | P0 |
| 引用 / 拒答 | ★★★★☆ | P0（企业可信） |
| 向量库（Milvus/pgvector/Qdrant） | ★★★★☆ | pgvector 做深；Milvus 概念 |
| Agentic RAG | ★★★☆☆↑ | P2 小实验 |
| GraphRAG | ★★★☆☆ | P2/P3 概念 |
| RAGAs 等评测库 | ★★★★☆ | 可选；自建 golden 更重要 |

### 4.4 模型与 Prompt

| 技能 | 频率 | 结论 |
|---|---|---|
| 多模型（DeepSeek/通义/OpenAI 兼容） | ★★★★☆ | P0（国内） |
| Structured Output | ★★★★☆ | P0 |
| Prompt / **Context Engineering** | ★★★★★ | 升级为上下文体系，不单卷话术 |
| 微调 LoRA | ★★★☆☆ | 非主线 |
| vLLM/私有化 | ★★★☆☆ | 概念即可 |

### 4.5 工程化（中高级差异点）

| 技能 | 频率 | 结论 |
|---|---|---|
| Docker Compose | ★★★★★ | P0 |
| 评测体系 / golden set | ★★★★★↑ | P0；含轨迹 |
| Trace / Langfuse/LangSmith | ★★★★★ | P0 二选一 |
| 成本：路由/缓存/预算 | ★★★★☆↑ | P1 |
| CI 回归 | ★★★★☆ | P0（smoke） |
| K8s | ★★★☆☆ | 概念 |
| AI Coding 工具 | ★★★★☆↑ | 日常使用 |

### 4.6 框架招聘数据要点（海外 agentic 样本）

- 市场雇的是 **stack**（常见点名约 2 个框架），不是单一赢家。  
- LangChain 出现率最高（底座）；LangGraph 第二（有状态运行时）。  
- **MCP 是跨框架最稳定的伴生技能**（约 17%–24% 与各框架共现）。  
- LlamaIndex 更偏检索层；CrewAI/AutoGen 几乎从不单独出现。  
- 含义：学 **LangChain 组件 + LangGraph 深 + MCP**，比「五个框架各玩一周」更贴市场。

---

## 5. 代表性 JD 信号（摘要）

### 5.1 国内应用/平台型（高频交集）

反复出现的职责块：

1. LangGraph / LangChain / LlamaIndex 至少一种，复杂状态机或多 Agent  
2. MCP 把 Agent 接到 DB / ERP / 内部知识库；工具注册、发现、鉴权、限流、监控  
3. Skills 抽象：动态加载、版本、Schema  
4. RAG 全链路优化；部分写知识图谱  
5. 长文本、Token、状态持久化、Session；生产稳定与成本  
6. 可观测、压测、Caching、异常容错  

**启示**：你的旗舰模块划分（网关/RAG/MCP/Skills/HITL/Eval/Trace）与头部 JD **同构** —— 执行到位即可对标，无需换项目名。

### 5.2 业务落地型（携程差旅 Agent 等）

- 单/多 Agent、规划、工具、工作流  
- RAG 高级优化（混合、重排、图谱融合）  
- 幻觉、数据安全、上下文  
- 2B 价值指标（效率、成本）  

**启示**：作品集要有 **业务指标话术**，哪怕评测集是自建的。

### 5.3 海外 Applied AI / MCP 岗

- 编排、工具层、RAG、**evaluation harness**、观测  
- MCP Server 暴露企业能力；多 Agent 协调为加分  
- 「Applied AI ≈ reliability engineer」—— 评测不是加分项，是岗位本体  

**启示**：第 13–14 周的评测与观测，决定你是「中级可交付」还是「只会 demo」。

### 5.4 算法伪装岗（应避开的信号）

JD 同时强调：PyTorch 训练、RLHF/SFT 落地、顶会、奖励函数设计 —— 与应用工程画像冲突时 **直接跳过**，避免浪费面试周期。

---

## 6. 面试高频考点（决定通过率）

JD 常只写一行，面试会挖实现：

| 考点 | 面试官想听 | 计划落点 |
|---|---|---|
| Agent vs Chatbot | 决策+工具+状态闭环 | 旗舰 1 分钟版 |
| 手写 ReAct | Thought-Action-Observation；失败怎么办 | 第 6 周 |
| 死循环 | max steps + 重复检测 + 熔断 | 第 6/8 周代码 |
| MCP vs FC | 动态发现、N+M、资产化、权限 | 第 8 周 |
| RAG 差 | 诊断→分块/混合/rerank→评测证明 | 第 4–5 周 badcase |
| 记忆 | 工作/短期/长期；截断策略 | 第 7 周 |
| 多 Agent 何时用 | 隔离 vs 通信成本；多数时候不用 | 第 12 周 + 讲稿 |
| 成本 | 路由、缓存、工具子集、Workflow vs Agent | 第 14 周 |
| Injection | 数据/指令隔离、工具描述审计 | 第 8/15 周 |
| Context Engineering | 预算、检索、记忆、工具描述四支柱 | 第 2/7 周 |

准备策略：**五张真实踩坑牌**（死循环、检索、MCP、成本、恢复）> 背 100 道题。

---

## 7. 技能投入产出矩阵（排期用）

| 优先级 | 技能包 | 建议投入（18 周内） | 不投入的代价 |
|---|---|---|---|
| P0 | 网关+结构化+工具 | 2 周 | 无工程可信度 |
| P0 | 可评测 RAG | 3 周 | 过不了企业知识库面 |
| P0 | 手写 Loop + LangGraph + HITL | 2 周 | 过不了 Agent 手撕/系统设计 |
| P0 | MCP + 安全底线 | 1 周（聚焦） | 丢 2026 硬筛选词 |
| P0 | 旗舰合并 MVP | 4 周 | 无作品集 |
| P0 | 评测轨迹+观测+部署 | 3 周 | 卡在「会做 demo」 |
| P1 | Context/记忆/Skills/轻量多 Agent/成本 | 打散嵌入上述周 | 中高级面深度不够 |
| P2 | Dify、Agentic RAG、GraphRAG 概念、SDK 对照 | ≤1 周合计 | 个别面试加分丢失 |
| P3 | K8s 实操、重前端、微调、AutoGen 深挖 | **0** | 几乎无（对目标岗） |

**砍掉清单的经济学**：每深挖一个 P3 框架 ≈ 牺牲半周评测或 MCP 深度；而招聘数据显示评测/MCP/LangGraph 的边际回报更高。

---

## 8. 与学习计划的对标总表

```
市场需求                         高效终局版计划
────────────────────────────────────────────
Python/FastAPI/Pydantic          ✅ 第1–2周+全程
多模型含国内                     ✅ 第1–2周
LangChain 显性                   ✅ 组件级，非全量
LangGraph 深                     ✅ 第7周起主编排
手写 Agent Loop                  ✅ 第6周
RAG+评测                         ✅ 第3–5、13周
Agentic RAG                      ✅ 第4周可选小实验
MCP Server                       ✅ 第8周
Skills                           ✅ 第11周（避免第8周爆炸）
记忆/Checkpointer                ✅ 第7周
Context Engineering              ✅ 第2/7周叙事与实现
HITL/安全/injection              ✅ 第8、15周
轨迹评测+Langfuse                ✅ 第13–14周
轻量多 Agent                     ✅ 第12周可选
Dify 对照                        ✅ 第12周2天
成本路由缓存                     ✅ 第14周
Docker Compose                   ✅ 第12、15周
K8s/微调/AutoGen主线             ❌ 明确不学
```

旧版「重大缺口（MCP/LangChain）」在 6 月补丁后已进主线；7 月增量是 **Context Engineering 叙事、轨迹评测、轻量多 Agent、框架做减法**。

---

## 9. 简历与投递

### 9.1 ATS 关键词串

```text
Python | FastAPI | Pydantic | LangChain | LangGraph | RAG | Agentic RAG |
Agent | MCP | Function Calling | Context Engineering | Structured Output |
Human-in-the-loop | Checkpointer | pgvector | PostgreSQL | Redis | Docker |
Langfuse | Evaluation | Trajectory Eval | DeepSeek | 通义
```

### 9.2 年限包装原则

- 突出：**系统设计、稳定性、权限、观测、0→1 交付**  
- 弱化：「刚转行 / 在学 AI」  
- 对冲「2 年 LangChain」：用 **项目深度 + 关键词覆盖 + 可运行仓库**，不伪造工龄  

### 9.3 薪资带宽（仅供预期管理，2026 上半年公开信息）

| 类型 | 经验口径 | 月薪体感 |
|---|---|---|
| 一线大厂应用/Agent | 3–5 年+ | 约 30–60k 级（含多薪） |
| 一线/新一线中型 | 3–5 年 | 约 20–40k |
| 二线/交付型 | 2–4 年 | 约 15–25k |
| 垂直行业 Agent | 视业务 | 带宽大，看落地经验 |

10 年工程背景应走 **中高级应用/平台** 叙事，避免与应届「调过 API」简历同质化内卷。

### 9.4 投递漏斗建议

1. 先投与旗舰同构的 JD（MCP+RAG+LangGraph）。  
2. 每面必更新：题库 + README 弱点。  
3. 连续同质挂在「无评测/无 MCP」时，优先补作品而非改投算法岗。

---

## 10. 参考链接（抽样）

| 资源 | 链接 |
|---|---|
| MCP 官方 | https://modelcontextprotocol.io/ |
| LangGraph | https://docs.langchain.com/oss/python/langgraph/overview |
| 框架招聘统计（2026） | https://agentic-engineering-jobs.com/ai-agent-frameworks-job-market-2026 |
| 后端→Agent 转型（JavaGuide） | https://javaguide.cn/roadmap/backend-to-ai-agent-roadmap.html |
| AI Engineer 高信号项目 | https://technovids.com/ai-engineer-projects |
| 猎聘类智能体/MCP JD | 以当时在线 JD 为准（MCP、LangGraph、Skills、可观测为高频字段） |
| 学习计划正文 | [Agent中级开发工程师学习计划（终极攻略版）.md](./Agent中级开发工程师学习计划（终极攻略版）.md) |

---

## 11. 最终研判

1. **值得花 360 小时**：工程化 Agent + 可评测 RAG + MCP + 观测回归 —— 与 2026-07 招聘主需求对齐。  
2. **不值得花主线时间**：多框架集邮、重前端、训练微调、K8s 深度、AutoGen 深挖。  
3. **中高级差异化**：不是「也会 LangChain」，而是 **评测轨迹 + 成本账 + 安全边界 + 能讲清取舍的旗舰系统**。  
4. **执行纪律**：每周只完成路线图上最重要的一件可演示事；范围膨胀是转型失败的第一原因。

> 下一步：严格按更新后的学习计划推进仓库 `coding/projects/01`→`06`；每 4 周用本文 §7 矩阵自检是否在学 P3 垃圾时间。
