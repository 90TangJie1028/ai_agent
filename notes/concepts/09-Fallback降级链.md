# Fallback 降级链（D13 精华）

## 一句话

**Retry** 换时间（同一 provider 再试）；**Fallback** 换引擎（换 provider）。通义适配与 D12 同构，本日记概念，代码以后实操。

## Retry vs Fallback

| | Retry（D3） | Fallback（D13） |
|:---|:---|:---|
| 换什么 | 不换 provider | 换 provider |
| 适合 | 429、短暂 5xx、网络抖 | 厂商挂了、重试耗尽、模型下线 |
| 本仓库 | `retry.py` | 尚未实现；加在 `gateway.chat` 外包一层即可 |

就像 Cursor：同一模型可自动再试；模型/厂商不可用则换模型——后者是 fallback。

**差异**：Cursor 藏在产品层；P1 要自己定链顺序和「何种错误才切」。

## 只记 3 条设计

1. **链要显式**：`primary → [moonshot, dashscope]`，环境变量或构造参数，别写死业务。
2. **只有厂商级可恢复失败才切**：连接失败 / 5xx / 超时耗尽 → 可 fallback；**400 参数错 / 401 / ValidationError** → 不切（换了多半还错，还掩盖根因）。
3. **观测要看见切过谁**：最终 `CallRecord.provider` 是成功的那个；进阶记 `tried=[...]`。

## 为何 FC 闭环先不做 fallback

- **单次 `chat`**：无中间状态，整句换厂商即可。
- **FC 闭环**：多轮 API + 本地工具 + `messages` 已绑某一厂商；中途换引擎是半截对话换引擎，难在**有状态**，不是「工具能力不足」。

工具弱 / 结果差 → Agent 能力与策略问题；厂商降级 → 可用性问题。两轴别混。

## 通义（刻意跳过）

DashScope 兼容模式 = 另一套 `base_url` + Key + 模型；`config` / `_build_adapters` 已接好。填 `DASHSCOPE_API_KEY` 即用，无新概念。

## 以后实操最小形状

```text
for name in [primary, *fallback_chain]:
    未配置 → skip
    gw = 调该 adapter
    成功 → return（record.provider = name）
return 最后一次失败
```

验收：mock 主失败、备成功 → 断言最终走备。

## 自测

1. 429 先 retry 还是 fallback？→ **retry**
2. 非法 `response_format` 得 400，切 moonshot 吗？→ **不切**
3. 为何 FC 闭环比单次 chat 更难 fallback？→ **messages 有中间状态，半截换引擎**
