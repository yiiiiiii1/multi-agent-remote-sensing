import os
from pathlib import Path

from dotenv import load_dotenv
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType

print("1. 开始加载环境变量")
load_dotenv(Path(__file__).with_name(".env"))

api_key = os.getenv("OPENAI_COMPATIBILITY_API_KEY") or os.getenv(
    "OPENAI_API_KEY"
)
base_url = os.getenv("OPENAI_COMPATIBILITY_API_BASE_URL") or os.getenv(
    "OPENAI_API_BASE_URL"
)
model_name = os.getenv("CAMEL_MODEL_TYPE", "gpt-4o-mini")
timeout = float(os.getenv("MODEL_TIMEOUT", "60"))

if not api_key:
    raise RuntimeError(
        "没有找到 API key，请在 my_camel_project/.env 中设置 "
        "OPENAI_API_KEY 或 OPENAI_COMPATIBILITY_API_KEY。"
    )
if not base_url:
    raise RuntimeError(
        "没有找到 API 地址，请在 my_camel_project/.env 中设置 "
        "OPENAI_API_BASE_URL。"
    )

print("2. 开始创建模型")
print(f"模型：{model_name}")
print(f"地址：{base_url}")
print(f"单次超时：{timeout:g} 秒")
model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type=model_name,
    url=base_url,
    api_key=api_key,
    model_config_dict={},
    timeout=timeout,
    max_retries=0,
    api_mode=os.getenv("CAMEL_API_MODE", "responses"),
)
print("3. 开始创建 Agent")
agent = ChatAgent(
    system_message="You are a helpful assistant.",
    model=model,
)

print("4. 开始请求 API")
response = agent.step("用一句话介绍 CAMEL。")

print("5. 收到结果")
print(response.msg.content)
