# 第 2 周 · Structured Output + Tools（P1 完结）

**日期**：2026-06-29 ~ 07-05  
**项目目录**：`coding/projects/01-model-gateway`  
**周验收**：双模型切换 + 工具调用 + 参数校验失败可捕获

---

## D8 · 周一 06-29 · Pydantic 结构化输出

| 学习 30m | Pydantic v2 `BaseModel`、`Field`、`model_json_schema()` |
| 编码 120m | `schemas.py`：`ChatRequest`、`StructuredAnswer`；`gateway.chat_structured()` |
| 测试 45m | schema 生成快照测试 |
| 文档 30m | `notes/concepts/04-结构化输出.md` |

---

## D9 · 周二 06-30 · JSON mode vs Structured Outputs

| 学习 30m | DeepSeek JSON 模式 / `response_format`；失败重试策略（OpenAI 文档可作参考） |
| 编码 120m | 对比实验脚本 `experiments/structured_vs_json.py` |
| 测试 45m | 同一 prompt 两种模式成功率对比表 |
| 文档 30m | 实验结论写入笔记 |

---

## D10 · 周三 07-01 · ToolRegistry

| 学习 30m | Function Calling 消息格式；tool / tool_result 角色 |
| 编码 120m | `tools/registry.py`：注册、JSON Schema 导出、`validate_args()` |
| 测试 45m | 非法参数抛 `ValidationError` |
| 文档 30m | 工具设计原则笔记 |

---

## D11 · 周四 07-02 · 计算器工具端到端 ✅

| 学习 30m | Function Calling 消息格式；DeepSeek tool_calls 字段 |
| 编码 120m | `tools/calculator.py`；`gateway.chat_with_tools()` 闭环（默认 DeepSeek） |
| 测试 45m | 「123 * 456」工具调用 E2E |
| 文档 30m | 更新 P1 README CLI：`tools calc` |

**产物**：`calculator.py` + `chat_with_tools` + `scripts/d11_chat_with_tools_debug.py`；笔记 `07-Function-Calling消息格式.md`

---

## D12 · 周五 07-03 · Kimi / Moonshot 第二适配器 ✅

| 学习 30m | Moonshot API 与 DeepSeek 差异（base_url、模型名） |
| 编码 120m | `adapters/moonshot.py`；`ModelRouter` 按 provider 路由 |
| 测试 45m | 同一 prompt 在 deepseek / moonshot 各调 1 次（integration） |
| 文档 30m | `.env.example` 补充 MOONSHOT 字段 |

**产物**：默认模型 `kimi-k2.6`；`tests/test_moonshot_routing.py` + `scripts/d12_dual_provider_debug.py`；笔记 `08-Moonshot适配器与Provider路由.md` |

---

## D13 · 周六 07-04 · 通义 + 降级（可选）

| 学习 30m | DashScope OpenAI 兼容接口 |
| 编码 90m | `adapters/dashscope` 或复用 `OpenAICompatAdapter` |
| 编码 30m | DeepSeek 失败时 fallback 到 moonshot / dashscope |
| 测试 45m | mock 主模型失败走 fallback |
| 文档 30m | `notes/projects/P1-总结.md` 初稿 |

---

## D14 · 周日 07-05 · P1 收尾复盘

| 学习 30m | 预习 RAG 概念：embedding、chunk |
| 编码 60m | P1 代码审查、type hint 补全 |
| 测试 45m | 全量 pytest；`p1-v0.1.0` tag |
| 文档 90m | `week-02-复盘.md`；P1 总结定稿 |
| 计划 15m | 周一：创建 P2 项目骨架 |

**周验收**：
- [ ] DeepSeek + Moonshot（或通义）双模型可切换
- [ ] 工具参数错误可捕获
- [ ] P1 README 完整
