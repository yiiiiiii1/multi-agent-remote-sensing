# 02 RolePlaying 双智能体 · 运行日志

> 保存 `02_RolePlaying双智能体.py` 的完整运行记录，供复现与对照使用。
> 与 `01_最小双智能体_日志.md` 配套。

## 一、实验信息

| 项目 | 内容 |
|------|------|
| 实验日期 | 2026-09-11 |
| 实验编号 | 02 |
| 实验名称 | RolePlaying 双智能体自动对话 |
| 参考示例 | `clones/camel/examples/ai_society/role_playing.py` |
| 实验代码 | `多智能体遥感调研/experiments/02_RolePlaying双智能体.py` |
| 运行命令 | `bash run_demo.sh 02` |
| 模型 | DeepSeek `deepseek-chat` |
| 接口地址 | `https://api.deepseek.com` |
| CAMEL 版本 | 0.2.91a7 |
| 运行结果 | 正常完成，未报错 |

## 二、实验目的

验证 CAMEL 内置的 `RolePlaying` 社会能否驱动两个 Agent 围绕同一任务自动多轮对话，观察：

1. 两个角色的系统提示如何约束各自行为；
2. Task Specifier 如何把一句简单任务扩展成清晰提示；
3. AI User 与 AI Assistant 如何分工推进、何时判定任务完成。

## 三、配置摘要

### 3.1 角色

| 角色 | 名称 | 定位 |
|------|------|------|
| AI Assistant | 遥感算法工程师 | 负责实际产出方案 |
| AI User | 遥感应用研究员 | 提出需求、给出输入、推动任务 |

### 3.2 任务

- 原始任务：`为遥感影像变化检测设计一个多智能体协作方案`
- 指定后任务（Task Specifier 自动扩展）：
  `设计"城市扩张侦探"多智能体：卫星影像解析员提取建筑、植被变化；时间序列分析员检测突变；地图叙事员自动生成热力图与报告，协同输出变化检测结果。`

### 3.3 系统提示要点（自动生成）

- Assistant 侧规则：始终以 `Solution:` 开头，结尾必须为 `Next request.`，不得反转角色、不得反过来指挥对方。
- User 侧规则：始终以 `Instruction:` + `Input:` 的固定格式下达单条指令，任务完成时只回复 `<CAMEL_TASK_DONE>`。

## 四、运行过程记录

共 6 轮，每轮由 AI User 下达一条指令，AI Assistant 给出一份方案。

| 轮次 | AI User 指令（摘要） | AI Assistant 交付内容 |
|------|---------------------|----------------------|
| 1 | 设计总体架构，明确三个子智能体职责、输入输出接口与协同流程 | 分层架构（编排层 + 三个子智能体 + 数据总线）、统一时空基准、数据契约、事件驱动协同原则 |
| 2 | 设计卫星影像解析员：预处理、建筑/植被变化提取、置信度评估 | Sentinel-2 预处理流程、NDBI/NDVI+CVA 与 U-Net 融合、change_raster 输出契约 |
| 3 | 设计时间序列分析员：时序特征、突变检测（PELT/BFAST/CUSUM）、事件分类 | 时序构建、多算法投票融合、四类事件分类规则、置信度四因子加权 |
| 4 | 设计地图叙事员：热力图、交互地图、自然语言报告 | 静态热力图、Leaflet 交互地图、事实优先 + LLM 润色的报告生成 |
| 5 | 设计三子智能体协同编排：共享上下文、反馈回环、冲突消解 | Orchestrator、Shared Context、事件总线、低置信度回环、加权投票冲突消解、端到端示例 |
| 6 | `<CAMEL_TASK_DONE>` | 交付总结与最终输出 JSON |

### 终止情况

- 第 6 轮 AI User 输出 `<CAMEL_TASK_DONE>`，主循环据此跳出。
- 未触发 `chat_turn_limit = 8`。
- 未出现 `terminated`（无超时、无异常中断）。

## 五、关键观察

1. **角色不串位**：6 轮中 AI User 只下达指令，AI Assistant 只输出方案，始终未反转角色，说明系统提示约束有效。
2. **Task Specifier 生效**：原始任务只有一句话，被自动扩展为包含三个子智能体与协同目标的完整任务描述。
3. **单指令推进**：AI User 每轮只给一条指令，任务被自然拆成"总体架构 → 三个子模块 → 编排"的顺序，体现了任务分解。
4. **自终止机制**：AI User 在认为任务完成后主动回复 `<CAMEL_TASK_DONE>`，而不是靠轮次上限强行结束。
5. **输出偏"设计文档"**：AI Assistant 产出的是方案与代码接口（含大量伪代码），尚未真正执行遥感计算，符合本阶段"先跑通协作机制"的目标。

## 六、最终输出（AI Assistant 汇总）

```json
{
  "task_id": "city_expansion_001",
  "status": "completed",
  "summary": "2018-2023年间，研究区建筑扩张12.5 km²，植被减少9.8 km²，2020年为突变高峰，主要集中于城市东部边缘。",
  "change_map": "final_change_map.tif",
  "heatmap": "heatmap.png",
  "interactive_map": "map.html",
  "report": "report.pdf",
  "overall_confidence": 0.86,
  "consistency_score": 0.92
}
```

> 注：以上数值是模型在对话中构造的示例数据，**不是真实遥感计算结果**。

## 七、与 01 实验的区别

| 对比项 | 01 最小双智能体 | 02 RolePlaying 双智能体 |
|--------|----------------|------------------------|
| 控制方式 | 手动把上一步输出喂给下一步 | 框架托管的自动多轮对话 |
| 结构 | 固定流水线（研究员→审稿人→整合者） | 双向对话（AI User ↔ AI Assistant） |
| 结束方式 | 脚本跑完固定三步 | 由 AI User 判定并回复 `<CAMEL_TASK_DONE>` |
| 观察重点 | 消息如何传递 | 角色规则、任务分解、自终止 |

## 八、待改进

1. 脚本未打印 token 用量与耗时，后续可读取 `response.info` 记录每轮开销。
2. 只跑了设计层面，下一步可把某个子智能体替换为真正调用工具/代码的 Agent。
3. 可加入 `with_critic_in_the_loop`，对比有/无 critic 时输出质量的差异（对应最小消融实验）。

## 九、完整生成文本

以下为终端原始输出（模型生成内容，未做任何修改）。

---

模型：deepseek-chat | 地址：https://api.deepseek.com

=== AI Assistant 系统提示 ===

BaseMessage(role_name='遥感算法工程师', role_type=<RoleType.ASSISTANT: 'assistant'>, meta_dict={'task': '设计“城市扩张侦探”多智能体：卫星影像解析员提取建筑、植被变化；时间序列分析员检测突变；地图叙事员自动生成热力图与报告，协同输出变化检测结果。', 'assistant_role': '遥感算法工程师', 'user_role': '遥感应用研究员'}, content='===== RULES OF ASSISTANT =====\nNever forget you are a 遥感算法工程师 and I am a 遥感应用研究员. Never flip roles! Never instruct me!\nWe share a common interest in collaborating to successfully complete a task.\nYou must help me to complete the task.\nHere is the task: 设计“城市扩张侦探”多智能体：卫星影像解析员提取建筑、植被变化；时间序列分析员检测突变；地图叙事员自动生成热力图与报告，协同输出变化检测结果。. Never forget our task!\nI must instruct you based on your expertise and my needs to complete the task.\n\nI must give you one instruction at a time.\nYou must write a specific solution that appropriately solves the requested instruction and explain your solutions.\nYou must decline my instruction honestly if you cannot perform the instruction due to physical, moral, legal reasons or your capability and explain the reasons.\nUnless I say the task is completed, you should always start with:\n\nSolution: <YOUR_SOLUTION>\n\n<YOUR_SOLUTION> should be very specific, include detailed explanations and provide preferable detailed implementations and examples and lists for task-solving.\nAlways end <YOUR_SOLUTION> with: Next request.', video_bytes=None, image_list=None, image_detail='auto', video_detail='auto', parsed=None, reasoning_content=None)

=== AI User 系统提示 ===

BaseMessage(role_name='遥感应用研究员', role_type=<RoleType.USER: 'user'>, meta_dict={'task': '设计“城市扩张侦探”多智能体：卫星影像解析员提取建筑、植被变化；时间序列分析员检测突变；地图叙事员自动生成热力图与报告，协同输出变化检测结果。', 'assistant_role': '遥感算法工程师', 'user_role': '遥感应用研究员'}, content='===== RULES OF USER =====\nNever forget you are a 遥感应用研究员 and I am a 遥感算法工程师. Never flip roles! You will always instruct me.\nWe share a common interest in collaborating to successfully complete a task.\nI must help you to complete the task.\nHere is the task: 设计“城市扩张侦探”多智能体：卫星影像解析员提取建筑、植被变化；时间序列分析员检测突变；地图叙事员自动生成热力图与报告，协同输出变化检测结果。. Never forget our task!\nYou must instruct me based on my expertise and your needs to solve the task ONLY in the following two ways:\n\n1. Instruct with a necessary input:\nInstruction: <YOUR_INSTRUCTION>\nInput: <YOUR_INPUT>\n\n2. Instruct without any input:\nInstruction: <YOUR_INSTRUCTION>\nInput: None\n\nThe "Instruction" describes a task or question. The paired "Input" provides further context or information for the requested "Instruction".\n\nYou must give me one instruction at a time.\nI must write a response that appropriately solves the requested instruction.\nI must decline your instruction honestly if I cannot perform the instruction due to physical, moral, legal reasons or my capability and explain the reasons.\nYou should instruct me not ask me questions.\nNow you must start to instruct me using the two ways described above.\nDo not add anything else other than your instruction and the optional corresponding input!\nKeep giving me instructions and necessary inputs until you think the task is completed.\nWhen the task is completed, you must only reply with a single word <CAMEL_TASK_DONE>.\nNever say <CAMEL_TASK_DONE> unless my responses have solved your task.', video_bytes=None, image_list=None, image_detail='auto', video_detail='auto', parsed=None, reasoning_content=None)

=== 原始任务 ===
为遥感影像变化检测设计一个多智能体协作方案

=== 指定后的任务提示 ===
设计“城市扩张侦探”多智能体：卫星影像解析员提取建筑、植被变化；时间序列分析员检测突变；地图叙事员自动生成热力图与报告，协同输出变化检测结果。

---------- 第 1 轮 ----------

[AI User]
Instruction: 设计“城市扩张侦探”多智能体系统的总体架构，明确三个子智能体（卫星影像解析员、时间序列分析员、地图叙事员）的职责、输入输出接口和协同流程。
Input: 任务目标为协同输出城市扩张变化检测结果；三个子智能体分别负责建筑/植被变化提取、突变检测、热力图与报告生成。

[AI Assistant]
Solution: 下面是“城市扩张侦探”多智能体系统的总体架构设计，围绕三个子智能体的职责、输入输出接口与协同流程展开。整体采用“共享上下文 + 事件驱动 + 结果融合”的架构，保证三个子智能体既能独立完成专业任务，又能通过统一数据契约协同输出变化检测结果。

## 1. 总体架构

### 1.1 分层设计

```
┌─────────────────────────────────────────────────────────────┐
│                    编排层 Orchestrator                       │
│  - 任务调度、状态管理、冲突消解、最终结果融合                 │
│  - 维护共享上下文 Shared Context（时序、空间、元数据）        │
└───────────────┬─────────────────┬─────────────────┬─────────┘
                │                 │                 │
                ▼                 ▼                 ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ 卫星影像解析员     │ │ 时间序列分析员     │ │ 地图叙事员         │
│ Image Analyst      │ │ Temporal Analyst   │ │ Map Narrator       │
│ 职责：建筑/植被    │ │ 职责：突变检测     │ │ 职责：热力图+报告  │
│ 变化提取           │ │                   │ │                   │
└─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘
          │                     │                     │
          ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│              数据总线 Data Bus / 共享存储层                  │
│  - 原始影像、变化栅格、时间序列特征、突变事件、热力图、报告  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 核心设计原则

1. **统一时空基准**：所有子智能体使用同一 CRS（如 EPSG:4326 / UTM）、同一时间切片集合、同一网格分辨率，避免空间错位。
2. **数据契约优先**：每个子智能体输出标准化 JSON/GeoTIFF，字段固定，便于下游消费。
3. **事件驱动协同**：影像解析员产出变化后触发时间序列分析员；突变事件产出后触发地图叙事员。
4. **可解释性**：每个结论附带置信度、证据链（像元数、时间点、统计量）。

---

## 2. 子智能体职责与输入输出接口

### 2.1 卫星影像解析员（Image Analyst）

**职责**
- 对多时相卫星影像进行预处理：辐射定标、大气校正、云掩膜、几何配准。
- 提取建筑变化：利用建筑指数（NDBI）、语义分割模型（U-Net / DeepLabV3+）或变化向量分析（CVA）。
- 提取植被变化：利用 NDVI、EVI，计算植被增减区域。
- 输出逐像元/逐对象的变化类别与置信度。

**输入接口**
```json
{
  "task_id": "city_expansion_001",
  "image_pairs": [
    {"t0": "2018-06-01", "t1": "2023-06-01",
     "t0_path": "s3://data/city_2018.tif",
     "t1_path": "s3://data/city_2023.tif"}
  ],
  "aoi": {"type": "Polygon", "coordinates": [[...]]},
  "crs": "EPSG:32650",
  "resolution": 10,
  "classes": ["building_gain", "building_loss", "vegetation_gain", "vegetation_loss"]
}
```

**输出接口**
```json
{
  "task_id": "city_expansion_001",
  "change_raster": "s3://output/change_2018_2023.tif",
  "change_stats": {
    "building_gain_pixels": 125430,
    "building_loss_pixels": 3200,
    "vegetation_gain_pixels": 45210,
    "vegetation_loss_pixels": 98760
  },
  "confidence_mean": 0.87,
  "method": "NDBI+NDVI threshold + U-Net refinement",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**关键实现示例**
```python
def extract_change(img_t0, img_t1):
    ndbi_t0 = (img_t0.swir - img_t0.nir) / (img_t0.swir + img_t0.nir)
    ndbi_t1 = (img_t1.swir - img_t1.nir) / (img_t1.swir + img_t1.nir)
    ndvi_t0 = (img_t0.nir - img_t0.red) / (img_t0.nir + img_t0.red)
    ndvi_t1 = (img_t1.nir - img_t1.red) / (img_t1.nir + img_t1.red)

    building_gain = (ndbi_t1 - ndbi_t0 > 0.1) & (ndvi_t1 - ndvi_t0 < -0.1)
    vegetation_loss = (ndvi_t1 - ndvi_t0 < -0.15)

    # 可选：用 U-Net 对 building_gain 做形态学后处理
    return building_gain, vegetation_loss
```

---

### 2.2 时间序列分析员（Temporal Analyst）

**职责**
- 接收影像解析员的变化栅格与统计量，结合历史时间序列（如 Landsat/Sentinel 长时序）。
- 检测突变点：使用 BFAST、CUSUM、Prophet、 ruptures（PELT）等算法。
- 区分“渐变”与“突变”，标注突变时间、突变幅度、方向（扩张/收缩）。
- 输出突变事件列表与时间序列特征。

**输入接口**
```json
{
  "task_id": "city_expansion_001",
  "change_raster": "s3://output/change_2018_2023.tif",
  "time_series": [
    {"date": "2015-06-01", "ndvi": 0.62, "ndbi": -0.15},
    {"date": "2016-06-01", "ndvi": 0.60, "ndbi": -0.13},
    ...
  ],
  "aoi": {...},
  "detection_method": "PELT",
  "penalty": 10
}
```

**输出接口**
```json
{
  "task_id": "city_expansion_001",
  "breakpoints": [
    {"date": "2020-05-15", "type": "building_gain", "magnitude": 0.23,
     "confidence": 0.91, "location": [116.40, 39.90]},
    {"date": "2021-08-20", "type": "vegetation_loss", "magnitude": -0.31,
     "confidence": 0.88, "location": [116.42, 39.91]}
  ],
  "trend": {"building": "+0.08/year", "vegetation": "-0.12/year"},
  "method": "PELT + BFAST",
  "timestamp": "2024-01-01T10:05:00Z"
}
```

**关键实现示例**
```python
import ruptures as rpt

def detect_breakpoints(series, penalty=10):
    algo = rpt.Pelt(model="rbf").fit(series)
    breakpoints = algo.predict(pen=penalty)
    events = []
    for bp in breakpoints[:-1]:
        magnitude = series[bp] - series[bp-1]
        events.append({
            "index": bp,
            "magnitude": float(magnitude),
            "type": "building_gain" if magnitude > 0 else "vegetation_loss"
        })
    return events
```

---

### 2.3 地图叙事员（Map Narrator）

**职责**
- 接收变化栅格与突变事件，生成空间热力图、变化地图、时序动画。
- 自动生成自然语言报告：摘要、关键发现、时间线、空间分布、建议。
- 输出可交互 Web 地图（如 Leaflet / Mapbox）与 PDF/Markdown 报告。

**输入接口**
```json
{
  "task_id": "city_expansion_001",
  "change_raster": "s3://output/change_2018_2023.tif",
  "breakpoints": [...],
  "change_stats": {...},
  "aoi": {...},
  "report_format": ["html", "pdf", "markdown"],
  "language": "zh-CN"
}
```

**输出接口**
```json
{
  "task_id": "city_expansion_001",
  "heatmap_url": "s3://output/heatmap_2018_2023.png",
  "interactive_map": "s3://output/map.html",
  "report_markdown": "s3://output/report.md",
  "report_pdf": "s3://output/report.pdf",
  "summary": "2018-2023年间，研究区建筑面积增加12.5%，植被减少9.8%，主要突变发生在2020年5月...",
  "timestamp": "2024-01-01T10:10:00Z"
}
```

**关键实现示例**
```python
import matplotlib.pyplot as plt
import seaborn as sns

def generate_heatmap(change_raster, aoi):
    # 将变化栅格转为密度热力图
    data = raster_to_array(change_raster)
    plt.figure(figsize=(10, 8))
    sns.kdeplot(x=data.x, y=data.y, weights=data.building_gain, cmap="Reds")
    plt.title("城市建筑扩张热力图 (2018-2023)")
    plt.savefig("heatmap.png")

def generate_report(stats, breakpoints):
    summary = f"""
    # 城市扩张侦探报告

    ## 关键发现
    - 建筑增加像元：{stats['building_gain_pixels']}
    - 植被减少像元：{stats['vegetation_loss_pixels']}
    - 主要突变时间：{breakpoints[0]['date']}

    ## 建议
    加强城市边缘区生态廊道保护。
    """
    return summary
```

---

## 3. 协同流程

### 3.1 事件驱动时序

```
[用户任务]
   │
   ▼
[Orchestrator 初始化 Shared Context]
   │
   ├──► [卫星影像解析员] 预处理 + 变化提取
   │         │
   │         ▼ 发布 change_raster + change_stats
   │
   ├──► [时间序列分析员] 监听 change_raster，执行突变检测
   │         │
   │         ▼ 发布 breakpoints + trend
   │
   └──► [地图叙事员] 监听 change_raster + breakpoints
             │
             ▼ 生成 heatmap + report
   │
   ▼
[Orchestrator 融合所有输出 → 最终变化检测结果]
```

### 3.2 协同规则

| 规则 | 说明 |
|------|------|
| 依赖顺序 | 影像解析员 → 时间序列分析员 → 地图叙事员 |
| 并行机会 | 建筑变化与植被变化可在影像解析员内部并行 |
| 反馈机制 | 若时间序列分析员发现突变置信度低，可请求影像解析员用更高分辨率重算局部区域 |
| 冲突消解 | 若两智能体结论冲突，Orchestrator 以置信度加权投票，并标注不确定性 |
| 一致性校验 | 变化像元总数应与突变事件覆盖区域大致吻合，否则触发复核 |

### 3.3 共享上下文示例

```json
{
  "task_id": "city_expansion_001",
  "aoi": {...},
  "time_range": ["2015-01-01", "2023-12-31"],
  "crs": "EPSG:32650",
  "resolution": 10,
  "artifacts": {
    "change_raster": "s3://output/change.tif",
    "breakpoints": "s3://output/breakpoints.json",
    "heatmap": "s3://output/heatmap.png",
    "report": "s3://output/report.md"
  },
  "status": "completed",
  "confidence": 0.89
}
```

---

## 4. 最终输出

Orchestrator 融合后输出统一变化检测结果：

```json
{
  "task_id": "city_expansion_001",
  "summary": "2018-2023年城市建筑扩张12.5%，植被减少9.8%，2020年5月为突变高峰。",
  "change_map": "s3://output/final_change_map.tif",
  "heatmap": "s3://output/heatmap.png",
  "report": "s3://output/report.pdf",
  "breakpoints": [...],
  "confidence": 0.89,
  "evidence_chain": [
    {"agent": "ImageAnalyst", "output": "change_stats"},
    {"agent": "TemporalAnalyst", "output": "breakpoints"},
    {"agent": "MapNarrator", "output": "report"}
  ]
}
```

---

## 5. 落地建议

- **技术栈**：Python + Rasterio + GDAL + PyTorch（分割）+ ruptures（突变）+ Folium/Leaflet（地图）+ LLM（报告生成）。
- **部署**：Docker 容器化三个子智能体，通过消息队列（Kafka/RabbitMQ）或 Airflow DAG 编排。
- **评估指标**：变化检测 F1、突变检测 Precision/Recall、报告可读性人工评分。

Next request.

---------- 第 2 轮 ----------

[AI User]
Instruction: 基于总体架构，请详细设计卫星影像解析员的实现方案，包括数据预处理流程、建筑与植被变化提取算法、置信度评估方法，并给出核心代码接口。
Input: 使用 Sentinel-2 10m 多光谱影像，时间跨度为 2018-2023，AOI 为某城市建成区，需支持建筑增益/损失、植被增益/损失四类变化。

[AI Assistant]
Solution: 下面给出卫星影像解析员的详细实现方案，聚焦 Sentinel-2 10m 多光谱影像、2018-2023 时间跨度、城市建成区 AOI，覆盖数据预处理、建筑/植被四类变化提取、置信度评估与核心代码接口。

---

## 1. 数据源与总体流程

### 1.1 数据源规格

| 项目 | 说明 |
|------|------|
| 卫星 | Sentinel-2 MSI Level-2A（地表反射率） |
| 波段 | B02(蓝)、B03(绿)、B04(红)、B08(NIR)、B11(SWIR1)、B12(SWIR2) |
| 分辨率 | 10m（B02/B03/B04/B08）、20m（B11/B12，需重采样至10m） |
| 时间跨度 | 2018-2023，每年选取生长季（6-8月）无云合成影像 |
| AOI | 城市建成区矢量边界，用于裁剪 |
| 投影 | UTM（按AOI所在带号），统一 EPSG |

### 1.2 处理流程总览

```
原始 L2A 影像
   │
   ▼
[1] 数据预处理
   ├─ 大气校正校验（L2A已含）
   ├─ 云/阴影掩膜（SCL 波段 + s2cloudless）
   ├─ 波段重采样与统一网格
   ├─ 时间合成（年合成 / 季合成）
   ├─ 几何配准（亚像元级）
   └─ AOI 裁剪与归一化
   │
   ▼
[2] 特征指数计算
   ├─ NDVI（植被）
   ├─ NDBI（建筑）
   ├─ NDWI（水体，用于排除）
   └─ BSI（裸土）
   │
   ▼
[3] 变化提取（双轨）
   ├─ 轨道A：指数阈值 + 变化向量分析（CVA）
   └─ 轨道B：语义分割模型（U-Net）
   │
   ▼
[4] 融合与后处理
   ├─ 形态学滤波
   ├─ 最小图斑过滤
   └─ 四类变化掩膜
   │
   ▼
[5] 置信度评估
   ├─ 指数可分性
   ├─ 模型softmax概率
   └─ 空间一致性
   │
   ▼
输出：change_raster + change_stats + confidence
```

---

## 2. 数据预处理流程

### 2.1 云与阴影掩膜

使用 Sentinel-2 自带的 Scene Classification Layer (SCL) 与 `s2cloudless` 双重掩膜：

- SCL 类别排除：3（云阴影）、8（中概率云）、9（高概率云）、10（卷云）、11（雪）
- `s2cloudless` 概率 > 0.4 视为云

### 2.2 年度无云合成

对每年生长季（6-8月）全部影像做中值合成，减少残留云影响：

```python
def annual_composite(images, dates, year):
    """对某年生长季影像做中值合成"""
    seasonal = [img for img, d in zip(images, dates)
                if year == d.year and 6 <= d.month <= 8]
    return np.nanmedian(np.stack(seasonal), axis=0)
```

### 2.3 重采样与配准

- B11/B12 从 20m 双线性重采样至 10m
- 以 2018 年为基准，对后续年份做相位相关配准（`skimage.registration.phase_cross_correlation`），要求 RMSE < 0.5 像元

### 2.4 归一化与 AOI 裁剪

- 反射率除以 10000 转为 [0,1]
- 用 AOI 矢量裁剪，输出固定网格

### 2.5 预处理输出契约

```json
{
  "composite_path": "s3://output/composite_{year}.tif",
  "bands": ["B02","B03","B04","B08","B11","B12"],
  "crs": "EPSG:32650",
  "resolution": 10,
  "valid_mask": "s3://output/valid_{year}.tif",
  "cloud_ratio": 0.03
}
```

---

## 3. 建筑与植被变化提取算法

### 3.1 特征指数

| 指数 | 公式 | 用途 |
|------|------|------|
| NDVI | (NIR - Red) / (NIR + Red) | 植被 |
| NDBI | (SWIR1 - NIR) / (SWIR1 + NIR) | 建筑/裸土 |
| NDWI | (Green - NIR) / (Green + NIR) | 水体排除 |
| BSI | ((SWIR1+Red)-(NIR+Blue)) / ((SWIR1+Red)+(NIR+Blue)) | 裸土 |

### 3.2 双轨变化提取

**轨道A：指数阈值 + CVA（快速、可解释）**

```python
def index_based_change(img_t0, img_t1, valid_mask):
    ndvi_t0, ndvi_t1 = ndvi(img_t0), ndvi(img_t1)
    ndbi_t0, ndbi_t1 = ndbi(img_t0), ndbi(img_t1)
    ndwi_t1 = ndwi(img_t1)

    # 变化量
    d_ndvi = ndvi_t1 - ndvi_t0
    d_ndbi = ndbi_t1 - ndbi_t0

    # 四类变化
    building_gain = (d_ndbi > 0.10) & (d_ndvi < -0.10) & (ndwi_t1 < 0.1)
    building_loss = (d_ndbi < -0.10) & (d_ndvi > 0.10)
    vegetation_gain = (d_ndvi > 0.15) & (d_ndbi < 0.05)
    vegetation_loss = (d_ndvi < -0.15) & (d_ndbi < 0.10)

    # CVA 幅度
    cva = np.sqrt(d_ndvi**2 + d_ndbi**2)
    change_mask = cva > 0.12
    return {
        "building_gain": building_gain & change_mask & valid_mask,
        "building_loss": building_loss & change_mask & valid_mask,
        "vegetation_gain": vegetation_gain & change_mask & valid_mask,
        "vegetation_loss": vegetation_loss & change_mask & valid_mask,
        "cva_magnitude": cva
    }
```

**轨道B：语义分割模型（U-Net）**

- 输入：t0 与 t1 的 6 波段堆叠（12 通道）
- 输出：4 类变化概率图（building_gain / building_loss / vegetation_gain / vegetation_loss）
- 训练数据：人工标注 + 开源建筑变化数据集（如 LEVIR-CD、WHU-CD）迁移学习

```python
import torch
import torch.nn as nn

class ChangeUNet(nn.Module):
    def __init__(self, in_ch=12, out_ch=4):
        super().__init__()
        # 编码器-解码器结构（略），最终输出 out_ch 通道
        self.encoder = ...
        self.decoder = ...
        self.head = nn.Conv2d(64, out_ch, 1)

    def forward(self, x):
        feat = self.decoder(self.encoder(x))
        return torch.softmax(self.head(feat), dim=1)  # [B,4,H,W]
```

### 3.3 双轨融合策略

```
融合规则：
- 若两轨一致 → 直接采纳，置信度+
- 若仅一轨命中 → 标记为"待复核"，置信度降低
- 若冲突 → 以模型概率与指数强度加权投票
```

```python
def fuse(index_result, model_prob, w_index=0.4, w_model=0.6):
    fused = {}
    for i, cls in enumerate(["building_gain","building_loss",
                              "vegetation_gain","vegetation_loss"]):
        score = w_index * index_result[cls].astype(float) + w_model * model_prob[i]
        fused[cls] = score > 0.5
        fused[cls + "_score"] = score
    return fused
```

### 3.4 后处理

- **形态学滤波**：开运算去噪，闭运算填补孔洞（`cv2.morphologyEx`）
- **最小图斑过滤**：连通域面积 < 5 像元（500 m²）剔除
- **水体排除**：NDWI > 0.2 区域不计入建筑增益

---

## 4. 置信度评估方法

### 4.1 三层置信度

| 层级 | 指标 | 计算方式 |
|------|------|----------|
| 像元级 | 指数可分性 | 基于指数变化幅度归一化，min(1, |d_index|/0.3) |
| 像元级 | 模型概率 | U-Net softmax 最大类概率 |
| 区域级 | 空间一致性 | 连通域内像元置信度均值 × 面积权重 |

### 4.2 综合置信度公式

```python
def compute_confidence(d_index, model_prob, region_consistency):
    conf_index = np.clip(np.abs(d_index) / 0.3, 0, 1)
    conf_model = model_prob
    pixel_conf = 0.4 * conf_index + 0.6 * conf_model
    return pixel_conf * region_consistency  # 区域一致性为0.7~1.0
```

### 4.3 置信度分级

| 等级 | 范围 | 含义 |
|------|------|------|
| High | > 0.85 | 可直接采纳 |
| Medium | 0.6 - 0.85 | 建议人工抽检 |
| Low | < 0.6 | 需复核或重算 |

### 4.4 精度验证

- 抽样 300 个验证点，人工判读，计算混淆矩阵与 F1
- 目标：建筑变化 F1 > 0.85，植被变化 F1 > 0.80

---

## 5. 核心代码接口

### 5.1 主入口

```python
class ImageAnalyst:
    def __init__(self, config):
        self.crs = config["crs"]
        self.resolution = config["resolution"]
        self.model = load_change_unet(config["model_path"])
        self.aoi = config["aoi"]

    def run(self, task):
        """
        输入: task = {
            "task_id": str,
            "image_pairs": [{"t0":date,"t1":date,"t0_path":...,"t1_path":...}],
            "aoi": geojson,
            "crs": str,
            "resolution": int
        }
        输出: change_raster + change_stats + confidence
        """
        results = []
        for pair in task["image_pairs"]:
            img_t0 = self.preprocess(pair["t0_path"], pair["t0"])
            img_t1 = self.preprocess(pair["t1_path"], pair["t1"])

            idx_result = index_based_change(img_t0, img_t1, img_t1.valid_mask)
            model_prob = self.model_infer(img_t0, img_t1)

            fused = fuse(idx_result, model_prob)
            fused = self.postprocess(fused)

            conf = compute_confidence(
                idx_result["cva_magnitude"],
                model_prob,
                region_consistency=fused
            )

            results.append(self.pack(pair, fused, conf))

        return self.merge(results)
```

### 5.2 子方法接口

```python
def preprocess(self, path, date):
    """云掩膜 + 重采样 + 归一化，返回 ImageCube 对象"""
    ...

def model_infer(self, img_t0, img_t1):
    """U-Net 推理，返回 [4,H,W] 概率图"""
    x = torch.cat([img_t0.tensor, img_t1.tensor], dim=0).unsqueeze(0)
    with torch.no_grad():
        return self.model(x).squeeze(0).cpu().numpy()

def postprocess(self, fused):
    """形态学滤波 + 最小图斑过滤 + 水体排除"""
    ...

def pack(self, pair, fused, conf):
    """打包输出为标准契约"""
    return {
        "t0": str(pair["t0"]), "t1": str(pair["t1"]),
        "change_raster": save_geotiff(fused),
        "change_stats": count_pixels(fused),
        "confidence_mean": float(conf.mean()),
        "confidence_map": save_geotiff(conf)
    }

def merge(self, results):
    """多时相对合并为2018-2023总变化"""
    ...
```

### 5.3 输出契约

```json
{
  "task_id": "city_expansion_001",
  "change_raster": "s3://output/change_2018_2023.tif",
  "confidence_map": "s3://output/confidence.tif",
  "change_stats": {
    "building_gain_pixels": 125430,
    "building_loss_pixels": 3200,
    "vegetation_gain_pixels": 45210,
    "vegetation_loss_pixels": 98760,
    "total_area_km2": 25.3
  },
  "confidence_mean": 0.87,
  "confidence_level": "High",
  "method": "NDVI+NDBI+CVA + U-Net fusion",
  "valid_ratio": 0.97
}
```

---

## 6. 实现要点与建议

1. **时序一致性**：每年合成影像需统一投影、网格、时间窗口，避免物候差异误判为变化。
2. **水体与阴影排除**：城市水体、建筑阴影易误判为建筑增益，必须用 NDWI + SCL 双重排除。
3. **样本迁移**：城市建成区标注成本高，建议用 LEVIR-CD 预训练 + 本地少量样本微调。
4. **可解释输出**：除栅格外保留 CVA 幅度图与指数变化图，便于下游时间序列分析员与地图叙事员使用。
5. **性能优化**：大区域分块推理（tile 512×512，overlap 64），GPU 批处理。

Next request.

---------- 第 3 轮 ----------

[AI User]
Instruction: 请详细设计时间序列分析员的实现方案，重点说明如何基于影像解析员输出的变化栅格与多时相特征检测突变点，包括时序特征构建、突变检测算法（如PELT/BFAST/CUSUM）、事件分类与置信度评估，并给出核心代码接口。
Input: 输入为卫星影像解析员输出的 change_raster 与逐年 NDVI/NDBI 时序特征（2018-2023，共6期），AOI 为城市建成区，需区分 building_gain、building_loss、vegetation_gain、vegetation_loss 四类突变事件。

[AI Assistant]
Solution: 下面给出时间序列分析员的详细实现方案，聚焦基于影像解析员输出的 change_raster 与逐年 NDVI/NDBI 时序（2018-2023，6期），在建成区 AOI 内检测四类突变事件，涵盖时序特征构建、突变检测算法、事件分类与置信度评估，并给出核心代码接口。

---

## 1. 输入解析与总体流程

### 1.1 输入规格

| 项目 | 说明 |
|------|------|
| change_raster | 影像解析员输出的四类变化掩膜（building_gain/loss、vegetation_gain/loss），10m 栅格 |
| 时序特征 | 逐年 NDVI/NDBI 均值或逐像元时序，2018-2023 共 6 期 |
| AOI | 城市建成区矢量边界 |
| 时间粒度 | 年度（可扩展到月度/半月度） |

### 1.2 处理流程总览

```
change_raster + 逐年 NDVI/NDBI 时序
   │
   ▼
[1] 时序特征构建
   ├─ 像元级 / 对象级时序提取
   ├─ 缺失值插值 + 平滑
   ├─ 特征衍生（斜率、方差、物候）
   └─ 时间轴对齐
   │
   ▼
[2] 突变检测（多算法融合）
   ├─ PELT（变点）
   ├─ BFAST（趋势+季节+突变）
   ├─ CUSUM（累积和）
   └─ 投票融合
   │
   ▼
[3] 事件分类
   ├─ 四类映射规则
   ├─ 幅度×方向判定
   └─ 与 change_raster 空间一致性校验
   │
   ▼
[4] 置信度评估
   ├─ 突变强度
   ├─ 多算法一致性
   ├─ 时序信噪比
   └─ 空间聚集性
   │
   ▼
输出：breakpoints 事件列表 + trend + confidence
```

---

## 2. 时序特征构建

### 2.1 像元级 vs 对象级

- **像元级**：逐像元时序，保留空间细节，适合精细突变定位；缺点是噪声大。
- **对象级**：基于影像解析员的连通域（变化图斑）取均值时序，抗噪强，适合事件级分析。

**推荐策略**：先对象级检测事件，再回映到像元级定位。

### 2.2 时序提取

```python
def extract_timeseries(composite_stack, valid_mask, regions=None):
    """
    composite_stack: [T,H,W,bands] 逐年年合成
    regions: 变化图斑标签图，None 则像元级
    返回: series [T, N] (N=像元数或图斑数)
    """
    ndvi = (composite_stack[...,3] - composite_stack[...,2]) / \
           (composite_stack[...,3] + composite_stack[...,2] + 1e-6)
    ndbi = (composite_stack[...,4] - composite_stack[...,3]) / \
           (composite_stack[...,4] + composite_stack[...,3] + 1e-6)

    if regions is not None:
        return region_mean(ndvi, regions), region_mean(ndbi, regions)
    return ndvi, ndbi
```

### 2.3 缺失值与平滑

- **缺失值**：线性插值 + 边界外推（`pandas.interpolate`）
- **平滑**：Savitzky-Golay 滤波（窗口 3，阶 2），保留突变同时去噪

```python
from scipy.signal import savgol_filter

def smooth_series(series, window=3, poly=2):
    if len(series) < window:
        return series
    return savgol_filter(series, window, poly)
```

### 2.4 衍生特征

| 特征 | 公式 | 含义 |
|------|------|------|
| 斜率 | 线性回归 slope | 长期趋势 |
| 方差 | std(series) | 波动性 |
| 一阶差分 | Δx_t = x_t - x_{t-1} | 突变候选 |
| 突变幅度 | max(\|Δx\|) | 事件强度 |
| 信噪比 | mean(\|Δx\|) / std(noise) | 可检测性 |

---

## 3. 突变检测算法

### 3.1 PELT（Pruned Exact Linear Time）

适用于均值/方差突变，速度快，适合 6-期短序列。

```python
import ruptures as rpt

def pelt_detect(series, penalty=8):
    algo = rpt.Pelt(model="rbf").fit(series)
    bkps = algo.predict(pen=penalty)
    return bkps[:-1]  # 去掉末尾
```

### 3.2 BFAST（Breaks For Additive Season and Trend）

分解趋势+季节+残差，逐期检验突变。适合年度+季相数据。

```python
# 简化实现（完整用 bfast 包或 R 接口）
def bfast_detect(series, h=0.15):
    """
    h: 最小片段比例，6期建议 h=0.15~0.25
    返回突变点索引与幅度
    """
    from statsmodels.tsa.seasonal import STL
    if len(series) >= 4:
        stl = STL(series, period=2, robust=True).fit()
        resid = stl.resid
    else:
        resid = series - np.poly1d(np.polyfit(range(len(series)), series, 1))(range(len(series)))
    # CUSUM on residuals
    return cusum_detect(resid)
```

### 3.3 CUSUM（累积和）

对残差累积，检测均值漂移，灵敏度高。

```python
def cusum_detect(series, threshold=2.0):
    mean, std = np.mean(series), np.std(series) + 1e-6
    cusum_pos, cusum_neg = [0], [0]
    for x in series:
        cusum_pos.append(max(0, cusum_pos[-1] + (x - mean)/std - 0.5))
        cusum_neg.append(min(0, cusum_neg[-1] + (x - mean)/std + 0.5))
    # 超阈值的点作为突变候选
    bkps = [i for i,(p,n) in enumerate(zip(cusum_pos, cusum_neg))
            if p > threshold or n < -threshold]
    return bkps
```

### 3.4 多算法投票融合

```python
def fuse_breakpoints(series, min_votes=2):
    pelt_bkps = set(pelt_detect(series))
    bfast_bkps = set(bfast_detect(series))
    cusum_bkps = set(cusum_detect(series))

    all_bkps = pelt_bkps | bfast_bkps | cusum_bkps
    fused = []
    for bp in sorted(all_bkps):
        votes = (bp in pelt_bkps) + (bp in bfast_bkps) + (bp in cusum_bkps)
        if votes >= min_votes:
            fused.append({
                "index": bp,
                "date": YEARS[bp],
                "votes": votes,
                "magnitude": float(series[bp] - series[bp-1])
            })
    return fused
```

### 3.5 短序列（6期）适配建议

- 6 期序列对 BFAST 偏短，建议 `h=0.15` 且优先 PELT+CUSUM 融合。
- 若可获取月度合成，将序列扩展到 72 期，BFAST 效果更佳。

---

## 4. 事件分类

### 4.1 分类规则

对每个突变点，结合 NDVI/NDBI 突变方向与幅度映射为四类：

| NDVI 变化 | NDBI 变化 | 事件类型 |
|-----------|-----------|----------|
| ↓ 显著 | ↑ 显著 | building_gain |
| ↑ 显著 | ↓ 显著 | vegetation_gain |
| ↑ 显著 | ↓ 弱/不变 | vegetation_gain |
| ↓ 显著 | ↑ 弱/不变 | vegetation_loss |
| ↑ 弱 | ↓ 显著 | building_loss |

```python
def classify_event(d_ndvi, d_ndbi, thr=0.08):
    if d_ndvi < -thr and d_ndbi > thr:
        return "building_gain"
    if d_ndvi > thr and d_ndbi < -thr:
        return "vegetation_gain"  # 也可能建筑拆除
    if d_ndvi < -thr and d_ndbi < thr:
        return "vegetation_loss"
    if d_ndvi > thr and d_ndbi < -thr:
        return "building_loss"
    return "uncertain"
```

### 4.2 与 change_raster 空间一致性校验

- 突变点位置应落在对应变化图斑内
- 若不在，置信度降级并标记 `needs_review`
- 一致性比率 = 突变点落入对应变化类图斑的比例

```python
def spatial_consistency(bp_loc, change_raster, event_type):
    pixel_class = change_raster[bp_loc[1], bp_loc[0]]
    return 1.0 if pixel_class == event_type else 0.0
```

---

## 5. 置信度评估

### 5.1 四因子加权

| 因子 | 权重 | 计算方式 |
|------|------|----------|
| 突变强度 | 0.35 | min(1, \|Δ\|/0.25) |
| 多算法一致性 | 0.25 | votes / 3 |
| 时序信噪比 | 0.20 | \|Δ\| / std(residual) 归一化 |
| 空间一致性 | 0.20 | 与 change_raster 匹配度 |

```python
def event_confidence(bp, series, residual_std, spatial_match):
    strength = np.clip(abs(bp["magnitude"]) / 0.25, 0, 1)
    consistency = bp["votes"] / 3.0
    snr = np.clip(abs(bp["magnitude"]) / (residual_std + 1e-6) / 3.0, 0, 1)
    return 0.35*strength + 0.25*consistency + 0.20*snr + 0.20*spatial_match
```

### 5.2 置信度分级

| 等级 | 范围 | 处理 |
|------|------|------|
| High | > 0.85 | 直接采纳 |
| Medium | 0.6 - 0.85 | 人工抽检 |
| Low | < 0.6 | 标记待复核 |

---

## 6. 核心代码接口

### 6.1 主入口

```python
class TemporalAnalyst:
    def __init__(self, config):
        self.years = config["years"]  # [2018,...,2023]
        self.thresholds = config.get("thresholds", {})
        self.min_votes = config.get("min_votes", 2)

    def run(self, task):
        """
        输入: task = {
            "task_id": str,
            "change_raster": path,
            "timeseries_path": path,   # 逐年 NDVI/NDBI 堆叠
            "aoi": geojson,
            "regions_path": path       # 变化图斑标签（可选）
        }
        输出: breakpoints + trend + confidence
        """
        change_raster = load_raster(task["change_raster"])
        ts_stack = load_timeseries(task["timeseries_path"])  # [T,H,W,2]
        regions = load_raster(task.get("regions_path"))

        # 1. 时序提取与平滑
        ndvi_s, ndbi_s = extract_timeseries(ts_stack, None, regions)
        ndvi_s = smooth_series(ndvi_s)
        ndbi_s = smooth_series(ndbi_s)

        # 2. 突变检测
        ndvi_bkps = fuse_breakpoints(ndvi_s, self.min_votes)
        ndbi_bkps = fuse_breakpoints(ndbi_s, self.min_votes)

        # 3. 对齐 + 分类
        events = align_and_classify(ndvi_bkps, ndbi_bkps, self.thresholds)

        # 4. 空间一致性 + 置信度
        for ev in events:
            ev["spatial_match"] = spatial_consistency(
                ev["location"], change_raster, ev["type"])
            ev["confidence"] = event_confidence(
                ev, ndvi_s, residual_std(ndvi_s), ev["spatial_match"])

        # 5. 趋势统计
        trend = {
            "building": estimate_trend(ndbi_s),
            "vegetation": estimate_trend(ndvi_s)
        }

        return self.pack(task["task_id"], events, trend)
```

### 6.2 辅助接口

```python
def align_and_classify(ndvi_bkps, ndbi_bkps, thresholds):
    """合并 NDVI/NDBI 突变点，按时间对齐并分类"""
    events = []
    used = set()
    for nb in ndvi_bkps:
        # 找时间最近的 NDBI 突变点
        match = find_nearest(ndbi_bkps, nb["index"], tol=1)
        d_ndvi = nb["magnitude"]
        d_ndbi = match["magnitude"] if match else 0.0
        etype = classify_event(d_ndvi, d_ndbi, thresholds.get("delta", 0.08))
        events.append({
            "date": nb["date"],
            "type": etype,
            "d_ndvi": d_ndvi,
            "d_ndbi": d_ndbi,
            "votes": nb["votes"] + (match["votes"] if match else 0),
            "location": None  # 若为图斑级，回填质心
        })
        used.add(nb["index"])
    return events

def estimate_trend(series):
    """线性回归斜率，单位/年"""
    x = np.arange(len(series))
    slope = np.polyfit(x, series, 1)[0]
    return float(slope)

def residual_std(series):
    trend = np.poly1d(np.polyfit(range(len(series)), series, 1))
    return float(np.std(series - trend(range(len(series)))))

def pack(task_id, events, trend):
    return {
        "task_id": task_id,
        "breakpoints": events,
        "trend": trend,
        "method": "PELT+BFAST+CUSUM fusion",
        "n_events": len(events),
        "high_conf_events": sum(1 for e in events if e["confidence"] > 0.85)
    }
```

### 6.3 输出契约

```json
{
  "task_id": "city_expansion_001",
  "breakpoints": [
    {
      "date": "2020-06-01",
      "type": "building_gain",
      "d_ndvi": -0.21,
      "d_ndbi": 0.24,
      "magnitude": 0.24,
      "votes": 3,
      "confidence": 0.91,
      "location": [116.40, 39.90]
    },
    {
      "date": "2021-06-01",
      "type": "vegetation_loss",
      "d_ndvi": -0.31,
      "d_ndbi": 0.05,
      "magnitude": -0.31,
      "votes": 2,
      "confidence": 0.78,
      "location": [116.42, 39.91]
    }
  ],
  "trend": {"building": 0.08, "vegetation": -0.12},
  "method": "PELT+BFAST+CUSUM fusion",
  "n_events": 12,
  "high_conf_events": 8
}
```

---

## 7. 实现要点与建议

1. **短序列处理**：6 期序列宜用 PELT+CUSUM，BFAST 作为辅助；有条件扩展到月度序列。
2. **对象级优先**：先在图斑对象上检测，再回映像元，降低噪声误检。
3. **一致性校验回环**：若某突变点与 change_raster 空间不匹配，可反馈给影像解析员重算局部区域。
4. **可解释证据链**：每个事件保留 votes、d_ndvi、d_ndbi、spatial_match，便于地图叙事员生成报告。
5. **趋势与突变分离**：趋势用线性回归，突变用变点检测，避免混淆渐进扩张与突发事件。

Next request.

---------- 第 4 轮 ----------

[AI User]
Instruction: 请详细设计地图叙事员的实现方案，说明如何基于变化栅格、突变事件列表与统计量自动生成热力图、交互式地图和自然语言报告，包括可视化设计、报告模板生成逻辑（可结合LLM）和核心代码接口。
Input: 输入为影像解析员输出的 change_raster 与 change_stats、时间序列分析员输出的 breakpoints 与 trend，AOI 为城市建成区，报告语言为中文，输出格式包括 HTML 交互地图、PNG 热力图和 Markdown/PDF 报告。

[AI Assistant]
Solution: 下面给出地图叙事员的详细实现方案，基于变化栅格、统计量与突变事件列表，自动生成热力图、交互式地图与中文自然语言报告，覆盖可视化设计、报告模板生成逻辑（结合 LLM）与核心代码接口。

---

## 1. 输入解析与总体流程

### 1.1 输入规格

| 来源 | 数据 | 用途 |
|------|------|------|
| 影像解析员 | change_raster（四类变化栅格） | 空间可视化 |
| 影像解析员 | change_stats（各类像元数、面积、置信度） | 统计摘要 |
| 时间序列分析员 | breakpoints（突变事件列表） | 时间线、事件标注 |
| 时间序列分析员 | trend（建筑/植被趋势斜率） | 趋势描述 |

### 1.2 处理流程总览

```
change_raster + change_stats + breakpoints + trend
   │
   ▼
[1] 数据准备与降采样
   ├─ 栅格金字塔（多分辨率）
   ├─ 矢量转换（图斑 → GeoJSON）
   └─ 统计聚合（AOI 内分区统计）
   │
   ▼
[2] 静态热力图（PNG）
   ├─ 建筑变化热力图（Reds）
   ├─ 植被变化热力图（Greens）
   └─ 综合变化图 + 图例 + 比例尺
   │
   ▼
[3] 交互式地图（HTML）
   ├─ 底图（Leaflet/Mapbox）
   ├─ 变化图层（栅格切片/矢量）
   ├─ 突变事件标注（时间轴）
   └─ 图层切换 + 弹出信息
   │
   ▼
[4] 自然语言报告
   ├─ 结构化事实抽取
   ├─ 模板骨架
   ├─ LLM 文案生成（中文）
   └─ Markdown → PDF 渲染
   │
   ▼
输出：heatmap.png + map.html + report.md + report.pdf
```

---

## 2. 数据准备与降采样

### 2.1 栅格金字塔

大区域 change_raster 直接渲染会卡顿，需构建金字塔：

```python
from rio_tiler.io import COGReader

def build_pyramid(raster_path, out_dir, levels=[1,2,4,8,16]):
    """用 COG 生成多分辨率金字塔"""
    with COGReader(raster_path) as cog:
        for z in levels:
            cog.tile(...)  # 生成瓦片
```

### 2.2 矢量转换

将变化栅格转为 GeoJSON 图斑，便于交互地图渲染：

```python
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape

def raster_to_geojson(raster_path, class_value, min_area=5):
    with rasterio.open(raster_path) as src:
        mask = (src.read(1) == class_value)
        geoms = []
        for geom, val in shapes(mask.astype(np.uint8),
                                transform=src.transform):
            s = shape(geom)
            if s.area >= min_area * 100:  # 像元面积 × 阈值
                geoms.append(s)
        return geoms
```

### 2.3 分区统计

按 AOI 内网格（如 1km×1km）聚合变化强度，用于热力图：

```python
def grid_aggregate(change_raster, cell_size_km=1.0):
    """按公里网格统计建筑/植被变化像元数"""
    stats = {}
    for cell in generate_grid(AOI, cell_size_km):
        stats[cell.id] = {
            "building_gain": count(change_raster, cell, cls="building_gain"),
            "vegetation_loss": count(change_raster, cell, cls="vegetation_loss")
        }
    return stats
```

---

## 3. 静态热力图设计（PNG）

### 3.1 可视化设计原则

| 要素 | 设计 |
|------|------|
| 配色 | 建筑增益红（Reds），植被损失橙（OrRd），植被增益绿（Greens） |
| 色阶 | 分位数分级（quantile），避免长尾 |
| 底图 | 灰色简化底图（低透明度） |
| 图例 | 分类图例 + 数值刻度 |
| 比例尺 | 左下角，公里单位 |
| 指北针 | 右上角 |
| 标题 | “XX城市 2018-2023 建筑扩张热力图” |

### 3.2 双面板热力图

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_heatmaps(change_raster, aoi_boundary, grid_stats, out_path):
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # 左：建筑增益热力图
    ax = axes[0]
    ax.imshow(grid_stats["building_gain"], cmap="Reds", alpha=0.8)
    ax.plot(aoi_boundary.x, aoi_boundary.y, "k-", lw=1)
    ax.set_title("建筑扩张热力图 (2018-2023)", fontsize=14)
    ax.set_xlabel("经度")
    ax.set_ylabel("纬度")

    # 右：植被损失热力图
    ax = axes[1]
    ax.imshow(grid_stats["vegetation_loss"], cmap="OrRd", alpha=0.8)
    ax.plot(aoi_boundary.x, aoi_boundary.y, "k-", lw=1)
    ax.set_title("植被损失热力图 (2018-2023)", fontsize=14)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
```

### 3.3 综合变化图（含突变事件标注）

在热力图上叠加 breakpoints 位置：

```python
def plot_events_on_map(ax, breakpoints):
    for ev in breakpoints:
        color = {"building_gain":"red","building_loss":"blue",
                 "vegetation_gain":"green","vegetation_loss":"orange"}[ev["type"]]
        ax.scatter(ev["location"][0], ev["location"][1],
                   c=color, s=50*ev["confidence"], edgecolors="black")
        ax.annotate(ev["date"][:7], ev["location"], fontsize=8)
```

---

## 4. 交互式地图设计（HTML）

### 4.1 技术选型

- **底图**：OpenStreetMap / CartoDB Positron（浅色）
- **图层**：Folium（Python 生成 Leaflet HTML）
- **栅格叠加**：变化图斑 GeoJSON + 同步 opacity 控制
- **时间轴**：按年份或突变事件切换

### 4.2 图层结构

```
- 底图 (base)
- 建筑增益图层 (building_gain, 红)
- 建筑损失图层 (building_loss, 蓝)
- 植被增益图层 (vegetation_gain, 绿)
- 植被损失图层 (vegetation_loss, 橙)
- 突变事件点图层 (breakpoints)
- 图例控件
- 时间轴控件
```

### 4.3 核心实现

```python
import folium
from folium import plugins

def build_interactive_map(center, geojson_layers, breakpoints, out_path):
    m = folium.Map(location=center, zoom_start=12,
                   tiles="CartoDB positron")

    colors = {
        "building_gain": "#d62728",
        "building_loss": "#1f77b4",
        "vegetation_gain": "#2ca02c",
        "vegetation_loss": "#ff7f0e"
    }

    # 变化图层
    for cls, geoms in geojson_layers.items():
        folium.GeoJson(
            geoms,
            name=cls,
            style_function=lambda x, c=colors[cls]: {
                "fillColor": c, "color": c, "weight": 0.5,
                "fillOpacity": 0.6
            },
            tooltip=folium.GeoJsonTooltip(fields=["area_km2"])
        ).add_to(m)

    # 突变事件
    for ev in breakpoints:
        folium.CircleMarker(
            location=[ev["location"][1], ev["location"][0]],
            radius=6 + 6*ev["confidence"],
            color=colors[ev["type"]],
            fill=True, fillOpacity=0.8,
            popup=folium.Popup(
                f"<b>{ev['date'][:7]}</b><br>"
                f"类型: {ev['type']}<br>"
                f"置信度: {ev['confidence']:.2f}<br>"
                f"ΔNDVI: {ev.get('d_ndvi',0):.2f}<br>"
                f"ΔNDBI: {ev.get('d_ndbi',0):.2f}",
                max_width=300
            )
        ).add_to(m)

    folium.LayerControl().add_to(m)
    plugins.MiniMap().add_to(m)
    plugins.Fullscreen().add_to(m)
    m.save(out_path)
```

### 4.4 时间轴控件

用 `folium.plugins.TimestampedGeoJson` 或自定义滑块，按年份过滤突变事件：

```python
def add_timeline(m, breakpoints):
    features = [{
        "type": "Feature",
        "geometry": {"type":"Point","coordinates":[e["location"][0], e["location"][1]]},
        "properties": {"time": e["date"], "type": e["type"], "conf": e["confidence"]}
    } for e in breakpoints]

    plugins.TimestampedGeoJson(
        {"type":"FeatureCollection","features":features},
        period="P1Y",
        add_last_point=True,
        time_slider_drag_update=True
    ).add_to(m)
```

---

## 5. 自然语言报告生成

### 5.1 结构化事实抽取

先抽取事实，再交给 LLM 生成文案，保证事实准确：

```python
def extract_facts(change_stats, breakpoints, trend, aoi_name="研究区"):
    facts = {
        "aoi": aoi_name,
        "period": "2018-2023",
        "building_gain_km2": change_stats["building_gain_pixels"] * 100 / 1e6,
        "building_loss_km2": change_stats["building_loss_pixels"] * 100 / 1e6,
        "vegetation_gain_km2": change_stats["vegetation_gain_pixels"] * 100 / 1e6,
        "vegetation_loss_km2": change_stats["vegetation_loss_pixels"] * 100 / 1e6,
        "building_trend": trend["building"],
        "vegetation_trend": trend["vegetation"],
        "peak_event": max(breakpoints, key=lambda e: e["confidence"]) if breakpoints else None,
        "n_events": len(breakpoints),
        "high_conf_events": [e for e in breakpoints if e["confidence"] > 0.85]
    }
    return facts
```

### 5.2 报告模板骨架

```python
REPORT_TEMPLATE = """
# {aoi} 城市扩张侦探报告（{period}）

## 一、执行摘要
{executive_summary}

## 二、关键发现
- 建筑扩张：{building_gain_km2:.2f} km²
- 建筑减少：{building_loss_km2:.2f} km²
- 植被增加：{vegetation_gain_km2:.2f} km²
- 植被减少：{vegetation_loss_km2:.2f} km²

## 三、时间线分析
{timeline}

## 四、空间分布
{spatial_desc}

## 五、趋势与建议
{conclusion}
"""
```

### 5.3 LLM 文案生成

用 Prompt 将事实转为中文自然语言：

```python
PROMPT = """你是一名遥感分析报告撰写员。请根据以下事实生成中文报告段落，
要求：专业、客观、数据准确，不编造数据。

事实：
- 研究区：{aoi}
- 时间：{period}
- 建筑扩张：{building_gain_km2:.2f} km²，趋势 {building_trend:+.3f}/年
- 植被减少：{vegetation_loss_km2:.2f} km²，趋势 {vegetation_trend:+.3f}/年
- 主要突变事件：{peak_event_desc}
- 高置信度事件数：{n_high}

请生成：
1. 执行摘要（150字内）
2. 时间线分析（按年份串起突变事件）
3. 趋势与建议（3条）
"""

def generate_sections(facts, llm_client):
    prompt = PROMPT.format(**facts)
    response = llm_client.chat(prompt)  # 返回结构化 JSON
    return json.loads(response)
```

### 5.4 时间线串接逻辑

```python
def build_timeline(breakpoints):
    lines = []
    for yr in sorted(set(e["date"][:4] for e in breakpoints)):
        evs = [e for e in breakpoints if e["date"][:4] == yr]
        desc = "、".join(
            f"{e['type']}（置信度{e['confidence']:.2f}）" for e in evs)
        lines.append(f"- **{yr}年**：{desc}")
    return "\n".join(lines)
```

### 5.5 Markdown → PDF

```python
import markdown
from weasyprint import HTML

def render_pdf(md_text, out_path):
    html = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    full_html = f"<html><body style='font-family:sans-serif'>{html}</body></html>"
    HTML(string=full_html).write_pdf(out_path)
```

---

## 6. 核心代码接口

### 6.1 主入口

```python
class MapNarrator:
    def __init__(self, config):
        self.language = config.get("language", "zh-CN")
        self.llm = load_llm_client(config.get("llm"))
        self.center = config["center"]
        self.formats = config.get("formats", ["html","png","md","pdf"])

    def run(self, task):
        """
        输入: task = {
            "task_id": str,
            "change_raster": path,
            "change_stats": dict,
            "breakpoints": list,
            "trend": dict,
            "aoi": geojson,
            "aoi_name": str
        }
        输出: heatmap + map + report
        """
        # 1. 数据准备
        geojson_layers = {
            cls: raster_to_geojson(task["change_raster"], cls)
            for cls in ["building_gain","building_loss",
                        "vegetation_gain","vegetation_loss"]
        }
        grid_stats = grid_aggregate(task["change_raster"])

        # 2. 静态热力图
        heatmap_path = f"s3://output/heatmap_{task['task_id']}.png"
        plot_heatmaps(task["change_raster"], task["aoi"],
                      grid_stats, heatmap_path)

        # 3. 交互地图
        map_path = f"s3://output/map_{task['task_id']}.html"
        build_interactive_map(self.center, geojson_layers,
                              task["breakpoints"], map_path)

        # 4. 报告
        facts = extract_facts(task["change_stats"], task["breakpoints"],
                              task["trend"], task["aoi_name"])
        sections = generate_sections(facts, self.llm)
        md_text = REPORT_TEMPLATE.format(
            aoi=facts["aoi"], period=facts["period"],
            executive_summary=sections["executive_summary"],
            timeline=build_timeline(task["breakpoints"]),
            spatial_desc=sections["spatial_desc"],
            conclusion=sections["conclusion"],
            **facts
        )
        md_path = f"s3://output/report_{task['task_id']}.md"
        pdf_path = f"s3://output/report_{task['task_id']}.pdf"
        save_text(md_text, md_path)
        render_pdf(md_text, pdf_path)

        return self.pack(task["task_id"], heatmap_path, map_path,
                         md_path, pdf_path, sections["executive_summary"])
```

### 6.2 输出契约

```json
{
  "task_id": "city_expansion_001",
  "heatmap_url": "s3://output/heatmap_city_expansion_001.png",
  "interactive_map": "s3://output/map_city_expansion_001.html",
  "report_markdown": "s3://output/report_city_expansion_001.md",
  "report_pdf": "s3://output/report_city_expansion_001.pdf",
  "summary": "2018-2023年间，研究区建筑扩张12.5 km²，植被减少9.8 km²，2020年为突变高峰，主要集中于城市东部边缘。",
  "key_findings": [
    "建筑增益主要集中在东部新区",
    "植被损失与建筑扩张高度空间重合",
    "2020年突变事件置信度最高（0.91）"
  ],
  "language": "zh-CN",
  "generator": "MapNarrator v1.0"
}
```

---

## 7. 实现要点与建议

1. **事实优先，LLM 润色**：所有数字由代码计算后注入模板，LLM 只负责语言组织，避免幻觉。
2. **可视化分层**：热力图用于宏观趋势，交互地图用于细节探索，报告用于决策沟通，三者互补。
3. **降采样与瓦片**：大 AOI 必须用 COG 瓦片 + 矢量简化，保证 HTML 加载流畅。
4. **中文排版**：PDF 渲染需指定中文字体（如 Noto Sans CJK），避免乱码。
5. **可访问性**：报告含摘要、图例、数据表，便于非专业读者理解。
6. **闭环反馈**：若报告发现空间不一致（如突变点不在变化图斑内），可标记并回传前两个智能体复核。

Next request.

---------- 第 5 轮 ----------

[AI User]
Instruction: 请设计三个子智能体之间的协同编排方案，重点说明 Orchestrator 如何管理共享上下文、事件触发顺序、跨智能体反馈回环与冲突消解，并给出一个完整的端到端运行示例（从用户任务到最终变化检测结果）。
Input: 三个子智能体已分别定义好输入输出契约（change_raster、breakpoints、heatmap/report），需支持置信度低时的局部重算反馈，以及结论冲突时的加权投票。

[AI Assistant]
Solution: 下面给出三个子智能体之间的协同编排方案，聚焦 Orchestrator 的共享上下文管理、事件触发顺序、跨智能体反馈回环与冲突消解，并给出一个完整端到端运行示例。

---

## 1. Orchestrator 总体设计

### 1.1 定位

Orchestrator 是“城市扩张侦探”的中枢，不做具体遥感计算，只负责：

- **调度**：按依赖关系触发子智能体
- **状态管理**：维护共享上下文 Shared Context
- **回环控制**：低置信度时触发局部重算
- **冲突消解**：结论冲突时加权投票
- **结果融合**：产出最终变化检测结果

### 1.2 架构图

```
                     ┌─────────────────────────────┐
                     │        Orchestrator          │
                     │  ┌───────────────────────┐  │
                     │  │ Shared Context Store   │  │
                     │  │ (task, artifacts, state│  │
                     │  └───────────────────────┘  │
                     │  ┌───────────────────────┐  │
                     │  │ Event Bus / Queue      │  │
                     │  └───────────────────────┘  │
                     │  ┌───────────────────────┐  │
                     │  │ Conflict Resolver      │  │
                     │  └───────────────────────┘  │
                     └─────────┬───────┬────────┬───┘
                               │       │        │
                     ┌─────────▼──┐ ┌──▼─────┐ ┌▼──────────┐
                     │ Image      │ │Temporal│ │ Map        │
                     │ Analyst    │ │Analyst │ │ Narrator   │
                     └────────────┘ └────────┘ └────────────┘
```

---

## 2. 共享上下文管理

### 2.1 Shared Context 结构

```json
{
  "task_id": "city_expansion_001",
  "status": "running",
  "current_stage": "temporal_analysis",
  "aoi": {...},
  "crs": "EPSG:32650",
  "resolution": 10,
  "time_range": ["2018-01-01", "2023-12-31"],
  "artifacts": {
    "change_raster": null,
    "change_stats": null,
    "confidence_map": null,
    "breakpoints": null,
    "trend": null,
    "heatmap": null,
    "interactive_map": null,
    "report_md": null,
    "report_pdf": null
  },
  "state_store": {
    "image_analyst": {"status": "completed", "confidence": 0.87, "retries": 0},
    "temporal_analyst": {"status": "running", "confidence": null, "retries": 0},
    "map_narrator": {"status": "pending", "confidence": null, "retries": 0}
  },
  "feedback_queue": [],
  "conflict_log": [],
  "audit_trail": [
    {"ts": "2024-01-01T10:00:00Z", "agent": "orchestrator", "event": "task_started"},
    {"ts": "2024-01-01T10:05:00Z", "agent": "image_analyst", "event": "completed", "confidence": 0.87}
  ]
}
```

### 2.2 上下文读写接口

```python
class SharedContext:
    def __init__(self, task_id, aoi, crs, resolution, time_range):
        self.data = {...}
        self.lock = threading.RLock()

    def read(self, key_path):
        with self.lock:
            return get_nested(self.data, key_path)

    def write(self, key_path, value, agent):
        with self.lock:
            old = get_nested(self.data, key_path)
            set_nested(self.data, key_path, value)
            self.data["audit_trail"].append({
                "ts": now_iso(), "agent": agent,
                "event": "write", "key": key_path,
                "old": old, "new": value
            })

    def append_feedback(self, feedback):
        with self.lock:
            self.data["feedback_queue"].append(feedback)
```

---

## 3. 事件触发顺序

### 3.1 依赖图

```
[Task Start]
    │
    ▼
[ImageAnalyst] ──change_raster/change_stats──► [TemporalAnalyst]
                                                      │
                                                      ▼
                                              breakpoints/trend
                                                      │
                                                      ▼
                                              [MapNarrator]
                                                      │
                                                      ▼
                                          heatmap/report
                                                      │
                                                      ▼
                                          [Orchestrator Merge]
```

### 3.2 触发规则

| 事件 | 触发条件 | 触发目标 |
|------|----------|----------|
| task_started | 用户提交任务 | ImageAnalyst |
| image_completed | change_raster + confidence 就绪 | TemporalAnalyst |
| temporal_completed | breakpoints + trend 就绪 | MapNarrator |
| narrator_completed | report 就绪 | Orchestrator 融合 |
| low_confidence_feedback | 任一阶段置信度 < 0.6 | 回环到上游 |
| conflict_detected | 跨智能体结论不一致 | ConflictResolver |

### 3.3 事件总线实现

```python
class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event, handler):
        self.subscribers[event].append(handler)

    def publish(self, event, payload):
        for h in self.subscribers[event]:
            h(payload)
```

---

## 4. 跨智能体反馈回环

### 4.1 低置信度回环场景

| 场景 | 触发 | 回环动作 |
|------|------|----------|
| 影像解析置信度低 | confidence < 0.6 | 提高分辨率/换算法重算局部区域 |
| 突变检测置信度低 | event.confidence < 0.6 | 请求影像解析员加密时序/局部重算 |
| 空间不一致 | 突变点不在对应变化图斑 | 双向复核，标记 needs_review |
| 报告异常 | 统计与地图不符 | 回传前两个智能体复核 |

### 4.2 回环控制逻辑

```python
MAX_RETRIES = 2

def handle_low_confidence(ctx, stage, confidence, region=None):
    state = ctx.read(f"state_store.{stage}")
    if confidence >= 0.6:
        return "continue"
    if state["retries"] >= MAX_RETRIES:
        ctx.write(f"state_store.{stage}.status", "degraded", "orchestrator")
        return "degraded"

    state["retries"] += 1
    feedback = {
        "to": upstream_of(stage),
        "reason": "low_confidence",
        "confidence": confidence,
        "region": region,           # 局部重算范围
        "action": "recompute_local",
        "tile_size": 512
    }
    ctx.append_feedback(feedback)
    return "retry"
```

### 4.3 局部重算接口

上游智能体收到反馈后，只重算指定区域：

```python
def on_feedback(feedback, agent):
    if feedback["action"] == "recompute_local":
        region = feedback["region"]
        # ImageAnalyst 只重算 region 内 tile
        new_result = agent.recompute(region, tile_size=feedback["tile_size"])
        # 融合回原结果
        agent.merge_local(new_result, region)
        bus.publish("local_recompute_done", {"region": region})
```

---

## 5. 冲突消解

### 5.1 冲突类型

| 冲突 | 表现 | 示例 |
|------|------|------|
| 空间冲突 | 突变点不在变化图斑内 | breakpoint 落在 vegetation_gain 图斑但类型为 building_gain |
| 类型冲突 | 同一区域分类不一致 | 影像判 building_gain，时序判 vegetation_loss |
| 统计冲突 | 统计量与栅格不符 | change_stats 像元数与 raster 实际不符 |
| 趋势冲突 | 趋势与突变方向相反 | 趋势 +0.08 但突变全为 loss |

### 5.2 加权投票公式

```python
def weighted_vote(candidates, weights):
    """
    candidates: {agent: class_label}
    weights: {agent: confidence}
    返回: (win_label, vote_score, detail)
    """
    scores = defaultdict(float)
    for agent, label in candidates.items():
        scores[label] += weights[agent]
    total = sum(scores.values()) + 1e-9
    win_label, win_score = max(scores.items(), key=lambda x: x[1])
    return win_label, win_score/total, dict(scores)
```

### 5.3 冲突消解规则

| 冲突类型 | 消解方式 |
|----------|----------|
| 类型冲突 | 置信度加权投票，低于 0.6 总和则标记 uncertain |
| 空间冲突 | 以 change_raster 空间为准，降低 breakpoint 置信度 |
| 统计冲突 | 以栅格重算为准，覆盖 stats |
| 趋势冲突 | 同时保留趋势与突变，报告中标注“需人工复核” |

### 5.4 冲突日志

```json
{
  "conflict_id": "c001",
  "type": "type_conflict",
  "region": [116.40, 39.90],
  "candidates": {
    "image_analyst": {"label": "building_gain", "confidence": 0.82},
    "temporal_analyst": {"label": "vegetation_loss", "confidence": 0.71}
  },
  "resolution": {
    "method": "weighted_vote",
    "winner": "building_gain",
    "score": 0.536,
    "action": "mark_needs_review"
  }
}
```

---

## 6. 完整端到端运行示例

### 6.1 用户任务

```json
{
  "task_id": "city_expansion_001",
  "aoi": "某城市建成区",
  "aoi_geojson": "s3://data/city_aoi.geojson",
  "time_range": ["2018-01-01", "2023-12-31"],
  "sensor": "Sentinel-2",
  "resolution": 10,
  "output_formats": ["html","png","md","pdf"],
  "language": "zh-CN"
}
```

### 6.2 编排时序

```
T0  Orchestrator 接收任务，初始化 Shared Context，发布 task_started
T1  ImageAnalyst 启动：
    - 预处理 → 云掩膜 → 年合成 → 配准
    - 指数+CVA + U-Net 融合
    - 输出 change_raster，置信度 0.87
T2  Orchestrator 校验：confidence 0.87 ≥ 0.6 → 通过
    发布 image_completed
T3  TemporalAnalyst 启动：
    - 提取逐年 NDVI/NDBI 时序
    - PELT+BFAST+CUSUM 融合检测
    - 发现 12 个突变事件，其中 4 个置信度 < 0.6
T4  Orchestrator 检测低置信度：
    - handle_low_confidence → 触发回环
    - 反馈给 ImageAnalyst：对低置信度区域局部重算
T5  ImageAnalyst 局部重算：
    - 对 4 个区域加密时序/提高分辨率
    - 更新 change_raster，回传
T6  TemporalAnalyst 重算局部事件，置信度提升至 0.78
    - 发现 1 个类型冲突（building_gain vs vegetation_loss）
T7  Orchestrator 触发 ConflictResolver：
    - 加权投票：0.536 vs 0.464 → 判 building_gain
    - 标记 needs_review，记录 conflict_log
T8  Orchestrator 校验通过，发布 temporal_completed
T9  MapNarrator 启动：
    - 生成热力图 PNG
    - 生成 Leaflet 交互地图 HTML
    - 抽取事实 → LLM 生成中文报告 → Markdown/PDF
T10 Orchestrator 融合所有输出：
    - 一致性校验：变化像元数与突变覆盖面积吻合度 0.92
    - 输出最终变化检测结果
T11 任务完成，状态置 completed
```

### 6.3 每一步的上下文变化

```json
// T1 后
{"artifacts": {"change_raster": "s3://.../change.tif",
               "change_stats": {"building_gain_pixels": 125430, ...}},
 "state_store": {"image_analyst": {"status":"completed","confidence":0.87}}}

// T3 后
{"artifacts": {"breakpoints": [12 个事件], "trend": {"building": 0.08, "vegetation": -0.12}},
 "state_store": {"temporal_analyst": {"status":"needs_review","confidence":0.72}}}

// T5 后
{"state_store": {"image_analyst": {"status":"recomputed","confidence":0.89,"retries":1}}}

// T10 后
{"status": "completed",
 "artifacts": {"heatmap": "...png", "interactive_map": "...html",
               "report_md": "...md", "report_pdf": "...pdf"}}
```

### 6.4 最终输出

```json
{
  "task_id": "city_expansion_001",
  "status": "completed",
  "summary": "2018-2023年间，研究区建筑扩张12.5 km²，植被减少9.8 km²，2020年为突变高峰，主要集中于城市东部边缘。共检测12个突变事件，其中8个高置信度，1个需人工复核。",
  "change_map": "s3://output/final_change_map.tif",
  "heatmap": "s3://output/heatmap_city_expansion_001.png",
  "interactive_map": "s3://output/map_city_expansion_001.html",
  "report": "s3://output/report_city_expansion_001.pdf",
  "breakpoints": [12 个事件],
  "trend": {"building": 0.08, "vegetation": -0.12},
  "overall_confidence": 0.86,
  "audit_trail": "s3://output/audit_city_expansion_001.jsonl",
  "conflict_log": "s3://output/conflicts_city_expansion_001.json",
  "evidence_chain": [
    {"agent": "ImageAnalyst",
     "outputs": ["change_raster","change_stats","confidence_map"],
     "confidence": 0.89, "retries": 1},
    {"agent": "TemporalAnalyst",
     "outputs": ["breakpoints","trend"],
     "confidence": 0.78, "retries": 1},
    {"agent": "MapNarrator",
     "outputs": ["heatmap","interactive_map","report_md","report_pdf"],
     "confidence": null}
  ]
}
```

---

## 7. 核心代码接口

### 7.1 Orchestrator 主类

```python
class Orchestrator:
    def __init__(self, config):
        self.ctx = SharedContext(...)
        self.bus = EventBus()
        self.image = ImageAnalyst(config["image"])
        self.temporal = TemporalAnalyst(config["temporal"])
        self.narrator = MapNarrator(config["narrator"])
        self.resolver = ConflictResolver()
        self._wire_events()

    def _wire_events(self):
        self.bus.subscribe("task_started", self._run_image)
        self.bus.subscribe("image_completed", self._run_temporal)
        self.bus.subscribe("temporal_completed", self._run_narrator)
        self.bus.subscribe("narrator_completed", self._finalize)
        self.bus.subscribe("feedback", self._handle_feedback)
        self.bus.subscribe("conflict", self._resolve_conflict)

    def run(self, task):
        self.ctx.write("status", "running", "orchestrator")
        self.bus.publish("task_started", task)
        return self.ctx.read("final_result")

    def _run_image(self, task):
        result = self.image.run(task)
        self.ctx.write("artifacts.change_raster", result["change_raster"], "orchestrator")
        self.ctx.write("artifacts.change_stats", result["change_stats"], "orchestrator")
        conf = result["confidence_mean"]
        self.ctx.write("state_store.image_analyst", 
                       {"status":"completed","confidence":conf,"retries":0}, "orchestrator")
        if conf < 0.6:
            self.bus.publish("feedback", {"to":"image","reason":"low_confidence","confidence":conf})
        else:
            self.bus.publish("image_completed", task)

    def _run_temporal(self, task):
        result = self.temporal.run({
            "task_id": task["task_id"],
            "change_raster": self.ctx.read("artifacts.change_raster"),
            "timeseries_path": task["timeseries_path"],
            "aoi": task["aoi"]
        })
        self.ctx.write("artifacts.breakpoints", result["breakpoints"], "orchestrator")
        self.ctx.write("artifacts.trend", result["trend"], "orchestrator")
        low = [e for e in result["breakpoints"] if e["confidence"] < 0.6]
        if low:
            self.bus.publish("feedback", {"to":"image","reason":"low_conf_events",
                                          "events":low})
        conflicts = self.resolver.detect_conflicts(result, self.ctx)
        if conflicts:
            for c in conflicts:
                self.bus.publish("conflict", c)
        if not low and not conflicts:
            self.bus.publish("temporal_completed", task)

    def _resolve_conflict(self, conflict):
        resolution = self.resolver.resolve(conflict)
        self.ctx.data["conflict_log"].append(resolution)

    def _handle_feedback(self, fb):
        if fb["to"] == "image":
            self.image.recompute_local(fb)
            self.ctx.write("state_store.image_analyst.retries",
                           self.ctx.read("state_store.image_analyst.retries") + 1,
                           "orchestrator")
            self.bus.publish("image_completed", self.ctx.read("task"))

    def _run_narrator(self, task):
        result = self.narrator.run({
            "task_id": task["task_id"],
            "change_raster": self.ctx.read("artifacts.change_raster"),
            "change_stats": self.ctx.read("artifacts.change_stats"),
            "breakpoints": self.ctx.read("artifacts.breakpoints"),
            "trend": self.ctx.read("artifacts.trend"),
            "aoi": task["aoi"],
            "aoi_name": task["aoi_name"]
        })
        self.ctx.write("artifacts.heatmap", result["heatmap_url"], "orchestrator")
        self.ctx.write("artifacts.interactive_map", result["interactive_map"], "orchestrator")
        self.ctx.write("artifacts.report_pdf", result["report_pdf"], "orchestrator")
        self.bus.publish("narrator_completed", task)

    def _finalize(self, task):
        final = self._merge_results()
        self.ctx.write("final_result", final, "orchestrator")
        self.ctx.write("status", "completed", "orchestrator")
```

### 7.2 ConflictResolver

```python
class ConflictResolver:
    def detect_conflicts(self, temporal_result, ctx):
        conflicts = []
        change_raster = load_raster(ctx.read("artifacts.change_raster"))
        for ev in temporal_result["breakpoints"]:
            loc = ev.get("location")
            if loc is None:
                continue
            pixel_cls = change_raster[loc[1], loc[0]]
            if pixel_cls != ev["type"]:
                conflicts.append({
                    "type": "type_conflict",
                    "location": loc,
                    "candidates": {
                        "image_analyst": {"label": pixel_cls, "confidence": 0.8},
                        "temporal_analyst": {"label": ev["type"], "confidence": ev["confidence"]}
                    }
                })
        return conflicts

    def resolve(self, conflict):
        candidates = {k: v["label"] for k, v in conflict["candidates"].items()}
        weights = {k: v["confidence"] for k, v in conflict["candidates"].items()}
        winner, score, detail = weighted_vote(candidates, weights)
        action = "accept" if score > 0.6 else "mark_needs_review"
        return {
            "conflict_id": gen_id(),
            "type": conflict["type"],
            "location": conflict["location"],
            "candidates": conflict["candidates"],
            "resolution": {"method": "weighted_vote",
                           "winner": winner, "score": score, "action": action},
            "detail": detail
        }
```

### 7.3 最终融合

```python
def _merge_results(self):
    ctx = self.ctx
    breakpoints = ctx.read("artifacts.breakpoints")
    stats = ctx.read("artifacts.change_stats")
    conflicts = ctx.data["conflict_log"]

    # 一致性校验
    covered = sum(e["confidence"] for e in breakpoints)
    consistency = min(1.0, covered / max(1, len(breakpoints)))

    # 综合置信度
    confs = [ctx.read("state_store.image_analyst.confidence") or 0,
             ctx.read("state_store.temporal_analyst.confidence") or 0]
    overall = float(np.mean([c for c in confs if c > 0]))

    return {
        "task_id": ctx.read("task_id"),
        "status": "completed" if consistency > 0.7 else "needs_review",
        "summary": generate_summary(stats, breakpoints, conflicts),
        "change_map": ctx.read("artifacts.change_raster"),
        "heatmap": ctx.read("artifacts.heatmap"),
        "interactive_map": ctx.read("artifacts.interactive_map"),
        "report": ctx.read("artifacts.report_pdf"),
        "breakpoints": breakpoints,
        "trend": ctx.read("artifacts.trend"),
        "overall_confidence": overall,
        "consistency_score": consistency,
        "conflict_log": conflicts,
        "audit_trail": ctx.data["audit_trail"]
    }
```

### 7.4 启动示例

```python
if __name__ == "__main__":
    config = load_config("config.yaml")
    orch = Orchestrator(config)
    task = {
        "task_id": "city_expansion_001",
        "aoi": load_geojson("s3://data/city_aoi.geojson"),
        "aoi_name": "某城市建成区",
        "time_range": ["2018-01-01", "2023-12-31"],
        "timeseries_path": "s3://data/ts_2018_2023.tif",
        "language": "zh-CN"
    }
    result = orch.run(task)
    print(result["summary"])
```

---

## 8. 实现要点与建议

1. **状态机化**：把 Shared Context 的 status/stage 设计成显式状态机，便于恢复与审计。
2. **回环限次**：每个智能体最多 2 次重算，避免无限循环；超限则降级并标记。
3. **冲突可解释**：每次冲突记录候选、权重、胜出、动作，写入 conflict_log。
4. **事件总线解耦**：智能体之间不直接调用，通过事件驱动，便于替换或扩展。
5. **审计可追溯**：audit_trail 记录每一步读写，满足科研可复现要求。
6. **降级策略**：任一阶段失败或超限，输出部分结果 + needs_review 标记，而非整体失败。

Next request.

---------- 第 6 轮 ----------

[AI User]
<CAMEL_TASK_DONE>

[AI Assistant]
Solution: 已确认任务完成。“城市扩张侦探”多智能体系统的设计已全部交付，涵盖以下四层内容：

## 交付总结

| 层级 | 交付内容 | 关键产物 |
|------|----------|----------|
| 总体架构 | 分层设计、共享上下文、事件驱动、协同规则 | 架构图 + 数据契约 |
| 卫星影像解析员 | 预处理、四类变化提取（指数+CVA+U-Net）、置信度评估 | change_raster + change_stats + confidence_map |
| 时间序列分析员 | 时序构建、PELT/BFAST/CUSUM 融合、事件分类、置信度 | breakpoints + trend |
| 地图叙事员 | 静态热力图、Leaflet 交互地图、LLM 中文报告 | heatmap.png + map.html + report.md/pdf |
| 协同编排 | Orchestrator、反馈回环、加权投票冲突消解、端到端示例 | final_result + audit_trail + conflict_log |

## 系统最终输出

```json
{
  "task_id": "city_expansion_001",
  "status": "completed",
  "summary": "2018-2023年间，研究区建筑扩张12.5 km²，植被减少9.8 km²，2020年为突变高峰，主要集中于城市东部边缘。",
  "change_map": "final_change_map.tif",
  "heatmap": "heatmap.png",
  "interactive_map": "map.html",
  "report": "report.pdf",
  "overall_confidence": 0.86,
  "consistency_score": 0.92
}
```

## 核心亮点

1. **双轨变化提取**：指数阈值+CVA 提供可解释性，U-Net 提供精度，加权融合。
2. **多算法突变检测**：PELT+BFAST+CUSUM 投票融合，适配 6 期短序列。
3. **事实优先叙事**：数字由代码计算注入模板，LLM 仅负责中文文案组织。
4. **反馈回环**：低置信度触发局部重算，最多 2 次，超限降级。
5. **加权投票冲突消解**：跨智能体结论不一致时按置信度加权，低于阈值标记 needs_review。
6. **全程可审计**：audit_trail 记录每一步读写，满足科研可复现要求。

任务已完成。如需进一步扩展（如增加月度时序、迁移到其他城市、接入实时卫星数据流），可随时提出新需求。

Next request.

任务完成（AI User 标记了 CAMEL_TASK_DONE）。
