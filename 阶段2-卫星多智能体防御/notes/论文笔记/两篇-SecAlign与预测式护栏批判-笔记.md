# 两篇：SecAlign（CCS'25）与《Predictive Safety Guardrails Do Not Always Make LLM Agents Safer》

读法：两篇 PDF 全文用 pymupdf 提取逐页读完，页码按 PDF 物理页（= 正文页码，两篇一致）。

---

## 论文 A：SecAlign: Defending Against Prompt Injection with Preference Optimization

- **会议**：CCS '25（ACM SIGSAC Conference on Computer and Communications Security），2025 年 10 月 13–17，台北。**正会**，15 页，DOI 10.1145/3719027.3744836。（p1）
- **核心问题**：微调式注入防御一碰到训练时没见过的优化型注入就垮（StruQ 在 GCG 类攻击下 >50% ASR，p1），原因是不是训练目标只教模型"该输出什么"、没教它"不该输出什么"——如果把"抗注入"当成一种偏好来优化，能不能在不掉通用能力的前提下泛化到未见攻击？
- **方法机制**：
  1. 拿公开指令微调集（Cleaned Alpaca）造偏好三元组 (x, y_w, y_l)：往 data 段末尾塞**另一条样本**的指令当注入（90% Straightforward / 10% Completion），于是 y_w = 本条的回答，y_l = 被注入那条样本的回答。注入不用人写。（p6, Algorithm 1）
  2. 用 DPO 优化 Eq.(3)，β=0.1，最大化 y_w 与 y_l 的对数似然间隔。LoRA r=64，4×A100，3 epoch。（p5, p8）
  3. 关键洞察：分类器上"鼓励 y*"≈"压制 y'"，但 LLM 输出空间是 V^L，"只最大化 p(y_w|x)"（Eq.1，StruQ 的做法）跟"压低 p(y_l|x)"只是弱相关——这就是已有防御脆的根因。（p5）
  4. Fig.2 证据：StruQ 把 y_l 的 logprob 压到 −140，SecAlign 压到 −300，y_w 不掉。（p5）
- **与 SSH 的异同**：见下节"关系"。
- **实验**：
  - 数据：AlpacaFarm 805 条评通用能力、其中 208 条带 data 段评安全；训练用 Cleaned Alpaca（与评测不同域）；另加 SEP（9.1K）、InjecAgent。（p7, p10）
  - 指标：AlpacaEval2 WinRate（GPT-4-turbo 当裁判）+ Max ASR。
  - 对手：3 个免优化攻击（Ignore / Completion / Ignore-Completion）+ 3 个优化型（GCG、AdvPrompter、NeuralExec），5 个模型。
  - 数字：Llama3-8B-Instruct 优化型 ASR 降到 **8%**、Mistral-7B-Instruct **1%**；未防御 89%/97%，StruQ 27%/45%；免优化攻击全 5 模型 **0%**。（p8, Table 6）
  - Table 2（p10）免优化 Max ASR：Llama3-8B-Instruct None 51 / In-Context 0.5 / SecAlign 0；Llama-7B None 75 / In-Context 45 / SecAlign 0。
  - Table 3（p10）OOD：SEP ASR start/middle/end = 11.0 / 3.6 / 6.5（None 54.7/39.5/64.0；StruQ 2.1/0.1/0.1 但 utility 只剩 18.9），SecAlign SEP utility 46.6 vs None 50.0；InjecAgent ASR 0（None 75.9，StruQ 2.2）。
  - Table 1（p9）BIPIA 设定下：WinRate 62.94 → 61.92（BIPIA 掉到 32.29），ASR 36 → 0。
  - Table 4（p10）通用能力：MMLU 掉 2–3 分（62.7→59.5、65.3→63.1），Winogrande/AGIEval/CommonSenseQA 基本平。
  - Table 5（p11）DPO vs ORPO vs KTO：GCG ASR 15 / 34 / 9，GPU 时长 2×4 / 1.5×4 / 10×4 小时。
  - Fig.6（p11）：只用 20% 训练数据，ASR 仍低于用全量的 StruQ。
- **代码**：https://github.com/facebookresearch/SecAlign （p1 正文"Our code is here."的超链接）。后续 70B 版见引文 [24] Meta SecAlign。
- **自陈局限**（p12）：必须指令/数据有明确分隔符；做不到 100%；注入在 data 末尾时最有效；只管注入不管越狱/数据抽取；明说"We do not regard SecAlign as a standalone solution"，建议和检测类（PromptGuard/Prompt Shields）叠成多层。
- **一句话判断**：这是"把防御训进模型权重"的路线，和 SSH 的"外挂一个推演监控器"正交；它给了你一个可引用的强 baseline（≤10% ASR、不掉能力），也给了你一个把柄——它需要白盒 + 明确分隔符 + 重训，星上小模型场景里这三点都难。

---

## 论文 B：Predictive Safety Guardrails Do Not Always Make LLM Agents Safer

作者：Weixiang Zhao, Zhihao Liu, Guancheng Li, Yanyan Zhao, Bing Qin, Ting Liu（哈工大）。

- **会议**：**论文没写会议**。首页只有 `arXiv:2611.02815v1 [cs.AI] 2 Nov 2026`（p1），是纯预印本，没有任何会议/workshop 字样。
- **核心问题**：预测式护栏的收益到底从哪来——是真的"预测得准 + 决策照着预测改"，还是只是"多了几道门 + 多问了几次"？把预测→行动这条链拆成三段（怎么整合、预测准不准、决策信不信）分别体检。
- **它反驳的具体论点（逐条 + 页码）**：
  1. **"预测介入越深越安全"** → 不单调。Prediction-Informed 让 Qwen3.5-27B 的 HA SAR **−3.41**、GLM-5.3-Flash **−1.87**，只有 GPT-5.6-Terra +2.61；Prediction-Constrained 把 Terra 的 SAR 抬 +5.78 但 TCR 掉 −4.66。（p5, Table 1）
  2. **"多花算力换安全"** → 换来的是 6.31×（数字流程）/ 3.15×（家务）token，安全和完成率都不保证。（p6, Table 2）
  3. **"预测改变了行为 = 预测起了作用"** → HA 上调用率 25.00–47.47%、动作改变率 88.10–95.29%，但安全改善只有 0–20%，Terra 是 **0.00%**。（p5–p6, Table 3）
  4. **"总体准确率能代表安全预测能力"** → 非风险样本占多数时，accuracy 可以很高而 risk recall / RC 很低；accuracy 更高的模型反而漏更多风险。（p7–p8, Fig.2）
  5. **"短期准 = 长期也准"** → h>1 之后 risk recall 和 RC 明显下滑，而 accuracy 看着还稳。（p7–p8；作者自己承认"degradation is not strictly monotonic for every model and condition"，p7）
  6. **"预测可靠 → 决策就会用"** → 5 种扰动下安全增益还在：Irrelevant 让 SAR +3.46 却让 TCR −10.49；**Full Inversion 反过来给风险信号，SAR 反而 90.1 / AVS 88.6，但 TCR 只剩 13.7**。（p8, Fig.3）
  7. **"逐动作本地验证 → 轨迹安全"** → Sandbox 反馈 84.7 SAR / 85.3 AVS / 78.3 TCR，后续违规照旧存在。（p8）
  8. **"模型会把预测当证据"**（定性）→ 零风险预测被用来给已备好的动作盖章（Cases 4–6，p26）；照着不可行建议做、失败后继续冒险动作（Case 7，p27）。
- **实验设计与证据强度**：
  - 结构：RQ1 在线（3 种整合档 × 4 个 backbone × 2 环境）；RQ2 离线（7 个预测模型 × {Direct, Iterative} × {Full, Train-derived, Generic} × 时域 h1–h6 / h1–h3）；RQ3 在线（8 个反馈条件，Qwen3.5-27B 主表 + GLM/Gemini 附录）。
  - 环境：HarnessAudit-Bench（HA，数字工作流，p3/p16）+ IS-Bench（家务具身，p3）。
  - 证据类型：**纯实验诊断，没有定理、没有界、没有形式化证明**。是"实验反例 + 机制拆解"，不是证明。
  - 样本量：**论文没写**——全文没有任何轨迹数 / 任务数 / 随机种子数（我逐页找过）。这是它最硬的弱点。
  - 统计：没有置信区间、没有显著性检验；−1.87 这种量级的差值完全可能在噪声里。
  - 抽象与正文不一致：摘要说 "seven policy models"（p1），RQ1 实际只有 4 个 backbone（p3–p4），7 是 RQ2 的预测模型数（p6）。引用时要注意。
  - 最有说服力的一条：Full Inversion 把风险信号反了，SAR 还能到 90.1 而 TCR 崩到 13.7（p8）——这是干净的 dissociation，说明"安全分"是门控循环刷出来的，不是预测内容带来的。
- **是否点名 SSH / 推测类方法**：
  - **没有点 SSH**，全文 0 次出现 "SSH"、"speculative"、"honeypot"、"tree"、"branch"、"MCTS"。
  - 点的是**这一整类范式**，原话：`"...an emerging paradigm of world-model-driven predictive safety guardrails, which use anticipated future consequences to assess risk before execution"`（p1）。
  - 具体点名的系统是 SafePred、SafeMCP、JANUS、SeerGuard（p3），都是单步/直接预测 + 门控，**没有一个是多分支树状推演**。
  - 唯一擦边：p4 说为了不在 RQ1 引入 `"an additional recursive rollout procedure"` 而只用 Direct 模式——即**它主动回避了 SSH 那种 rollout**。
- **对 SSH 的实际威胁**：**限制适用条件，不是驳倒。**
  - 打不到的地方：SSH 的核心主张（动手前把未来摊开比只看历史强）它没测；它也没跟任何训练时防御比；它的"预测"是单次 Direct 判断，不是 M=5/D=4 的树。
  - 打得到的地方，三条：
    1. **深度**：SSH 的 D=4 正好落在它测出 recall/RC 掉得最狠的区间（h>1）。树叶子如果是这种质量，"看叶子判风险"的地基就松了。
    2. **归因**：SSH 报的增益可能来自告警后的重采样/引导（最多 5 次），不是树本身。这篇的 Full-Inversion 对照正是 SSH 缺的那个 ablation——SSH 需要一个"把树打乱/换成随机树"的对照才能证明前瞻内容有用。
    3. **忠实性**：SSH 的检测器读叶子，若 policy 把低风险当绿灯，同样的"预测当安慰剂"失效模式套得上（对应 p26 Cases 4–6）。
  - 反过来也要防它：这篇自己的设定比 SSH 弱（单步预测 + 一道门），在此处的负结果不能直接外推到树状推演。
- **代码**：github.com/REH502/rethinking-predictive-safety （p1 摘要末尾）。
- **一句话判断**：**很适合拿去跟导师讨论边界**——它不否定"往前看"，但给了三个必须回答的问题（增益归因、长时域可靠性、决策忠实性）和一份现成的 ablation 清单；引用时把它当"批判性 checklist"而不是"已定论的证据"，因为它没写样本量、没有显著性检验、还是 1 天前的预印本。

---

## 两篇与 SSH 的位置关系（一页话）

| | SecAlign | 预测式护栏批判 | SSH |
|---|---|---|---|
| 介入时机 | 训练时（改权重） | 推理时（外挂门控） | 推理时（外挂推演） |
| 需不需要白盒 | 要（DPO 重训） | 不要（调 API 即可） | 不要（但模拟器是自己训的） |
| 看几步 | 单次调用 | 单步预测 + 门控 | M=5 分支 × D=4 深 |
| 输出 | 直接给安全回答 | 风险分 + 阻断 | 风险分 + 引导/重采样/终止 |
| 对星上小模型 | 重训成本高、要分隔符 | 便宜、可插拔 | 便宜、可插拔 |

一句话：SecAlign 是"把模型训硬"，批判那篇是"证明外挂门控不一定管用"，SSH 要活着就得证明"外挂推演比外挂门控多赚的那部分，确实来自推演"。
