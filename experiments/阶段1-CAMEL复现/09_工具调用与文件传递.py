"""CAMEL 实验 09：不同 Agent 调用不同工具，并通过文件传递结果。

参考示例：
- clones/camel/examples/toolkits/function_tool_example.py（自定义工具 @tool）
- clones/camel/examples/toolkits/file_toolkit.py（官方 FileToolkit）

设计（3 步，不跑太多轮）：
- A 数据生成员：自定义工具 create_rainfall_dataset → 写出 rainfall.csv
- B 数据分析员：自定义工具 analyze_rainfall        → 读 CSV、写出 analysis.md
- C 报告撰写员：官方 FileToolkit                    → 读 analysis.md、写出 report.md

Agent 之间不只传文本：A→B 传 rainfall.csv，B→C 传 analysis.md。
所有产物写到 ./tool_outputs/。
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict

from camel.agents import ChatAgent
from camel.toolkits import FileToolkit, tool

from camel_demo_config import create_model, load_demo_config

OUTPUT_DIR = Path(__file__).with_name("tool_outputs")
RAINFALL_CSV = OUTPUT_DIR / "rainfall.csv"
ANALYSIS_MD = OUTPUT_DIR / "analysis.md"
REPORT_MD = OUTPUT_DIR / "report.md"

MONTHS = [
    "1月", "2月", "3月", "4月", "5月", "6月",
    "7月", "8月", "9月", "10月", "11月", "12月",
]
RAINFALL_MM = [35, 42, 68, 95, 140, 210, 245, 198, 132, 78, 50, 30]


@tool()
def create_rainfall_dataset() -> Dict[str, Any]:
    r"""生成一份 12 个月的降雨量数据集，并保存为 rainfall.csv。

    Returns:
        Dict[str, Any]: 包含文件路径与行数。
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with RAINFALL_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["month", "rainfall_mm"])
        for month, value in zip(MONTHS, RAINFALL_MM):
            writer.writerow([month, value])
    return {"path": str(RAINFALL_CSV), "rows": len(MONTHS)}


@tool()
def analyze_rainfall() -> Dict[str, Any]:
    r"""读取 rainfall.csv，计算总降雨量、月均、最湿月与最干月，
    并把分析结果写入 analysis.md。

    Returns:
        Dict[str, Any]: 包含分析文件路径与关键统计量。
    """
    with RAINFALL_CSV.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    values = [float(r["rainfall_mm"]) for r in rows]
    names = [r["month"] for r in rows]
    total = sum(values)
    average = total / len(values)
    wettest = names[values.index(max(values))]
    driest = names[values.index(min(values))]

    lines = [
        "# 降雨量分析",
        "",
        f"- 总降雨量：{total:.0f} mm",
        f"- 月均降雨量：{average:.1f} mm",
        f"- 最湿月份：{wettest}（{max(values):.0f} mm）",
        f"- 最干月份：{driest}（{min(values):.0f} mm）",
        "",
        "## 逐月数据",
        "",
        "| 月份 | 降雨量(mm) |",
        "| --- | --- |",
    ]
    lines += [f"| {n} | {v:.0f} |" for n, v in zip(names, values)]
    ANALYSIS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "path": str(ANALYSIS_MD),
        "total_mm": total,
        "average_mm": round(average, 1),
        "wettest": wettest,
        "driest": driest,
    }


def print_tool_calls(response) -> None:
    calls = response.info.get("tool_calls") if response.info else None
    if not calls:
        print("  (本次没有调用工具)")
        return
    for call in calls:
        print(f"  - 调用工具：{call.tool_name}")
        print(f"    参数：{call.args}")
        print(f"    结果：{call.result}")


def main() -> None:
    config = load_demo_config()
    print(f"模型：{config.model} | 地址：{config.base_url}")
    model = create_model(config)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # A：数据生成员，只带一个自定义工具
    agent_a = ChatAgent(
        system_message=(
            "你是数据生成员。请调用 create_rainfall_dataset 工具生成数据，"
            "不要自己编造数据，也不要手工写文件。"
        ),
        model=model,
        tools=[create_rainfall_dataset],
    )

    # B：数据分析员，只带另一个自定义工具
    agent_b = ChatAgent(
        system_message=(
            "你是数据分析员。数据文件是 rainfall.csv。"
            "请调用 analyze_rainfall 工具完成分析并生成 analysis.md。"
        ),
        model=model,
        tools=[analyze_rainfall],
    )

    # C：报告撰写员，使用官方 FileToolkit（读写文件）
    file_toolkit = FileToolkit(working_directory=str(OUTPUT_DIR))
    agent_c = ChatAgent(
        system_message=(
            "你是报告撰写员。你可以读写工作目录下的文件。"
            "请读取 analysis.md，并写出最终的中文报告 report.md。"
        ),
        model=model,
        tools=file_toolkit.get_tools(),
    )

    print("\n===== 步骤 1：A 生成数据（rainfall.csv）=====")
    resp_a = agent_a.step("请生成一份 12 个月的降雨量数据集。")
    print(resp_a.msgs[0].content)
    print_tool_calls(resp_a)

    if not RAINFALL_CSV.exists():
        print(f"\n[中断] 没有找到 {RAINFALL_CSV}，A 可能没有调用工具。")
        return

    print("\n===== 步骤 2：B 分析数据（analysis.md）=====")
    resp_b = agent_b.step(
        "rainfall.csv 已经准备好，请分析并写出 analysis.md。"
    )
    print(resp_b.msgs[0].content)
    print_tool_calls(resp_b)

    if not ANALYSIS_MD.exists():
        print(f"\n[中断] 没有找到 {ANALYSIS_MD}，B 可能没有调用工具。")
        return

    print("\n===== 步骤 3：C 读取分析并写报告（report.md）=====")
    resp_c = agent_c.step(
        "请先读取工作目录下的 analysis.md，"
        "然后据此写出最终报告到 report.md，要求含结论与建议。"
    )
    print(resp_c.msgs[0].content)
    print_tool_calls(resp_c)

    print("\n===== 产物检查 =====")
    for path in (RAINFALL_CSV, ANALYSIS_MD, REPORT_MD):
        status = "OK" if path.exists() else "缺失"
        size = path.stat().st_size if path.exists() else 0
        print(f"[{status}] {path.name}  ({size} 字节)")

    if REPORT_MD.exists():
        print("\n===== report.md 内容 =====")
        print(REPORT_MD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
