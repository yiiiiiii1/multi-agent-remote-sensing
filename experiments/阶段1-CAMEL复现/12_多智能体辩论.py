"""CAMEL 实验 12：多智能体辩论（对抗场景）。

参考：
- clones/camel/examples/ai_society/role_playing.py（官方 RolePlaying 用法）
- clones/camel/docs/key_modules/societies.md（AI User 负责 "instruct or
  challenge"，AI Assistant 负责产出）
- 列表里提到的 role_playing_with_critic.py（因 DeepSeek 只支持 n=1，
  官方 critic 的多候选择优不可用，这里改为「正反方辩论 + 裁判」）

角色：
- AI Assistant = 正方辩手（支持辩题）
- AI User      = 反方辩手（反对辩题，负责 challenge）
- 裁判          = 额外一个 ChatAgent，最后中立汇总
"""

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.societies import RolePlaying

from camel_demo_config import create_model, load_demo_config

TOPIC = "多智能体系统是否适合落地到遥感应用"
CHAT_TURN_LIMIT = 3


def format_transcript(transcript) -> str:
    if not transcript:
        return "（暂无发言）"
    return "\n\n".join(f"【{speaker}】\n{text}" for speaker, text in transcript)


def main() -> None:
    config = load_demo_config()
    print(f"模型：{config.model} | 地址：{config.base_url}")
    model = create_model(config)

    session = RolePlaying(
        assistant_role_name="正方辩手（支持该观点）",
        assistant_agent_kwargs=dict(model=model),
        user_role_name="反方辩手（反对该观点）",
        user_agent_kwargs=dict(model=model),
        task_prompt=(
            f"就辩题「{TOPIC}」展开辩论：正方支持，反方反对，"
            "双方都必须针对对方的发言进行反驳，并给出具体理由或例子。"
        ),
        with_task_specify=True,
        task_specify_agent_kwargs=dict(model=model),
    )

    print("\n=== 正方系统提示 ===\n")
    print(session.assistant_sys_msg)
    print("\n=== 反方系统提示 ===\n")
    print(session.user_sys_msg)
    print(f"\n=== 指定后的任务 ===\n{session.specified_task_prompt}")

    transcript = []
    n = 0
    input_msg = session.init_chat()
    print(f"\n辩题：{TOPIC}\n")

    while n < CHAT_TURN_LIMIT:
        n += 1
        print(f"\n---------- 第 {n} 轮 ----------")
        assistant_response, user_response = session.step(input_msg)

        if assistant_response.terminated:
            reasons = assistant_response.info.get("termination_reasons")
            print(f"\n正方结束，原因：{reasons}")
            break
        if user_response.terminated:
            reasons = user_response.info.get("termination_reasons")
            print(f"\n反方结束，原因：{reasons}")
            break

        print(f"\n[反方（AI User）]\n{user_response.msg.content}")
        print(f"\n[正方（AI Assistant）]\n{assistant_response.msg.content}")
        transcript.append(("反方", user_response.msg.content or ""))
        transcript.append(("正方", assistant_response.msg.content or ""))

        if "CAMEL_TASK_DONE" in (user_response.msg.content or ""):
            print("\n反方标记了 CAMEL_TASK_DONE，辩论提前结束。")
            break

        input_msg = assistant_response.msg

    judge = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="裁判",
            content=(
                "你是中立裁判，不站队。只根据双方实际发言做总结，"
                "不引入双方都没提到的论据，并明确区分共识与分歧。"
            ),
        ),
        model=model,
    )
    judge_prompt = (
        f"辩题：{TOPIC}\n\n"
        f"完整辩论记录：\n{format_transcript(transcript)}\n\n"
        "请作为裁判输出：\n"
        "1. 正方核心论点（2-3 条）\n"
        "2. 反方核心论点（2-3 条）\n"
        "3. 双方共识\n"
        "4. 仍存分歧\n"
        "5. 你的最终判断与理由"
    )
    print("\n===== 裁判总结 =====")
    judge_response = judge.step(judge_prompt)
    verdict = judge_response.msgs[0].content if judge_response.msgs else ""
    print(f"\n[裁判]\n{verdict}")

    print("\n===== 简要统计 =====")
    print(f"辩论轮数：{n}")
    print(f"发言条数：{len(transcript)}")
    print(f"裁判总结长度：{len(verdict)} 字")


if __name__ == "__main__":
    main()
