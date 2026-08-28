"""
Configuration for the Student Assistant.

All configuration comes from environment variables (loaded from a .env file
if present). Nothing is hard-coded — especially not API keys.

Copy .env.example to .env and fill in your values:
    OPENAI_API_KEY   your key (leave blank to run in offline MOCK mode)
    OPENAI_MODEL     e.g. gpt-4o-mini
    OPENAI_BASE_URL  optional, for OpenAI-compatible providers
"""

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; environment variables still work without it.
    pass


@dataclass
class Settings:
    openai_api_key: str | None
    openai_model: str
    openai_base_url: str | None
    academic_url: str
    math_url: str
    force_offline: bool

    @property
    def use_mock(self) -> bool:
        """Use the offline mock 'LLM' when forced, or when no API key is set."""
        return self.force_offline or not self.openai_api_key

    @property
    def mode(self) -> str:
        return "MOCK (offline, no API key needed)" if self.use_mock else \
               f"REAL (OpenAI-compatible, model={self.openai_model})"


def load_settings() -> Settings:
    force_offline = os.getenv("OFFLINE", "").strip().lower() in ("1", "true", "yes")
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_base_url=os.getenv("OPENAI_BASE_URL") or None,
        academic_url=os.getenv("ACADEMIC_MCP_URL", "http://127.0.0.1:8001/mcp"),
        math_url=os.getenv("MATH_MCP_URL", "http://127.0.0.1:8002/mcp"),
        force_offline=force_offline,
    )
