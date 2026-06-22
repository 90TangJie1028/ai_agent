from model_gateway.adapters.openai_compat import OpenAICompatAdapter
from model_gateway.config import ProviderConfig, load_providers


class DeepSeekAdapter(OpenAICompatAdapter):
    def __init__(self, config: ProviderConfig | None = None) -> None:
        cfg = config or load_providers()["deepseek"]
        super().__init__(cfg)
