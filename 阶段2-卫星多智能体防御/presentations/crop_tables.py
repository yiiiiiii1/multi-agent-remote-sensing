# -*- coding: utf-8 -*-
"""按显式坐标裁「论文原表格/原图」，用于实验结果页。
坐标单位 pt，从页面左上角算。表格位置由人工核对文本块后确定——比自动检测可靠。
"""
import os
import numpy as np
import pymupdf
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PAPERS = os.path.join(os.path.dirname(HERE), "papers")
OUT = os.path.join(os.path.dirname(HERE), "figures")
DPI = 400

FILES = {
    "A1": "A1 - Beyond Single-Model Injection (2609.22949).pdf",
    "A2": "A2 - Trust Propagation and Structural Containment (2609.17648).pdf",
    "A5": "A5 - Crescendo Multi-Turn Jailbreaking (2404.01833).pdf",
    "AA": "新增1 - Adaptive Adversaries Multi-Turn Benchmark (2607.18063).pdf",
    "B1": "B1 - CaMeL Defeating Prompt Injections by Design (2503.18813).pdf",
    "B2": "B2 - Design Patterns for Securing LLM Agents (2506.08837).pdf",
    "SSH": "新增6 - Speculative Safety Honeypot (2609.39549).pdf",
    "VIGIL": "新增3 - VIGIL Verify-Before-Commit (2601.05755).pdf",
}

# 名字, 文件, 页码(0基), (x0, y0, x1, y1)
JOBS = [
    ("t1-a1-attack",   "A1", 2, (305, 65, 545, 350)),    # Table 1 攻击向量分类
    ("t2-a1-defense",  "A1", 3, (305, 65, 545, 212)),    # Table 2 四层防御效果
    ("t3-a2-tiers",    "A2", 3, (44, 51, 306, 152)),     # TABLE I 各 tier 的攻击效果
    ("t4-crescendo",   "A5", 9, (51, 318, 562, 412)),    # Table 4 各越狱方法对比
    ("t5-aa-matrix",   "AA", 13, (106, 67, 507, 144)),   # Table 3 前沿矩阵
    ("f3-aa-rounds",   "AA", 20, (130, 334, 471, 512)),  # Figure 8 不同轮数截断的 ASR 曲线
    ("t8-aa-memory",   "AA", 18, (177, 68, 433, 202)),   # Table 12 记忆因子实验
    ("t6-b2-cases",    "B2", 9, (93, 66, 507, 304)),     # Table 1 案例 × 模式
    ("t7-vigil-siren", "VIGIL", 6, (66, 70, 530, 252)),  # Table 2（截取表头 + 第一个模型块）
    ("f1-camel-perf",  "B1", 11, (0, 0, 0, 0)),          # 占位（下方单独处理）
    ("f2-ssh-risk",    "SSH", 6, (0, 0, 0, 0)),          # 占位
]


def trim(img, pad=8, thr=248):
    a = np.asarray(img.convert("L"))
    m = a < thr
    if not m.any():
        return img
    r = np.where(m.any(axis=1))[0]
    c = np.where(m.any(axis=0))[0]
    return img.crop((max(0, c.min() - pad), max(0, r.min() - pad),
                     min(img.width, c.max() + pad + 1), min(img.height, r.max() + pad + 1)))


def main():
    for name, key, pno, (x0, y0, x1, y1) in JOBS:
        if x1 <= x0:
            print(f"  · {name}: 坐标待定，跳过")
            continue
        doc = pymupdf.open(os.path.join(PAPERS, FILES[key]))
        pix = doc[pno].get_pixmap(dpi=DPI, clip=pymupdf.Rect(x0, y0, x1, y1))
        img = trim(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
        img.save(os.path.join(OUT, name + ".png"))
        print(f"  ✓ {name}.png  {img.width}×{img.height}  比例 {img.width/img.height:.2f}")


if __name__ == "__main__":
    main()
