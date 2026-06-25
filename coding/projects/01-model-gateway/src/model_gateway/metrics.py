"""调用指标（D5 实现）；本文件仅字段设计草案。"""

# CallRecord — 单次 chat 完整记录，供 bench / 成本聚合使用
#
# 字段设计：
#   provider: str           # 厂商 deepseek / moonshot / ...
#   model: str              # 实际模型名
#   prompt_tokens: int
#   completion_tokens: int
#   total_tokens: int
#   latency_ms: int         # 端到端耗时
#   cost_usd: float         # 按 pricing.yaml 折算
#   success: bool
#   error_type: str | None  # TimeoutError / RateLimitError / ...
#   timestamp: float        # time.time() 调用完成时刻
#
# GatewayResult — chat() 返回值包装（D5）
#   result: ChatResult
#   record: CallRecord
#
# MetricsCollector — 内存聚合，bench 结束时 dump JSON
#   records: list[CallRecord]
#   def add(record: CallRecord) -> None
#   def summary() -> dict  # success_rate, total_tokens, total_cost_usd, p95_latency_ms
