"""Lab-01：用 DeepSeek 完成第一次 LLM API 调用。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# 加载仓库根目录 .env
ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")


def main() -> None:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print("请先在 .env 中配置 DEEPSEEK_API_KEY")
        print("参考: .env.example")
        sys.exit(1)

    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    )
    model = os.getenv("DEFAULT_MODEL", "deepseek-chat")

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "介绍一下湖北省武穴市。"}],
    )

    message = response.choices[0].message.content
    usage = response.usage

    print("模型回复:")
    print(message)
    print()
    if usage:
        print(
            f"tokens: total={usage.total_tokens}, "
            f"prompt={usage.prompt_tokens}, completion={usage.completion_tokens}"
        )


if __name__ == "__main__":
    main()
