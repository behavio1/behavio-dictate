#!/bin/zsh
set -euo pipefail

SCRIPT_PATH="$(python3 -c 'import pathlib, sys; print(pathlib.Path(sys.argv[1]).resolve())' "$0")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

cd "$SCRIPT_DIR"
source "$SCRIPT_DIR/venv/bin/activate"
exec python "$SCRIPT_DIR/dictate.py" --config "$SCRIPT_DIR/config.yaml" --global --language pl --model mlx-community/whisper-large-v3-turbo --hotkey cmd_r
