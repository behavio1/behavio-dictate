#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$PROJECT_DIR/venv/bin/python}"

if [[ "$(uname)" != "Darwin" ]]; then
    echo "Error: macOS is required to build the app bundle."
    exit 1
fi

if [[ "$(uname -m)" != "arm64" ]]; then
    echo "Error: Apple Silicon is required for the MLX-based macOS build."
    exit 1
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Error: Python environment not found at $PYTHON_BIN"
    echo "Run ./setup.sh first or set PYTHON_BIN explicitly."
    exit 1
fi

if ! "$PYTHON_BIN" -c "import PyInstaller" >/dev/null 2>&1; then
    echo "Installing PyInstaller into the selected environment..."
    "$PYTHON_BIN" -m pip install pyinstaller >/dev/null
fi

rm -rf "$PROJECT_DIR/build" "$PROJECT_DIR/dist/Behavio Dictate.app" "$PROJECT_DIR/dist/Behavio Dictate" "$PROJECT_DIR/dist/Behavio Dictate-macOS.zip" "$PROJECT_DIR/dist/Behavio Dictate-share.zip"

"$PYTHON_BIN" -m PyInstaller --clean "$PROJECT_DIR/Whisper Dictate PL.spec"

mkdir -p "$PROJECT_DIR/dist"

cat > "$PROJECT_DIR/dist/README-macOS.txt" <<'EOF'
Behavio Dictate

How to run:
1. Move Behavio Dictate.app to Applications.
2. Open the app.

First run:
- the configured Whisper model is downloaded once from Hugging Face,
- current default model size is about 1.5 GB,
- after download, the app works locally.

If macOS blocks the app:
1. Right click the app.
2. Choose Open.
3. Confirm the launch.

Required permissions for global mode:
- Microphone
- Accessibility
- Input Monitoring
EOF

ditto -c -k --sequesterRsrc --keepParent "$PROJECT_DIR/dist/Behavio Dictate.app" "$PROJECT_DIR/dist/Behavio Dictate-macOS.zip"

TMP_DIR="$(mktemp -d "/tmp/behavio-dictate.XXXXXX")"
cp -R "$PROJECT_DIR/dist/Behavio Dictate.app" "$TMP_DIR/Behavio Dictate.app"
cp "$PROJECT_DIR/dist/README-macOS.txt" "$TMP_DIR/README-macOS.txt"
ditto -c -k --sequesterRsrc --keepParent "$TMP_DIR" "$PROJECT_DIR/dist/Behavio Dictate-share.zip"
rm -rf "$TMP_DIR"

echo "Build complete:"
echo "  $PROJECT_DIR/dist/Behavio Dictate.app"
echo "  $PROJECT_DIR/dist/Behavio Dictate-macOS.zip"
echo "  $PROJECT_DIR/dist/Behavio Dictate-share.zip"
