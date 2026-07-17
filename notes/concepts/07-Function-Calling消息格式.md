# Function Calling / Tool Calls（D10 速查）

复习用。核心在代码：`tools/registry.py` → D11 `chat_with_tools`。

## 一句话

模型**可以**在答用户之前，先声明「我要调哪个工具、参数是什么」；**你本地执行**工具，把结果用 `role=tool` 塞回对话；模型再根据结果生成最终回答。信息越准，回答通常越准——但前提是 Schema 对、校验过、历史消息完整。

## 和你直觉的对齐（纠一点）

| 你的理解 | 更精确的说法 |
|:---|:---|
| 得出答案前调用工具查信息 | **多数时候是**；模型也可能直接答（不调工具） |
| 调用 agent 的工具 | 今天是 **function tools**；完整 Agent Loop 是第 6 周 |
| 汇总给模型再答 | ✅：`assistant(tool_calls)` + `tool(结果)` 再请求一轮 |
| 信息越准答案越准 | ✅；所以参数必须 **validate**，不能信模型瞎编的 JSON |

## 消息闭环（只记形状）

```text
① 请求：messages=[user] + tools=[工具定义]
② 响应：assistant + tool_calls[{id, name, arguments}]
③ 本地：按 name 找工具 → validate_args → 执行（D11）
④ 再请求：messages 追加 assistant 消息 + {role:tool, tool_call_id, content}
⑤ 响应：assistant.content = 最终自然语言答案
```

最小字段：

| 位置 | 关键字段 |
|:---|:---|
| 请求 `tools[]` | `type=function`，`function.name/description/parameters` |
| 响应 `tool_calls[]` | `id`，`function.name`，`function.arguments`（**字符串**） |
| 回传 `role=tool` | `tool_call_id`（对上 id），`content`（工具结果文本） |

官方示例：[DeepSeek Tool Calls](https://api-docs.deepseek.com/guides/tool_calls)

## 和 D8/D9 的关系

```text
StructuredAnswer.model_json_schema()  → 约束「模型说什么」
ToolRegistry → args_model.model_json_schema() → 约束「模型调工具时传什么」
```

两边最后都要 **Pydantic validate**。文档也写了：`arguments` 可能不是合法 JSON，也可能多出未定义字段。

## Registry 在链路里干什么（D10）

```text
注册 name + description + args_model
    → to_openai_tools()  生成请求里的 tools=
    → validate_args()    校验模型吐出的 arguments
执行 handler             → D11，今天可先留空或占位
```

## 类比

| 概念 | TS / C++ |
|:---|:---|
| `tools` 目录 | 可调用 API 签名表 |
| `tool_calls` | 一次 RPC 请求（name + args） |
| `role=tool` | RPC 响应；`tool_call_id` 像关联 ID |
| 差异 | 参数是模型生成的字符串，**无编译期保证** |

## Debug 入口

```powershell
cd coding\projects\01-model-gateway
pytest tests\test_tool_registry.py -q
```
