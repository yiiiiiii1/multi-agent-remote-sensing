"""Shared configuration for the CAMEL beginner demos (DeepSeek)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from camel.models import ModelFactory
from camel.types import ModelPlatformType

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - only used before optional setup
    load_dotenv = None


ENV_FILE = Path(__file__).with_name(".env")

# 先把本地 .env 读进来（其中可能包含 CAMEL_ROOT）。
if load_dotenv is not None:
    load_dotenv(ENV_FILE, override=False)


def resolve_camel_root() -> Optional[Path]:
    """定位 CAMEL 源码克隆目录。

    顺序：
      1. 环境变量 CAMEL_ROOT（可写在 .env 或终端里）；
      2. 相对本文件向上几层的常见位置；
      3. home 目录下的常见位置。
    找到含 ``camel/__init__.py`` 的目录即返回。
    """
    candidates = []

    env_root = os.getenv("CAMEL_ROOT")
    if env_root:
        candidates.append(Path(env_root).expanduser())

    here = Path(__file__).resolve()
    for parent in here.parents[:4]:
        candidates.append(parent / "clones" / "camel")

    candidates += [
        Path.home() / "Documents" / "Code" / "clones" / "camel",
        Path.home() / "clones" / "camel",
    ]

    for candidate in candidates:
        if (candidate / "camel" / "__init__.py").exists():
            return candidate
    return None


CAMEL_ROOT = resolve_camel_root()


@dataclass(frozen=True)
class DemoConfig:
    api_key: str
    base_url: str
    model: str


def load_demo_config() -> DemoConfig:
    """Load local .env first, then fall back to the current shell."""
    env_file = ENV_FILE
    if not env_file.exists() and CAMEL_ROOT is not None:
        env_file = CAMEL_ROOT / ".env"
    if load_dotenv is not None:
        load_dotenv(env_file, override=False)

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "没有找到模型 API key。请把 DEEPSEEK_API_KEY=你的_API_KEY "
            f"写入 {ENV_FILE}，或先在终端设置 DEEPSEEK_API_KEY。"
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
