# 图片索引：8 篇论文的模型图与结果表

> 全部由 PDF 直接渲染/裁剪（200–220 dpi），**做 PPT 时可直接拖进去**。
> 每张图/表都标了来源论文、页码、对应卡片。共 30 张。
> 更新时间：2026-09-26

## 一、模型图（讲"这篇论文怎么做"）

| 文件 | 是什么 | 来源 | 用在 |
|---|---|---|---|
| `meta_sop.png` | Figure 1 人类团队 SOP ↔ MetaGPT 角色与产物 | MetaGPT, p.2 | `卡片-MetaGPT.md`｜模型页 |
| `meta_flow.png` | Figure 3 软件开发流程实例（PRD→设计→任务→代码→QA） | MetaGPT, p.5 | `卡片-MetaGPT.md`｜模型页 |
| `camel_framework.png` | Figure 1 角色扮演流程（Task Specifier → User/Assistant） | CAMEL, p.4 | `卡片-CAMEL.md`｜模型页 |
| `autogen_overview.png` | Figure 1 三面板：Agent 定制 / 对话模式 / 对话实例 | AutoGen, p.1 | `卡片-AutoGen.md`｜模型页 |
| `chatdev_chain.png` | Figure 2 Chat Chain：3 阶段 5 子任务 | ChatDev, p.3 | `卡片-ChatDev.md`｜模型页 |
| `macnet_dag.png` | Figure 1 MACNET：DAG 组织 Agent | MacNet, p.1 | `卡片-MacNet.md`｜模型页 |
| `macnet_topo.png` | Figure 2/3 六种拓扑 + 节点 actor / 边 critic | MacNet, p.3 | `卡片-MacNet.md`｜模型页 |
| `agentverse_f1.png` | Figure 1 四阶段循环（招募→决策→执行→评估→反馈） | AgentVerse, p.2 | `卡片-AgentVerse.md`｜模型页 |
| `tran_framework.png` | Fig. 2 协作通道四维 + 协调编排层 | Tran 2025, p.9 | 规划文档｜开场分类骨架 |
| `yan_taxonomy.png` | 通信为中心的分类树（系统级 + 系统内） | Yan 2025, p.3 | 规划文档｜模型结构一节 |
| `talemi_eco.png` | Figure 1 遥感 Agentic AI 四层生态 | Talemi 2026, p.1 | 规划文档｜应用场景一节 |
| `geollm_arch.png` | Figure 1 六类专职 Agent + 编排器 | GeoLLM-Squad, p.2 | `卡片-GeoLLM-Squad.md`｜模型页 |
| `geollm_scaling.png` | Figure 2 单 vs 多智能体扩展性消融（关键图） | GeoLLM-Squad, p.4 | `卡片-GeoLLM-Squad.md`｜实验页主图 |

## 二、结果图与表格（讲"效果如何"）

| 文件 | 是什么 | 来源 | 用在 |
|---|---|---|---|
| `tbl_metagpt_softwaredev.png` | Table 1 SoftwareDev 统计（可执行性 3.75、人工修复 0.83） | MetaGPT, p.8 | `卡片-MetaGPT.md`｜实验页 |
| `tbl_metagpt_roles.png` | Table 3 角色消融（可执行性 1.0 → 4.0） | MetaGPT, p.9 | `卡片-MetaGPT.md`｜动机实验 |
| `tbl_camel_eval.png` | Table 1 CAMEL vs 单模型（76.3% vs 10.4%） | CAMEL, p.9 | `卡片-CAMEL.md`｜实验页 |
| `tbl_camel_humaneval.png` | Table 3 CAMEL-7B HumanEval(+) pass@k | CAMEL, p.10 | `卡片-CAMEL.md`｜实验页 |
| `autogen_fig4.png` | Figure 4 四应用结果（ALFWorld +15%） | AutoGen, p.7 | `卡片-AutoGen.md`｜实验页 |
| `tbl_chatdev_main.png` | Table 1 主实验（Executability 0.88 vs 0.41） | ChatDev, p.6 | `卡片-ChatDev.md`｜实验页 |
| `tbl_chatdev_pairwise.png` | Table 2 两两偏好（对 MetaGPT 人类评委 88%） | ChatDev, p.6 | `卡片-ChatDev.md`｜实验页备用 |
| `tbl_chatdev_cost.png` | Table 3 成本（耗时/Token/文件数/行数） | ChatDev, p.6 | `卡片-ChatDev.md`｜实验页备用 |
| `tbl_chatdev_ablation.png` | Table 4 消融（去 CDH、去角色） | ChatDev, p.7 | `卡片-ChatDev.md`｜动机实验 |
| `tbl_macnet_main.png` | Table 1 主实验（六拓扑 + 四基线） | MacNet, p.6 | `卡片-MacNet.md`｜实验页 |
| `tbl_agentverse_main.png` | Table 1 主实验（CoT / Solo / Group） | AgentVerse, p.4 | `卡片-AgentVerse.md`｜实验页 |
| `tbl_debate_reasoning.png` | Table 1 推理任务对比 | Multiagent Debate, p.6 | `卡片-Debate.md`｜实验页 |
| `tbl_debate_factual.png` | Table 2 事实性（传记 / MMLU / 棋步） | Multiagent Debate, p.7 | `卡片-Debate.md`｜实验页 |
| `debate_results.png` | Figure 1 六基准柱状图 | Multiagent Debate, p.2 | `卡片-Debate.md`｜实验页主图 |
| `tbl_geollm_tasks.png` | Table II 五类遥感工作流与数据产品 | GeoLLM-Squad, p.2 | `卡片-GeoLLM-Squad.md`｜实验页 |
| `tbl_geollm_main.png` | Table III 主实验（正确率 60.29% vs 单 Agent 43.32%） | GeoLLM-Squad, p.3 | `卡片-GeoLLM-Squad.md`｜实验页 |
| `tbl_geollm_slm.png` | Table IV 小模型对比（Magentic 崩到 9%） | GeoLLM-Squad, p.4 | `卡片-GeoLLM-Squad.md`｜动机实验 |

## 三、备用（还没裁，需要就说）

| 论文 | 图/表 | 位置 | 适合讲什么 |
|---|---|---|---|
| Multiagent Debate | Figure 4/5 算术题逐轮收敛实例 | p.5 | "辩论怎么把两个错误答案收敛成正确答案" |
| ChatDev | Figure 3 语言分布饼图（NL 57.5% / PL 42.8%） | p.8 | "自然语言管设计、编程语言管调试" |
| MacNet | Figure 7 协作 scaling law 曲线 | p.8 | "加多少 Agent 才值" |
| AgentVerse | Figure 2/3 氢能站咨询、计算器开发案例 | p.5–6 | "动态组队"的真实过程 |
| CAMEL | Table 2 递进微调（知识涌现） | p.10 | "生成数据分领域有效" |
