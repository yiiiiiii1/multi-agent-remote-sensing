#!/bin/bash
# 双击：把 papers/ 里的新 PDF 同步进 Zotero（已导过的自动跳过）
cd "$(dirname "$0")/../.." || exit 1
echo "================================"
echo " 同步 papers/ → Zotero"
echo "================================"
echo
echo "提醒：条目会进 Zotero 左边【当前选中】的分类，"
echo "      想放指定的分类，先在 Zotero 里点好那个分类。"
echo
read -r -p "按回车开始（Ctrl+C 取消）..."
echo
python3 tools/zotero/import-papers.py
echo
read -r -p "按回车关闭窗口..."
