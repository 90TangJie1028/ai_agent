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

## D11 走读：用户问「123 * 456」

下面每一步都是**真实会进 API 的形状**。`chat_with_tools` 要做的事，就是按这个顺序拼 / 拆这些对象。

### 第 1 次请求（你 → API）

`tools` 来自 `registry.to_openai_tools()`；`messages` 只有用户那一句。

```json
{
  "model": "deepseek-chat",
  "messages": [
    { "role": "user", "content": "请计算 123 * 456" }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression.",
        "parameters": {
          "type": "object",
          "properties": {
            "expression": {
              "type": "string",
              "description": "arithmetic expression",
              "minLength": 1
            }
          },
          "required": ["expression"]
        }
      }
    }
  ]
}
```

要点：

- `tools` 是**目录**（能调什么），不是这次要调哪个
- `tool_choice` 默认 `auto`：模型可调可不调；D11 先不管强制调用

### 第 1 次响应（API → 你）

模型决定用工具时，`finish_reason` 常为 `tool_calls`；正文可能为空。

```json
{
  "choices": [
    {
      "finish_reason": "tool_calls",
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "calculator",
              "arguments": "{\"expression\": \"123 * 456\"}"
            }
          }
        ]
      }
    }
  ]
}
```

务必盯住的三个坑：

| 字段 | 真相 |
|:---|:---|
| `arguments` | **字符串**，不是对象；要 `json.loads` 再 `validate_args` |
| `id` | 后面 `role=tool` 的 `tool_call_id` 必须对上这个 |
| `content` | 可能是 `null`；有 tool_calls 时别指望这里有答案 |

文档原话：模型**不保证**合法 JSON，也可能多出 Schema 里没有的字段 → 所以才有 D10 的 `validate_args`。

### 本地执行（你，不调 API）

```text
name = tool_calls[0].function.name          # "calculator"
raw  = tool_calls[0].function.arguments     # '{"expression":"123 * 456"}'
result = registry.call(name, raw)           # → 56088（或 "56088"）
```

类比：像 Cocos 里收到自定义事件 → 按事件名找监听 → 校验 payload → 执行；API 只负责「宣告要调」，**真正算数的是你本地**。

### 第 2 次请求（你 → API）

历史要**完整**：user → assistant(带 tool_calls) → tool(结果)。缺任何一段，模型对不上上下文。

```json
{
  "model": "deepseek-chat",
  "messages": [
    { "role": "user", "content": "请计算 123 * 456" },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call_abc123",
          "type": "function",
          "function": {
            "name": "calculator",
            "arguments": "{\"expression\": \"123 * 456\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "call_abc123",
      "content": "56088"
    }
  ],
  "tools": [ "……同上，通常仍带上……" ]
}
```

要点：

- 追加的是**整条** assistant 消息（含 `tool_calls`），不是只塞一段摘要
- `role=tool` 用 `tool_call_id`，不是 `name`（name 已在上一轮 assistant 里）
- `content` 一般是字符串（数字也转成 `"56088"`）

### 第 2 次响应（API → 你）

```json
{
  "choices": [
    {
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "123 × 456 = 56088",
        "tool_calls": null
      }
    }
  ]
}
```

这时 `chat_with_tools` 可以把 `content` 当作最终答案返回。

### 和普通 `chat()` 差在哪（写代码时的心智）

```text
普通 chat:     messages = [user 一句话]     → content 字符串
带工具闭环:   messages 会变长            → 中间可能先拿到 tool_calls
适配器要改:   不能只收 message:str；要能传 messages + tools，并吐出 tool_calls
```

### 自检题（不看答案先想）

1. 为什么第 2 次请求还要把第 1 次的 `assistant.tool_calls` 原样 append？  
2. `arguments` 若是 `"{expression: 123}"`（非法 JSON），应在哪一层失败？  
3. 模型若直接答 `"56088"` 且没有 `tool_calls`，闭环该怎么结束？

<details>
<summary>参考答案</summary>

1. API 协议要求：每个 `role=tool` 必须对应某次 assistant 声明的 `tool_call_id`；缺了 assistant 那条，关联断了。  
2. `registry.validate_args`（或 `call` 内部）→ `ValidationError`；不要让非法参数进 handler。  
3. 没有 tool_calls 就当普通回复，直接返回 `content`（`tool_choice=auto` 时合法）。

</details>

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

## calculator 本地实现（D11 · B）

- `eval_safe`：用 `ast` 白名单求值，**禁止**裸 `eval`（否则模型若塞 `__import__...` 就成任意代码执行）
- 对外契约名固定 `calculator`；本地函数可叫 `run_calculator` / `eval_safe`
- Cursor 对照：Agent 选 `Shell` 只是宣告；真正跑命令的是 IDE——同理，模型选 `calculator`，算数在你进程里

## chat_with_tools 闭环（D11 · C）

```text
gateway.chat_with_tools
  → adapter.chat_messages(messages, tools=...)
  → 若有 tool_calls：registry.call → append assistant + role=tool
  → 再 chat_messages → 最终 content
```

| 模块 | 职责 |
|:---|:---|
| `ChatResult.tool_calls` / `to_assistant_message()` | 把 API 形状带回 messages |
| `OpenAICompatAdapter.chat_messages` | 真 API：传 messages + tools，解析 tool_calls |
| `MockAdapter.chat_messages` | 离线两轮：先 tool_calls，再读 role=tool 拼答案 |
| `ModelGateway.chat_with_tools` | 串起闭环；`max_tool_rounds=1` |

Cursor 对照：你聊天里看到的「调用 Shell → 输出 → 继续写」就是这个循环；差异是 Cursor 产品封装了多轮，P1 在 `gateway.py` 里手写。

```powershell
cd coding\projects\01-model-gateway
pytest tests\test_calculator.py tests\test_chat_with_tools.py -q
python -m model_gateway.cli tools calc "123 * 456" --provider mock
```

## Debug 入口

```powershell
cd coding\projects\01-model-gateway
pytest tests\test_tool_registry.py -q
```
