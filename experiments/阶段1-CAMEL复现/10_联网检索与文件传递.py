"""CAMEL 实验 10：联网检索真实数据 + Agent 之间用文件传递。

参考示例：
- clones/camel/examples/toolkits/search_toolkit.py（Tavily 搜索）
- clones/camel/examples/toolkits/file_toolkit.py（官方 FileToolkit）

设计（3 步，不跑太多轮）：
- 1 检索员：Tavily 联网搜索真实网页 + 文件工具 → 写 search_outputs/web_notes.md
- 2 分析员：文件工具                              → 读 web_notes.md，写 web_analysis.md
- 3 报告员：文件工具                              → 读 web_analysis.md，写 web_report.md

真实数据来自 Tavily 实时返回的标题 / URL / 摘要；文件在 Agent 间传递。
需要：.env 里有 TAVILY_API_KEY，且已安装 tavily-python。
"""

from __future__ import annotations

from pathlib import Path

from camel.agents import ChatAgent
from camel.toolkits import FileToolkit, SearchToolkit

from camel_demo_config import create_model, load_demo_config

OUTPUT_DIR = Path(__file__).with_name("search_outputs")
NOTES_MD = OUTPUT_DIR / "web_notes.md"
ANALYSIS_MD = OUTPUT_DIR / "web_analysis.md"
REPORT_MD = OUTPUT_DIR / "web_report.md"

TOPIC = "多智能体系统在遥感变化检测中的应用"


def print_tool_calls(response) -> None:
    calls = response.info.get("tool_calls") if response.info else None
    if not calls:
        print("  (本次没有调用工具)")
        return
    for call in calls:
        args = str(call.args)
        if len(args) > 300:
            args = args[:300] + " ..."
        result = str(call.result)
        if len(result) > 300:
            result = result[:300] + " ..."
        print(f"  - 调用工具：{call.tool_name}")
        print(f"    参数：{args}")
        print(f"    结果：{result}")


def main() -> None:
    config = load_demo_config()
    print(f"模型：{config.model} | 地址：{config.base_url}")
    model = create_model(config)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    search_toolkit = SearchToolkit()
    file_toolkit_a = FileToolkit(working_directory=str(OUTPUT_DIR))
    file_toolkit_b = FileToolkit(working_directory=str(OUTPUT_DIR))
    file_toolkit_c = FileToolkit(working_directory=str(OUTPUT_DIR))

    # 1 检索员：搜索 + 读写文件
    agent_search = ChatAgent(
        system_message=(
            "你是资料检索员。你必须用 search_tavily 工具上网搜索真实信息，"
            "不要凭记忆编造。"
            "请围绕主题做 2 到 3 次不同角度的搜索（每次取 3 条结果）。"
            "然后把每个结果整理进 web_notes.md，每条包含：标题、链接 URL、"
            "以及内容摘要。只使用工具返回的真实 URL，不要自己造链接。"
        ),
        model=model,
        tools=[search_toolkit.search_tavily, *file_toolkit_a.get_tools()],
    )

    # 2 分析员：只用文件工具，产出结构化对比表（不是叙述总结）
    agent_analysis = ChatAgent(
        system_message=(
            "你是分析员。请读取工作目录下的 web_notes.md，产出一份"
            "**结构化对比表**：对其中提到的每个系统/工作，抽取这些列："
            "系统名 | 年份 | 来源机构 | 方法 | 数据集或基准 | 报告结果(数字) | 来源URL。"
            "信息缺失就写“未提及”。\n"
            "另外附一张**来源可信度分级表**："
            "A=期刊全文，B=arXiv 预印本，C=官方文档/教程，D=新闻稿。\n"
            "只输出表格，不要写大段叙述性总结。把结果写入 web_analysis.md。"
        ),
        model=model,
        tools=file_toolkit_b.get_tools(),
    )

    # 3 报告员：只用文件工具，产出决策简报（不照抄表格）
    agent_report = ChatAgent(
        system_message=(
            "你是调研负责人。请读取工作目录下的 web_analysis.md，"
            "产出一份**决策简报**，面向“下一步该读什么、该怎么做”：\n"
            "1) 最该先读的 3-5 篇（按可信度与相关性排序，附链接）；\n"
            "2) 目前证据最充分的结论；\n"
            "3) 尚缺的信息 / 需要核实的点；\n"
            "4) 建议的下一步。\n"
            "不要重复罗列所有条目，也不要照抄表格。写入 web_report.md。"
        ),
        model=model,
        tools=file_toolkit_c.get_tools(),
    )

    print(f"\n主题：{TOPIC}")

    print("\n===== 步骤 1：检索员联网搜索（web_notes.md）=====")
    resp1 = agent_search.step(
        f"主题：{TOPIC}\n"
        "请先联网搜索 2-3 次，整理真实结果，写入 web_notes.md。"
        "文件名就用 web_notes.md（相对工作目录）。"
    )
    print(resp1.msgs[0].content)
    print_tool_calls(resp1)

    if not NOTES_MD.exists():
        print(f"\n[中断] 没有找到 {NOTES_MD}，检索员可能没有写文件。")
        print("请把上面的输出发我，我据此调整提示词。")
        return

    print("\n===== 步骤 2：分析员产出对比表（web_analysis.md）=====")
    resp2 = agent_analysis.step(
        "请读取 web_notes.md，产出一张系统对比表 + 一张来源可信度分级表，"
        "写入 web_analysis.md。不要写叙述性总结。"
    )
    print(resp2.msgs[0].content)
    print_tool_calls(resp2)

    if not ANALYSIS_MD.exists():
        print(f"\n[中断] 没有找到 {ANALYSIS_MD}，分析员可能没有写文件。")
        return

    print("\n===== 步骤 3：报告员产出决策简报（web_report.md）=====")
    resp3 = agent_report.step(
        "请读取 web_analysis.md，产出决策简报写入 web_report.md："
        "先读清单 + 证据结论 + 待核实项 + 下一步建议。不要照抄表格。"
    )
    print(resp3.msgs[0].content)
    print_tool_calls(resp3)

    print("\n===== 产物检查 =====")
    for path in (NOTES_MD, ANALYSIS_MD, REPORT_MD):
        status = "OK" if path.exists() else "缺失"
        size = path.stat().st_size if path.exists() else 0
        print(f"[{status}] {path.name}  ({size} 字节)")

    if REPORT_MD.exists():
        print("\n===== web_report.md 内容 =====")
        print(REPORT_MD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
