from model_gateway.adapters.openai_compat import OpenAICompatAdapter
from model_gateway.config import ProviderConfig, load_providers


class MoonshotAdapter(OpenAICompatAdapter):
    """Kimi / 月之暗面 Moonshot API。"""

    def __init__(self, config: ProviderConfig | None = None) -> None:
        cfg = config or load_providers()["moonshot"]
        super().__init__(cfg)
