#!/usr/bin/env python3
"""把 papers/ 文件夹里的 PDF 自动导入 Zotero，并让 Zotero 自己抓元数据。

原理：走 Zotero 连接器接口 /connector/saveStandaloneAttachment，
Zotero 收到 PDF 后会自动识别（autoRecognizeFiles 默认开）并建父条目。

用法：
    python3 tools/zotero/import-papers.py                # 默认两个 papers 文件夹
    python3 tools/zotero/import-papers.py --dry-run      # 只列一遍，不动 Zotero
    python3 tools/zotero/import-papers.py --folder 某目录

注意：条目会进 Zotero 左边**当前选中**的分类，跑之前先点好目标分类。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
BASE = "http://127.0.0.1:23119"
API = BASE + "/api/users/0"
LEDGER = Path(__file__).resolve().parent / "imported.json"

DEFAULT_FOLDERS = [
    REPO / "阶段1-协作机制调研/papers",
    REPO / "阶段2-卫星多智能体防御/papers",
]

ARXIV_NEW = re.compile(r"(\d{4}\.\d{4,5})")
ARXIV_OLD = re.compile(r"([a-z-]+(?:\.[A-Z]{2})?/\d{7})")


def http(method: str, url: str, body: bytes | None = None, headers: dict | None = None):
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def api_get(path: str):
    req = urllib.request.Request(API + path, headers={"Zotero-API-Version": "3"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def zotero_alive() -> bool:
    try:
        http("GET", BASE + "/connector/ping")
        return True
    except Exception:
        return False


def library_index() -> tuple[set[str], set[str], list[str]]:
    """返回 (已存在的 PDF 文件名集合, 已存在的 arXiv/DOI 标识集合, 已存在的条目标题)。"""
    filenames: set[str] = set()
    ids: set[str] = set()
    titles: list[str] = []
    for item_type in ("attachment", "preprint", "journalArticle", "conferencePaper"):
        start = 0
        while True:
            batch = api_get(f"/items?limit=100&start={start}&itemType={item_type}")
            for it in batch:
                d = it["data"]
                if d.get("filename"):
                    filenames.add(d["filename"].lower())
                for field in ("archiveID", "DOI", "url", "extra"):
                    v = (d.get(field) or "").lower()
                    for m in ARXIV_NEW.finditer(v):
                        ids.add(m.group(1))
                    for m in ARXIV_OLD.finditer(v):
                        ids.add(m.group(1))
                if d.get("title"):
                    titles.append(d["title"])
            if len(batch) < 100:
                break
            start += 100
    return filenames, ids, titles


def norm(text: str) -> set[str]:
    return {t for t in re.sub(r"[^0-9a-z]+", " ", text.lower()).split() if len(t) > 1}


def title_from_name(name: str) -> str | None:
    """从「作者 等 - 年份 - 标题.pdf」里抠出标题。"""
    stem = name[:-4] if name.lower().endswith(".pdf") else name
    parts = [p.strip() for p in stem.split(" - ")]
    if len(parts) >= 2 and not re.fullmatch(r"[\d\W]+", parts[-1]):
        return parts[-1]
    return None


def looks_duplicate(title: str, known_titles: list[str]) -> str | None:
    t = norm(title)
    if not t:
        return None
    for known in known_titles:
        k = norm(known)
        if not k:
            continue
        overlap = len(t & k) / max(len(t), len(k))
        if overlap >= 0.7:
            return known
    return None


def arxiv_id_from_name(name: str) -> str | None:
    m = ARXIV_NEW.search(name) or ARXIV_OLD.search(name)
    return m.group(1) if m else None


def load_ledger() -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {}


def save_ledger(data: dict) -> None:
    LEDGER.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def import_one(pdf: Path) -> tuple[bool, str]:
    """POST 一个 PDF 给 Zotero。返回 (是否成功, 说明)。"""
    blob = pdf.read_bytes()
    sid = str(uuid.uuid4())
    # HTTP 头只能是 latin-1，所以中文标题让 json 转成 \uXXXX 转义（Zotero 那边 JSON.parse 会还原）
    meta = json.dumps({"sessionID": sid, "title": pdf.name, "url": pdf.as_uri()})
    status, body = http(
        "POST",
        BASE + f"/connector/saveStandaloneAttachment?sessionID={sid}",
        body=blob,
        headers={
            "X-Metadata": meta,
            "Content-Type": "application/pdf",
            "Content-Length": str(len(blob)),
        },
    )
    if status != 201:
        return False, f"HTTP {status} {body[:120].decode(errors='replace')}"

    # 等 Zotero 抓完元数据，看看抓成了什么
    deadline = time.time() + 30
    while time.time() < deadline:
        time.sleep(2)
        s, b = http(
            "POST",
            BASE + "/connector/getRecognizedItem",
            body=json.dumps({"sessionID": sid}).encode(),
            headers={"Content-Type": "application/json"},
        )
        if s == 200 and b:
            try:
                info = json.loads(b)
                return True, f"已识别：{info.get('title', '')}"
            except Exception:
                pass
        elif s == 204:
            continue
    return True, "已导入，但元数据没识别出来（要手动填）"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", action="append", default=None, help="要扫描的文件夹，可重复")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="文件名读不出标题的也导")
    args = ap.parse_args()

    folders = [Path(f).expanduser().resolve() for f in args.folder] if args.folder else DEFAULT_FOLDERS
    if not zotero_alive():
        print("Zotero 没开（或 23119 端口不通），先把 Zotero 打开。")
        return 1

    pdfs: list[Path] = []
    for folder in folders:
        if not folder.is_dir():
            print(f"跳过（不是文件夹）：{folder}")
            continue
        pdfs += sorted(p for p in folder.rglob("*.pdf") if not p.name.startswith("."))

    filenames, known_ids, known_titles = library_index()
    ledger = load_ledger()
    print(f"扫到 {len(pdfs)} 个 PDF，Zotero 里已有 {len(filenames)} 个附件。\n")

    todo, skipped, unsure = [], [], []
    for pdf in pdfs:
        key = str(pdf.relative_to(REPO)) if str(pdf).startswith(str(REPO)) else str(pdf)
        aid = arxiv_id_from_name(pdf.name)
        title = title_from_name(pdf.name)
        dup = looks_duplicate(title, known_titles) if title else None
        if key in ledger:
            skipped.append((pdf, "上次已导过"))
        elif pdf.name.lower() in filenames:
            skipped.append((pdf, "Zotero 里已有同名文件"))
        elif aid and aid in known_ids:
            skipped.append((pdf, f"Zotero 里已有 arXiv:{aid}"))
        elif dup:
            skipped.append((pdf, f"Zotero 里已有同篇：{dup[:50]}"))
        elif not title and not aid and not args.force:
            unsure.append(pdf)
        else:
            todo.append(pdf)

    for pdf, why in skipped:
        print(f"  跳过  {pdf.name}  —— {why}")
    for pdf in unsure:
        print(f"  拿不准 {pdf.name}  —— 文件名里没标题也没 arXiv 号，怕重复导入。要导就加 --force")
    for pdf in todo:
        print(f"  待导入 {pdf.name}")
    print()

    if args.dry_run:
        print("dry-run，什么都没动。")
        return 0

    if not todo:
        print("没有要导的，收工。")
        return 0

    ok = fail = 0
    for i, pdf in enumerate(todo, 1):
        print(f"[{i}/{len(todo)}] {pdf.name}")
        try:
            success, msg = import_one(pdf)
        except Exception as exc:  # 单个文件出问题不要中断整批
            success, msg = False, f"出错：{exc}"
        print(f"        {msg}")
        if success:
            ok += 1
            key = str(pdf.relative_to(REPO)) if str(pdf).startswith(str(REPO)) else str(pdf)
            ledger[key] = {"name": pdf.name, "size": pdf.stat().st_size, "at": time.strftime("%Y-%m-%d %H:%M")}
            save_ledger(ledger)
        else:
            fail += 1

    print(f"\n完成：成功 {ok}，失败 {fail}，跳过 {len(skipped)}。")
    print("提示：没识别出元数据的，在 Zotero 里选中那个附件 → 右键「抓取 PDF 元数据」。")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
