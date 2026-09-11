"""A small, runnable CAMEL ChatAgent example.

Run from the repository root:

    python3 -m my_camel_project.main "Explain what an AI agent is."

Without a question, the script starts an interactive chat.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType


def build_agent() -> ChatAgent:
    """Create a ChatAgent using an OpenAI-compatible model endpoint."""
    load_dotenv(Path(__file__).with_name(".env"))

    model_name = os.getenv("CAMEL_MODEL_TYPE", "gpt-4o-mini")
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv(
        "OPENAI_COMPATIBILITY_API_KEY"
    )
    base_url = os.getenv("OPENAI_API_BASE_URL") or os.getenv(
        "OPENAI_COMPATIBILITY_API_BASE_URL"
    )

    if not api_key:
        raise RuntimeError(
            "Missing API key. Set OPENAI_API_KEY in my_camel_project/.env."
        )

    model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
        model_type=model_name,
        api_key=api_key,
        url=base_url,
        model_config_dict={
            "temperature": float(os.getenv("CAMEL_TEMPERATURE", "0.2")),
        },
    )

    return ChatAgent(
        system_message=(
            "You are a helpful AI assistant. "
            "Answer clearly and concisely, and use Chinese when the user "
            "writes in Chinese."
        ),
        model=model,
    )


def ask(agent: ChatAgent, question: str) -> str:
    """Send one user message and return the assistant text."""
    response = agent.step(question)
    if response.msg is None or not response.msg.content:
        raise RuntimeError("The model returned an empty response.")
    return response.msg.content


def interactive_chat(agent: ChatAgent) -> None:
    """Keep the conversation alive until the user enters /exit or Ctrl-D."""
    print("CAMEL agent is ready. Enter /exit to quit.")
    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not question:
            continue
        if question.lower() in {"/exit", "/quit"}:
            return

        try:
            print(f"\nAgent: {ask(agent, question)}")
        except Exception as exc:
            print(f"\nRequest failed: {exc}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a CAMEL ChatAgent.")
    parser.add_argument(
        "question",
        nargs="?",
        help="Ask one question and exit; omit it for interactive chat.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    agent = build_agent()
    if args.question:
        print(ask(agent, args.question))
    else:
        interactive_chat(agent)


if __name__ == "__main__":
    main()
