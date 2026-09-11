# CAMEL 入门实验

本目录是「多智能体遥感调研」的复现代码与运行日志，目标是把 CAMEL 的核心机制先跑通，再接入遥感。

## 目录约定

| 文件 | 作用 |
|---|---|
| `XX_名称.py` | 实验代码 |
| `XX_名称_日志.md` | 对应的运行记录 |
| `camel_demo_config.py` | 公共模型配置（DeepSeek） |
| `run_demo.sh` | 运行脚本 |
| `待完成list.md` | 任务清单 |
| `.env` | API key（不要提交） |

## 1. 准备环境

CAMEL 源码和虚拟环境在 `clones/camel`，无需重新安装。先配置 key：

```bash
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
```

## 2. 运行实验

在本目录下运行：

```bash
bash run_demo.sh 01   # 最小双智能体（手动流水线）
bash run_demo.sh 02   # RolePlaying 自动双智能体对话
```

## 3. 已完成实验

### 01 最小双智能体
`研究员 Agent -> 审稿人 Agent -> 整合者 Agent`，手动把一个 Agent 的输出喂给下一个。
重点看 `researcher.step(...)`、`reviewer.step(...)` 和最终的 `final_prompt`。

### 02 RolePlaying 双智能体
用 CAMEL 内置 `RolePlaying`，AI User 与 AI Assistant 围绕同一任务自动多轮对话，直到完成或终止。
重点看 `session.init_chat()` 和 `session.step(...)`。

## 4. 第一次修改任务

1. 把研究问题改成「多智能体如何用于遥感变化检测」。
2. 把审稿人角色改成「遥感领域专家」。
3. 暂时删除审稿人，只让研究员回答。
4. 比较有无审稿人时，答案是否更可靠（最小消融实验）。
