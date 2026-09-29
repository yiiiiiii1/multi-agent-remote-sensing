# 汇报卡片 C1：GeoLLM-Squad（遥感落地 · 多智能体地理空间 Copilot）

> 论文：Multi-Agent Geospatial Copilots for Remote Sensing Workflows
> 作者：Chaehong Lee, Varatheepan Paramanayakam, Andreas Karatzas 等（UT Austin / Southern Illinois University / **Microsoft**）· arXiv:2501.16254 · 2025
> 本地 PDF：`papers/Soni 等 - 2025 - Multi-Agent Geospatial Copilots for Remote Sensing Workflows.pdf`
> 汇报定位：**唯一一篇把多智能体用在我研究的领域、并给出量化提升的论文**。它回答的正是我的核心疑问——"多智能体到底比单智能体强在哪、强多少"。

---

## P1 动机与难点

### 这篇论文要解决什么问题
遥感工作流本身很复杂——需要多种数据、工具和分析方法，还要有隐性的地学专业知识。举例：同一片区域，若云量超过阈值，地学家会用**地面站温度数据或 SAR 影像**替代地表温度（SLT）产品和光学影像。这种"**SAR-over-EO**"的隐性判断逻辑，很难通过提示词硬塞给现有的地理空间 Copilot。

### 难点（论文自己点名的）
1. **单体 LLM 是瓶颈**：有限上下文窗口和 token 容量，撑不起真实遥感应用需要的时空尺度。
2. **专业逻辑难以提示词化**：像"云量高就换 SAR"这种条件判断，靠堆 prompt 无法稳定实现。
3. **工具规模爆炸**：任务一多，工具数量从几十涨到几百，单体 Agent 的上下文装不下。
4. **云端成本**：论文特别指出，要求必须用 GPT 级模型做编排，对地学家来说成本太高——所以多智能体系统还必须能跑在**开源小模型（SLM）**上。

### 研究目的
提出 **GeoLLM-Squad**：把"**智能体编排**"和"**地理空间任务求解**"**拆开**——主 Agent 只负责拆解任务和调度，具体任务交给一个个专职 sub-agent。以此突破单体 LLM 的上下文瓶颈。

---

## P2 模型

### 核心思路：编排与求解分离
这是全篇最重要的一句话：**Unlike existing single-agent approaches that rely on monolithic LLM, GeoLLM-Squad separates agentic orchestration from geospatial task-solving.**

- **Orchestrator（编排者）**：接收用户请求 → 分解成子任务 → 为每个子任务生成清晰提示 → **安排执行顺序**（例如必须先 load 再 filter）。
- **专职 Sub-agents**：每个子任务交给一个专职 Agent，各自持有自己的**专属工具集**。

### 编排到底怎么编（论文原话拆解）

论文原文（III. Methodology · Orchestrator）：

> Our scheduling follows **compositional reasoning** to devise **program-like schedules in natural language**, which specify **the sequential set of agents to execute the task and their (sub)prompts**. Execution follows the prescribed schedule, and the Orchestrator **aggregates return messages to check task completion**. **If incomplete, the schedule is revised and the loop is repeated**.

拆成三步：

1. **编排者生成"排班表"**：不是让 Agent 自由聊天，而是直接产出一段**程序式排班表**——哪些 Agent、按什么顺序、每个的提示词是什么。
2. **按表执行**：轮到谁，谁就跑自己的工具集，跑完把结果消息**交回编排者**（Agent 之间不直接通信）。
3. **闭环**：编排者汇总所有返回消息，检查任务完成没。没完成就**改排班表重跑**；完成则把最终结果和更新后的地图返回用户。

**论文给的完整例子**（用户："从 2024 年 NDVI 数据，推荐 Brisbane 的轮作区域并在图上显示"）：

```
schedule = [ Database  (Load NDVI..),
             DataOps   (Filter Brisbane),
             Agriculture (Recommend crop rotation areas based on ..),
             Map       (Plot..) ]
```

四个要点：**顺序由编排者定**（load 必须先于 filter）、**每个 Agent 只拿到自己的 sub-prompt**、**每个 Agent 只管自己的动作空间**（农业 Agent 的工具里直接有"基于低 NDVI 聚类推荐轮作"，不需要自己加载 NDVI 数据）、**Agent 之间零通信**。

### 它的协作方式：中心化 · 星形 · 零 Agent 间通信

**这是本卡片最容易被追问、也最能体现读懂的一点**：GeoLLM-Squad 严格说**不是"多个 Agent 一起商量"，而是"一个调度器写程序、一堆执行单元按序跑"**——本质是把单体 Agent 的上下文压力**拆开**，不是把智能拆开。

| 系统 | Agent 之间通信吗 | 协调靠什么 |
|---|---|---|
| CAMEL | 是（点对点双 Agent） | 角色设定 |
| ChatDev | 是（对话链） | Chat Chain |
| MetaGPT | 是（发布订阅共享池） | SOP |
| AutoGen | 是（可编程拓扑） | 开发者定义 |
| AgentVerse | 是（讨论 + 评审） | recruiter + 评估反馈 |
| **GeoLLM-Squad** | **否** | **编排者的排班表 + 完成度检查** |

**两个容易被说错的术语**（讲的时候要分清）：
1. **是星形，不是层级**。严格意义的"层级结构"指多层（组长管组员、主管管组长）；GeoLLM-Squad 只有**一层**——编排者在顶，7 个 Agent **平级**在下面，谁也不管谁。真正算多层的是 MetaGPT（PM→架构师→项目经理→工程师→QA）和 MacNet 的 Layer 拓扑。
2. **是调度员，不是主管**。编排者有**调度权**（谁先跑、谁后跑、给什么提示词），但没有**管理权**——不能改 Agent 职责、不能招人、不能开除人、不能让 Agent 互相商量。对比 AgentVerse：那里有**真的 HR**，会按任务现场招人、淘汰不合格的人；GeoLLM-Squad 的 7 个 Agent 是**写死的名单**。

**纠错粒度：事后，最粗**。一轮内部 Agent 跑完只把 message 交回编排者，编排者**不中途干预**；只有**整条流水线跑完**才检查完成度并决定是否重排。对比：AgentVerse 有 evaluation Agent 在**执行前**把关，MetaGPT 有**可执行反馈**（跑测试读错误）。GeoLLM-Squad 的纠错发生在事后，粒度最粗——编排者一旦排错顺序，整条链就错了，**没有 Agent 能中途纠正**。

**它买的是"隔离"**：521 个 API 工具被分散到各专职 Agent，每个 Agent 上下文里只装自己那几个工具——**这正是它能扛住"超过 3 个领域"的原因**（单 Agent 就是在这里崩的）。代价则是上述的纠错粒度粗、强依赖编排者能力（论文自己承认这是瓶颈）。

### 六类 Agent（Figure 1）
| Agent | 职责 |
|---|---|
| **Map / UI Agent** | 地图交互（如"缩放到布里斯班"） |
| **GeoDataOps Agent** | 数据操作（筛选月份、准备热力图） |
| **DatabaseOps Agent** | 数据产品查询（有哪些 MODIS 产品可用） |
| **Agriculture Analysis Agent** | 农业分析（NDVI 聚类、轮作推荐） |
| **Climate Monitoring Agent** | 气候监测（AOD550、LST） |
| **Forestry Monitoring Agent** | 林业监测（树冠覆盖、树损对比） |
| **Urban Analysis Agent** | 城市分析（人口热点） |
| **Satellite Vision Agent** | 卫星视觉（YOLO 检测桥梁等） |

### 两项提升提示的能力（可借鉴到我的工作）
- **TS（Intent-based Tool Selection，意图式工具选择）**：用相似度检索从一个"提示-方案"训练集里找最像的例子，给**单个 Agent 内部**做 few-shot 引导。
- **WM（Workflow Memory，工作流记忆）**：在**工作流层面**积累提示-方案对，给**跨 Agent**做 few-shot 引导。

> TS 管"这个 Agent 该用哪个工具"，WM 管"这个流程该怎么做"——一个管内部、一个管跨 Agent，两者正交。

### 技术栈
建在两套开源框架上：**GeoLLM-Engine 当前端**（交互式地图 UI + 对话式功能 + API 工具），**AutoGen 当后端**（LLM function-calling 实现多智能体通信与编排）。**这和卡片 A3 的 AutoGen 直接串起来了**。

### 对着图怎么讲
- **Figure 1**：底部一排是各类专职 Agent 的对话示例（Map/UI、GeoDataOps、DatabaseOps、Agriculture、Climate、Urban、Forestry、Satellite Vision），右下角是 GeoLLM-Squad 的编排器。**这张图讲"任务怎么被拆给不同专家"**。
- **Figure 2**：左半边是五个任务上各方法的正确率柱状图；右半边是关键——**任务数从 1 增加到 5 时各方法的正确率曲线**。
- **讲图时补一句**：图里每个 Agent 都在和用户/自己对话，看起来像"多个 Agent 在协作"；但实现上**每个 Agent 只跟编排者交换消息**，Agent 之间没有边——**图上看不到连线，因为没有连线**。

![GeoLLM-Squad Figure 1 多智能体地理空间 Copilot](../figures/geollm_arch.png)
*Figure 1｜六类专职 Agent + 编排器，建在 AutoGen 与 GeoLLM-Engine 之上。来源：arXiv:2501.16254, p.2*

---

## P3 实验结果

### 任务与数据（Table II）
五个真实遥感工作流，覆盖澳大利亚东部：
| 应用 | 指标 | 数据产品 | 分辨率 |
|---|---|---|---|
| Agriculture 农业 | NDVI、Ref B2 | MOD13A3、MOD09GA | 1km, 2024 |
| Climate 气候 | LST、AOD550 | MYD11A2、MCD19A2 | 1km, 2024 |
| Urban 城市 | Built-S、人口 | GHS-BUILT-S/POP | 3 arcsec, 2020 |
| Forest 林业 | 树冠、树损 | Tree Cover/Loss GFC | 1 arcsec, 2020 |
| Vision 视觉 | 检测、LCC | xView、FAIR1M、fMoW、BigEarthNet | — |

![GeoLLM-Squad Table II 任务与数据](../figures/tbl_geollm_tasks.png)
*Table II｜五类遥感工作流的指标、数据产品与示例提示。来源：arXiv:2501.16254, p.2*

### 主实验：正确率 + 成本（Table III，GPT-4o-mini）

![GeoLLM-Squad Table III 主实验](../figures/tbl_geollm_main.png)
*Table III｜主实验：与单智能体 GeoLLM-Engine、多智能体 Chameleon / Magentic 的完整对比。来源：arXiv:2501.16254, p.3*

| 方法 | 类型 | **正确率 Crct.Rt%** | Avg Tokens |
|---|---|---|---|
| GeoLLM-Engine⁺ | **单 Agent** | 39.84 / 41.86 / **43.32** | 19–22k |
| Chameleon | 多 Agent | 39.26 / 40.14 / 41.03 | 24–58k |
| Magentic | 多 Agent | 30.08 / 30.37 / 33.98 | **142–210k** |
| **GeoLLM-Squad** | 多 Agent | **60.29** | 78.49k |

**三个最该讲的数字**：
1. **正确率 60.29% vs 单 Agent 43.32%** —— 论文口径的"**17% 提升**"。
2. **Magentic 是反面教材**：token 花了 **21 万**，正确率只有 **33.98%**。原因：**过多重试循环和反复重规划**。→ 说明"多智能体"本身不保证更好，**编排机制才是关键**。
3. **GeoLLM-Squad 用 78k token 拿到 60.29%**，比 Chameleon（58k / 41.03%）贵一些但正确率高出近 20 个点——**性价比明显更优**。

### 主实验二：单 vs 多智能体的**扩展性消融**（Figure 2，最值得讲的一张）

![GeoLLM-Squad Figure 2 单/多智能体扩展性](../figures/geollm_scaling.png)

*Figure 2｜左：五个任务各自的正确率；右：任务数从 1 增到 5 时的组合任务正确率。来源：arXiv:2501.16254, p.4*

**结论（论文原话要点）**：
> 随着组合任务数增加，全局提示复杂度和 token 需求显著增长，**单智能体系统在超过三个领域（约 300 个工具）后就会失效**；而多智能体把工具集分散到专职 Agent 上，**能在任务复杂度上升时保持稳定性能**。

**这就是"多智能体到底强在哪"的实证答案**：不是单任务更强，而是**能扛住复杂度增长**。

### 动机实验：换成开源小模型会怎样（Table IV）

![GeoLLM-Squad Table IV 小模型对比](../figures/tbl_geollm_slm.png)
*Table IV｜GPT-4o-mini 与 Qwen-2.5（7B / 3B）上的正确率对比。来源：arXiv:2501.16254, p.4*

| LLM | 方法 | 正确率 % |
|---|---|---|
| Qwen-2.5-7B | Chameleon | 25.54 |
| Qwen-2.5-7B | Magentic | **9.29**（几乎等于噪声） |
| Qwen-2.5-7B | **GeoLLM-Squad** | **40.29** |
| Qwen-2.5-3B | Chameleon | 21.11 |
| Qwen-2.5-3B | Magentic | 7.81 |
| Qwen-2.5-3B | **GeoLLM-Squad** | **36.95** |

**结论**：换成小模型后，**Chameleon 掉最多 20 个点，Magentic 直接崩到 9% 以下**，而 GeoLLM-Squad 7B 版还能达到 GPT 驱动的 Chameleon 水平。→ **编排机制越依赖强模型，越不能落地**；这也是我能用得起实验的前提。

### 评价指标（对我很有参考价值）
- **Agentic Correctness（智能体正确率）**：**正确工具调用步骤的比例**——即"是否按预期顺序调用了正确的函数"。这是**过程指标**，不是答案对错。
- **ϵ（mean-square percentage error）**：把 Agent 实际访问的数据点与"金标准"数据点比较，缺失项算误差，跨 2000 条提示计算。
- 论文明确说：这类指标比"任务成功率"或"文本相似度"**更能反映对下游任务的影响**。

---

## 一句话总结
GeoLLM-Squad 把"编排"从"求解"里拆出来，用专职 sub-agent 分摊工具集，在真实遥感工作流上把正确率从 43% 提到 **60%（+17%）**；更关键的是它证明了**多智能体的优势不在单任务更强，而在任务复杂度增长时不崩**——这正好给了我的"用多智能体纠偏遥感模型"一个可引用的量化依据。

**协作方式一句话**：它不是"多个 Agent 一起商量"，而是**一个调度员（编排者）写排班表、一圈平级执行者按序跑、Agent 之间零通信、事后才纠错**——本质是把单体 Agent 的**上下文压力**拆开，而不是把智能拆开。
### 被追问：既然建在 AutoGen 上，怎么保证是星形？

**看起来像个矛盾**：AutoGen 的 auto-reply 让"对话驱动控制流"，那拓扑岂不是涌现的？不是。

**关键区别**：auto-reply 管的是**怎么回**，不管**回给谁**。论文原话：

> Once an agent receives a message from another agent, it automatically invokes generate_reply and **sends the reply back to the sender** unless a termination condition is satisfied.

注意"**back to the sender**"——回给发送者，不是让 LLM 任选下一个说话的人。

**所以拓扑由开发者的代码决定**：

| 写法 | 拓扑 |
|---|---|
| `A.initiate_chat(B, msg)` | 固定双人对话，对方写死 |
| 注册 reply function | 回复函数里指定发给谁 |
| GroupChat + GroupChatManager | **星形**（消息全经 manager 转发，agent 之间不直接通信） |

**GeoLLM-Squad 属于第一种**：编排者跟每个子 Agent 各建一条双人对话，子 Agent 的"对方"永远是编排者——它们的发送目标里**根本没有彼此**，所以物理上绕不开中心。**星形是代码结构保证的，不是靠 Agent 自觉。**

**额外一条**：AutoGen 自己的 GroupChat 本来就是星形（所有消息经 manager 转发）。所以"星形"在 AutoGen 里是现成模式，不是跟框架对着干。

**那什么是涌现的**：

| 涌现（由消息内容决定） | 不涌现（由代码决定） |
|---|---|
| 要来回几轮 | 谁跟谁连 |
| 要不要执行代码 | 有几个 Agent |
| 报错怎么修 | 谁是中心 |
| 什么时候结束 | |

图的结构是写死的，图上的流量是涌现的。

**一句话答法**："auto-reply 决定对话怎么往下走，不是谁跟谁连。子 Agent 之间根本没有彼此的发送目标，只跟编排者建了双人对话——星形是代码结构保证的。"
