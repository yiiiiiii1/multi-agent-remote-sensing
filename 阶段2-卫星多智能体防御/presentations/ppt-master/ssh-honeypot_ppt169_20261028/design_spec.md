<!-- ppt-master-schema: design-spec/v1 -->
# SSH 单篇精读 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | SSH 单篇精读 |
| Canvas Format | PPT 16:9 (1280 × 720) |
| Page Count | 10 |
| Primary Language | zh-CN |
| Target Audience | 导师；熟悉 LLM 与 Agent 安全，本次主要检验我是否真正读懂一篇论文，而不只记住结论 |
| Communication Intent | 单篇论文精读汇报：把 ICML 2026 的 Speculative Safety Honeypot 讲透——它把 Agent 防御从“回顾历史”改成“动手前推演”，用三个模拟器异步建推测树、以真实动作剪枝，并靠决策冗余降低对单个检测器精度的依赖 |
| Desired Audience Outcome | 导师能确认我读懂了：核心研究问题能一句话说清、四张图能指着讲、术语与数字不出错、能说出它自己承认的局限 |
| Core Message / Ask / Action | 这篇论文不问“你已经做了什么”，问“你接下来会做什么”；它的优势不是多了一层检测，而是让检测器不必那么准也行 |
| Delivery Context | 主要是当面讲给导师听，边讲边对着图解释；次要为会后留档 |
| Artifact Afterlife | 作为本次精读留档，并作为后续读论文的样板 |
| Reading Mode | balanced |
| Content Strategy | balanced（默认）：保留全部事实与数字，按论文 Introduction 的论证顺序重组，不复述小节编号 |
| Design Style | Mode: custom（instructional 拆解再排序）+ Visual style: custom（炭黑—青绿，冷峻技术页） |
| AI Image Acquisition Path | 不适用（image_usage = none，全部素材为论文原图） |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — final Stage-2 proactive policy（默认启用） |
| Custom Animations | disabled — final Stage-2 proactive policy（默认关闭） |
| Narration Audio | disabled — final Stage-2 proactive policy（默认关闭） |
| Created Date | 2026-10-28 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280 × 720 |
| viewBox | `0 0 1280 720` |
| Margins | 左右 72 px，上 56 px，下 56 px |
| Content Area | 1136 × 608 |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Mode Behavior**: 拆解再排序：先立两类威胁与两个问题，再依次拆开动机场景、架构、三处关键设计，最后落到证据与边界；每页只承担一个讲解步骤，同类概念用同形结构并列；标题直说这页讲什么；关键术语第一次出现时先定义再用，每处设计都点出它的代价。
- **Mode References**: instructional
- **Visual style**: custom
- **Visual style_behavior**: 冷峻技术页：纯白底、无渐变无阴影；标题用炭黑大字，一条 48 px 的极短青色横杠作结构锚；正文小字克制，强调只出现在两个位置——青色给“方法/结论”，焦橙给“风险/代价”。图一律原图直放，不加边框、不加底色、不加投影，让论文自己的线条说话。页脚只有一条发丝分隔线和页码。
- **Visual style References**: swiss-minimal
- **Theme**: 像一份打印出来的技术评审稿：白纸、炭黑字、一条青色标尺；没有装饰，只有图、数字和判断
- **Tone**: 冷静、精确、有取舍；不替论文说好话

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #FFFFFF | 页面底色，大面积留白 |
| Secondary background | #F4F6F7 | 卡片、分区底板、对照表底 |
| Primary | #16202A | 标题、结构线、主要图形、表头 |
| Accent | #0E8A7D | 方法与结论：三个模拟器、Beam Search、优势判断 |
| Secondary accent | #C2410C | 风险与代价：攻击、局限、前提、告警相关数字 |
| Body text | #1F2933 | 正文与说明文字 |
| Secondary text | #5E6B75 | 注释、图注、来源行 |
| Divider | #DDE2E6 | 细规则线、表格分隔、页脚 |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | neutral sans, crisp | Microsoft YaHei | Arial | sans-serif |
| Body | neutral sans, readable | Microsoft YaHei | Arial | sans-serif |

- **Title stack**: Microsoft YaHei, Arial, sans-serif
- **Body stack**: Microsoft YaHei, Arial, sans-serif

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 24 |
| Title | 42 |
| Subtitle | 32 |
| Lead | 28 |
| Annotation | 18 |
| Footnote | 16 |
| Display | 64 |

- **Role rationale**: 新增 `figure-caption` 20 px（图注）、`figure-label` 18 px（图上标注位）；论文原图内含小字，图注不得小于 20 px，否则整页失衡。

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 页标题给判断句 → 一行青色副线补条件 → 主体（图 / 三格 / 表） → 页脚一行来源
- **Composition tendency**: 图页给图最大面积（图占正文区 62% 以上），文字页最多三块并置；不出现等权卡片墙；每页只有一个焦点
- **Cross-page continuity**: 左上角一条 48 px 青色横杠 + 页脚发丝线固定；四张论文原图统一“无边框直放”，靠留白而不是容器分隔
- **Spacing posture**: 图页疏朗，文字页适度收紧；页与页之间不用装饰过渡
- **Spacing anchors**: 页边距 72 / 块间距 28 / 栏间距 36 / 圆角 6 / 正文行距 34

## VI. Icon Usage Specification

- **Primary bundled library**: tabler-outline
- **Stroke Width**: 2

| Icon Path | Suitable Scenarios |
| --- | --- |
| tabler-outline/mail | 邮件场景、间接注入入口 |
| tabler-outline/user | 用户、用户模拟器 |
| tabler-outline/robot | 助手模拟器、目标 Agent |
| tabler-outline/tool | 环境模拟器、工具返回 |
| tabler-outline/binary-tree | 推测树、分支展开 |
| tabler-outline/scissors | 剪枝、匹配后收窄 |
| tabler-outline/filter | 检测器、风险打分 |
| tabler-outline/alert-triangle | 攻击、风险、告警 |
| tabler-outline/arrow-right | 流程次序、异步传递 |
| tabler-outline/check | 优势、已实现 |
| tabler-outline/x | 局限、代价 |
| tabler-outline/settings | 超参、阈值 |

## VII. Visualization Reference List

| Page | Family | Template | Usage |
| --- | --- | --- | --- |
| P08 | table | comparison_matrix | 对照三组实验各自的基准、回答的问题与关键数字 |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ssh-fig1.png | 1076×471 | 2.28 | 动机图：用户请求被邮件里的注入劫持，SSH 在动手前推出转账与改密码 | figure | 居中偏左，右侧留出三行讲图标注的呼吸位，不加边框 | no-crop | user | Existing | Fig. 1 | keep | 正文 |
| ssh-fig2.png | 2084×972 | 2.14 | 模型图：异步发送消息列表、三个模拟器建树、真实动作剪枝、右侧 Beam Search 细节 | figure | 通栏置于页面中部，上下各留 28 px，右侧 Beam Search 细节不得被裁 | no-crop | user | Existing | Fig. 2 | keep | 正文 |
| ssh-fig3.png | 1022×539 | 1.90 | 结果图：All 与 w/o. Zero 两组、双轴（风险分柱 + 告警率虚线） | figure | 半宽置左，右侧放两条结论；不得缩放至刻度不可读 | no-crop | user | Existing | Fig. 3 | keep | 正文 |
| ssh-table2.png | 1335×623 | 2.14 | Table 2 原表：HarmBench / Circuit Breaker 两子集 × M=1–5 | table | 右侧直放，不加框 | no-crop | user | Existing | Table 2 | keep | 正文 |
| ssh-table3.png | 1335×312 | 4.28 | Table 3 原表：BFCL-v3 四项与 Overall + XSTest 拒答率 | table | 左下直放，不加框 | no-crop | user | Existing | Table 3 | keep | 正文 |
| ssh-fig4.png | 2084×413 | 5.05 | 结果图：AgentDojo/ActorAttack 暴露率与命中率对比，最右为 BFCL-v3 深度 2–5 | figure | 通栏置底，五个子图横向平铺；M 轴刻度必须可读 | no-crop | user | Existing | Fig. 4 | keep | 正文 |

## IX. Content Outline

### 一、两类威胁

#### Slide 01 - 封面

- **Audience move**: 只知道我在读一篇论文 → 立刻知道读的是哪一篇、它主张什么
- **Relationships**: none
- **Composition**: 炭黑大标题占上半，青色短杠作结构锚，右下角三行出处信息；大留白
- **Cover impact**: 一句主张把“回顾 vs 前瞻”的对立立住
- **Title**: Speculative Safety Honeypot
- **Core message**: 现有检测回头看历史；它改成在 Agent 动手之前先推演
- **Content**:
  - · 英文全题：Toward Proactive Defense Against Multi-turn Agent Attacks
  - · 作者：Zezhong Wang, Xueyang Tang, Rui Lian, Yang Lou, Heqing Huang（华为，香港）
  - · 出处：ICML 2026（PMLR 306）· 单篇精读

#### Slide 02 - 第一类：多轮越狱；第二类：间接注入

- **Audience move**: 以为“注入”就是模型说错话 → 能分清两类威胁各自谁在攻击、藏在哪
- **Relationships**: 两类威胁并列（membership），第二类由 Fig. 1 实例化（link）
- **Composition**: 左栏两类威胁各一条，右栏论文 Fig. 1 原图直放；图不加边框
- **Title**: 两类威胁：坏人装成用户，还是藏在邮件里
- **Core message**: 多轮越狱是攻击者本人当用户；间接注入是用户干净、脏东西在 Agent 读到的数据里
- **Content**:
  - · 多轮越狱：攻击者一轮轮把模型带偏，靠累积语义压过安全对齐（Crescendo、ASJA、AMA）
  - · 间接注入 IPI：恶意指令藏在文档或工具返回里，利用 Agent 对反馈的信任（InjecAgent、AgentDojo、STAC）
  - · 实例：用户只说“总结今天的邮件”，邮件里藏着改写指令
- **Images**: ssh-fig1.png，右侧居中，宽约 560 px

### 二、两个问题

#### Slide 03 - 现有防御卡在两处

- **Audience move**: 觉得“加个过滤器就行” → 看见它既缺能力，又卡在一个两难里
- **Relationships**: 两个问题并列（membership）；底部站位条把这篇论文钉在空位上（link）
- **Composition**: 上下两块，各自左侧一条色条；页脚一条炭黑横条写站位
- **Title**: 它既看不到未来，又卡在漏和误中间
- **Core message**: 缺的是对将来执行路径的预测；而严格与宽松之间没有免费的解
- **Content**:
  - · 问题一：提示类方法与外部检测器都只在当前这段上下文里判，缺乏对将来执行路径的预测
  - · 问题二：严格过滤导致误报高，放宽阈值又漏掉拆散在序列里的深层意图
  - · 站位：推测解码已把“推测”推到动作级（DSP、Speculative Action、SpecReason），但不做安全；安全只用到了 token 级（SSD）

### 三、方法

#### Slide 04 - A · 系统与训练：三个模拟器

- **Audience move**: 以为防御件应该“更稳” → 理解它反过来用一个更容易被骗的模拟器
- **Relationships**: 三个模拟器并列（membership）；训练策略依附于助手模拟器（parent）
- **Composition**: 上部三个模拟器等宽并置；下部一条训练策略带，左右两段对照保真与敏感
- **Title**: 三个模拟器，都故意不做安全对齐
- **Core message**: 探子必须肯往坏处走，才能预报坏处——这是它成立的前提，不是疏忽
- **Content**:
  - · 用户模拟器：生成多样、模糊的意图，覆盖边角输入
  - · 助手模拟器：代理目标 Agent，学它的执行习惯与错误模式
  - · 环境模拟器：给合成反馈，不真执行，推演隔离且无害
  - · 训练：Differentiated Alignment——平时保真（11,000 条蒸馏），对抗时敏感（4,700 条良性注入）；高风险场景下敏感优先于保真

#### Slide 05 - B · 推测：一棵树怎么长出来

- **Audience move**: 不知道“推演”如何落地 → 能指着图说出三块各自在干什么、M 和 D 控制什么
- **Relationships**: 左侧输入、中部建树、右侧搜索三者构成一条推进链（order）
- **Composition**: 论文 Fig. 2 原图通栏居中，占正文区 62%；下方一行参数条
- **Title**: 一个骨干，三个模拟器，一棵树
- **Core message**: Agent 异步把消息列表扔给 SSH，三个模拟器把未来摊成树，真实动作回来再剪
- **Content**:
  - · 图注：论文 Fig. 2，异步发消息列表 → 建推测树 → 真实动作剪枝 → 检测叶节点
  - · 输入：克隆当前 message list 异步送出，Agent 不等
  - · 建树：骨干 3B + 三个 LoRA 轮流出招；关键节点展开，普通节点只采一次
  - · 搜索：聚类后轮询取 M 条，再按被选次数分配下一层预算；M = 5、D = 4
- **Images**: ssh-fig2.png，通栏，宽 1136 px

#### Slide 06 - C · 验证与打分：对不上就留着

- **Audience move**: 以为“报警就该掐死” → 看到它先重采样，最多五次才中断
- **Relationships**: 匹配、剪枝、打分、双阈值、响应五步依次推进（order）
- **Composition**: 左侧五步竖排流程，右侧一块对照写双阈值与三种响应
- **Title**: 对上就剪窄，对不上就留着
- **Core message**: 风险分是有风险的叶子占比；报警后先重采样而不是直接终止
- **Content**:
  - · 匹配：函数调用比函数名 + 参数（精确），文本用 SimHash 算相似度
  - · 剪枝：匹配上只保留那一支；匹配不上保留原树，当未来风险的参考
  - · 打分：检测器看剩余叶节点，送进去的是从根到叶的整条路径；风险分 = 有风险的叶子 / 总叶子
  - · 双阈值：命中走低阈值（推测可信，从严），未命中走高阈值（防误报）
  - · 响应：引导 / 重采样 / 直接终止；实验选重采样，最多五次，仍无安全动作才中断

### 四、Key advantages

#### Slide 07 - 它凭什么更好：两句话

- **Audience move**: 以为优势是“多了一层检测” → 明白它的优势是让检测器不必那么准
- **Relationships**: 两条优势并列（membership），第二条由 86M 的数字支撑（link）
- **Composition**: 上下两块大字论述，第二块下方挂一行支撑数字；不排卡片
- **Title**: 它的优势不是多了一层检测
- **Core message**: 给检测器一棵未来的树，再靠决策冗余把“必须判准”这件事变成“多项互相兜底”
- **Content**:
  - · 优势一：把超出当前上下文的预测信息喂给现有检测器
  - · 优势二：判断依据从单个孤立节点，变成整棵树上的风险趋势演化——所以降低了对单个检测器绝对精度的依赖
  - · 支撑：PromptGuard 单独 12.25% ASR、Judger 单独 10.48%，加上 SSH 都变 0%；连 86M 的 PromptGuard 也能做到

### 证据与边界

#### Slide 08 - 三组实验，回答三个问题

- **Audience move**: 看到 0% 就以为结案 → 知道还有“不乱报”和“不伤功能”两道
- **Relationships**: 三组实验各自对应一个待答问题（order）；四个数字是共同结论（membership）
- **Composition**: 上部四行对照表；下部四个数字横排，数字青色、限定条件橙色
- **Title**: 先证明防得住，再证明不乱报
- **Core message**: 防住、不乱报、不伤功能，各有自己的基准和数字
- **Content**:
  - · 防间接注入 / AgentDojo（97 任务·629 用例）/ 能不能防住 / ASR 0%，连 86M 的 PromptGuard 也行
  - · 防多轮越狱 / ActorAttack（1,200 目标 × 3 路径）/ 灵敏度够不够 / 暴露率 HarmBench 99.5%、Circuit Breaker 96.0%
  - · 不伤功能 / BFCL-v3（1,000 用例）· XSTest（200 条）/ 代价多大 / BFCL-v3 Overall 45.13 → 44.88，XSTest 拒答 0%
  - · 四个数字：0%（ASR）· 99.5%/96.0%（暴露率）· 0.2%（误报率）· 1.3%（探子参数占比）
- **Visualization**: 对比矩阵 `experiment-matrix`（实验 / 基准 / 回答什么 / 关键数字）
- **Native-ready**: `experiment-matrix=yes`

#### Slide 09 - 不误报，和两条它自己承认的局限

- **Audience move**: 怀疑 0% 是靠疯狂报警换来的 → 看到正常任务零告警，也知道它贵在哪、错在哪
- **Relationships**: 左右两图对照（contrast）；下方两条局限与一条前提并列（membership）
- **Composition**: 上半 Fig. 3 置左、Fig. 4 通栏置右下方；下半两条局限横排，页脚一行前提
- **Title**: 报警率 57% 对 0%，代价是算力和误报
- **Core message**: 有攻击时告警 57.2% / 81.5%，正常任务 0% / 0%；但并发推测贵，一次误报要 3–7 秒
- **Content**:
  - · 图注左：论文 Fig. 3，All 与 w/o. Zero 两组，柱子是风险分、虚线是告警率
  - · 图注右：论文 Fig. 4，左侧比暴露率与命中率，最右为 BFCL-v3 深度 2–5 命中率
  - · 局限一：M = 5 并发分支的显存与功耗不可忽略，参数只多 1.3% 但并发是实打实的
  - · 局限二：系统级 FPR 0.2%，一次误报带 3–7 秒延迟；开放任务里“有野心”与“有恶意”边界很薄
  - · 前提：探子被带偏的能力，就是它的漏报边界（从训练一节提炼，论文未列为 limitation）
- **Images**: ssh-fig3.png 半宽置左上，ssh-fig4.png 通栏置下

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under `notes/`
- **Content**: 以 `sources/SSH讲解骨架-ABCD.md` 与 `sources/SSH精读PPT-设计.md` 为唯一事实来源；图页按“指着图讲”的口语写，不念幻灯片；数字只讲论文原文给出的，术语第一次出现时补一句人话
- **Total duration**: 约 24 分钟，另留 1 分钟机动
- **Notes style**: conversational, 面向当面讲解与追问
- **Presentation purpose**: 让导师确认我真读懂了这篇论文——核心研究问题一句话说清、四张图能指着讲、术语与数字不出错
