"""CAMEL 入门 02：用官方 RolePlaying 跑真正的双智能体对话。

参考源码：clones/camel/examples/ai_society/role_playing.py

和 01 的区别：
- 01 是我们手动把一个 Agent 的输出喂给下一个，属于“流水线”。
- 02 用 CAMEL 内置的 RolePlaying 社会，AI User 和 AI Assistant
  会围绕同一个任务来回对话，直到任务完成或被终止。

两个角色：
- AI User（用户角色）：提出需求、给出反馈、推动任务前进。
- AI Assistant（助手角色）：负责实际产出。

任务指定 Agent（with_task_specify）会先把一句简单任务
扩展成更清晰的“指定任务提示词”，这也是官方示例的重点之一。
"""

from camel.societies import RolePlaying

from camel_demo_config import create_model, load_demo_config


def main() -> None:
    config = load_demo_config()
    print(f"模型：{config.model} | 地址：{config.base_url}")
    model = create_model(config)

    task_prompt = "为遥感影像变化检测设计一个多智能体协作方案"
    chat_turn_limit = 8

    session = RolePlaying(
        assistant_role_name="遥感算法工程师",
        assistant_agent_kwargs=dict(model=model),
        user_role_name="遥感应用研究员",
        user_agent_kwargs=dict(model=model),
        task_prompt=task_prompt,
        with_task_specify=True,
        task_specify_agent_kwargs=dict(model=model),
    )

    print("\n=== AI Assistant 系统提示 ===\n")
    print(session.assistant_sys_msg)
    print("\n=== AI User 系统提示 ===\n")
    print(session.user_sys_msg)

    print(f"\n=== 原始任务 ===\n{task_prompt}")
    print(f"\n=== 指定后的任务提示 ===\n{session.specified_task_prompt}")

    n = 0
    input_msg = session.init_chat()
    while n < chat_turn_limit:
        n += 1
        print(f"\n---------- 第 {n} 轮 ----------")
        assistant_response, user_response = session.step(input_msg)

        if assistant_response.terminated:
            reasons = assistant_response.info.get("termination_reasons")
            print(f"\nAI Assistant 结束，原因：{reasons}")
            break
        if user_response.terminated:
            reasons = user_response.info.get("termination_reasons")
            print(f"\nAI User 结束，原因：{reasons}")
            break

        print(f"\n[AI User]\n{user_response.msg.content}")
        print(f"\n[AI Assistant]\n{assistant_response.msg.content}")

        if "CAMEL_TASK_DONE" in (user_response.msg.content or ""):
            print("\n任务完成（AI User 标记了 CAMEL_TASK_DONE）。")
            break

        input_msg = assistant_response.msg


if __name__ == "__main__":
    main()
