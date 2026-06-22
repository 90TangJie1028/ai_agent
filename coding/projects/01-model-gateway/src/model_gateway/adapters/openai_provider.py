from model_gateway.adapters.openai_compat import OpenAICompatAdapter
from model_gateway.config import ProviderConfig, load_providers


class OpenAIProviderAdapter(OpenAICompatAdapter):
    """官方 OpenAI；国内环境可暂不配置 Key，后续再启用。"""

    def __init__(self, config: ProviderConfig | None = None) -> None:
        cfg = config or load_providers()["openai"]
        super().__init__(cfg)
