# SSH 开源同类调研（第二版·系统扫描）

**日期**：2026-11-04（第二版）
**要回答的问题**：有没有跟 SSH 类似、但**开源**的论文，要求 **CCF-A**。

---

## 先说这一版改了什么（因为第一版是撞见式检索，漏了）

**第一版做法**：6 次网页搜索 + 顺着线索往下挖。**这是撞见式，发现一个算一个，不能声称覆盖。**

**这一版做法**：固定词族 × 固定会议清单 × 固定年份，系统扫两轮。

- **查询**：两轮共 **51 个查询**，分 8 个词族（事前预测/蜜罐沙箱/多轮注入/运行时护栏/影子实例/规格预测/信息流控制/能力控制……）
- **数据源**：OpenAlex（免费、带会议字段、不限流；DBLP 被限流 429，改用这个）
- **会议过滤**：只留 CCF-A（S&P / USENIX Sec / CCS / NDSS / ICML / NeurIPS / ICLR / ACL / ASE / ICSE / FSE / ISSTA / AAAI / IJCAI / OSDI / SOSP / CVPR）
- **年份**：2023 至今

**扫出来的结果：第一版漏了 3 篇 CCF-A 防御论文，还记错了 1 篇的会议。**

| 变化 | 具体 |
|---|---|
| **新增** | **DRIFT**（NeurIPS 2025，注入隔离防御，**已开源** ★62） |
| **新增** | **KG-Guard**（ICML 2025，知识图谱引导的多轮越狱防御） |
| **新增** | **ShadowPlay**（ASE 2025，角色型注入防御） |
| **新增** | **C-SafeGen**（NeurIPS 2025，流式护栏，可认证） |
| **新增** | **The Task Shield**（ACL 2025）、**Causal Influence Prompting**（ACL 2025）、**TrustAgent**（ACL 2024）、**R-Judge**（ACL 2024，**已开源** ★116）、**AirGapAgent**（CCS 2024） |
| **修正** | **DataSentinel 是 S&P 2025，不是 ICML 2024**（我第一版凭印象写错了） |

**结论没变，但证据面完全不一样了**——第一版是"我搜到 9 篇里没有"，这一版是"51 个查询扫遍 CCF-A 清单，仍然没有"。

---

## 一句话结论

**仍然没有一篇是 SSH 的开源替代品。**

**SSH 独有的三块**——三个角色模拟器分工、M=5 分支轨迹树、告警后重采样——**扫遍 CCF-A 仍然找不到对应物**。

**但"事前预测"这个大类是有人做的**，只是都不到 SSH 那个粒度：

| 要什么 | 哪篇 | 但它缺什么 |
|---|---|---|
| 能跑的 CCF-A 开源基线 | **ProbGuard**（ASE 2026，[开源](https://github.com/haoyuwang99/ProbGuard)） | 预测符号状态概率，不是未来动作；无攻击者模型 |
| 能抄的架构思路 | **DreamGuard**（预印本，无代码） | 前瞻只有 1 步隐状态，无树无分支 |
| 能抄的落地方式 | **SelfDefend**（USENIX Sec 2025，[开源](https://github.com/SelfDefend)） | 只看当前这轮，没有"未来"概念 |
| 另一个强防御基线 | **DRIFT**（NeurIPS 2025，[开源](https://github.com/SaFo-Lab/DRIFT)） | 规则+注入隔离，不预测 |
| 必须知道的反方观点 | **Predictive Safety Guardrails Do Not Always Make LLM Agents Safer**（预印本） | 没点名 SSH，但三条打在软肋上 |

---

## 一、完整全景表（CCF-A，按"做法"分组）

### A. 事前预测 / 前瞻这一类（跟 SSH 同族，4 篇）

| 论文 | 会议 | 开源 | 关键限制 |
|---|---|---|---|
| **ProbGuard** | ASE 2026 正会（p1 版权块） | ✅ `haoyuwang99/ProbGuard` | 预测 DTMC 的**符号状态**走向，动作不进模型；无攻击者建模；每域要手写谓词+CTL |
| **DreamGuard** | **预印本**（无会议标注） | ❌ 无 | 前瞻只 **1 步隐状态**，latent 空间，无树无分支；只在自建基准上训练校准 |
| **TurnGate** | **正文写 "Preprint."**（p1）；GitHub 自称 ICML 2026 AIWILD（workshop） | ✅ `Graph-COM/TurnGate` | **不是 CCF-A**，按预印本引；是逐轮分类器，不推演 |
| **Predictive Safety Guardrails…** | **预印本**（2026-11-02） | ✅ `REH502/rethinking-predictive-safety` | 批判性论文，见第三节 |

### B. 注入防御（跟 SSH 打同一类威胁，4 篇）

| 论文 | 会议 | 开源 | 做法 |
|---|---|---|---|
| **SecAlign** | CCS 2025 正会 | ✅ `facebookresearch/SecAlign` ★104 | 把抗注入用 DPO 训进权重；优化型攻击 ASR 降到 8%/1%（Table 6, p8） |
| **DRIFT** | **NeurIPS 2025** | ✅ `SaFo-Lab/DRIFT` ★62 | 动态规则 + 注入隔离 |
| **The Task Shield** | ACL 2025 | 未查到 | 强制任务对齐防间接注入 |
| **ShadowPlay** | ASE 2025 | `aalosbeh/ShadowPlay`（★0，疑非官方） | 角色型注入与依赖攻击防御 |

### C. 多轮攻击防御（威胁模型最贴，2 篇）

| 论文 | 会议 | 开源 | 备注 |
|---|---|---|---|
| **KG-Guard** | **ICML 2025** | ❌ 未查到 | 知识图谱引导的多轮越狱防御框架 |
| **TurnGate**（上表） | 预印本 | ✅ | 研究"该在第几轮拦"，有最早致害轮 t\* 的形式化 |

### D. 运行时监控 / 护栏（3 篇）

| 论文 | 会议 | 开源 | 备注 |
|---|---|---|---|
| **C-SafeGen** | NeurIPS 2025 | 未查到 | 可认证的流式护栏（claim-based） |
| **TrustAgent** | ACL 2024 | 未查到 | 安全可信 Agent 框架 |
| **R-Judge** | ACL 2024 | ✅ `Lordog/R-Judge` ★116 | Agent 风险意识**基准**，不是防御 |

### E. 执行隔离 / 信息流控制（3 篇）

| 论文 | 会议 | 开源 | 备注 |
|---|---|---|---|
| **IsolateGPT** | NDSS 2025 | ✅ `llm-platform-security/SecGPT` | 执行隔离架构 |
| **Fides** | **NeurIPS**（年份待核） | ✅ `microsoft/fides` ★125 | 信息流控制做形式化保证 |
| **AirGapAgent** | CCS 2024 | 未查到 | 隐私场景的物理隔离 |

### F. 检测 / 基准（3 篇）

| 论文 | 会议 | 开源 | 备注 |
|---|---|---|---|
| **DataSentinel** | **S&P 2025**（第一版写错成 ICML 2024） | 未查到官方 | 博弈论式注入检测 |
| **AgentDojo** | NeurIPS 2024 D&B | ✅ `ethz-spylab/agentdojo` ★985 | SSH 自己也用这个基准 |
| **InjecAgent** | ACL 2024 | ✅ | 间接注入基准 |

**合计：CCF-A 相关论文 19 篇，其中确认开源 11 篇。**

---

## 二、深读过的三篇（原文全文，不是摘要）

### ProbGuard（ASE 2026）——最接近的 CCF-A 开源骨架

**机制**（p3–6）：CTL 不变式 `ψ = AG¬unsafe` → 谓词抽象成 0/1 向量 → `valid_tran` 剪掉不可能的转移 → 数 trace 学 DTMC（Laplace α=1）→ 每步算 `P_safe`，低于 θ 就介入。**全链没有神经网络训练。**

**数字**：具身域 unsafe 40.63% → 2.60%（停@0.9），但完成率只剩 10.42%；引导@0.9 是 14.07% unsafe + 47.74% 完成率（Table 2, p10）。开销缓存后 **5–8 ms**（p10–11）。误报随阈值暴涨：θ=0.3→0%、θ=0.5→75%、θ=0.7→100%（p8）。

**缺**：不生成未来动作；无攻击者模型（威胁是 LLM 自身随机性，无注入）；单阈值，无重采样。

### DreamGuard（预印本，无代码）——概念最像 SSH

**机制**（p3–5）：RSSM + GRU 转移，给定 a_t 算出 h_{t+1}，采样下一时刻隐状态 ẑ_{t+1}，两个 MLP 头在**预测出来的状态**上打分。**深度 1 步，latent 空间，无树无分支。** 双阈值用 split-conformal 定 λ_block/λ_hold → PASS/HOLD/BLOCK。

**为什么值得引**：动机跟 SSH 一模一样（明确对立于 reactive guardrail, p1）；**25 ms/call**，比 TRACES 快 3.3×、GuardAgent 快 250×；SafetyDrift 上 F1 96.4 / FPR 3.7 / PHIR 96.3%、提前 3.63 步（Table 1/2, p6）。

**自己的坑**：只在 SafetyDrift 一个自建基准训练+校准；即时危害基准上提前介入很弱（AgentDojo PHIR 仅 16.8%、ASB 17.3%, Table 2）。

### 批判论文——最该拿去跟导师讨论

**没点名 SSH**（全文 0 次出现 SSH/speculative/honeypot/tree/branch/MCTS），点的是整类范式：

> "...an emerging paradigm of world-model-driven predictive safety guardrails, which use anticipated future consequences to assess risk before execution"（p1）

**三条打得到 SSH 的**：
1. **深度**：h>1 后 recall 和 risk-correlation 明显下滑，accuracy 还看着稳（p7–8）。**SSH 的 D=4 正好落在掉最狠的区间**
2. **归因**：Full Inversion 把风险信号反过来，SAR 反而 90.1、TCR 崩到 13.7（p8, Fig.3）→ "安全分"可能是门控循环刷出来的。**SSH 的增益来自树还是重采样？这篇的对照正是 SSH 缺的 ablation**
3. **忠实性**：零风险预测被拿去给已备好的动作盖章（Cases 4–6, p26）

**硬伤**：没写样本量；没置信区间没显著性检验；摘要说 "seven policy models" 但 RQ1 只有 4 个 backbone（p3–4）。

---

## 三、So what

**1. 她问「有没有开源可以对着做的」**

> SSH 没开源。我系统扫了 CCF-A，最接近的是 ASE 2026 的 ProbGuard——也是"动作前算安全概率、低于阈值就介入"，有代码。但它预测的是符号状态走向，不是"下一步调哪个工具"，也没有攻击者建模。

**2. 她问「SSH 是不是没人做过」**

> **不是没人做，是没人做到这个粒度。** 事前预测这条线有 ProbGuard（ASE 2026）、DreamGuard（预印本）、TurnGate（预印本）；多轮防御有 KG-Guard（ICML 2025）、TurnGate；注入防御有 SecAlign（CCS 2025）、DRIFT（NeurIPS 2025）。**但"未来摊成树 + 真实动作剪枝 + 三模拟器分工"这套组合，扫遍 CCF-A 只有 SSH。**

**3. 对卫星场景最值钱的数字**

DreamGuard 的 **25 ms/call** ——比 SSH 的"3–7 秒误报延迟"友好得多。做星上轻量化，这个数比 SSH 自己的更有说服力。

**4. 下一步（2 分钟）**

clone `SaFo-Lab/DRIFT` 和 `Graph-COM/TurnGate`，看它们的代码组织——DRIFT 是 NeurIPS 2025 真开源，TurnGate 有现成的"最早致害轮 t\*"标注格式，**卫星多步攻击链可以照这个标**。

---

## 四、这次覆盖到什么程度（诚实边界）

**覆盖到的**：
- 51 个查询，8 个词族，两轮
- CCF-A 会议清单（17 个）+ 2023 至今
- OpenAlex 全文检索 + 会议字段过滤

**没覆盖到的，要补还得再花时间**：

1. **期刊没扫**——TDSC / TIFS / TSE / TOPS 也是 CCF-A，这轮只扫了会议
2. **会议名匹配是启发式的**——OpenAlex 的 source display_name 五花八门，可能有会议被漏判（比如只写 "Proceedings of the 2025 ACM SIGSAC Conference"）
3. **OpenAlex 全文索引有滞后**——很新的论文（2026 下半年）可能还没进去，所以我另外用 arXiv 补了 DreamGuard 和批判论文
4. **新找到的这批只核实了"会议+题目+是否开源"，没深读方法**：KG-Guard、ShadowPlay、C-SafeGen、The Task Shield、TrustAgent、R-Judge、AirGapAgent、DRIFT、DataSentinel
5. **非英文文献没扫**

**所以说"全"是不敢的。能说的是：在 17 个 CCF-A 会议、2023 至今、51 个英文查询这个框里，该扫的扫了，结论稳定。**

---

## 五、前提声明

**从 PDF 原文读到的**：ProbGuard、SelfDefend、TurnGate、DreamGuard、SecAlign、批判论文——会议归属、数字、页码、代码地址。

**从 OpenAlex 元数据得到的（没读原文）**：KG-Guard、DRIFT、ShadowPlay、C-SafeGen、The Task Shield、TrustAgent、R-Judge、AirGapAgent、DataSentinel——只核到"会议+题目"，**引用前必须读原文**。

**推定待核**：
1. **SelfDefend 的 USENIX Security 2025**：本地是 arXiv 版，首页没印会议，依据是文件名+致谢 "shepherd"+议程
2. **Fides 的 NeurIPS 年份**：arXiv comment 为空
3. **DRIFT 的仓库是否官方**：`SaFo-Lab/DRIFT` ★62 看着像，但要读原文确认
4. **ProbGuard Table 3** 有一格上标 `530–10^5`，按 5.30×10⁵ 读

**原文 PDF**：`阶段2-卫星多智能体防御/papers/开源同类调研/`（8 篇）
