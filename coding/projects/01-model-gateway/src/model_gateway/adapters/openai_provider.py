from model_gateway.adapters.openai_compat import OpenAICompatAdapter
from model_gateway.config import ProviderConfig, load_providers


# 这是 OpenAI 官方 API 的适配器 (Adapter)。
# 继承自 OpenAICompatAdapter，实际上就是让本地框架以兼容 OpenAI Chat Completions 接口的方式接入官方 openai-python 客户端，
# 一般用于国外网络/正式 API Key。中国环境下通常不配置，或者等有需要时再启用 Key。

class OpenAIProviderAdapter(OpenAICompatAdapter):
    """官方 OpenAI；国内环境可暂不配置 Key，后续再启用。"""

    def __init__(self, config: ProviderConfig | None = None) -> None:
        cfg = config or load_providers()["openai"]
        super().__init__(cfg)

# 你的问题很常见，其实技术上完全可以把 DeepSeekProviderAdapter 直接写在这个 openai_provider.py 里，
# 逻辑一样不会有任何影响：
#
# class DeepSeekProviderAdapter(OpenAICompatAdapter):
#     """
#     DeepSeek 适配器（可选）。
#     - 用于对接 DeepSeek 官方 API。
#     - 默认从配置文件或 .env 里加载 DeepSeek 配置（API Key、BaseUrl等）。
#     """
#     def __init__(self, config: ProviderConfig | None = None) -> None:
#         cfg = config or load_providers()["deepseek"]
#         super().__init__(cfg)
#
# 但是推荐单独写 deepseek.py（哪怕只是继承一行），有这些考虑：
# 1. 方便用 from ... import DeepSeekAdapter；adapter 结构更清晰。
# 2. 后续如果厂商参数、默认模型等特性有变，分文件可以让扩展更灵活，不会影响 openai_provider.py 本身的结构。
# （你说写在 DeepSeekProviderAdapter 里确实不会污染 OpenAIProviderAdapter 类逻辑，但混在一个文件里还是会影响该文件的清晰度）
# 3. 每个厂商适配器一个 py 文件便于维护和查找，不容易混淆（不容易超长或包含太多类）。
# 如果你真的在意全都挤在 openai_provider.py 省文件，也没技术障碍，只是多人协作、大工程建议分文件更优雅。