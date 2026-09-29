# A5 笔记：Crescendo —— 多轮渐进式越狱

> **论文**：Great, Now Write an Article About That: The Crescendo Multi-Turn LLM Jailbreak Attack
> **作者**：Mark Russinovich, Ahmed Salem, Ronen Eldan（**Microsoft Azure**）
> **出处**：arXiv:2404.01833（2024，这篇稍早，但被 A1 引为多步攻击的代表）
> **本地 PDF**：`papers/A5 - Crescendo Multi-Turn Jailbreaking (2404.01833).pdf`（20 页）
> **一句话**：一种**多轮**越狱攻击——从无害的问题开始，**每次都引用模型自己上一轮的回答**逐步升级，最后把模型带到它本来会拒绝的地方。

---

## 一、为什么它是"逐步篡改认知"的标准范式

A1 的攻击大多是**单次**注入（只是效果会级联）。**Crescendo 是真正"多步"的**——攻击力不从单条提示来，而来自**对话历史的累积**。

论文的定义（摘要原话）：

> It begins with a general prompt or question about the task at hand and then **gradually escalates the dialogue by referencing the model's replies** progressively leading to a successful jailbreak.

**关键机制**：每一步都**引用模型自己上一轮说过的话**当依据。所以模型在每一轮里都"觉得"自己是在延续一个它已经同意的方向——**这就是"篡改认知使其合理化"**。

---

## 二、攻击效果

**测了这些系统**：ChatGPT、Gemini Pro、Gemini Ultra、LLaMA-2 70B、LLaMA-3 70B Chat、Anthropic Chat。

**自动化工具 Crescendomation**（已开源，集成进微软的 PyRIT），在 AdvBench 子集上：

| 对比对象 | 提升 |
|---|---|
| vs GPT-4 上其他 SOTA 越狱方法 | **+29% ~ +61%** |
| vs Gemini-Pro 上其他 SOTA 越狱方法 | **+49% ~ +71%** |

**还能破多模态模型**——让它们生成本来会拒绝的图片。

**转移性**（换模型用）：任务依赖很大。比如 "Election" 任务在两个模型上都 ≥90%，但 "Explicit" 和 "Manifesto" 几乎 0%。

---

## 三、为什么它难防（这段对你最重要）

论文反复强调：

> As Crescendo employs **benign questions and prompts** to execute the jailbreak, it poses a **significantly greater challenge for detection and mitigation** compared to other techniques.

**每一轮单看都是无害的**——所以：
- 单轮输入过滤器抓不到
- 靠"检测恶意提示"的思路失效
- 论文指出：**现有缓解措施主要针对单轮越狱，忽略了这种更简单但可利用的方法**

**它的本质局限**（也是防御机会）：**Crescendo 必须是多轮的**——所以**没有对话历史功能的系统天然更难被攻破**。

---

## 四、论文给的缓解方向

1. **训练数据预过滤**——排除可疑内容（但不彻底，且重训成本高）
2. **用 Crescendo 数据做对齐**——拿自动化工具生成攻击样本，反过来做安全对齐
3. **在多轮上做检测**——这是论文隐含的方向：既然攻击靠累积，防御也要看**整条对话轨迹**，而不是单轮

---

## 五、★ 映射到你的卫星场景

| Crescendo 的特点 | 对卫星防御的启示 |
|---|---|
| 每轮单看都无害 | **单点的输入过滤必然失效**——你导师说的"单步防御拦不住"就是这个意思 |
| 靠累积对话历史升级 | 防御必须**看轨迹**（多轮的状态），不是看单条消息 |
| 引用模型自己的回答当依据 | **模型自己的历史输出会变成攻击的"燃料"** → 所以要**给历史输出打标记/降权** |
| 必须多轮才能生效 | **限制轮次、强制状态重置**是最粗暴但有效的缓解 |
| 论文承认现有缓解只针对单轮 | **多轮防御是公认空白** ← 你的位置 |

**最该记住的一条**：**攻击的力量来自"累积"，所以防御的力量也必须来自"累积的检查"**——每一轮都比对"当前认知"和"初始意图"的偏差。这就是"连环锁"的技术含义。

---

## 六、局限

- 论文承认缓解方案都**不完备**（预过滤不彻底、重训昂贵）
- 需要多轮交互——**没有历史的系统更难攻破**（这也是它的适用边界）
- 转移性不稳定，任务依赖强

---

## 七、一句话总结

**Crescendo 用"每轮都无害"的方式，靠累积对话历史把模型一步步带到违规区——单轮检测对它无效，因为攻击力不在任何单条消息里，而在轨迹里。**
