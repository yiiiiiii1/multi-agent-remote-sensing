#!/usr/bin/env bash
# 运行 CAMEL 入门复现实验。
#
# 用法：
#   bash run_demo.sh 01   # 最小双智能体（手动流水线）
#   bash run_demo.sh 02   # RolePlaying 自动双智能体对话
set -euo pipefail

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAMEL_ROOT="$(cd "$DEMO_DIR/../../clones/camel" && pwd)"
VENV_PY="$CAMEL_ROOT/.venv/bin/python"

demo_id="${1:-01}"
script="$(ls "$DEMO_DIR/${demo_id}"_*.py 2>/dev/null | head -n 1 || true)"

if [[ -z "$script" ]]; then
  echo "找不到编号为 ${demo_id} 的实验脚本，请检查目录：$DEMO_DIR" >&2
  exit 1
fi

if [[ -x "$VENV_PY" ]]; then
  PY="$VENV_PY"
else
  PY="python3"
fi

cd "$DEMO_DIR"
exec "$PY" "$script"
