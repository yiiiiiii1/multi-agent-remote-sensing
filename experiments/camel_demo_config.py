"""Shared configuration for the CAMEL beginner demos (DeepSeek)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from camel.models import ModelFactory
from camel.types import ModelPlatformType

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - only used before optional setup
    load_dotenv = None


CAMEL_ROOT = Path(__file__).resolve().parents[2] / "clones" / "camel"
ENV_FILE = Path(__file__).with_name(".env")


@dataclass(frozen=True)
class DemoConfig:
    api_key: str
    base_url: str
    model: str


def load_demo_config() -> DemoConfig:
    """Load local .env first, then fall back to the current shell."""
    env_file = ENV_FILE if ENV_FILE.exists() else CAMEL_ROOT / ".env"
    if load_dotenv is not None:
        load_dotenv(env_file, override=False)

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "没有找到模型 API key。请把 DEEPSEEK_API_KEY=你的_API_KEY "
            f"写入 {env_file}，或先在终端设置 DEEPSEEK_API_KEY。"
        )

    return DemoConfig(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com"),
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    )


def create_model(config: DemoConfig):
    """Create one shared DeepSeek CAMEL model."""
    return ModelFactory.create(
        model_platform=ModelPlatformType.DEEPSEEK,
        model_type=config.model,
        api_key=config.api_key,
        url=config.base_url,
        timeout=180,
        max_retries=4,
    )
