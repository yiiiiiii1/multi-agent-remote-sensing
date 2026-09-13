# CAMEL 复现待完成 List

更新时间：2026-09-11
方向：多智能体遥感调研（先跑通机制，再接入遥感）
定位：**简单复现**，只覆盖综述《A survey on LLM-based multi-agent systems》的核心链路，不追求面面俱到。

图例：`[x]` 已完成 ｜ `[ ]` 待完成

---

## 综述对照（五模块，够用即可）

| 综述模块 | 对应实验 |
|---|---|
| Profile 角色画像 | 04 |
| Perception 感知 | 08 |
| Self-action 记忆 / 知识 / 动作 | 01、02、05、06、07、09、10 |
| Mutual-interaction 相互交互 | 03、11、12 |
| Evolution 进化 | 13 |
| 应用（问题求解） | 15、16 |

---

## 阶段 0：基础设施（已完成）

- [x] 环境与 API 配置（DeepSeek + 虚拟环境）
- [x] 01 手动双智能体流水线（研究员 → 审稿人 → 整合者）
- [x] 02 RolePlaying 自动双智能体对话

---

## 阶段 1：单智能体核心机制（先把一个 Agent 吃透）

- [x] 03 ~~RolePlaying + Critic（消融：有 / 无 critic 对比）~~
      **跳过**：DeepSeek 只支持 n=1，官方 critic 依赖多候选择优，不可用。
      参考 `examples/ai_society/role_playing_with_critic.py`
- [ ] 04 角色自动生成：Role Description / Persona（Profile 模块）
      参考 `examples/role_description/role_generation.py`
- [ ] 05 Agent 记忆：对话历史 vs 向量数据库（Memory 模块）
      参考 `examples/memories/agent_memory_example.py`
- [ ] 06 结构化输出：让 Agent 返回 JSON 而非自由文本
      参考 `examples/structured_response/json_format_response.py`
- [ ] 07 上下文压缩 / 摘要：长对话如何不爆上下文
      参考 `examples/agents/agent_summarize.py`

---

## 阶段 2：工具与环境交互（让 Agent 从"会说"变成"会调用"）

- [ ] 08 多模态感知：图像分析（Perception 模块）
      参考 `examples/vision/image_analysis.py`
- [ ] 09 自定义 FunctionTool + 代码执行（Action 模块）
      参考 `examples/toolkits/function_tool_example.py`、`examples/toolkits/file_toolkit.py`
      代码已就绪：`experiments/09_工具调用与文件传递.py`（3 个 Agent 各带不同工具，
      通过 rainfall.csv / analysis.md / report.md 传递文件；待运行）
- [ ] 10 RAG：给单智能体接检索增强（知识利用）
      参考 `examples/rag/single_agent_with_hybrid_rag.py`

---

## 阶段 3：多智能体协作（从"两个 Agent 对话"升级到"团队"）

- [x] 11 Workforce 基础：多个 worker 自动分工
      参考 `examples/workforce/multiple_single_agents.py`
      日志：`11_workforce分工_日志.md`
- [x] 12 多智能体辩论（对抗场景，综述 3.4.3）
      基于 `examples/ai_society/role_playing.py` 的 RolePlaying + 裁判改造
      日志：`12_多智能体辩论_日志.md`

---

## 阶段 4：进化与评估

- [ ] 13 反馈学习 / 自我反思（Evolution 模块）
      参考 `examples/memories/agent_memory_example.py` 与 Reflexion 思路
- [ ] 14 评估：单智能体评估流程
      参考 `examples/evaluation/single_agent.py`

---

## 阶段 5：遥感落地（本方向目标）

- [ ] 15 把某个 worker 替换为"遥感工具 Agent"（调用预处理 / 检测函数）
- [ ] 16 端到端：多智能体协作完成一次遥感变化检测调研报告
- [ ] 17 消融：Agent 数量、有无 critic、有无工具对结果的影响

---

## 建议顺序（先做这些）

1. 03 RolePlaying + Critic（最小消融，延续 02）
2. 04 角色生成 + 05 记忆（把单智能体机制补全）
3. 09 FunctionTool + 代码执行（让 Agent 会动手）
4. 11 Workforce 基础（从对话升级到团队）
5. 15 / 16 遥感落地

## 记录规范

每完成一个实验，产出：

1. 代码文件：`experiments/XX_名称.py`
2. 运行记录：`experiments/XX_名称_日志.md`
3. 在 `experiments/README.md` 登记命令与观察要点

## 补充：工具类实验（已运行，有日志）

- `09_工具调用与文件传递.py`：3 个 Agent 各带不同工具（自定义 @tool + 官方
  FileToolkit），通过 rainfall.csv / analysis.md / report.md 传递文件。
  日志：`09_工具调用与文件传递_日志.md`
- `10_联网检索与文件传递.py`：用 Tavily 联网获取**真实网页数据**，
  检索员→分析员→报告员，通过 web_notes.md / web_analysis.md / web_report.md 传递。
  日志：`10_联网检索与文件传递_日志.md`
