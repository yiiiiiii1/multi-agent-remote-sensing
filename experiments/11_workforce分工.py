"""CAMEL 实验 11：Workforce 多智能体自动分工。

参考：clones/camel/examples/workforce/multiple_single_agents.py

要点：
- 建 3 个纯对话 worker（不接工具）；
- 用 Workforce 的 AUTO_DECOMPOSE 模式，让协调者自动把任务拆开、派给 worker；
- 跑完打印日志树与 KPI，并把详细日志落盘。
"""

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.societies.workforce import Workforce
from camel.tasks import Task

from camel_demo_config import create_model, load_demo_config


def build_worker(role_name: str, content: str, model) -> ChatAgent:
    return ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name=role_name, content=content
        ),
        model=model,
    )


def main() -> None:
    config = load_demo_config()
    print(f"模型：{config.model} | 地址：{config.base_url}")
    model = create_model(config)

    researcher = build_worker(
        "检索员",
        "你是资料检索员。请围绕给定主题，快速梳理出关键概念、"
        "代表性方向与要点清单，条理清晰，不编造具体文献。",
        model,
    )
    analyst = build_worker(
        "分析员",
        "你是分析员。请基于既有材料，提炼核心结论、技术路线、"
        "主要争议与尚未解决的问题，指出不确定之处。",
        model,
    )
    writer = build_worker(
        "写作者",
        "你是报告写作者。请把前面的检索与分析整合成一份简明、"
        "结构化的中文报告，突出结论与限制。",
        model,
    )

    workforce = Workforce("遥感多智能体调研团队", default_model=model)
    workforce.add_single_agent_worker(
        "检索员：梳理主题关键概念与要点", worker=researcher
    )
    workforce.add_single_agent_worker(
        "分析员：分析要点、提炼结论与争议", worker=analyst
    )
    workforce.add_single_agent_worker(
        "写作者：汇总成结构化报告", worker=writer
    )

    task = Task(
        content=(
            "调研「多智能体系统在遥感变化检测中的应用」。需要覆盖："
            "1. 遥感变化检测的核心任务与难点；"
            "2. 多智能体系统能提供哪些能力；"
            "3. 现有结合方式与主要挑战；"
            "最后汇总成一份简明报告。"
        ),
        id="0",
    )

    print("\n=== 开始处理任务 ===\n")
    result = workforce.process_task(task)

    print("\n=== 最终结果 ===\n")
    print(result.result)

    print("\n=== Workforce 日志树 ===\n")
    print(workforce.get_workforce_log_tree())

    print("\n=== Workforce KPIs ===\n")
    for key, value in workforce.get_workforce_kpis().items():
        print(f"{key}: {value}")

    log_path = "11_workforce_logs.json"
    workforce.dump_workforce_logs(log_path)
    print(f"\n详细日志已保存到 {log_path}")


if __name__ == "__main__":
    main()
