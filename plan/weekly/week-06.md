# 第 6 周 · ReAct Agent（P3）

**日期**：2026-07-27 ~ 08-02  
**项目**：`coding/projects/03-react-agent`  
**周验收**：3 工具多步任务；能画状态流转图

---

## D36 · 周一 · 状态机设计

| 学习 30m | ReAct 论文；Think/Act/Observe |
| 编码 90m | `agent/state.py`：AgentState 枚举与字段 |
| 文档 30m | `notes/concepts/06-ReAct-Agent.md` + 手绘状态图拍照 |

## D37 · 周二 · Agent Loop 主循环

| 编码 120m | `agent_loop.py`：while 循环、解析 tool_call |
| 测试 45m | 单工具 1 步通过 |

## D38 · 周三 · Observation 回注

| 编码 120m | tool_result 消息格式；错误 observation 结构化 |
| 测试 45m | 工具失败时 loop 继续或退出 |

## D39 · 周四 · max_steps + 超时

| 编码 120m | `MAX_STEPS=10`；总超时 120s |
| 测试 45m | 故意死循环被截断 |

## D40 · 周五 · 死循环检测 + 熔断

| 学习 30m | 重复 tool+args 检测 |
| 编码 120m | `circuit_breaker.py` |
| 文档 30m | `notes/adr/002-agent-loop-safety.md` |

## D41 · 周六 · 三工具联调

| 编码 120m | 接入 P2 search_kb + read_file + calculator |
| 测试 45m | 「查 LangGraph 资料并总结」多步任务 |

## D42 · 周日 · 周复盘

| 文档 | `week-06-复盘.md`；`notes/projects/P3-总结.md` |
