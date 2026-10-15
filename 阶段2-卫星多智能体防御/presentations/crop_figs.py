# -*- coding: utf-8 -*-
"""
从论文 PDF 里裁「图」到 figures/。

只裁矢量图/位图，不裁表格——表格在 PPT 里用原生表格重画（只要表头和数据，不要描述）。

方法：
  1. 收集页面上的矢量绘图对象与位图对象
  2. 从「最靠近图注」的对象往上收，相邻对象垂直间隙 < 阈值就继续收（图是密集的，正文是稀疏的）
  3. 得到图的包围盒，按 DPI 渲染并自动裁白边

用法： python3 crop_figs.py [名字...]
"""
import os
import sys
import numpy as np
import pymupdf
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PAPERS = os.path.join(os.path.dirname(HERE), "papers")
OUT = os.path.join(os.path.dirname(HERE), "figures")
os.makedirs(OUT, exist_ok=True)

DPI = 400
GAP = 34          # 相邻图形对象的垂直间隙小于这个值（pt）就认为同属一张图

FILES = {
    "E4": "E4 - SoK Security of Multi Agent LLM Systems (2609.00595).pdf",
    "A1": "A1 - Beyond Single-Model Injection (2609.22949).pdf",
    "A2": "A2 - Trust Propagation and Structural Containment (2609.17648).pdf",
    "A5": "A5 - Crescendo Multi-Turn Jailbreaking (2404.01833).pdf",
    "AA": "新增1 - Adaptive Adversaries Multi-Turn Benchmark (2607.18063).pdf",
    "B1": "B1 - CaMeL Defeating Prompt Injections by Design (2503.18813).pdf",
    "B2": "B2 - Design Patterns for Securing LLM Agents (2506.08837).pdf",
    "SSH": "新增6 - Speculative Safety Honeypot (2609.39549).pdf",
    "VIGIL": "新增3 - VIGIL Verify-Before-Commit (2601.05755).pdf",
}

# 图名, 文件, 页码(0基), 图注 y(pt), 可选横向范围(页宽比例；双栏图需手工指定)
JOBS = [
    ("p1-crescendo-mech",    "A5", 3, 287.6),
    ("p1-crescendo-result",  "A5", 9, 287.8),
    ("p3-aa-threat",         "AA", 2, 243.9),
    ("p3-aa-matrix",         "AA", 3, 448.6),
    ("p4-a2-arch",           "A2", 2, 651.5),
    ("p5-camel-attack",      "B1", 3, 607.6, (0.53, 0.93)),   # 双栏：图在右栏
    ("p5-camel-arch",        "B1", 6, 316.1),
    ("p6-dp-selector",       "B2", 4, 267.1),
    ("p6-dp-dual",           "B2", 7, 238.4),
    ("p7-ssh-arch",          "SSH", 3, 298.5),
    ("p8-vigil-challenge",   "VIGIL", 0, 457.3),
    ("p8-vigil-arch",        "VIGIL", 4, 320.4),
    ("f1-camel-perf",        "B1", 11, 260.0),   # CaMeL Figure 8：可用性
    ("f2-ssh-risk",          "SSH", 6, 675.3),   # SSH Figure 3：平均风险分与告警率
    ("p0-air",               "E4", 1, 563.6),    # E4 Figure 1：MAS 安全的统一执行视图
]


def graphic_rects(page):
    out = []
    for dr in page.get_drawings():
        r = dr["rect"]
        if r.width > 4 and r.height > 4:
            out.append(r)
    for im in page.get_images(full=True):
        for r in page.get_image_rects(im[0]):
            out.append(r)
    return out


def gutter(page):
    """判断是不是双栏排版；是就返回分栏中线的 x，否则 None。"""
    W = page.rect.width
    # 排除页眉、通栏块（通栏段落会同时出现在中线上）
    blocks = [b for b in page.get_text("blocks")
              if b[1] > 70 and (b[2] - b[0]) < W * 0.70]
    if not blocks:
        return None
    left = [b for b in blocks if (b[0] + b[2]) / 2 < W * 0.42]
    right = [b for b in blocks if (b[0] + b[2]) / 2 > W * 0.58]
    mid = [b for b in blocks if W * 0.42 <= (b[0] + b[2]) / 2 <= W * 0.58]
    # 左右都有块、且中间几乎没有块 → 双栏
    if len(left) >= 3 and len(right) >= 3 and len(mid) <= 2:
        return W * 0.5
    return None


def figure_bbox(page, cap_y, gap=GAP):
    """从最靠近图注的图形对象往上收，返回图的范围。"""
    rects = [r for r in graphic_rects(page) if r.y1 <= cap_y + 4]
    if not rects:
        return None
    rects.sort(key=lambda r: r.y1, reverse=True)   # 靠图注的在前面
    u = pymupdf.Rect(rects[0])
    for r in rects[1:]:
        if u.y0 - r.y1 > gap:      # 与当前包围盒上方断开 → 到了图的顶
            break
        u |= r
    # 扩展 x：把与该纵向区间重叠的文本块也纳入（图里常有文字标签、注释框）
    # 双栏排版时只在同一栏内扩，避免把隔壁正文吸进来
    for b in page.get_text("blocks"):
        br = pymupdf.Rect(b[:4])
        if not (br.y1 > u.y0 and br.y0 < u.y1 and br.height < (u.height * 0.9)):
            continue
        u |= br
    return u


def trim(img, pad=8, thr=248):
    a = np.asarray(img.convert("L"))
    m = a < thr
    if not m.any():
        return img
    r = np.where(m.any(axis=1))[0]
    c = np.where(m.any(axis=0))[0]
    return img.crop((max(0, c.min() - pad), max(0, r.min() - pad),
                     min(img.width, c.max() + pad + 1), min(img.height, r.max() + pad + 1)))


def crop_region(doc, pno, rect, shrink_to_caption=None):
    """rect: pymupdf.Rect（pt）。shrink_to_caption: 若给了 y，就把底边收到这个 y（避免把图注裁进去）。"""
    page = doc[pno]
    r = pymupdf.Rect(rect)
    if shrink_to_caption is not None and r.y1 > shrink_to_caption:
        r.y1 = shrink_to_caption
    r.x0 = max(0, r.x0 - 2)
    r.x1 = min(page.rect.width, r.x1 + 2)
    pix = page.get_pixmap(dpi=DPI, clip=r)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def do_one(name, key, pno, cap_y, xr=None):
    doc = pymupdf.open(os.path.join(PAPERS, FILES[key]))
    page = doc[pno]
    bb = figure_bbox(page, cap_y)
    if bb is not None and xr:
        bb.x0 = page.rect.width * xr[0]
        bb.x1 = page.rect.width * xr[1]
    if bb is None:
        print(f"  ✗ {name}: 图注上方没有图形对象")
        return
    img = trim(crop_region(doc, pno, bb, shrink_to_caption=cap_y))
    if img.height < 40 or img.width < 60:
        print(f"  ✗ {name}: 裁出来太小 {img.width}×{img.height}")
        return
    img.save(os.path.join(OUT, name + ".png"))
    print(f"  ✓ {name}.png  {img.width}×{img.height}  比例 {img.width/img.height:.2f}")


if __name__ == "__main__":
    want = sys.argv[1:]
    for job in JOBS:
        if want and job[0] not in want:
            continue
        try:
            do_one(*job)
        except Exception as e:
            print(f"  ✗ {job[0]}: {type(e).__name__} {e}")
