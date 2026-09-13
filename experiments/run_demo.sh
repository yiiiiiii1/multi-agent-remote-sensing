#!/usr/bin/env bash
# 运行 CAMEL 入门复现实验。
#
# 用法：
#   bash run_demo.sh 01        # 最小双智能体（手动流水线）
#   bash run_demo.sh 02        # RolePlaying 自动双智能体对话
#   bash run_demo.sh --where   # 只显示解析到的 CAMEL 位置，不运行
#
# CAMEL 源码位置解析顺序：
#   1) 环境变量 CAMEL_ROOT
#   2) 相对本目录向上几层的 clones/camel
#   3) ~/Documents/Code/clones/camel 等常见位置
set -euo pipefail

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

resolve_camel_root() {
  local candidates=()
  if [[ -n "${CAMEL_ROOT:-}" ]]; then
    candidates+=("$CAMEL_ROOT")
  fi
  candidates+=(
    "$DEMO_DIR/../../clones/camel"
    "$DEMO_DIR/../../../clones/camel"
    "$DEMO_DIR/../../../../clones/camel"
    "$HOME/Documents/Code/clones/camel"
    "$HOME/Documents/my-research/clones/camel"
    "$HOME/clones/camel"
  )
  local c
  for c in "${candidates[@]}"; do
    if [[ -f "$c/camel/__init__.py" ]]; then
      printf '%s\n' "$c"
      return 0
    fi
  done
  return 1
}

CAMEL_ROOT_RESOLVED="$(resolve_camel_root || true)"

if [[ "${1:-}" == "--where" ]]; then
  echo "DEMO_DIR   = $DEMO_DIR"
  echo "CAMEL_ROOT = ${CAMEL_ROOT_RESOLVED:-<未找到>}"
  if [[ -n "$CAMEL_ROOT_RESOLVED" && -x "$CAMEL_ROOT_RESOLVED/.venv/bin/python" ]]; then
    echo "PYTHON     = $CAMEL_ROOT_RESOLVED/.venv/bin/python"
  else
    echo "PYTHON     = python3 (未找到 venv)"
  fi
  exit 0
fi

demo_id="${1:-01}"
script="$(ls "$DEMO_DIR/${demo_id}"_*.py 2>/dev/null | head -n 1 || true)"

if [[ -z "$script" ]]; then
  echo "找不到编号为 ${demo_id} 的实验脚本，请检查目录：$DEMO_DIR" >&2
  exit 1
fi

if [[ -n "$CAMEL_ROOT_RESOLVED" && -x "$CAMEL_ROOT_RESOLVED/.venv/bin/python" ]]; then
  PY="$CAMEL_ROOT_RESOLVED/.venv/bin/python"
else
  echo "警告：没找到 CAMEL 源码/venv，改用系统 python3。" >&2
  echo "      可设置环境变量 CAMEL_ROOT 指向 CAMEL 仓库根目录。" >&2
  PY="python3"
fi

cd "$DEMO_DIR"
exec "$PY" "$script"
