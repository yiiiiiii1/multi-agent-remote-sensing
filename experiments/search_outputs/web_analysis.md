# web_analysis：系统对比表 + 来源可信度分级表

> 分析对象：`web_notes.md`（Tavily 联网检索笔记，共 9 条编号结果，分属 3 个检索角度）

---

## 表 1：系统 / 工作对比表

| # | 系统名 | 年份 | 来源机构 | 方法 | 数据集或基准 | 报告结果(数字) | 来源URL |
|---|---|---|---|---|---|---|---|
| 1 | 遥感智能变化检测的深度学习方法（综述性工作，非单一系统） | 未提及 | 未提及（csgpc.org 网站） | 综述：CNN 局部编码 → 全局特征 → 时空联合分析；指出多时相关系建模不足 | 未提及 | 未提及（仅定性结论） | https://www.csgpc.org/detail/26031.html |
| 2 | **ChangeGPT** | 未提及 | 未提及（AlphaXiv 条目，无作者信息） | 分层智能体框架：LLM「大脑」+ 视觉基础模型 VFM「工具包」；三层结构＝应用层 / 规划导航器（含 3 个子层）/ 执行工具包；分层结构缓解 LLM 幻觉；查询驱动多步骤变化分析 | 自建 140 个精心策划问题的数据集（涵盖大小、类别、数量等类型及不同复杂度） | GPT-4-turbo 后端匹配率 **90.71%**；评估工具选择精确率/召回率与整体查询准确率；深圳前海湾真实城市变化监测案例验证 | https://www.alphaxiv.org/zh/abs/2601.02757 |
| 3 | **地理智能体（华为云）** | 未提及 | 华为云（Huawei Cloud） | 遥感数据业务化加工（正射、镶嵌、匀色、融合）+ AI 深度学习智能识别；以替代专家人工勾画图斑 | 未提及 | 未提及（仅定性描述效率低下问题） | https://www.huaweicloud.com/product/geogenius.html |
| 4 | **Change-Agent** | **2024**（arXiv 编号 2403.19646） | 未提及（arXiv 预印本） | 交互式系统：多层级变化解译模型（MCI）+ LLM 结合，连接专门视觉感知与高层推理；自然语言交互；引入多智能体协作（多样能力智能体协同解译） | 引入 **LEVIR-MIC** 数据集（支持 CD 与 CC 多任务学习） | 使用 **MIoU** 指标评估多类别变化检测性能（衡量预测掩膜与真值掩膜空间重叠） | https://arxiv.org/html/2403.19646v1 |
| 5 | An LLM-based multi-agent system for remote sensing analysis | **2025**（DOI 号 2025.2600178） | 清华大学地球系统科学系（作者：Jun Yang 教授） | 基于 LLM 的多智能体系统，三模块整合为统一框架；将多智能体系统形式化为图 G(V,E)（顶点=智能体/插件，边=交互）；针对遥感专属工作流、多源数据、演变需求做适配修改 | 未提及 | 未提及（论文定位为填补「遥感专用多智能体策略缺失」的空白） | https://www.tandfonline.com/doi/full/10.1080/20964471.2025.2600178 |
| 6 | **Change-Agent**（alphaXiv 解读版，与 #4 同一论文） | **2024**（arXiv 编号 2403.19646） | 未提及（AlphaXiv 解读版） | 同 #4；补充：遥感变化解译分化为变化检测 CD（像素级分类，输出二值/多类别掩膜）与变化描述 CC 两类任务；以 BiFA 等高表现基线对 MCI 模型变化检测分支做对比验证 | LEVIR-MIC（同 #4） | 未提及数字（仅说明较 BiFA 等基线验证新架构有效性） | https://www.alphaxiv.org/abs/2403.19646 |
| 7 | （同 #5，重复命中）An LLM-based multi-agent system for remote sensing analysis | 2025（同 #5） | 清华大学地球系统科学系（同 #5） | 同 #5；补充参考文献脉络：Minsky(1986)《The Society of Mind》、Mei 等(2024) 深度学习鲁棒性综述（Journal of Remote Sensing）、Zhang 等(2024) BB-GeoGPT（Information Processing & Management）、Paolanti 等(2024) AI 可信度伦理框架（Remote Sensing） | 未提及 | 未提及 | https://www.tandfonline.com/doi/full/10.1080/20964471.2025.2600178 |
| 8 | **GeoLLM-QA**（工具增强型智能体评估基准） | **2024**（ICLR 2024 ML4RS Workshop；文中提及 SkyEyeGPT 为 Zhan 等 2024） | **Microsoft CoStrategist R&D Group** | 面向真实用户任务的基准，评估工具增强型 LLM 在地理空间应用中的能力；指出多模态模型用于遥感任务（图像描述、VQA 等）；批评现有基准多假设问答输入模板 | **GeoLLM-QA**（自建基准） | 未提及（基准论文，无量化结果） | https://ml-for-rs.github.io/iclr2024/camera_ready/papers/65.pdf |
| 9 | LLM agent framework for intelligent change analysis in urban environment using remote sensing imagery | 未提及（期刊论文） | 未提及 | 基于遥感影像的城市环境智能变化分析的 LLM 智能体框架；参考文献涉 Guo 等(2025) 巴西城市树冠覆盖率、Xing 等(2024) 城市建筑洪水脆弱性、Wu 等(2017) 迭代慢特征分析+贝叶斯软融合后分类变化检测、Wang 等(2023) 自一致性改进思维链、Fang 等(2024) Changer 特征交互 | 未提及 | 未提及 | https://www.sciencedirect.com/science/article/abs/pii/S0926580525003814 |

**表 1 备注**

| 备注项 | 内容 |
|---|---|
| 重复命中 | #7 = #5（同一 URL）；#6 = #4（同一论文的 AlphaXiv 解读版） |
| 提及但未单列为条目的系统 | SkyEyeGPT（Zhan 等，2024，微调 VQA 智能体）；BB-GeoGPT（Zhang 等，2024）；BiFA（基线方法）；Changer（Fang 等，2024） |
| 缺失最严重的字段 | 「年份」仅 4 项可考（#4/#6=2024、#5/#7=2025、#8=2024）；「来源机构」仅 #5/#7（清华）、#8（Microsoft）可考；#2 ChangeGPT 无作者、无年份 |
| 唯一量化结果 | ChangeGPT 的 90.71% 匹配率（GPT-4-turbo 后端） |

---

## 表 2：来源可信度分级表

| 级别 | 定义 | 对应条目 | 具体来源 | URL |
|---|---|---|---|---|
| **A** | 期刊全文 | #5 / #7 | Big Earth Data（Taylor & Francis 全文页，DOI 10.1080/20964471.2025.2600178） | https://www.tandfonline.com/doi/full/10.1080/20964471.2025.2600178 |
| **A** | 期刊全文 | #9 | ScienceDirect（Advanced Engineering Informatics，文献页 S0926580525003814） | https://www.sciencedirect.com/science/article/abs/pii/S0926580525003814 |
| **B** | arXiv 预印本 | #4 | arXiv 2403.19646v1（Change-Agent） | https://arxiv.org/html/2403.19646v1 |
| **B** | arXiv 预印本（第三方解读版） | #6 | AlphaXiv 2403.19646（Change-Agent 解读） | https://www.alphaxiv.org/abs/2403.19646 |
| **B** | arXiv 预印本（第三方解读版） | #2 | AlphaXiv 2601.02757（ChangeGPT） | https://www.alphaxiv.org/zh/abs/2601.02757 |
| **B** | 预印本 / Workshop 论文（ICLR 2024 ML4RS Workshop camera-ready） | #8 | ICLR 2024 ML4RS Workshop 论文 65.pdf（GeoLLM-QA） | https://ml-for-rs.github.io/iclr2024/camera_ready/papers/65.pdf |
| **C** | 官方文档 / 教程 | #3 | 华为云「地理智能体」产品官方页面 | https://www.huaweicloud.com/product/geogenius.html |
| **D** | 新闻稿 / 非同行评议站点内容 | #1 | csgpc.org 站点综述文章（无作者、无年份、无出处标注） | https://www.csgpc.org/detail/26031.html |

**表 2 备注**

| 备注项 | 内容 |
|---|---|
| 分级依据 | 仅按 web_notes.md 中可见的来源类型判定；#2/#6 走 AlphaXiv 第三方解读页，非 arXiv 原文页，故标注为「预印本（第三方解读版）」 |
| 未出现在本表中的级别 | 无遗漏；A/B/C/D 四级均有对应条目 |
| 争议/待核实来源 | #1（csgpc.org，无作者年份，D 级最低）；#9（ScienceDirect 摘要页而非全文，本笔记仅见文献页） |
