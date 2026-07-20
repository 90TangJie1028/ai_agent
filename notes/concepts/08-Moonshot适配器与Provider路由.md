# Moonshot 第二适配器与 Provider 路由（D12）

## 一句话

DeepSeek / Kimi 都走 OpenAI 兼容协议；网关只换 `base_url` + `api_key` + `model`，调用形状不变。

## 和 DeepSeek 差在哪

| | DeepSeek | Moonshot（国内） |
|:---|:---|:---|
| Key | `DEEPSEEK_API_KEY` | `MOONSHOT_API_KEY` |
| base_url | `https://api.deepseek.com/v1` | `https://api.moonshot.cn/v1` |
| 默认模型 | `deepseek-chat` | `kimi-k2.6`（以 `/v1/models` 为准） |

协议层（`messages` / `tools` / `usage`）相同。就像 Cursor 换模型：对话面板不变，背后换引擎。

**差异**：Cursor 产品层封装切换；P1 要自己维护 `provider → Adapter` 字典。

## 代码里「路由」在哪

没有单独的 `ModelRouter` 类。实际就是：

1. `config.load_providers()`：有 Key 才进字典  
2. `ModelGateway._build_adapters()`：`{"deepseek": DeepSeekAdapter, "moonshot": MoonshotAdapter, ...}`  
3. `chat(..., provider="moonshot")`：查 `_adapters[name]` 再委托

```text
CLI --provider moonshot
  → gateway.chat(provider="moonshot")
  → MoonshotAdapter(OpenAICompatAdapter)
  → OpenAI(base_url=moonshot.cn).chat.completions.create(...)
```

`MoonshotAdapter` / `DeepSeekAdapter` 都是薄子类：只注入各自 `ProviderConfig`，真正发包在 `openai_compat.py`。

## 坑：模型名会下线

本账号 `/v1/models` 只返回 `kimi-k2.6`、`kimi-k2.7-code`。  
旧默认 `moonshot-v1-8k` → `NotFoundError`。

排查：

```powershell
# 或看平台文档；也可用脚本里的 load_providers + client.models.list()
python -m model_gateway.cli chat --provider moonshot --model kimi-k2.6 "你好"
```

`.env` 务必设：

```env
MOONSHOT_MODEL=kimi-k2.6
```

## 怎么验收

```powershell
cd coding/projects/01-model-gateway
python -m model_gateway.cli providers          # 应含 deepseek + moonshot
python scripts/d12_dual_provider_debug.py      # 同一 prompt 各一枪
pytest tests/test_moonshot_routing.py -v
pytest -m integration tests/test_moonshot_routing.py
```

## 和 D11 的关系

D11 证明 **同一 adapter** 上 FC 闭环能跑；D12 证明 **换 provider** 只改配置，不改 `chat` / `chat_with_tools` 主路径。D13 只收 **retry ≠ fallback** 概念（见 `09-Fallback降级链.md`），代码以后实操。
