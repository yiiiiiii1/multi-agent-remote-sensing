# CAMEL 复现总结（阶段汇报版）

> **报告定位**：面向导师汇报的复现工作说明。目的是在"简单复现、跑通机制"的定位下，展示可复现的工程流程、机制级验证结果，以及对结果的批判性核对。
> **阅读顺序建议**：先看「汇报摘要」，再看「复现成果」，细节见各实验日志。

---

![CAMEL Figure 1 角色扮演框架](../figures/camel_framework.png)
*Figure 1｜CAMEL 角色扮演流程：人类给出想法 + 分配角色 → Task Specifier 生成具体任务 → AI User 与 AI Assistant 多轮协作。来源：CAMEL, NeurIPS 2023, p.4*

## 汇报摘要

本阶段围绕 CAMEL 完成了**机制级复现**与**遥感落地验证**两条线：

1. **机制复现**：以 DeepSeek `deepseek-chat` 为后端，跑通 6 个实验，覆盖综述中 Self-Action 与 Mutual-Interaction 两个模块的核心机制——手动流水线、RolePlaying 自动协作、自定义工具与文件传递、真实联网检索、Workforce 自动分工、多智能体辩论。
2. **工程规范**：所有实验统一"代码 + 日志"规范，固定配置与轮数上限，记录运行事实与失效观察，仓库已发布 GitHub（`.env` 未上传）。

**结论**：CAMEL 核心机制已跑通，结论已如实核对。

---

## 一、复现目标与工程配置

- **目标**：先跑通 CAMEL 多智能体核心机制，再落到遥感方向。
- **模型**：DeepSeek `deepseek-chat`，base_url `https://api.deepseek.com/v1`。
- **框架**：CAMEL `0.2.91a7`（本地 editable 安装）。
- **配置管理**：`experiments/camel_demo_config.py` 支持 `CAMEL_ROOT` 自动查找（环境变量 → 相对路径 → 常见位置）；密钥仅存 `.env`，已加入 `.gitignore`。
- **运行方式**：`bash run_demo.sh <编号>`；`bash run_demo.sh --where` 可查看解析到的框架路径。
- **可复现性处理**：修复了仓库移动后 venv editable `.pth` 指向旧路径导致 `import camel` 失败的问题，改为自动查找，保证换机器/换目录后可复现。

---

## 二、机制复现成果

| 编号 | 实验 | 覆盖机制（综述对应） | 状态 |
|---|---|---|---|
| 01 | 最小双智能体（手动流水线） | Self-Action / 消息串联 | 完成 |
| 02 | RolePlaying 双智能体 | Mutual-Interaction / 合作 | 完成 |
| 03 | RolePlaying + Critic 消融 | 多候选评审 | 经平台验证不可行，记录为负结果 |
| 09 | 工具调用与文件传递 | Self-Action / 动作空间 | 完成 |
| 10 | 联网检索与文件传递 | Knowledge Retrieval / RAG 前置 | 完成（含一轮改进） |
| 11 | Workforce 多智能体分工 | Mutual-Interaction / 中心化协作 | 完成 |
| 12 | 多智能体辩论 | Mutual-Interaction / 对抗场景 | 完成 |

### 01 手动流水线
- 三 Agent（研究员 → 审稿人 → 整合者）仅 `system_message` 不同，编排由代码显式控制。
- 确立 CAMEL 的原子操作：`response = agent.step(prompt)` → `response.msgs[0].content`。
- 价值：为后续自动编排提供可对照的基线。

### 02 RolePlaying 自动协作
- AI User（遥感应用研究员）与 AI Assistant（遥感算法工程师）围绕同一任务自动多轮对话。
- 开启 `with_task_specify=True`，先由 Task Specifier 把模糊任务扩写为清晰提示词。
- 实测 6 轮后由 AI User 标记 `<CAMEL_TASK_DONE>` 正常终止，角色全程未串位。

### 03（负结果，已记录）
- 官方 critic 依赖 `n>1` 多候选择优；实测 DeepSeek 仅支持 `n=1`（400 报错），官方机制无法直接复现。
- 结论：在"忠于官方机制"的原则下**不采用"手动多次生成再挑选"的替代实现**（该实现已非官方机制，且样本量不足以支撑可靠结论），故按负结果归档。这一判断避免了一个误导性的"伪复现"。

### 09 工具调用与文件传递
- 三个 Agent 各带不同工具，**通过文件而非纯文本传递**：
  - A（自定义 `create_rainfall_dataset`）→ `rainfall.csv`
  - B（自定义 `analyze_rainfall`，读 CSV 做统计）→ `analysis.md`
  - C（官方 `FileToolkit`，读 analysis.md）→ `report.md`
- 验证：C 的报告完整出现 B 的统计数值，证明**文件确实被下游读取消费**，而非各写各的。

### 10 联网检索与文件传递（含迭代）
- 检索员用 Tavily 获取 **9 条真实网页结果**（真实标题/URL/摘要），写入 `web_notes.md`。
- **第一版问题**：分析员与报告员工具相同、提示词同构、产物同态，导致职责重叠（报告员仅复述）。
- **改进**：分析员强制输出**系统对比表 + 来源可信度分级表**；报告员只写**决策简报**，两者形态与职责分离。
- **改进后效果**：报告员主动发现 9 条中 #5=#7、#4=#6 重复（独立样本 6 个）；指出唯一量化结果来自"无作者、无年份"的第三方页；据此判定"多智能体优于单智能体"在本批材料中**无可核查数据，只能作为假设**。这体现了流水线具备来源批判能力。
- 领域发现：主流范式为"**LLM 作大脑 + 视觉/变化检测模型作眼睛**"。

### 11 Workforce 自动分工
- "协调者 + 3 worker（检索/分析/写作）"自动把「多智能体在遥感变化检测中的应用」拆成 4 个子任务并处理依赖（0.4 依赖 0.1/0.2/0.3）。
- KPI：4/4 成功，失败 0，耗时约 30 秒；产出 `11_workforce_logs.json`。
- **重要辨析**：worker 为代码中显式注册，协调者生成的是**任务**而非**角色**；据此判定实验 11 对应综述 Profile 的**预定义策略**，而非"运行时动态生成"。CAMEL 的 `_create_worker_node_for_task` 具备动态造角色能力，但本实验未触发。

### 12 多智能体辩论
- 采用官方 `RolePlaying`：AI Assistant 为正方、AI User 为反方，3 轮对抗，另设裁判 Agent 汇总。
- 裁判输出双方论点、4 条共识、4 条分歧，并判定"正方成立但需附加条件"。

---

## 三、机制复现的阶段性结论

1. **消息传递可以超越文本**：实验 09/10 证明以文件（csv/md）作为 Agent 间中间产物可行，与 MetaGPT "结构化通信"思想一致。
2. **编排粒度可分层**：手动流水线（01）适合可控场景；RolePlaying（02/12）适合开放式协作；Workforce（11）适合任务分解与派发。
3. **职责不分离会导致伪协作**：实验 10 第一版说明，若下游只是同构复述，多 Agent 并未产生增量价值——**分工必须带来信息变换（计算、结构化或判断）**，这是后续设计的重要准则。

---

## 五、仓库与工程状态

- 目录演进：`科研学习仓库/多智能体遥感调研` → `my-research/multi-agent-remote-sensing`，路径已全局统一。
- 结构：`papers/`（论文）、`notes/`（精读与总结）、`experiments/`（代码 + 日志 + 配置 + 清单）、`archive/`。
- 已发布 GitHub：`https://github.com/yiiiiiii1/multi-agent-remote-sensing`（Public，`.env` 未上传）。

---

## 六、结论与下一步

**结论**
1. CAMEL 的多智能体核心机制（手动编排、RolePlaying、Workforce 分工、辩论、工具 + 文件传递）已完整跑通并有日志可查。
2. 探究出"分工必须带来信息变换"这一可执行的设计准则。

**下一步（按优先级）**
1. **04 角色自动生成 + 现场招人**：补齐综述 Profile 模块，验证运行时动态造角色。
3. **13 反馈学习 / 自我反思**：补齐 Evolution 模块。
4. **16 端到端**：多智能体协作完成一次遥感变化检测调研报告。
5. **08 多模态感知**：视觉链路已实测可用，可让 Agent 真正看图（含 9 张错误可视化图）。
