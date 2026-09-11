# 多智能体遥感调研

更新时间：2026-09-11

> **当前定位**
>
> 先用一个结构清楚、代码公开的通用多智能体框架，把「角色、通信、任务分解、协作流程」跑通；
> 遥感只作为后续应用场景，暂时不接入真正的卫星影像模型。

## 目录结构

```text
多智能体遥感调研/
├── README.md          # 本文件：方向总览与学习路线
├── papers/            # 论文 PDF
├── notes/             # 论文精读笔记
├── experiments/       # 复现代码与运行日志（含待完成list.md）
└── archive/           # 早期零散实验，保留但不维护
```

## 复现对象：CAMEL

- 项目：<https://github.com/camel-ai/camel>
- 论文：*CAMEL: Communicative Agents for "Mind" Exploration of Large Language Model Society*
- 源码位置：`clones/camel`（外部克隆，只读，不要往里放自己的代码）

选择 CAMEL 的原因：

- 角色扮演式对话机制清晰，适合观察两个 Agent 如何往返协作；
- 提供大量 Agent、工具、记忆、数据生成示例，便于逐步扩展；
- 比 MetaGPT 更适合研究通信方式、记忆和规模化实验。

## 学习路线（对齐综述五模块）

参考论文：*A survey on LLM-based multi-agent systems: workflow, infrastructure, and challenges*（`papers/s44336-024-00009-2.pdf`）。

| 综述模块 | 要跑通的能力 | 对应实验 |
|---|---|---|
| Profile 画像 | 角色定义与自动生成 | 04 |
| Perception 感知 | 多模态信息输入 | 08 |
| Self-action 自主行动 | 记忆、知识、工具调用 | 01、02、05、06、07、09、10 |
| Mutual-interaction 相互交互 | 消息传递与多智能体协作 | 03、11、12 |
| Evolution 进化 | 反馈学习与自我反思 | 13 |
| 应用 | 端到端问题求解 | 15、16 |

完整任务见 `experiments/待完成list.md`。

## 如何运行

```bash
cd experiments
cp .env.example .env      # 填入 DEEPSEEK_API_KEY
bash run_demo.sh 01       # 最小双智能体
bash run_demo.sh 02       # RolePlaying 双智能体
```

## 遥感落地思路

把多智能体团队中的某个 worker 替换为「遥感工具 Agent」：

- 图像预处理 Agent
- 目标检测 Agent
- 变化检测 Agent
- 结果解释 Agent

这样遥感只是工具和数据域的替换，不影响对多智能体系统基本结构的理解。
