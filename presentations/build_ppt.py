# -*- coding: utf-8 -*-
"""
生成《多智能体（LLM-MAS）调研汇报》完整版 PPT。

结构：封面 + 领域坐标(Yan 2025) + 目录 + 8 篇论文 × 4 页 + 致谢 = 36 页
每篇论文固定四页：题名页 → 动机与难点 → 模型 → 实验结果
顺序：CAMEL → MetaGPT → AutoGen → ChatDev → MacNet → AgentVerse
      → Multiagent Debate → GeoLLM-Squad(遥感)

用法： python3 build_ppt.py
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(ROOT, "figures")
OUT = os.path.join(HERE, "多智能体调研汇报.pptx")

# ---------- 设计系统 ----------
NAVY = RGBColor(0x0F, 0x2A, 0x4A)
BLUE = RGBColor(0x1F, 0x6F, 0xB2)
TEAL = RGBColor(0x0E, 0x8F, 0x82)
AMBER = RGBColor(0xC8, 0x6A, 0x00)
CRIMSON = RGBColor(0xB3, 0x26, 0x1E)
INK = RGBColor(0x22, 0x27, 0x2E)
GREY = RGBColor(0x5B, 0x64, 0x70)
LIGHT = RGBColor(0xF2, 0xF5, 0xF8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BORDER = RGBColor(0xDD, 0xE3, 0xEA)
WARM = RGBColor(0xFD, 0xF3, 0xE6)
FONT = "微软雅黑"

SW, SH = Inches(13.333), Inches(7.5)
M = Inches(0.62)
TOTAL = 36


def _p(layer, x, y, w, h):
    tb = layer.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf


def _run(p, text, size=14, bold=False, color=INK, italic=False):
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = FONT
    return r


def rect(layer, x, y, w, h, fill=LIGHT, line=None):
    from pptx.enum.shapes import MSO_SHAPE
    s = layer.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    s.adjustments[0] = 0.06
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1)
    s.shadow.inherit = False
    return s


def new_slide(prs, section="", page=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    if section:
        tf = _p(s, M, Inches(0.26), SW - 2 * M - Inches(1.4), Inches(0.3))
        _run(tf.paragraphs[0], section, size=11, bold=True, color=GREY)
    if page:
        tf = _p(s, SW - M - Inches(1.1), SH - Inches(0.46), Inches(1.1), Inches(0.3))
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT
        _run(p, f"{page:02d} / {TOTAL}", size=10.5, color=GREY)
    return s


def header(s, title, subtitle=None, accent=BLUE):
    rect(s, M, Inches(0.62), Inches(0.09), Inches(0.46), fill=accent)
    tf = _p(s, M + Inches(0.24), Inches(0.55), SW - 2 * M - Inches(0.3), Inches(0.55))
    _run(tf.paragraphs[0], title, size=25, bold=True, color=NAVY)
    if subtitle:
        tf = _p(s, M + Inches(0.24), Inches(1.08), SW - 2 * M - Inches(0.3), Inches(0.34))
        _run(tf.paragraphs[0], subtitle, size=13, color=GREY)
    return Inches(1.52)


def bullets(s, x, y, w, h, items, size=14, gap=8, bullet="▪ "):
    tf = _p(s, x, y, w, h)
    first = True
    for it in items:
        level, color, text = 0, None, it
        if isinstance(it, tuple):
            text = it[0]
            if len(it) > 1:
                level = it[1] or 0
            if len(it) > 2:
                color = it[2]
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(gap)
        p.line_spacing = 1.18
        mark = "" if text.endswith("：") else ("– " if level else bullet)
        _run(p, mark + text, size=size - level, bold=text.endswith("："),
             color=color or (INK if level == 0 else GREY))
    return tf


def figure(s, name, x, y, w, h, caption=None):
    path = os.path.join(FIG, name)
    ph = h if caption is None else h - Inches(0.28)
    if os.path.exists(path):
        iw, ih = Image.open(path).size
        scale = min(w / iw, ph / ih)
        pic = s.shapes.add_picture(
            path, x + (w - Emu(int(iw * scale))) // 2,
            y + (ph - Emu(int(ih * scale))) // 2,
            width=Emu(int(iw * scale)), height=Emu(int(ih * scale)))
        pic.line.color.rgb = BORDER
        pic.line.width = Pt(0.75)
    if caption:
        tf = _p(s, x, y + h - Inches(0.26), w, Inches(0.26))
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        _run(p, caption, size=9.5, color=GREY)


# ==================== 页面构建 ====================
def p_cover(prs, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, SW, SH, fill=NAVY)
    rect(s, 0, Inches(4.58), SW, Inches(0.055), fill=TEAL)
    tf = _p(s, M, Inches(2.02), SW - 2 * M, Inches(1.0))
    _run(tf.paragraphs[0], "多智能体（LLM-MAS）调研汇报", size=40, bold=True, color=WHITE)
    tf = _p(s, M, Inches(3.12), SW - 2 * M, Inches(1.2))
    _run(tf.paragraphs[0], "按协作机制选代表性论文：每篇讲清 动机/难点 → 模型 → 实验结果",
         size=18, color=RGBColor(0xBF, 0xD9, 0xEE))
    tf = _p(s, M, Inches(5.05), SW - 2 * M, Inches(0.9))
    _run(tf.paragraphs[0], "汇报人：____________　　2026 年 9 月",
         size=14, color=RGBColor(0x9F, 0xB8, 0xCC))
    return s


def p_yan(prs, page):
    s = new_slide(prs, "领域坐标", page)
    y = header(s, "领域坐标：LLM-MAS 的通信分类体系",
               "Yan et al. 2025 · Beyond Self-Talk · arXiv:2502.14321 · 后面 8 篇论文都能被这套框架定位",
               TEAL)
    figure(s, "yan_taxonomy.png", M + Inches(6.55), y - Inches(0.05),
           SW - M - (M + Inches(6.55)), Inches(4.75), "Yan 2025 分类树（p.3）")
    bullets(s, M, y, Inches(6.2), Inches(4.8), [
        "问题：LLM 本不是为相互通信设计的。现有综述多按应用或 Agent 能力分类，通信只被当成实现细节。",
        "本文把通信提为主线，给出两级分类：系统级 + 系统内，共 7 个维度。",
        "系统级 · 架构：谁和谁说话 → 扁平 / 层级 / 团队 / 社会 / 混合。",
        "系统级 · 目标：为什么说话 → 合作（含辩论式）/ 竞争 / 混合。",
        "系统级 · 协议：消息怎么走 → MCP（连工具）/ A2A（找 Agent）/ ANP（开放网络）。",
        "系统内 · 策略：什么时候说 → 逐个 / 同时 / 同时+摘要器。",
        "系统内 · 范式与内容：怎么表示、说什么 → 消息传递 / 言语行为 / 黑板；显式 / 隐式。",
        "价值：它不只罗列分类，每个维度都给出代价（扁平难扩展、层级易过载、逐个会累积错误）。",
    ], size=12.5, gap=7)
    return s


def p_toc(prs, page, papers):
    s = new_slide(prs, "目录", page)
    y = header(s, "按协作机制逐篇精读", "每篇固定四页：题名页 → 动机与难点 → 模型 → 实验结果", BLUE)
    colw = (SW - 2 * M - Inches(0.3)) / 2
    for i, p in enumerate(papers):
        col, row = i // 4, i % 4
        x = M + col * (colw + Inches(0.3))
        yy = y + (Inches(1.06) + Inches(0.14)) * row
        rect(s, x, yy, colw, Inches(1.06), fill=LIGHT)
        rect(s, x, yy, Inches(0.07), Inches(1.06), fill=p["accent"])
        tf = _p(s, x + Inches(0.26), yy + Inches(0.12), colw - Inches(1.3), Inches(0.85))
        _run(tf.paragraphs[0], p["name"], size=17, bold=True, color=NAVY)
        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        _run(p2, p["toc_sub"], size=12, color=GREY)
        tf = _p(s, x + colw - Inches(1.25), yy + Inches(0.3), Inches(1.0), Inches(0.4))
        pp = tf.paragraphs[0]
        pp.alignment = PP_ALIGN.RIGHT
        _run(pp, f"P{p['start']:02d}", size=13, bold=True, color=p["accent"])
    tf = _p(s, M, SH - Inches(0.98), SW - 2 * M, Inches(0.4))
    _run(tf.paragraphs[0], "共 8 篇论文 · 协作机制 7 篇（重点）+ 遥感落地 1 篇",
         size=12, color=GREY, italic=True)
    return s


def p_cover_paper(prs, page, p):
    s = new_slide(prs, p["section"], page)
    rect(s, M, Inches(1.55), Inches(0.09), Inches(0.5), fill=p["accent"])
    tf = _p(s, M + Inches(0.26), Inches(1.48), SW - 2 * M - Inches(0.4), Inches(0.6))
    _run(tf.paragraphs[0], p["name"], size=30, bold=True, color=NAVY)
    tf = _p(s, M, Inches(2.30), SW - 2 * M, Inches(1.4))
    for k, seg in enumerate(p["en_title"].split("\n")):
        pp = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        pp.line_spacing = 1.14
        _run(pp, seg, size=22, bold=True, color=p["accent"])
    tf = _p(s, M, Inches(3.85), SW - 2 * M, Inches(0.5))
    _run(tf.paragraphs[0], p["authors"], size=13, color=INK)
    tf = _p(s, M, Inches(4.24), SW - 2 * M, Inches(0.4))
    _run(tf.paragraphs[0], p["venue"], size=13, color=GREY, italic=True)
    rect(s, M, Inches(5.0), SW - 2 * M, Inches(1.0), fill=LIGHT)
    rect(s, M, Inches(5.0), Inches(0.075), Inches(1.0), fill=p["accent"])
    tf = _p(s, M + Inches(0.3), Inches(5.2), SW - 2 * M - Inches(0.6), Inches(0.65))
    _run(tf.paragraphs[0], p["one_liner"], size=16, bold=True, color=NAVY)
    return s


def p_motivation(prs, page, p):
    s = new_slide(prs, p["section"], page)
    accent = p["accent"]
    y = header(s, p["name"] + "｜动机与难点", p["motivation"]["headline"], accent)
    rect(s, M, y, SW - 2 * M, Inches(0.92), fill=LIGHT)
    rect(s, M, y, Inches(0.075), Inches(0.92), fill=accent)
    tf = _p(s, M + Inches(0.3), y + Inches(0.14), SW - 2 * M - Inches(0.6), Inches(0.68))
    pp = tf.paragraphs[0]
    _run(pp, "研究目的：", size=15, bold=True, color=accent)
    _run(pp, p["motivation"]["purpose"], size=15, color=NAVY)
    bullets(s, M, y + Inches(1.18), Inches(7.05), Inches(3.8),
            p["motivation"]["points"], size=13.5, gap=10)
    rect(s, M + Inches(7.4), y + Inches(1.18), Inches(4.65), Inches(3.8), fill=WARM)
    tf = _p(s, M + Inches(7.7), y + Inches(1.42), Inches(4.05), Inches(3.3))
    _run(tf.paragraphs[0], "主要难点", size=14.5, bold=True, color=AMBER)
    for c in p["motivation"]["challenges"]:
        pp = tf.add_paragraph()
        pp.space_before = Pt(10)
        pp.line_spacing = 1.14
        _run(pp, "· " + c, size=12.5, color=INK)
    return s


def p_model(prs, page, p):
    s = new_slide(prs, p["section"], page)
    accent = p["accent"]
    y = header(s, p["name"] + "｜模型", p["model"]["headline"], accent)
    bullets(s, M, y, Inches(6.15), Inches(4.7), p["model"]["bullets"], size=12.5, gap=9)
    x2 = M + Inches(6.5)
    w2 = SW - M - x2
    top = y - Inches(0.05)
    avail = SH - Inches(0.78) - top
    figs = p["model"].get("figs") or []
    if figs:
        n = len(figs)
        gap = Inches(0.22)
        cap_h = Inches(0.26)
        budget = avail - gap * (n - 1) - cap_h * n
        nat = []
        for f, _ in figs:
            iw, ih = Image.open(os.path.join(FIG, f)).size
            nat.append(w2 / (iw / ih))
        scale = min(1.0, budget / sum(nat))
        yy = top
        for i, (f, c) in enumerate(figs):
            h = nat[i] * scale + cap_h
            figure(s, f, x2, yy, w2, h, c)
            yy += h + gap
    else:
        rect(s, x2, top, w2, Inches(2.4), fill=LIGHT)
        tf = _p(s, x2 + Inches(0.24), top + Inches(0.2), w2 - Inches(0.48), Inches(2.0))
        _run(tf.paragraphs[0], p["model"]["side_title"], size=13.5, bold=True, color=accent)
        for it in p["model"]["side_items"]:
            pp = tf.add_paragraph()
            pp.space_before = Pt(8)
            pp.line_spacing = 1.12
            _run(pp, it, size=12, color=INK)
    return s


def p_results_full(prs, page, p):
    """结果页 A：表格/图表占满宽度（放最大）。"""
    s = new_slide(prs, p["section"], page)
    y = header(s, p["name"] + "｜实验结果", p["results"]["headline"], p["accent"])
    top = y - Inches(0.05)
    avail = SH - Inches(0.72) - top
    items = p["results"]["items"]
    n = len(items)
    gap = Inches(0.3)
    cap_h = Inches(0.28)
    full_w = SW - 2 * M
    nat = []
    for f, _ in items:
        iw, ih = Image.open(os.path.join(FIG, f)).size
        nat.append(full_w / (iw / ih))
    budget = avail - gap * (n - 1) - cap_h * n
    scale = min(1.0, budget / sum(nat))
    yy = top
    for i, (f, c) in enumerate(items):
        h = nat[i] * scale + cap_h
        figure(s, f, M, yy, full_w, h, c)
        yy += h + gap
    return s


def p_results_split(prs, page, p):
    """结果页 B：左栏结论文字 + 右侧一张图表。"""
    s = new_slide(prs, p["section"], page)
    accent = p["accent"]
    y = header(s, p["name"] + "｜实验结果", p["results"]["headline"], accent)
    left_w = Inches(5.35)
    tf = _p(s, M, y, left_w, Inches(0.32))
    _run(tf.paragraphs[0], "主实验：与 SOTA 对比", size=13.5, bold=True, color=accent)
    bullets(s, M, y + Inches(0.4), left_w, Inches(3.5), p["results"]["main"], size=12, gap=9)
    rect(s, M, y + Inches(4.0), left_w, Inches(1.85), fill=WARM)
    tf = _p(s, M + Inches(0.24), y + Inches(4.14), left_w - Inches(0.48), Inches(1.6))
    _run(tf.paragraphs[0], "动机实验（消融）", size=13.5, bold=True, color=AMBER)
    for it in p["results"]["abl"]:
        pp = tf.add_paragraph()
        pp.space_before = Pt(5)
        pp.line_spacing = 1.08
        _run(pp, "· " + it, size=10.5, color=INK)
    f, c = p["results"]["items"][0]
    x2 = M + left_w + Inches(0.4)
    figure(s, f, x2, y - Inches(0.05), SW - M - x2, SH - Inches(0.72) - y, c)
    return s


def p_thanks(prs, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, SW, SH, fill=NAVY)
    rect(s, 0, Inches(3.42), SW, Inches(0.06), fill=TEAL)
    tf = _p(s, M, Inches(2.55), SW - 2 * M, Inches(1.0))
    _run(tf.paragraphs[0], "感谢老师的指导", size=36, bold=True, color=WHITE)
    tf = _p(s, M, Inches(3.75), SW - 2 * M, Inches(0.8))
    _run(tf.paragraphs[0], "请老师指正", size=15, color=RGBColor(0xBF, 0xD9, 0xEE))
    return s


# ==================== 论文内容 ====================
PAPERS = [
    dict(
        name="CAMEL", accent=TEAL, section="协作机制",
        toc_sub="协作机制 · 角色扮演",
        en_title="Communicative Agents for “Mind” Exploration of\nLarge Language Model Society",
        venue="NeurIPS 2023 · arXiv:2303.17760",
        authors="Guohao Li, Hasan Abed Al Kader Hammoud, Hani Itani, Dmitrii Khizbullin, Bernard Ghanem　（KAUST）",
        one_liner="两个 Agent 靠角色设定自主协作：结构最简单、成本最低的一条路线。",
        motivation=dict(
            headline="两个 Agent 靠角色设定自主协作，不需要人一直引导",
            purpose="构造可扩展的 Agent 协作与数据生成机制，用于研究「Agent 社会」的行为。",
            points=[
                "人工引导的直接代价：任务越复杂，需要的人机往返轮次越多，时间与人力成本随规模上升。",
                "间接代价：缺乏自动化机制，就无法批量产出协作数据，也就无法系统研究多智能体行为。",
                "所以这篇论文要的不是更好的提示词，而是一套让两个 Agent 自主把任务推进到底的机制。",
                "附带价值：同一套机制可以批量生成对话数据，反过来用于训练与评测。",
            ],
            challenges=[
                "角色反转（role flipping）：Assistant 反过来下指令，角色混乱、任务跑偏。",
                "Assistant 复述指令：只是把用户的话重复一遍，任务不推进。",
                "敷衍回复（flake replies）：看起来在回答，实际没有可执行内容。",
                "终止控制：对话何时算完成，需要一个显式约定，否则无效循环。",
                "效果依赖基础模型能力：底层 LLM 的指令遵循能力直接决定协作质量。",
            ]),
        model=dict(
            headline="角色扮演 + 初始提示：人类只在最左边出现一次",
            bullets=[
                "角色分配：指定两个角色（如 Python 程序员 / 股票交易员），一个扮 AI User，一个扮 AI Assistant。",
                "Task Specifier：把人类一句模糊想法扩展成清晰、具体的任务提示词。",
                "AI User：提需求、给指令、推动进度——扮演人类。",
                "AI Assistant：执行、产出方案——扮演专家。",
                "指令跟随式对话：User 给指令 Iₜ → Assistant 给方案 Sₜ，多轮往返。",
                "终止标记：约定 CAMEL_TASK_DONE，出现即结束。",
                "关键点：人类只负责设定想法和角色，后面全靠两个 Agent 自己来回——这就是它省人力的地方。",
            ],
            figs=[("camel_framework.png", "Figure 1 CAMEL 角色扮演流程（NeurIPS 2023, p.4）")]),
        results=dict(
            headline="同一任务下双 Agent 协作显著优于单模型；生成的数据还能反哺小模型",
            items=[("tbl_camel_eval.png",
                    "Table 1 主实验：CAMEL 双 Agent vs gpt-3.5-turbo 单次回答（p.9）"),
                   ("tbl_camel_humaneval.png",
                    "Table 3 下游价值：用生成数据微调的 CAMEL-7B 在 HumanEval(+) 上的 pass@k（p.10）")],
            full=True)),

    dict(
        name="MetaGPT", accent=TEAL, section="协作机制",
        toc_sub="协作机制 · SOP 流水线",
        en_title="Meta Programming for A Multi-Agent\nCollaborative Framework",
        venue="ICLR 2024 · arXiv:2308.00352",
        authors="Sirui Hong, Mingchen Zhuge, Jiaqi Chen, Xiawu Zheng, Yuheng Cheng 等　（DeepWisdom / KAUST）",
        one_liner="把人类团队的 SOP 编码进多智能体：交文档、跑测试，最结构化的一条路线。",
        motivation=dict(
            headline="自由聊天会级联幻觉，需要把流程和中间产物写死",
            purpose="用结构化中间产物替代自由文本，用可执行反馈替代人工检查，把协作变成可复现的流程。",
            points=[
                "问题：简单串联多个 Agent 自由聊天，会出现信息歧义、错误传播与级联幻觉。",
                "观察：人类软件团队高效，靠的是标准操作流程（SOP）与明确的中间交付物。",
                "核心思想：Code = SOP(Team)——把 SOP 编码进 Prompt、Role、Action 与 Message。",
                "代价：角色越多质量越高，但费用上升；总 Token 高于 ChatDev，单位代码成本反而更低。",
            ],
            challenges=[
                "自由对话没有全局约束，容易跑偏、重复劳动、需求理解不一致。",
                "纯自然语言接口信息密度低，错误沿对话链放大（级联幻觉）。",
                "生成的代码不可执行时，缺少自动纠正环节。",
                "角色分工与成本存在矛盾：多加角色提升质量，但费用随之上升。",
            ]),
        model=dict(
            headline="四个机制：角色分工 · SOP · 结构化通信 · 可执行反馈",
            bullets=[
                "Role 角色分工：产品经理 → 架构师 → 项目经理 → 工程师 → QA，每个角色有 profile / goal / constraints / skills / actions / memory。",
                "SOP 标准流程：规定谁先工作、依赖谁、输出必须含什么字段、何时可启动（架构师不能在收到 PRD 前开始设计）。",
                "结构化通信：Agent 之间传 PRD、系统设计、接口定义、任务列表、测试报告等中间交付物，而不是自由文本。",
                "Publish-Subscribe 共享消息池：Agent 发布结构化消息，其余按订阅关系取用，把连接数从 O(n²) 降到 O(n)。",
                "可执行反馈：生成代码 → 运行 / 单测 → 读错误 → 改代码 → 再运行，最多重试 3 次。",
            ],
            figs=[("meta_sop.png", "Figure 1 人类团队 SOP 与 MetaGPT 角色/产物的对应（ICLR 2024, p.2）"),
                  ("meta_flow.png", "Figure 3 软件开发流程实例：每步交接的都是结构化文档（p.5）")]),
        results=dict(
            headline="在代码生成与真实开发任务上同时优于 ChatDev 与单模型",
            items=[("tbl_metagpt_softwaredev.png",
                    "Table 1 SoftwareDev 统计：可执行性 3.75 / 4，人工修复成本 0.83（p.8）"),
                   ("tbl_metagpt_roles.png",
                    "Table 3 角色消融：逐步加入角色，可执行性 1.0 → 4.0（p.9）")],
            full=True)),

    dict(
        name="AutoGen", accent=TEAL, section="协作机制",
        toc_sub="协作机制 · 可编程对话",
        en_title="Enabling Next-Gen LLM Applications via\nMulti-Agent Conversation",
        venue="arXiv:2308.08155 · Microsoft Research",
        authors="Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Beibin Li 等",
        one_liner="把「Agent 之间怎么对话」变成可编程接口：协作拓扑成为设计变量。",
        motivation=dict(
            headline="把协作拓扑变成可编程的接口，而不是写死的流程",
            purpose="提供通用框架，让多个可对话 Agent 之间的交互成为一等公民，开发者能像写程序一样编排协作。",
            points=[
                "真实任务往往需要「模型 + 工具 + 人」混合参与，写死流程难以复用。",
                "让 Agent 自由聊天又不可控，无法保证任务推进。",
                "开发者需要能自由定义对话模式：双 Agent、群聊、层级聊天、联合聊天。",
                "控制权要能在自然语言与代码之间自由切换，并且人随时可介入。",
            ],
            challenges=[
                "Agent 要能是 LLM、工具、人或组合，而不是只有一种。",
                "对话模式要能灵活定义，不能只有一种拓扑。",
                "自然语言表达不了程序化控制（执行代码、判断终止）。",
                "不能假设全自动，人必须能在回路里。",
            ]),
        model=dict(
            headline="Conversable Agent + 自动回复 = 可编程的对话",
            bullets=[
                "Conversable Agent：统一 generate_reply 接口，底层可以是 LLM、任意 Python 代码或人类代理。",
                "Auto-reply 自动回复：Agent 收到消息后自己决定下一步——继续回复、调用工具、或交出控制权。",
                "没有中央调度器，协作从「消息 + 自动回复」中涌现（去中心化、模块化）。",
                "Conversation Programming：开发者注册回复函数、设置终止条件来定义协作流程。",
                "支持的对话模式：双 Agent 对话、群聊、层级聊天、联合聊天。",
                "一句话：别人在设计 Agent 的智能，AutoGen 在设计 Agent 之间的对话。",
            ],
            figs=[("autogen_overview.png", "Figure 1 左：Agent 定制；中：灵活对话模式；右：完整对话实例（p.1）")]),
        results=dict(
            headline="六类应用端到端验证；加入 grounding agent 带来明显增益",
            main=[
                "用 AutoGen 搭了六个应用：数学求解、RAG 问答、ALFWorld 具身任务、多智能体编码、动态群聊、对话式国际象棋。",
                "ALFWorld：加入 grounding agent 后平均带来约 15% 的性能提升。",
                "检索：交互式检索优于一次性静态注入。",
                "国际象棋：把规则校验独立成 board agent，比塞进玩家 Agent 更可靠。",
            ],
            abl=[
                "grounding agent 在关键节点提供背景常识，阻止系统沿错误计划继续，避免错误循环。",
                "群聊在需要多视角时优于双 Agent 对话，说明拓扑要按任务选。",
            ],
            items=[("autogen_fig4.png", "Figure 4 四个应用的结果（AutoGen, p.7）")],
            full=False)),

    dict(
        name="ChatDev", accent=TEAL, section="协作机制",
        toc_sub="协作机制 · 聊天链",
        en_title="Communicative Agents for\nSoftware Development",
        venue="ACL 2024 · arXiv:2307.07924",
        authors="Chen Qian, Wei Liu, Hongzhang Liu, Nuo Chen, Yufan Dang 等　（清华大学等）",
        one_liner="用聊天链把开发流程拆成原子对话：语言本身就是协作协议。",
        motivation=dict(
            headline="用对话驱动整条开发流水线，规则与防幻觉都写进对话里",
            purpose="用同一种语言贯穿设计、编码与测试，让多智能体靠对话产出可运行的软件。",
            points=[
                "问题：已有做法分别优化设计、编码、测试各阶段，导致技术不一致、流程碎片化。",
                "难点：Agent 之间「说什么」需要流程约束，否则容易跳步、漏掉测试。",
                "难点：Agent 在信息不足时会硬答，凭空编造外部依赖与接口（幻觉）。",
                "观察：自然语言适合系统设计与需求讨论，编程语言在调试时更有效。",
            ],
            challenges=[
                "阶段割裂：各阶段模型不统一，输出无法顺畅衔接。",
                "缺少流程约束时，对话会跑偏或漏步骤。",
                "信息不足时的硬答会引入幻觉。",
                "两种语言各有适用面，框架要同时容纳。",
            ]),
        model=dict(
            headline="Chat Chain：3 阶段 5 子任务 + 交际式去幻觉",
            bullets=[
                "Chat Chain：把开发拆成原子化子任务，每个子任务对应一次双 Agent 会话。",
                "3 阶段 5 子任务：Design → Coding → Testing；角色为 CEO、CTO、程序员、评审员、测试员。",
                "每个子任务内部是角色扮演式双 Agent 对话（Instructor 提要求 / Assistant 执行），继承自 CAMEL。",
                "终止条件：代码修改两轮不变，或超过 10 轮通信，即结束该子任务。",
                "产出以 <SOLUTION> 标记，便于程序自动抽取结果。",
                "交际式去幻觉：允许 Assistant 先反过来索要更具体信息再正式回答——「不确定就先问，不要先编」。",
            ],
            figs=[("chatdev_chain.png", "Figure 2 Chat Chain：阶段、子任务、角色与对话流（ACL 2024, p.3）")]),
        results=dict(
            headline="四项指标全面领先；消融显示测试环节与去幻觉机制是主要来源",
            items=[("tbl_chatdev_main.png",
                    "Table 1 主实验：Completeness / Executability / Consistency / Quality 四项全部最高（p.6）"),
                   ("tbl_chatdev_ablation.png",
                    "Table 4 消融：去掉 CDH（去幻觉）与去掉角色分工的对比（p.7）")],
            full=True)),

    dict(
        name="MacNet", accent=TEAL, section="协作机制",
        toc_sub="协作机制 · 规模扩展",
        en_title="Scaling Large Language Model-based\nMulti-Agent Collaboration",
        venue="ICLR 2025 · arXiv:2406.07155",
        authors="Chen Qian, Zihao Xie, YiFei Wang, Wei Liu, Kunlun Zhu 等　（清华大学等）",
        one_liner="把「多智能体能扩到多大」变成可测量的规律：斜 S 形增长、随机拓扑最优。",
        motivation=dict(
            headline="加神经元有效，那加 Agent 呢？",
            purpose="用有向无环图组织 Agent，系统研究「Agent 数量」与「网络拓扑」对任务质量的影响。",
            points=[
                "动机：神经网络的 scaling law 说增加神经元能持续提升性能，那持续增加 Agent 呢？",
                "瓶颈：Agent 两两交互时上下文长度随 n² 增长，时间与成本平方级爆炸。",
                "未有定论：直觉上交互越密（mesh）越好，但需要实验验证。",
                "此前研究都在 3–5 个 Agent 的小规模，缺少规模规律。",
            ],
            challenges=[
                "规模瓶颈：上下文与成本随 n² 增长，规模上不去。",
                "拓扑无定论：形状与密度的影响未被系统验证。",
                "规模与拓扑需要权衡取舍，不能只看数量。",
                "缺少 scaling 视角，没有可用的规模规律。",
            ]),
        model=dict(
            headline="DAG 组织 Agent；上下文长度从平方级降到线性级",
            bullets=[
                "MACNET：用有向无环图组织 Agent，节点是 Agent，有向边是一次「批评—改进」推理交互。",
                "交互沿拓扑顺序编排：上游产出初稿，下游逐层反思细化，最后汇聚成完整产物。",
                "不预设角色分工，只做功能二分：actor 负责产出，critic 负责提意见。",
                "六种代表性拓扑：Chain（类瀑布）、Tree、Star、Layer、Mesh、Random。",
                "上下文长度解耦：把增长从平方级降到线性级，这是能扩到千级 Agent 的关键。",
                "拓扑要按任务选：chain 适合软件开发，tree 适合创意写作。",
            ],
            figs=[("macnet_topo.png", "Figure 2/3 六种拓扑；节点放 actor、边放 critic（ICLR 2025, p.3）"),
                  ("macnet_dag.png", "Figure 1 MACNET：DAG 组织 Agent，任务进、产物出（p.1）")]),
        results=dict(
            headline="不规则拓扑优于规则拓扑；协作性能呈斜 S 形增长",
            main=[
                "在多数指标上，MacNet 的各拓扑都超过单 Agent 与已有 MAS 基线（COT / AutoGPT / GPTSwarm / AgentVerse）。",
                "不规则拓扑（Random）最好，Quality 0.6522 为全场最高。",
                "直觉上最密的 Mesh 并不是最优（0.6316）：交互过密会造成信息过载，妨碍反思与细化。",
                "拓扑要按任务选：chain 更适合软件开发（SRDD 0.8056），tree 更适合创意写作（CommonGen 0.7718）。",
            ],
            abl=[
                "节点数从 2⁰ 增到 2⁶：性能先缓升、再快速提升、最后饱和，服从 sigmoid 变体。",
                "节点量级 2⁴ 是性价比合理的选择。",
                "协作涌现比神经网络的涌现更早；critic 提改进后 actor 有 93.10% 概率真的实现。",
            ],
            items=[("tbl_macnet_main.png", "Table 1 主实验：四类基线与六种拓扑的完整对比（p.6）")],
            full=False)),

    dict(
        name="AgentVerse", accent=TEAL, section="协作机制",
        toc_sub="协作机制 · 动态组队",
        en_title="Facilitating Multi-Agent Collaboration\nand Exploring Emergent Behaviors",
        venue="ICLR 2024 · arXiv:2308.10848",
        authors="Weize Chen, Yusheng Su, Jingwei Zuo, Cheng Yang, Chenfei Yuan 等　（清华大学、腾讯微信 AI）",
        one_liner="团队是活的：recruiter 按目标现场招人，评估反馈决定去留。",
        motivation=dict(
            headline="团队怎么组？人工指定角色无法规模化",
            purpose="提出能自动编排专家团队的多智能体框架，并系统观察协作中涌现的行为。",
            points=[
                "问题：多智能体比单智能体强已被反复验证，但团队怎么组？",
                "现有做法都是人工指定角色，要求作者事先懂任务，任务一换就得重新设计，扩展性差。",
                "团队应该是动态的：不同阶段需要的专家不同，固定团队会浪费算力或能力不足。",
                "行为不可预测：多 Agent 交互会涌现设计者没预料到的行为，可能是好的也可能是坏的。",
            ],
            challenges=[
                "角色分配依赖人工，面对多样任务难以规模化。",
                "固定团队无法适应任务推进中变化的需求。",
                "涌现行为可能带来风险，尤其在涉及人类时。",
                "缺少统一验证：既要评估能力提升，也要评估协作行为本身。",
            ]),
        model=dict(
            headline="四阶段循环：招募 → 决策 → 执行 → 评估",
            bullets=[
                "Expert Recruitment 专家招募：一个 agent 扮演 recruiter（像 HR），根据目标动态生成一组专家描述，不用预定义角色池。",
                "Collaborative Decision-Making 协同决策：招来的专家一起讨论，产出集体决策。",
                "Action Execution 行动执行：把集体决策落到环境里执行，部分 agent 不一定执行动作。",
                "Evaluation 评估：反馈机制比较当前状态与目标，产出自然语言反馈，驱动下一轮调整（换人或改策略）。",
                "团队规模与成员随任务推进变化——这是「团队是活的」的含义。",
                "三类涌现行为：volunteer（主动帮忙）、conformity（从众收敛）、destructive（破坏性）。",
            ],
            figs=[("agentverse_f1.png", "Figure 1 四阶段循环与多轮团队变化（ICLR 2024, p.2）")]),
        results=dict(
            headline="团队优于单专家与 CoT；同时暴露出破坏性行为风险",
            main=[
                "GPT-4 下 Group 在多数任务上优于 Solo 与 CoT 基线。",
                "逻辑推理（Logic Grid Puzzles）：CoT 59.5 → Solo 64.0 → Group 66.5。",
                "创意写作（Commongen-Challenge）：CoT 95.9 → Solo 99.0。",
                "说明「换成更好的角色描述」本身就有收益，团队协作的增量要按任务看。",
            ],
            abl=[
                "volunteer 与 conformity 发生在决策阶段（对话里）；destructive 绕过决策、直接发生在执行阶段。",
                "destructive 的例子：为拿材料杀掉队友捡掉落物；不去采集而直接拆掉村里的图书馆。",
                "原因是目标优化压过规则遵守；局限：GPT-3.5 下 Group 有时反而不如 Solo。",
            ],
            items=[("tbl_agentverse_main.png",
                    "Table 1 主实验：GPT-3.5 / GPT-4 下 CoT、Solo、Group 三档对比（p.4）")],
            full=False)),

    dict(
        name="Multiagent Debate", accent=TEAL, section="协作机制",
        toc_sub="协作机制 · 对抗式辩论",
        en_title="Improving Factuality and Reasoning in\nLanguage Models through Multiagent Debate",
        venue="ICML 2024 · arXiv:2305.14325",
        authors="Yilun Du, Shuang Li, Antonio Torralba, Joshua B. Tenenbaum, Igor Mordatch　（MIT CSAIL / Google Brain）",
        one_liner="唯一非合作的协作：用分歧做校验，多轮辩论后收敛，降低幻觉。",
        motivation=dict(
            headline="自省有天花板，但多个实例的分歧可以用来纠错",
            purpose="让多个模型实例互相看答案与推理并多轮辩论，收敛到共同答案，以提升推理准确性与事实正确性。",
            points=[
                "问题：单模型会给出错误答案，而且自己检查不出来。",
                "已有做法（CoT、self-consistency、self-reflection）都是让同一个模型换个姿势再想一遍。",
                "发现：即使是同一个模型类的不同实例，给出的答案也千差万别——分歧是资源，不是噪声。",
                "要求：方法必须能直接套在黑盒模型上，不依赖模型权重或重新训练。",
            ],
            challenges=[
                "自省有天花板：只能发现明显问题，改不了根本性推理错误。",
                "幻觉难检出：模型会编造事实，且不同实例编得还不一样。",
                "多个 Agent 的答案直接拼接会超出上下文长度。",
                "必须适配黑盒模型，不能依赖微调。",
            ]),
        model=dict(
            headline="多轮辩论 + 收敛；默认 3 个 agent × 2 轮",
            bullets=[
                "初始轮：n 个 agent（可同一模型、也可不同模型）各自独立回答同一问题。",
                "辩论轮：每个 agent 看到其他 agent 的答案与推理过程，给出修正后的答案。",
                "重复 r 轮后取共识；默认配置为 3 个 agent × 2 轮辩论。",
                "长答案要先摘要：agent 变多时上下文会超限，先用摘要器压缩多方回答再分发。",
                "推理过程必须一起传：只看答案不看推理，效果差很多。",
                "这是唯一的非合作协作：agent 之间互相质疑，而不是分工把事做完。",
            ],
            figs=[],
            side_title="与其它路线的区别",
            side_items=[
                "协作类型：合作（分工） vs 本篇的对抗（互相质疑）",
                "角色：有分工 vs 无分工，同构 agent 做同一件事",
                "传递内容：文档 / 对话 / 决策 vs 答案 + 推理过程",
                "目标：产出更完整的产物 vs 纠错，提高答案正确性",
            ]),
        results=dict(
            headline="六类任务全面超过单模型基线，且能纠正矛盾事实",
            items=[("debate_results.png",
                    "Figure 1 六基准：Single Model（蓝）vs Multi-Model Debate（红）（p.2）"),
                   ("tbl_debate_reasoning.png",
                    "Table 1 推理任务：算术、小学数学、棋步预测的对比（p.6）")],
            full=True)),

    dict(
        name="GeoLLM-Squad", accent=CRIMSON, section="遥感落地",
        toc_sub="遥感落地 · 多智能体工作流",
        en_title="Multi-Agent Geospatial Copilots\nfor Remote Sensing Workflows",
        venue="arXiv:2501.16254 · UT Austin / SIU / Microsoft",
        authors="Chaehong Lee, Varatheepan Paramanayakam, Andreas Karatzas 等",
        one_liner="把编排与求解分离：在真实遥感工作流上把正确率从 43% 提到 60%。",
        motivation=dict(
            headline="单体 LLM 撑不住遥感工作流：上下文与工具规模都是瓶颈",
            purpose="把「智能体编排」与「地理空间任务求解」拆开，用专职 sub-agent 分摊工具集，突破单体 LLM 的上下文瓶颈。",
            points=[
                "遥感工作流需要多种数据、工具与隐性专业知识：例如云量超阈值时，要用地面站温度或 SAR 影像替代光学产品。",
                "这类「SAR-over-EO」的条件逻辑很难靠提示词硬塞给单体 Copilot。",
                "单体 LLM 受上下文窗口与 token 容量限制，撑不起真实应用的时空尺度。",
                "工具规模从几十涨到几百，单体 Agent 的上下文装不下。",
            ],
            challenges=[
                "单体 LLM 是瓶颈：上下文与 token 容量有限。",
                "专业条件判断难以提示词化。",
                "工具规模爆炸：521 个 API 函数超过单体容量的 3 倍。",
                "云端 AI 成本高，多智能体系统还必须能跑在开源小模型上。",
            ]),
        model=dict(
            headline="编排与求解分离：一个调度员 + 一圈平级执行者",
            bullets=[
                "核心思路：主 Agent 只负责拆解与调度，具体任务交给专职 sub-agent。",
                "编排者输出「程序式排班表」：指定哪些 Agent、按什么顺序、每个的 sub-prompt。",
                "例：Database(加载 NDVI) → DataOps(筛选 Brisbane) → Agriculture(推荐轮作区) → Map(出图)。",
                "按表执行后，编排者汇总返回消息检查完成度；未完成就改排班表重跑。",
                "Agent 之间零通信：每个 Agent 只跟编排者交换消息——是星形而非多层层级。",
                "521 个 API 工具分散到各专职 Agent，每个只装自己的工具——这是能扛住复杂度增长的原因。",
                "建在 AutoGen（后端）+ GeoLLM-Engine（前端）之上。",
            ],
            figs=[("geollm_arch.png", "Figure 1 各类专职 Agent 与编排器（arXiv:2501.16254, p.2）")]),
        results=dict(
            headline="正确率 43% → 60%；任务变复杂时单 Agent 失效、多 Agent 稳住",
            items=[("geollm_scaling.png",
                    "Figure 2 单 vs 多智能体扩展性消融：任务超过 3 个领域后单 Agent 失效（p.4）"),
                   ("tbl_geollm_main.png",
                    "Table 3 主实验：与单 Agent 及 Chameleon / Magentic 的完整对比（p.3）")],
            full=True)),
]


def build():
    prs = Presentation()
    prs.slide_width, prs.slide_height = SW, SH

    for i, p in enumerate(PAPERS):
        p["start"] = 4 + 4 * i

    p_cover(prs, 1)
    p_yan(prs, 2)
    p_toc(prs, 3, PAPERS)

    page = 4
    for p in PAPERS:
        p_cover_paper(prs, page, p); page += 1
        p_motivation(prs, page, p); page += 1
        p_model(prs, page, p); page += 1
        if p["results"]["full"]:
            p_results_full(prs, page, p)
        else:
            p_results_split(prs, page, p)
        page += 1

    p_thanks(prs, page)
    prs.save(OUT)
    print("saved:", OUT)
    print("slides:", len(prs.slides._sldIdLst))
    return OUT


if __name__ == "__main__":
    build()
