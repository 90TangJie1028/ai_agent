"""D12 学习：同一 prompt 在 DeepSeek / Moonshot 各打一枪（可断点走查）。

运行（需 .env 里 DEEPSEEK_API_KEY + MOONSHOT_API_KEY）:

    cd coding/projects/01-model-gateway
    ..\\..\\..\\.venv\\Scripts\\python.exe scripts/d12_dual_provider_debug.py

重点看:
  1. load_providers() 各自的 base_url / default_model
  2. gateway._adapters 字典里有 deepseek / moonshot
  3. chat(..., provider=...) 只换路由名，不换协议
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from model_gateway.config import load_providers
from model_gateway.gateway import ModelGateway

PROMPT = "只回复两个字：收到"
PROVIDERS = ("deepseek", "moonshot")


def main() -> None:
    configs = load_providers()
    print("已配置 providers:")
    for name in PROVIDERS:
        if name not in configs:
            raise SystemExit(f"未配置 {name.upper()}_API_KEY，请检查仓库根目录 .env")
        cfg = configs[name]
        print(f"  {name}: base_url={cfg.base_url}  model={cfg.default_model}")

    gateway = ModelGateway()
    print(f"\navailable_providers={gateway.available_providers}")
    print(f"adapters={sorted(gateway._adapters.keys())}")  # noqa: SLF001

    print(f"\nprompt={PROMPT!r}\n")
    for name in PROVIDERS:
        # 断点：看 name / adapter.provider / ChatResult
        gw = gateway.chat(PROMPT, provider=name)
        if gw.result is None:
            print(f"[{name}] FAIL  {gw.record.error_type}: {gw.record.error_message}")
            continue
        r = gw.result
        print(
            f"[{name}] OK  model={r.model}  "
            f"content={r.content!r}  "
            f"tokens={r.total_tokens}  latency={r.latency_ms}ms  "
            f"cost=${gw.record.cost_usd:.6f}"
        )


if __name__ == "__main__":
    main()
