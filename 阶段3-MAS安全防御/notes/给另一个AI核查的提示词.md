# 请帮我核查一份文献调研的结论

## 背景

我在做一个研究方向：**卫星场景下的多智能体安全防御 + 轻量化**。威胁是多步注入攻击（攻击者分几步篡改 Agent 的认知，单步防御拦不住）。导师要求我先精读一篇 CCF-A 论文，我选的是：

**Speculative Safety Honeypot (SSH): Toward Proactive Defense Against Multi-turn Agent Attacks**，ICML 2026（PMLR 306），华为香港。arXiv:2609.39549。

SSH 的做法（我读完全文后的理解，共 16 页，正文 8 页 + 附录 7 页）：
- 三个模拟器（用户 / 助手 / 环境），共用同一个无安全对齐的 3B 骨干（Dolphin3.0-Qwen2.5-3B）+ 三个 LoRA
- 异步把目标 Agent 的未来动作摊成一棵轨迹树（M=5 分支宽，D=4 深度）
- 真实动作回来后剪枝（对上就只留那一支，对不上保留整棵树）
- 检测器看剩余叶节点，风险分 = 有风险的叶子 / 总叶子
- 双阈值 τ₁ < τ₂（推测命中走低阈值，未命中走高阈值）
- 告警后三种响应：引导 / 重采样 / 终止；实验选重采样，最多 5 次
- 关键数字：ASR 0%、暴露率 HarmBench 99.5% / Circuit Breaker 96.0%、系统级 FPR 0.2%、探子参数占 235B 主模型的 1.3%

现在我需要你核查我下面这份调研。**请以审稿人的严格程度来做，不要客气。**

---

## 我要你检验的核心结论（共 6 条）

**结论 1**：不存在「CCF-A 正会 + 开源 + 事前预测」三者齐全的论文。CCF-A 正会且做事前预测的只有 SSH 一篇，而 SSH 不开源。

**结论 2**：这一族论文（自称 proactive / predictive guardrail）实际上分成三个不同的层次，不能用同一个词概括：
- **A 层（判当前这步）**：判断 Agent 眼下要执行的动作安不安全，执行前判。代表：ToolSafe
- **B 层（预判后果）**：预测这步执行后状态会变成什么。代表：SafePred、DreamGuard
- **C 层（推演未来动作序列）**：预测 Agent 接下来会做哪几步，展开成树。**只有 SSH**

**结论 3**：这一族至少 25 篇，几乎全部集中在 2025Q4–2026 的 arXiv 预印本。CCF-A 正会只有 SSH 一篇。

**结论 4**：开源的只有 5 个，星数与归属：
- ToolSafe：https://github.com/MurrayTom/ToolSafe ，★86
- SafePred：https://github.com/YurunChen/SafePred ，★71
- HarmonyGuard：https://github.com/YurunChen/HarmonyGuard ，★28
- IPIGuard：https://github.com/Greysahy/ipiguard ，★26
- WebGuard：https://github.com/OSU-NLP-Group/WebGuard ，★13

**结论 5**：SSH 的核心创新在推理层（轨迹树 + 剪枝 + 双阈值 + 重采样），不在训练层（Differentiated Alignment）。因此复现第一层（模拟器用 API 模型 prompt 扮演，自己写推理层，插在 AgentDojo 上）只需要 3–5 天、400–600 行 Python。

**结论 6**：复现 SSH 所需零件全部公开：Dolphin3.0-Qwen2.5-3B（HuggingFace: dphn/Dolphin3.0-Qwen2.5-3b）、Toucan（GitHub: intuit-ai-research/TOUCAN）、AgentDojo（★985）、ActorAttack（AI45Lab/ActorAttack ★135）。

---

## 我已经核实过的会议归属

| 论文 | 我认定的会议 | 依据 |
|---|---|---|
| ProbGuard | ASE 2026 正会 | PDF 首页版权块 |
| SecAlign | CCS 2025 正会 | PDF 首页 DOI 10.1145/3719027.3744836 |
| IsolateGPT | NDSS 2025 | arXiv 页注明 |
| DataSentinel | S&P 2025 | OpenAlex DOI 10.1109/sp61157.2025.00250 |
| The Task Shield | ACL 2025 正会 | DOI 10.18653/v1/2025.acl-long.1435 |
| AirGapAgent | CCS 2024 | DOI 10.1145/3658644.3690350 |
| DRIFT | NeurIPS 2025 | OpenAlex |
| C-SafeGen | NeurIPS 2025 | OpenAlex |
| SSH | ICML 2026 | 论文 PDF 首页 |

## 我判错过、后来修正的（请帮我复核这些修正对不对）

| 论文 | 我第一次错写成 | 我后来改成 | 依据 |
|---|---|---|---|
| KG-Guard | ICML 2025 | **ICMLCA 2025** | OpenAlex: "International Conference on Machine Learning and Computer Application" |
| ShadowPlay | ASE 2025 | **Cyber-AI 2025** | OpenAlex: "International Conference on Cybersecurity and AI-Based Systems" |
| TrustAgent | ACL 2024 | **Findings of EMNLP 2024** | DOI 10.18653/v1/2024.findings-emnlp.585 |
| R-Judge | ACL 2024 | **Findings of EMNLP 2024** | DOI 10.18653/v1/2024.findings-emnlp.79 |
| Causal Influence Prompting | ACL 2025 | **Findings of ACL 2025** | DOI 10.18653/v1/2025.findings-acl.784 |

## 我明确不确定的四项（已知风险，不必再告诉我"这可能有问题"，请直接查证）

1. **SelfDefend 是否 USENIX Security 2025 正会**：本地 PDF 是 arXiv 版，首页没印会议。依据是文件名 + 致谢里的 "shepherd" + USENIX 议程。
2. **Fides 是 NeurIPS 哪一年**：arXiv 2505.23643 的 comment 字段为空，只搜到 NeurIPS poster 页。
3. **ToolSafe 是否 Findings of ACL 2026**：这是从 DreamGuard 的引文里读到的，ToolSafe 自己那版 PDF 是 arXiv 版，首页没印会议。
4. **DRIFT 的仓库 SaFo-Lab/DRIFT 是否是官方**：★62 看着像，但没读 DRIFT 原文确认。

---

## 我的检索方法（供你判断覆盖是否有漏洞）

**四轮，四方法：**

1. **网页搜索**（撞见式）→ 9 篇
2. **OpenAlex 系统扫描**：51 个查询 × 8 个词族 × 17 个 CCF-A 会议 + 2023 至今 → 补 4 篇（但会议判错 5 篇）
3. **反查 2 篇（DreamGuard + 一篇批判论文）的参考文献** → 补出整族 11 篇
4. **反查 4 篇（加 SafePred、ToolSafe）的参考文献** → 又补 8 篇

**已承认未覆盖的：**
- **期刊没扫**（TDSC / TIFS / TSE / TOPS 也是 CCF-A）
- **非英文文献没扫**
- OpenAlex 索引有滞后，2026 下半年新论文可能没进去
- 反查轮里新找到的 9 篇（KG-Guard / ShadowPlay / C-SafeGen / The Task Shield / TrustAgent / R-Judge / AirGapAgent / DRIFT / DataSentinel）**只核了会议+题目+是否开源，没有读方法**

---

## 请你重点检查这七件事

1. **结论 1 和 3 对不对**：有没有我漏掉的「CCF-A 正会 + 开源 + 事前预测」论文？特别是 2023–2025 年发表的（不是 2026 预印本）。
2. **结论 2 的分层对不对**：A / B / C 三层这个划分站得住吗？有没有论文其实在做 C 层（多步动作树 / 树搜索 / MCTS / rollout 展开），但我归错了类？
3. **"C 层只有 SSH" 这个断言是否成立**：这是我最没底的一条。请专门去查有没有别的工作用「树 / 分支 / rollout / 前瞻展开」来做 Agent 安全。注意：不要只看 2026，也要看 2024–2025 的 CCF-A。
4. **上面那张"我判错后又修正"的表，修正对不对**：这五篇的真实会议归属是什么。
5. **结论 5 的工期估计是否离谱**：3–5 天、400–600 行写一个"三模拟器（prompt 版）+ 轨迹树 + Beam Search + 剪枝 + 双阈值 + 重采样"的骨架，插在 AgentDojo 上——你判断这个估算合理吗？偏乐观还是偏保守？
6. **结论 6 的零件是否真的全在**：Dolphin3.0-Qwen2.5-3b、Toucan、ActorAttack 这几个是否真的公开可下载、能用于训练。
7. **方法漏洞**：以我的检索方法，最容易漏掉哪一类论文？请给出具体的补检建议（要能执行的检索式，不要泛泛说"再查查"）。

---

## 输出格式要求

请按这个结构回答：

```
## 一、我确认成立的结论（逐条）
## 二、我判定有误或夸大的（逐条，指出错在哪、正确是什么、给依据）
## 三、我无法确证的（说明需要什么证据）
## 四、你漏掉的关键论文（如果有，给标题+会议+是否开源+与 SSH 的关系）
## 五、对结论 5 工期估计的判断（偏乐观/合理/偏保守 + 理由）
## 六、补检建议（可执行的检索式）
```

**请严格区分「你查到了证据」和「你根据常识推断」。凡是推断的，请标明"未核实"。**
