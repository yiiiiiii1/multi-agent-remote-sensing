# 新增 7-8：CMU「认知脆弱性」一篇 + S-LARF 一篇

> 结论先说：**这两篇都没有占掉「卫星场景下的认知层防御」。**
> CMU 那篇的标题是个陷阱——三个词都有，但内容只到「动作面硬化 + 输出纪律」。
> S-LARF 打的是星载 ML 检测器，对象根本不是一个 Agent 的信念。

---

## 一、Governing the Intelligence Loop（CMU，Khadija Taki，Heinz College）

### 出处与获取

- 原文链接（Kilthub）：`https://kilthub.cmu.edu/articles/preprint/.../33941098?file=68975056` —— 直连 403
- **实际拿到全文的路径**：Zenodo 镜像，DOI `10.5281/zenodo.22839735` → 文件 record `22860486`
  - `https://zenodo.org/api/records/22860486/files/Governing_the_Intelligence_Loop.pdf/content`
- **已落盘**：`papers/新增7 - Governing the Intelligence Loop (CMU preprint 2026).pdf`
- 规格：**4 页**，单作者，2026-09-20 预印本，**无会议/期刊**

### 这篇到底做了什么（一句话）

用 CrewAI 搭了一个三 Agent 的「航天网络威胁情报（CTI）报告写作流水线」，然后证明：**不给下游 Agent 任何工具 + 往系统提示里塞 10 条写作规矩，就能少编 CVE 号、少丢引用、被注入也不执行命令。**

### 关键结论：它没有定义 "Epistemic Fragility"

全文检索 `epistemi`，只有 5 处命中，**没有一处在下定义**：

| 位置 | 用词 |
|---|---|
| 标题 | Epistemic Fragility |
| §I.B 正文 | "introduce severe epistemic liabilities" |
| §I.B 小标题 | "Epistemic Failure Modes of Generative AI" |
| §I.B 正文 | "introduces fundamental epistemic vulnerabilities" |
| §VII 结论 | "reduces epistemic degradation" |

**"Epistemic Fragility" 只活在标题里。** 正文实际拿出来的，是 §I.B 的四条清单：

1. **Hallucination and Fabrication** —— 编出不存在的 CVE 编号 / 假称已被在野利用
2. **Provenance Erasure ("Sinking Citations")** —— 多 Agent 串起来推理时，标题、日期、段落级引用一路丢
3. **Uncalibrated Certainty** —— 拿猜测当结论说，违反 ICD 203
4. **Action-Surface Vulnerabilities** —— 给了 shell / file / web 工具，于是能被间接提示注入

**要害：第 1、2、3 条根本没有攻击者。** 那是模型自己写得不干净，是一个"文风 + 纪律"问题。
只有第 4 条有攻击者，而它的解法是**把工具拿走**——让 Agent 执行不了，不是让它不信。

### 被指的系统是什么

**不是卫星 Agent，不是星上系统，是一个"读文档、写简报"的离线流水线。**

- 输入：一个**已批准的文档语料** D = {d1..dn}（讲航天威胁的通告、论文、漏洞报告）
- 三个角色：Collector（原样抽字段）→ Analyst（打 ATT&CK / ATLAS 标签、判严重度）→ Writer（写简报）
- 输出：一份三段式文字简报（What Happened / Why It Matters / What to Watch）
- **不接卫星、不读遥测、不下指令、不碰遥操**

> **"space" 是它分析文档的题材，不是它运行的战场。** 这点最容易看错。

### 它给的「架构缓解」具体有 7 条

1. **工具与推理解耦**：Analyst 和 Writer 初始化 `tools = []`，零工具沙箱。"代码执行在数学上不可能"——这是它唯一敢说 deterministic 的保证
2. **Collector 收权限**：只给一个 `FileReaderTool`，路径白名单不可变，只允许读 approved 目录下的 txt/md
3. **Guardrails-as-Prompt**：10 条写进系统提示的规则。规则 1–5 管结构边界，6–8 管 ICD 203 行规（必须署名来源、必须显式对冲不确定性、缺数据必须拒绝编造），9–10 管密级标注
4. **入口防火墙**：独立 FastAPI 服务，用**纯字符串关键词计数**打分 s(t)=ΣI(k∈t)，τ≥2 进人工审批队列。作者明说**故意不用向量检索/分类器**，怕在入口就把注入面重新打开
5. **密码学溯源链**：SHA-256(source) → R_i → E_i → Brief，一路可审计
6. **元数据不许模型生成**：时间戳、run ID、密级横幅必须由 runtime 包装层注入。这条是因为他们真踩过——Writer 把 2025 年的文档写成了 2023 年 9 月的简报
7. **Human-on-the-loop**：人只在两个边界上出现——批入口文档、终审溯源

### 实验

**有，但规模很小，而且是"前后对比"，不是消融。**

设置：3 篇文档（空基对抗扰动 / 地面天线 PLC 的 RCE，CVSS 9.8 / GPS 欺骗），N=10 次试验，每条件 30 条观测。对比「无治理基线（工具全开、有 shell、无规矩）」vs「治理架构」。

| 维度 | 无治理 | 治理后 |
|---|---|---|
| 幻觉率（编 CVE / 编攻击者） | 23.3% (7/30) | **0.0% (0/30)** |
| 溯源保留（精确引用） | 40.0% (12/30) | **100.0% (30/30)** |
| 跨文档张冠李戴 | 30.0% (3/10) | **0.0% (0/10)** |
| 注入下的工具执行 | 80.0% (8/10) | **0.0% (0/10)** |

规则遵守率：规则 6/8/9 都是 100%（30/30），规则 7（不确定性对冲）93.3%（28/30）。

**作者自己承认的四个软肋（§V.C，原文就写了）：**

- 幻觉和混同的下降是**整包 guardrail 的联合效果**，拆不开每条规则的贡献，要拉丁方消融——没做
- 打分是**单标注员**，双盲多标注协议只是"已形式化"，没跑
- 注入那个 80%→0% 是**"移除工具接口"必然推出来的**，因果上无争议，但也因此**不构成任何认知层证据**
- 只有 3 篇文档、30 条样本

### 跟这个课题什么关系

- **它管的是「动作」还是「认知」？** 管动作。`tools = []` 是动作面硬化；入口关键词过滤 + 人工审批是入口把关；密码学溯源链是输出可审计。唯一沾认知的是第 6 条（元数据别让模型自己编）和第 3 条（写作纪律），两个都是**输出格式约束**，不是**信念状态建模**
- **它的"认知"和这个课题的"篡改认知"是一回事吗？** 不是。它的"认知问题"是**模型自己手不干净**（编号、丢引用、不校准），三条里没有攻击者；这个课题的"篡改认知"是**有对手、分步、通过合法渠道把假事实喂进去，让 Agent 形成一个错误但自洽的判断**。它连"Agent 相信什么"这个变量都没有建模——全文没有 belief state、没有跨步一致性、没有多 Agent 事实冲突检测
- **它把注入的"执行面"堵死了，但完全没管"信念面"。** 一个零工具 Agent 读到注入内容、把它当事实写进简报，任务照样彻底失败——而**这个场景它一次都没测**。它测的是"did it execute"，不是"did it believe"
- **有没有占掉方向？** 没有。它占的是「航天 CTI 报告生成 + 工具最小权限 + 溯源审计」这一格。而且它是 4 页政策学院预印本、单作者、单标注员、30 条样本，**证据强度撑不起"这块已经做完"**

### 它自己留给我们的缝

- §IV.D 明说入口防火墙是"可解释的关键词筛查、不是高召回语义检索"，**把它升级成隔离的语义检索区是 future work**——它知道入口是软肋，然后踢给了未来
- §V.C 承认只做了单步注入探针，没有多步
- 全文没有算力/轻量化成本讨论（地面 CrewAI + FastAPI 栈）
- 场景不是卫星运行：没有轨道参数、没有遥测、没有指令、没有遥操完整性

---

## 二、S-LARF: Layered Adversarial Resilience Framework for spaceborne anomaly detection

### 出处

- International Journal of Critical Infrastructure Protection, **Vol. 53 (2026), article 100851**
- DOI `10.1016/j.ijcip.2026.100851`
- 作者：Fadwa Belali, Abdellah Essetty, Slimane Bah
- 关键词：Adversarial machine learning / Space cybersecurity / NewSpace / Anomaly detection / Cubesats

### 读到了什么程度（重要）

**只读到摘要，正文没读到。** 逐个试过、全部失败：

| 路径 | 结果 |
|---|---|
| ScienceDirect 原文 | 403 |
| ScienceDirect abs / pii 变体 | 403 |
| `sdfe/arp/.../first-page-pdf` | 404 |
| ACM DL `10.1016/j.ijcip...` | 403 Cloudflare |
| dlnext.acm.org | 403 Cloudflare |
| Semantic Scholar API | 摘要被出版方 elide，返回 null |
| OpenAlex | 闭源，无摘要 |
| Unpaywall | `oa_status: closed`，`any_repository_has_fulltext: false` |
| colab.ws / ouci / scilit / oa.mg / x-mol | 403 / 503 / 无结果 |
| r.jina.ai / allorigins / codetabs 代理 | DNS 或 5xx |

**唯一拿到的是 Elsevier 存进 RePEc 的那段摘要，全文两句话（经 IDEAS 与 EconPapers 交叉验证一致）：**

> The rapid adoption of Artificial Intelligence (AI) and Machine Learning (ML) in CubeSat missions enables increased onboard autonomy and advanced telemetry monitoring, but it also introduces new cybersecurity risks associated with adversarial machine learning (AML). Existing space cybersecurity frameworks provide general guidance, yet do not explicitly address ML specific threat models and interaction driven attack surfaces arising from onboard anomaly detection.

**方法、层次怎么分、实验结果、有没有数字——全部不知道。不编。**

### 能说什么（只基于标题 + 摘要 + 关键词）

- 场景：**CubeSat 星上**（onboard），做的是**遥测异常检测**，为的是提高在轨自主性
- 威胁：**对抗机器学习（AML）**——即攻击者精心构造输入，骗过星上那个异常检测模型
- 缺口主张：现有航天网络安全框架只给通用指引，**没覆盖 ML 特有的威胁模型**，也没覆盖"onboard anomaly detection 带来的交互式攻击面"
- "Layered" 按字面是分层防护（defense in depth），但**具体是哪几层、每层做什么，正文没读到，不知道**

### 跟这个课题什么关系

- **它管的是「动作」还是「认知」？** 两个都不是，它管的是**「模型鲁棒性」**。对象是一个"判断输入是否异常"的 ML 分类器，不是 LLM Agent，也不是多 Agent 编排
- **它的"被篡改"和这个课题的"篡改认知"是一回事吗？** 表面像（都是"数据被动手脚"），实质不同。它防的是**对抗扰动**：给输入加人眼看不见的噪声让分类器判错，这是**单步、数学优化出来**的攻击，处理方式是鲁棒训练/检测/集成。这个课题防的是**语义级、分步、用自然语言**把 Agent 的世界模型推到错误位置。两者连失败模式都不是一类
- **跟"轻量化"有关吗？** 有关但方向不同：它在星上算力约束下做鲁棒性，是**模型效率 vs 鲁棒性**那条线；这个课题的轻量化是**多 Agent 防护机制本身要小**。可以引它当"星上算力受限是真实约束"的旁证
- **有没有占掉方向？** 没有。它连"Agent"这个词都不在对象里

---

## 三、对「所有防御都在看动作」这个判断的影响

**两篇都没推翻它，CMU 那篇还反过来加固了它。**

CMU 那篇是这批文献里离"认知"最近的，结果一看：它把"认知失败"降维成了三种**无攻击者的写作毛病**加一种**有攻击者的执行面**，然后用"拿走工具"一次性解决。它测的四项指标（幻觉率、溯源率、混同率、工具执行率）里，**前三项是输出质量，第四项是动作拦截，没有一项是"Agent 当前相信什么、这个信念跟证据是否一致"**。

所以：
- 「动作」这一侧：有 CaMeL、B2 设计模式、VIGIL、这篇 CMU，很挤
- 「输入真伪」这一侧：有 S-LARF 那类对抗 ML 工作，也不空
- 「Agent 的信念状态」这一侧：**还是空的**。这篇 CMU 甚至明确说了"下游 Agent 是 isolated memory context"——它是靠**切断信息流**来阻止污染，不是靠**检测污染**

### 可直接用作"最近的先验工作"的对比句

> 最接近的工作（Taki, 2026）在航天威胁情报流水线上用零工具沙箱消除了间接提示注入的执行面，并用提示级规则把幻觉从 23.3% 压到 0%；但其评估维度全部落在输出格式与动作拦截上，未建模 Agent 的信念状态，也未考虑分步注入下的信念漂移。

---

## 四、下一步该干的（两分钟能动手的）

1. 把 `补课文档-读完这份就知道差什么.md` 第 229 行那个「★ 跟你场景直接撞」改掉——**不撞**，改成「标题撞、内容不撞，可用作最近的先验工作」
2. S-LARF 走学校图书馆的 ScienceDirect 权限下一份 PDF，或者给通讯作者（Slimane Bah，Mohammed V University）发一封要 preprints 的邮件
