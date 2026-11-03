# SSH 开源同类调研

**日期**：2026-11-03
**要回答的问题**：有没有跟 SSH 类似、但**开源**的论文，要求 **CCF-A**。
**做法**：先广度（四个维度交叉检索），方向对的再读原文全文；**所有结论都从 PDF 原文读出来，标了页码，没有只读摘要**。

---

## 一句话结论

**没有一篇是 SSH 的开源替代品。**

SSH 独有的三块——**三个角色模拟器分工、M=5 分支的轨迹树、告警后重采样**——在 CCF-A 且开源的论文里**找不到对应物**。

**最接近的三篇各有分工**：

| 要什么 | 用哪篇 | 但它缺什么 |
|---|---|---|
| 能跑的 CCF-A 开源基线 | **ProbGuard**（ASE 2026） | 预测的是符号状态概率，不是未来动作序列；无攻击者模型 |
| 能抄的架构思路 | **DreamGuard**（预印本，无代码） | 前瞻只有 1 步隐状态，无树无分支 |
| 能抄的落地方式 | **SelfDefend**（USENIX Sec 2025） | 只看当前这轮，完全没有"未来"概念 |
| 必须知道的反方观点 | **Predictive Safety Guardrails Do Not Always Make LLM Agents Safer**（预印本） | 它没点名 SSH，但三条正好打在 SSH 最薄的地方 |

---

## 二、广度表（9 篇，逐篇核实过原文）

### CCF-A 且开源（5 篇）

| 论文 | 会议 | 开源地址 | 和 SSH 什么关系 |
|---|---|---|---|
| **ProbGuard**：Proactive Runtime Monitoring for LLM Agent Safety via Probabilistic Prediction | **ASE 2026 正会**（p1 版权块） | `github.com/haoyuwang99/ProbGuard`（参考文献 [43]，p13） | **最接近的骨架**：都主张动作前预测、每步算 [0,1] 风险分、卡阈值。但它用 DTMC 预测**符号状态**的概率，动作集合根本没进模型 |
| **SelfDefend**：LLMs Can Defend Themselves against Jailbreaking | **USENIX Security 2025**（推定，见文末核实说明） | `github.com/SelfDefend`；artifact DOI `10.5281/zenodo.14736935`（p15） | **能抄落地方式**：影子实例并发 + checkpoint 门控（影子先吐一个 token 就放行，做到近零延迟）+ GPT-4 蒸馏到 Llama-2-7b LoRA。但只看当前这轮，不预测未来 |
| **SecAlign**：Defending Against Prompt Injection with Preference Optimization | **CCS 2025 正会**（p1，DOI 10.1145/3719027.3744836） | `github.com/facebookresearch/SecAlign`（p1） | **正交**：把抗注入训进权重（DPO），不是外挂监控。优化型攻击 ASR 降到 Llama3-8B 8% / Mistral-7B 1%（Table 6, p8）。但要白盒 + 明确分隔符 + 重训，星上小模型三条都难 |
| **Fides**：Securing AI Agents with Information-Flow Control | **NeurIPS**（年份待核） | `github.com/microsoft/fides` | **正交**：信息流控制/污点追踪做形式化保证，跟"预测未来"不是一路 |
| **IsolateGPT**：An Execution Isolation Architecture for LLM-Based Agentic Systems | **NDSS 2025**（arXiv 页注明） | `github.com/llm-platform-security/SecGPT` | **正交**：执行隔离，把不可信数据关进独立环境跑 |

**另加一个基准（不算同类，但 SSH 自己就用它）**

| 论文 | 会议 | 开源 |
|---|---|---|
| **AgentDojo** | NeurIPS 2024 D&B（CCF-A） | `github.com/ethz-spylab/agentdojo` ★985 |

### 不是 CCF-A，但方向对、值得知道（4 篇）

| 论文 | 归属 | 开源 | 为什么还要知道 |
|---|---|---|---|
| **TurnGate**：One Turn Too Late | **正文只写 "Preprint."（p1）**；GitHub 自称 ICML 2026 AIWILD（workshop）→ **不算 CCF-A** | `github.com/Graph-COM/TurnGate` | 它研究"该在第几轮拦"（最早致害轮 t\*），是**时机评估**最现成的参照。但它是个**不推演的逐轮分类器**：输入（历史 + 候选回复），输出 PASS/BLOCK |
| **DreamGuard**：Efficient Runtime Guardrail via Risk-Aware World Model | **纯预印本**（arXiv 2608.05695，无会议标注） | **无公开代码**（附录只说"随投稿的数据包"，p13） | **概念上最像 SSH 的一篇**：world model 前瞻 + 双阈值（λ_block/λ_hold）+ 三档处置（PASS/HOLD/BLOCK）+ **25 ms/call** |
| **Predictive Safety Guardrails Do Not Always Make LLM Agents Safer** | **纯预印本**（arXiv 2611.02815） | `github.com/REH502/rethinking-predictive-safety`（p1） | **直接质疑这一整类范式**，详见下一节 |
| **DEFER**（arXiv 2610.07657） | 预印本 | 待核 | 只提了一句：能确定性判定的直接拒，其余再判。宽度参考 |

---

## 三、深读的三篇，各自的关键事实

### ProbGuard（ASE 2026）——最接近的 CCF-A 开源骨架

**它怎么做的**（p3–6）
1. 规格写成 CTL 不变式 `ψ = AG¬unsafe`，用 PCTL 问"从当前状态继续跑，一直安全的概率是多少"
2. 专家给一组布尔谓词，把具体状态抽象成 0/1 向量；用 `valid_tran` 剪掉物理不可能的转移
3. 数 trace 里的状态转移次数学一个 **DTMC**（连续时间马尔可夫链），Laplace 平滑 α=1；**全链没有神经网络训练**
4. 每步算 `P_safe`，低于阈值 θ 就介入（停 / 报警 / 引导）
5. 换新领域只要三样：状态抽象函数、`valid_tran`、CTL 性质，各约 200–250 行 Python

**关键数字**
- 具身域：无监控 unsafe 40.63% / 完成率 59.38% → 停@0.9 降到 **2.60%** unsafe，但完成率只剩 10.42%；引导@0.9 是 14.07% unsafe + 47.74% 完成率（Table 2, p10）
- 开销：缓存后 **5–8 ms**，8 状态 13 ms（p10–11）
- 误报随阈值暴涨：θ=0.3 → 0% FP，θ=0.5 → 75%，θ=0.7 → 100%（p8）

**它缺什么**：不生成未来动作；没有攻击者模型（威胁是 LLM 自身随机性，无注入、无三角色）；单阈值，介入只有停/反思，没有"重采样 5 次"。

### DreamGuard（预印本）——概念最像，但没代码

**它到底预测什么**（p3–5）
- RSSM 结构的 world model，GRU 转移。给定要执行的 a_t，先算 h_{t+1}，再采样**下一时刻的隐状态** ẑ_{t+1}，两个 MLP 头在这个**预测出来的状态**上打分
- **深度只有 1 步，在 latent 空间，无树无分支无剪枝**
- 双阈值用 split-conformal 在校准集上分别定 λ_block（严）和 λ_hold（松）→ 输出 PASS/HOLD/BLOCK

**为什么值得当参照**
- 动机跟 SSH 一模一样：明确把自己和 "reactive guardrail" 对立（p1）
- **25 ms/call**，比 TRACES 快 3.3×、GuardAgent 快 250×——**星上算力可行性可以直接引这个数**
- SafetyDrift 上 F1 96.4 / FPR 3.7 / PHIR 96.3%、提前 3.63 步（Table 1/2, p6）

**它自己的坑**（原文承认）
- 只在 SafetyDrift 一个自建基准上训练+校准，其余三个零样本迁移
- 即时危害基准上提前介入能力很弱：AgentDojo PHIR 只有 16.8%、ASB 17.3%（Table 2）——说明它主要靠"当前动作危险"救场

### 批判论文——最该拿去跟导师讨论的一篇

**它没点名 SSH**（全文 0 次出现 SSH / speculative / honeypot / tree / branch / MCTS），点的是整类范式：

> "...an emerging paradigm of world-model-driven predictive safety guardrails, which use anticipated future consequences to assess risk before execution"（p1）

**它点名的系统**：SafePred、SafeMCP、JANUS、SeerGuard——全是单步预测+门控，**没有一个多分支树状推演**。

**三条打得到 SSH 的**（都标了页码）

1. **深度**：h>1 之后预测的 recall 和 risk-correlation 明显下滑，而 accuracy 看着还稳（p7–8）。**SSH 的 D=4 正好落在它测出掉最狠的区间**
2. **归因**：Full Inversion 实验把风险信号反过来，SAR 反而到 **90.1**、TCR 崩到 13.7（p8, Fig.3）——说明"安全分"可能是门控循环刷出来的，不是预测内容带来的。**SSH 的增益到底来自树，还是来自告警后的重采样（最多 5 次）？这篇的对照正是 SSH 缺的那个 ablation**
3. **忠实性**：零风险预测会被拿去给已备好的动作盖章（Cases 4–6, p26）。检测器读叶子节点，同样的"预测当安慰剂"能套上

**但它也有硬伤，引用要小心**
- **没写样本量**（逐页找过，全文没有任何轨迹数/任务数/种子数）
- **没有置信区间、没有显著性检验**，−1.87 这种差值可能在噪声里
- 摘要说 "seven policy models"，RQ1 实际只有 4 个 backbone（p3–4），7 是 RQ2 的预测模型数——**引用时容易说错**
- 它自己留了余地：设定比 SSH 弱（单步 + 一道门），负结果不能直接外推

---

## 四、So what：这轮调研对现在的用处

**1. 如果她问「有没有开源可以对着做的」**

> SSH 自己没开源，我查了同类，**CCF-A 里最接近的是 ASE 2026 的 ProbGuard**——也是"动作前先算一个安全概率，低于阈值就介入"，有代码。但它预测的是符号状态的走向，不是"Agent 下一步会调哪个工具"，也没有攻击者建模，所以不能当替代品。

**2. 如果她问「SSH 是不是没人做过」**

> **不是。** 事前预测这条线有人做：ProbGuard（ASE 2026）、DreamGuard（预印本）、TurnGate（预印本）。**但把"未来摊成树 + 用真实动作剪枝 + 多角色模拟"这套组合做出来的，目前只看到 SSH。** 而且现在已经有论文在质疑这整类范式（Predictive Safety Guardrails…, 2026-11），说的正是"深度一长预测就不准""增益可能来自后处理"。

**3. 对卫星场景最有用的一条**

DreamGuard 的 **25 ms/call** 是星上算力的直接证据——比 SSH 的"3–7 秒误报延迟"友好得多。**如果方向要做轻量化，这个数字比 SSH 自己的更有说服力。**

**4. 下一步最值得做的一件事（2 分钟内）**

clone TurnGate 看 `data/` 里 MTID 的标注格式——那是现成的"最早致害轮 t\*"标注样例，**卫星多步攻击链的"第几步算越界"可以直接照这个格式标**。

---

## 五、核实状态（哪些是原文读到的，哪些是推定的）

**从 PDF 原文读到的**：所有会议归属（除 SelfDefend）、所有数字、所有页码、所有代码地址。

**推定的，引用前要再确认**：
1. **SelfDefend 的 USENIX Security 2025**：本地 PDF 是 arXiv 版，首页没印会议。依据是文件名 + 致谢里的 "shepherd"（USENIX 用词）+ USENIX 议程。**要引用的话建议再去 USENIX 官网核一次。**
2. **Fides 的 NeurIPS 年份**：arXiv 2505.23643 的 comment 里没写，只搜到 NeurIPS poster 页。**年份待核。**
3. **Fides 和 IsolateGPT 的方法细节**：这轮只核实了"会议 + 开源 + 一句话定位"，**没有深读方法**。如果要用在汇报里，得补读。
4. **TurnGate 的会议归属**：**论文正文写的是 "Preprint."**，只有 GitHub 自称 ICML 2026 AIWILD。**按预印本引用，别说成 ICML 正会。**
5. **ProbGuard Table 3** 有一格是上标格式（`530–10^5`），按 5.30×10⁵ 读。

**原文 PDF 都存在**：`阶段2-卫星多智能体防御/papers/开源同类调研/`
