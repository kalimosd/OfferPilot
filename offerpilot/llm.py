"""LLM initialization with multi-provider support."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@lru_cache(maxsize=1)
def get_llm():
    """Return a ChatModel instance based on environment config.

    Supports any provider via langchain's init_chat_model:
      - OFFERPILOT_MODEL=deepseek-chat  (needs OFFERPILOT_API_KEY + OFFERPILOT_BASE_URL)
      - OFFERPILOT_MODEL=claude-sonnet-4-20250514  (needs ANTHROPIC_API_KEY)
      - OFFERPILOT_MODEL=gemini-2.0-flash  (needs GOOGLE_API_KEY)
      - OFFERPILOT_MODEL=gpt-4o-mini  (needs OPENAI_API_KEY)
    """
    from langchain.chat_models import init_chat_model

    model = os.environ.get("OFFERPILOT_MODEL", "deepseek-chat")
    api_key = os.environ.get("OFFERPILOT_API_KEY") or os.environ.get("DEEPSEEK_API_KEY", "")
    base_url = os.environ.get("OFFERPILOT_BASE_URL", "")

    # DeepSeek or other OpenAI-compatible APIs with custom base_url
    if base_url or _is_openai_compatible(model):
        if not base_url and model.startswith("deepseek"):
            base_url = "https://api.deepseek.com"
        kwargs = {"api_key": api_key, "base_url": base_url} if api_key else {}
        return init_chat_model(model, model_provider="openai", **kwargs)

    # Native providers — they read their own env vars (ANTHROPIC_API_KEY, etc.)
    return init_chat_model(model)


def _is_openai_compatible(model: str) -> bool:
    return any(model.startswith(p) for p in ("deepseek", "qwen", "yi-", "glm"))
