"""CAMEL 入门：手动串联研究员、审稿人和整合者。

这个文件故意不使用复杂的 Workforce。
先把“消息从一个 Agent 传给另一个 Agent”看清楚，再学习自动编排。
"""

from camel.agents import ChatAgent
from openai import APIConnectionError, APIStatusError

from camel_demo_config import create_model, load_demo_config


def ask(agent: ChatAgent, prompt: str) -> str:
    """向 Agent 发送一次消息，并取出文本回答。"""
    try:
        response = agent.step(prompt)
        return response.msgs[0].content
    except APIStatusError as exc:
        if exc.status_code >= 500:
            raise RuntimeError(
                f"模型服务暂时不可用（HTTP {exc.status_code}）。"
                "请稍等几十秒后重新运行；如果持续失败，检查 .env 中的"
                " DEEPSEEK_MODEL。"
            ) from exc
        raise RuntimeError(
            f"模型请求失败（HTTP {exc.status_code}）。"
            "请检查 API key、模型名和接口地址。"
        ) from exc
    except APIConnectionError as exc:
        raise RuntimeError(
            "无法连接模型接口。请检查网络、代理和 LINKAGI_API_BASE_URL。"
        ) from exc


def main() -> None:
    config = load_demo_config()
    print(f"模型：{config.model} | 地址：{config.base_url}")
    model = create_model(config)

    researcher = ChatAgent(
        system_message=(
            "你是一名研究助理。请围绕用户问题给出结构化分析，"
            "明确区分事实、推测和不确定之处。不要为了显得完整而编造引用。"
        ),
        model=model,
        retry_attempts=4,
        retry_delay=2.0,
    )

    reviewer = ChatAgent(
        system_message=(
            "你是一名严格的同行评审员。你会检查另一名研究助理的回答，"
            "寻找逻辑漏洞、未经支持的结论、遗漏的反例和概念混淆。"
            "请提出具体修改建议，而不是只说‘很好’。"
        ),
        model=model,
        retry_attempts=4,
        retry_delay=2.0,
    )

    synthesizer = ChatAgent(
        system_message=(
            "你是一名负责最终定稿的研究负责人。请综合原始分析和审稿意见，"
            "给出准确、简洁、适合初学者理解的结论。不要隐藏不确定性。"
        ),
        model=model,
        retry_attempts=4,
        retry_delay=2.0,
    )

    question = "多智能体系统为什么可能比单智能体更强？什么时候反而更差？"

    research = ask(
        researcher,
        f"请研究并回答这个问题：{question}\n"
        "请用三个部分组织：可能的优势、可能的失败原因、如何验证。",
    )
    print("\n=== 研究员 Agent ===\n")
    print(research)

    review = ask(
        reviewer,
        f"请审查下面这份分析。\n\n"
        f"原问题：{question}\n\n"
        f"研究员的分析：\n{research}",
    )
    print("\n=== 审稿人 Agent ===\n")
    print(review)

    final = ask(
        synthesizer,
        f"请根据原始分析和审稿意见，写出一份简洁、谨慎的最终回答。\n\n"
        f"原始分析：\n{research}\n\n"
        f"审稿意见：\n{review}\n\n"
        "要求：保留有依据的观点，修正明显问题，并列出仍然不确定的地方。",
    )
    print("\n=== 最终整合结果 ===\n")
    print(final)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(f"\n运行失败：{exc}")
        raise SystemExit(1)
