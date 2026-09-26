# -*- coding: utf-8 -*-
"""
生成《多智能体（LLM-MAS）调研汇报》PPT —— 分批生成。

顺序（用户指定）：封面 → Yan 2025 → 目录 → CAMEL(3页) → MetaGPT(3页) → ...
本批生成：封面 + Yan 2025 + 目录 + CAMEL 三页 = 7 页

用法： python3 build_ppt.py
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
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
FONT = "微软雅黑"
MONO = "Consolas"

SW, SH = Inches(13.333), Inches(7.5)
M = Inches(0.62)
TOTAL = 26                      # 全篇预计页数，用于页码显示


def _p(layer, x, y, w, h):
    tb = layer.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf


def _run(p, text, size=14, bold=False, color=INK, font=FONT, italic=False):
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = font
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
    """items: str | (text, level) | (text, level, color)"""
    tf = _p(s, x, y, w, h)
    first = True
    for it in items:
        level, color, text = 0, None, it
        if isinstance(it, tuple):
            text = it[0]
            if len(it) > 1:
                level = it[1]
            if len(it) > 2:
                color = it[2]
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(gap)
        p.line_spacing = 1.18
        mark = "" if text.endswith("：") else ("– " if level else bullet)
        _run(p, mark + text, size=size - level,
             bold=text.endswith("："), color=color or (INK if level == 0 else GREY))
    return tf


def figure(s, name, x, y, w, h, caption=None):
    path = os.path.join(FIG, name)
    ph = h if caption is None else h - Inches(0.30)
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
        tf = _p(s, x, y + h - Inches(0.28), w, Inches(0.28))
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        _run(p, caption, size=9.5, color=GREY)


# ==================== 页面 ====================
def p_cover(prs, page):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, SW, SH, fill=NAVY)
    rect(s, 0, Inches(4.58), SW, Inches(0.055), fill=TEAL)
    tf = _p(s, M, Inches(2.02), SW - 2 * M, Inches(1.0))
    _run(tf.paragraphs[0], "多智能体（LLM-MAS）调研汇报", size=40, bold=True, color=WHITE)
    tf = _p(s, M, Inches(3.12), SW - 2 * M, Inches(1.2))
    p = tf.paragraphs[0]
    _run(p, "按协作机制选代表性论文：每篇讲清 动机/难点 → 模型 → 实验结果",
         size=18, color=RGBColor(0xBF, 0xD9, 0xEE))
    tf = _p(s, M, Inches(5.05), SW - 2 * M, Inches(0.9))
    _run(tf.paragraphs[0], "汇报人：____________　　导师：李倩　　2026 年 9 月",
         size=14, color=RGBColor(0x9F, 0xB8, 0xCC))
    return s


def p_yan(prs, page):
    s = new_slide(prs, "领域坐标", page)
    y = header(s, "领域坐标：LLM-MAS 的通信分类体系",
               "Yan et al. 2025 · Beyond Self-Talk · arXiv:2502.14321 · 后面的 7 篇论文都能被这套框架定位", TEAL)
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


ROADMAP = [
    ("CAMEL", "协作机制 · 角色扮演", "04–06", TEAL),
    ("MetaGPT", "协作机制 · SOP 流水线", "07–09", TEAL),
    ("AutoGen", "协作机制 · 可编程对话", "10–12", TEAL),
    ("ChatDev", "协作机制 · 聊天链", "13–15", TEAL),
    ("MacNet", "协作机制 · 规模扩展", "16–18", TEAL),
    ("AgentVerse", "协作机制 · 动态组队", "19–21", TEAL),
    ("Multiagent Debate", "协作机制 · 对抗式辩论", "22–24", TEAL),
    ("GeoLLM-Squad", "遥感落地 · 多智能体工作流", "25", CRIMSON),
]


def p_toc(prs, page):
    s = new_slide(prs, "目录", page)
    y = header(s, "按协作机制逐篇精读", "每篇固定三页：动机与难点 → 模型 → 实验结果", BLUE)
    left, right = ROADMAP[:4], ROADMAP[4:]
    colw = (SW - 2 * M - Inches(0.3)) / 2
    for col, items in enumerate([left, right]):
        x = M + col * (colw + Inches(0.3))
        for i, (name, sub, pg, c) in enumerate(items):
            yy = y + (Inches(1.06) + Inches(0.14)) * i
            rect(s, x, yy, colw, Inches(1.06), fill=LIGHT)
            rect(s, x, yy, Inches(0.07), Inches(1.06), fill=c)
            tf = _p(s, x + Inches(0.26), yy + Inches(0.14), colw - Inches(0.5), Inches(0.8))
            p = tf.paragraphs[0]
            _run(p, name, size=17, bold=True, color=NAVY)
            p2 = tf.add_paragraph()
            p2.space_before = Pt(2)
            _run(p2, sub, size=12, color=GREY)
            tf = _p(s, x + colw - Inches(1.1), yy + Inches(0.3), Inches(0.85), Inches(0.4))
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.RIGHT
            _run(p, "P" + pg.split("–")[0], size=13, bold=True, color=c)
    tf = _p(s, M, SH - Inches(1.0), SW - 2 * M, Inches(0.4))
    _run(tf.paragraphs[0], "共 8 篇论文 · 协作机制 7 篇（重点）+ 遥感落地 1 篇",
         size=12, color=GREY, italic=True)
    return s


def paper_cover(prs, page, idx, name, venue, accent, one_liner):
    """每篇论文的第 1 页：先给结构提示"""
    s = new_slide(prs, "协作机制", page)
    y = header(s, name, venue, accent)
    rect(s, M, y, SW - 2 * M, Inches(1.0), fill=LIGHT)
    rect(s, M, y, Inches(0.075), Inches(1.0), fill=accent)
    tf = _p(s, M + Inches(0.3), y + Inches(0.16), SW - 2 * M - Inches(0.6), Inches(0.7))
    p = tf.paragraphs[0]
    _run(p, f"论文 {idx} / 8", size=12.5, bold=True, color=accent)
    p2 = tf.add_paragraph()
    p2.space_before = Pt(4)
    _run(p2, one_liner, size=16, bold=True, color=NAVY)
    steps = [("P1", "动机与难点", "要解决什么问题 · 难点在哪 · 研究目的"),
             ("P2", "模型", "对着模型图讲清主要工作与机制"),
             ("P3", "实验结果", "主实验（对比 SOTA）+ 动机实验（消融）")]
    yy = y + Inches(1.35)
    for tag, t, d in steps:
        rect(s, M, yy, SW - 2 * M, Inches(1.0), fill=WHITE, line=BORDER)
        tf = _p(s, M + Inches(0.3), yy + Inches(0.26), Inches(0.9), Inches(0.5))
        _run(tf.paragraphs[0], tag, size=19, bold=True, color=accent)
        tf = _p(s, M + Inches(1.25), yy + Inches(0.16), SW - 2 * M - Inches(1.6), Inches(0.75))
        p = tf.paragraphs[0]
        _run(p, t, size=15, bold=True, color=NAVY)
        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        _run(p2, d, size=12, color=GREY)
        yy += Inches(1.15)
    return s


def p_motivation(prs, page, name, headline, purpose, points, challenges, accent):
    s = new_slide(prs, "协作机制", page)
    y = header(s, name + "｜动机与难点", headline, accent)
    rect(s, M, y, SW - 2 * M, Inches(0.92), fill=LIGHT)
    rect(s, M, y, Inches(0.075), Inches(0.92), fill=accent)
    tf = _p(s, M + Inches(0.3), y + Inches(0.14), SW - 2 * M - Inches(0.6), Inches(0.68))
    p = tf.paragraphs[0]
    _run(p, "研究目的：", size=15, bold=True, color=accent)
    _run(p, purpose, size=15, color=NAVY)
    bullets(s, M, y + Inches(1.18), Inches(7.05), Inches(3.7), points, size=13.5, gap=10)
    rect(s, M + Inches(7.4), y + Inches(1.18), Inches(4.65), Inches(3.7), fill=RGBColor(0xFD, 0xF3, 0xE6))
    tf = _p(s, M + Inches(7.7), y + Inches(1.42), Inches(4.05), Inches(3.2))
    _run(tf.paragraphs[0], "难点（论文自己点名的）", size=14.5, bold=True, color=AMBER)
    for c in challenges:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        p.line_spacing = 1.14
        _run(p, "· " + c, size=12.5, color=INK)
    return s


def p_model(prs, page, name, headline, left_items, fig, fig_caption,
            right_title=None, right_items=None, accent=TEAL, bottom=None):
    s = new_slide(prs, "协作机制", page)
    y = header(s, name + "｜模型", headline, accent)
    bullets(s, M, y, Inches(6.3), Inches(4.7), left_items, size=13, gap=9)
    x2 = M + Inches(6.65)
    w2 = SW - M - x2
    figure(s, fig, x2, y - Inches(0.05), w2, Inches(3.5), fig_caption)
    if right_title:
        rect(s, x2, y + Inches(3.55), w2, Inches(1.5), fill=LIGHT)
        tf = _p(s, x2 + Inches(0.24), y + Inches(3.72), w2 - Inches(0.48), Inches(1.25))
        _run(tf.paragraphs[0], right_title, size=13.5, bold=True, color=accent)
        for it in (right_items or []):
            p = tf.add_paragraph()
            p.space_before = Pt(4)
            p.line_spacing = 1.1
            _run(p, it, size=11.5, color=INK)
    if bottom:
        tf = _p(s, M, SH - Inches(0.82), SW - 2 * M, Inches(0.5))
        _run(tf.paragraphs[0], bottom, size=11, color=GREY, italic=True)
    return s


def p_results(prs, page, name, headline, main_items, abl_items, metrics, accent, fig=None, cap=None):
    s = new_slide(prs, "协作机制", page)
    y = header(s, name + "｜实验结果", headline, accent)
    half = (SW - 2 * M - Inches(0.35)) / 2
    for i, (title, items, c) in enumerate([
            ("主实验：与 SOTA 对比", main_items, accent),
            ("动机实验：消融与机制验证", abl_items, TEAL)]):
        x = M + i * (half + Inches(0.35))
        rect(s, x, y, half, Inches(3.15), fill=WHITE, line=BORDER)
        rect(s, x, y, half, Inches(0.42), fill=c)
        tf = _p(s, x + Inches(0.24), y + Inches(0.08), half - Inches(0.48), Inches(0.32))
        _run(tf.paragraphs[0], title, size=14, bold=True, color=WHITE)
        bullets(s, x + Inches(0.24), y + Inches(0.6), half - Inches(0.48), Inches(2.45),
                items, size=12, gap=7)
    if fig:
        figure(s, fig, M, y + Inches(3.35), SW - 2 * M, Inches(1.85), cap)
    else:
        rect(s, M, y + Inches(3.4), SW - 2 * M, Inches(0.85), fill=LIGHT)
        tf = _p(s, M + Inches(0.3), y + Inches(3.54), SW - 2 * M - Inches(0.6), Inches(0.62))
        p = tf.paragraphs[0]
        _run(p, "数据集 / 评价指标：", size=13, bold=True, color=NAVY)
        _run(p, metrics, size=12.5, color=INK)
    return s


def build():
    prs = Presentation()
    prs.slide_width, prs.slide_height = SW, SH
    p_cover(prs, 1)
    p_yan(prs, 2)
    p_toc(prs, 3)
    paper_cover(prs, 4, 1, "CAMEL",
                "Li, Hammoud, Itani, Khizbullin, Ghanem · NeurIPS 2023 · arXiv:2303.17760",
                TEAL, "两个 Agent 靠角色设定自主协作：结构最简单、成本最低的一条路线")

    # ---- CAMEL（第 5–7 页）----
    p_motivation(
        prs, 5, "CAMEL",
        "两个 Agent 靠角色设定自主协作，不需要人一直引导",
        "构造可扩展的 Agent 协作与数据生成机制，用于研究「Agent 社会」的行为。",
        ["问题：chat-based LLM 解决复杂任务，成功高度依赖人类一步步引导对话，费时费力。",
         "而且人工介入限制了对「多智能体社会」的大规模研究。",
         "目标：让两个 communicative agent 在没有人类持续介入的情况下自主协作。",
         "附带价值：可用 LLM 自动生成大规模对话数据，用于研究多智能体协作行为。",
         "本文是这条路线里结构最简单、成本最低的一篇，也是我自己复现过的框架。"],
        ["角色反转（role flipping）：Assistant 反过来下指令，角色混乱、任务跑偏。",
         "Assistant 复述指令：只是把用户的话重复一遍，任务不推进。",
         "敷衍回复（flake replies）：看起来在回答，实际没有可执行内容。",
         "终止控制：对话何时算完成，需要一个显式约定，否则无效循环。",
         "效果依赖基础模型能力：底层 LLM 的指令遵循能力直接决定协作质量。"],
        TEAL)

    p_model(
        prs, 6, "CAMEL",
        "角色扮演 + 初始提示：人类只在最左边出现一次",
        [("角色分配：指定两个角色（如 Python 程序员 / 股票交易员），一个扮 AI User，一个扮 AI Assistant。", 0),
         ("Task Specifier：把人类一句模糊想法扩展成清晰、具体的任务提示词。", 0),
         ("AI User：提需求、给指令、推动进度——扮演人类。", 0),
         ("AI Assistant：执行、产出方案——扮演专家。", 0),
         ("指令跟随式对话：User 给指令 Iₜ → Assistant 给方案 Sₜ，多轮往返。", 0),
         ("终止标记：约定 CAMEL_TASK_DONE，出现即结束。", 0),
         ("关键点：人类只负责设定想法和角色，后面全靠两个 Agent 自己来回——这就是它省人力的地方。", 0, TEAL)],
        "camel_framework.png",
        "Figure 1 CAMEL 角色扮演流程（NeurIPS 2023, p.4）",
        "与其它路线对比",
        ["MetaGPT：SOP 流水线，流程静态",
         "AutoGen：开发者编程定义对话模式",
         "CAMEL：固定双 Agent，灵活性最低、成本最低"],
        TEAL,
        bottom="讲法：指着图从左边讲起——人类输入想法与角色 → Task Specifier 生成具体任务 → 右侧两个 Agent 多轮协作。")
    p_results(
        prs, 7, "CAMEL",
        "同一任务下，双 Agent 协作显著优于单模型单次回答",
        ["对照设置：CAMEL 双 Agent 协作方案 vs gpt-3.5-turbo 单次（single-shot）回答。",
         "AI Society · 人工评测：CAMEL 胜 76.3%，单模型胜 10.4%，平局 13.3%（453 份人类投票）。",
         "AI Society · GPT-4 评测：CAMEL 胜 73.0%，单模型胜 23.0%，平局 4.0%。",
         "Code · GPT-4 评测：CAMEL 胜 76.0%，单模型胜 24.0%，平局 0%。",
         "人工评测与 GPT-4 评测结论高度一致，说明自动评委在这类任务上可信。"],
        ["机制验证：用生成数据递进微调 LLaMA-7B（AI Society → Code → Math → Science），各领域持续提升。",
         "CAMEL-7B 在 HumanEval pass@100 达 57.9%，高于 LLaMA-7B 的 36.5% 与 Vicuna-7B 的 42.9%。",
         "观察到的失效模式：角色反转、Assistant 复述指令、敷衍回复。",
         "结论：多 Agent 协作的有效性被验证，但稳定协作依赖提示设计，不是自动成立。"],
        "自生成四类数据集；指标为人工投票胜率与 GPT-4 评委胜率；下游用 HumanEval / HumanEval⁺ 的 pass@k。",
        TEAL)

    prs.save(OUT)
    print("saved:", OUT)
    print("slides:", len(prs.slides._sldIdLst))
    return OUT


if __name__ == "__main__":
    build()
