#!/bin/bash
# Whisper Dictate — Setup Script
# Run: chmod +x setup.sh && ./setup.sh

set -e

echo "========================================================"
echo "  Whisper Dictate — Setup"
echo "========================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check we're on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${RED}Error: This app only runs on macOS.${NC}"
    exit 1
fi

# Check Apple Silicon
if [[ "$(uname -m)" != "arm64" ]]; then
    echo -e "${RED}Error: This app requires Apple Silicon (M1/M2/M3/M4).${NC}"
    exit 1
fi

# Check Homebrew
if ! command -v brew &>/dev/null; then
    echo -e "${RED}Error: Homebrew not found. Install it from https://brew.sh${NC}"
    exit 1
fi

# Step 1: Install PortAudio
echo -e "${YELLOW}[1/5] Installing PortAudio (for microphone access)...${NC}"
if brew list portaudio &>/dev/null; then
    echo "  PortAudio already installed."
else
    brew install portaudio
fi
echo ""

# Step 2: Find Python 3.11+
echo -e "${YELLOW}[2/5] Setting up Python...${NC}"
PYTHON=""
for ver in python3.12 python3.13 python3.14 python3.11; do
    if command -v "$ver" &>/dev/null; then
        PYTHON="$ver"
        break
    fi
done

if [[ -z "$PYTHON" ]]; then
    echo "  No Python 3.11+ found. Installing Python 3.12 via Homebrew..."
    brew install python@3.12
    PYTHON="python3.12"
fi
echo "  Using: $PYTHON ($($PYTHON --version))"
echo ""

# Step 3: Create virtual environment
echo -e "${YELLOW}[3/5] Creating virtual environment...${NC}"
if [[ -d "venv" ]]; then
    echo "  Virtual environment already exists. Recreating..."
    rm -rf venv
fi
$PYTHON -m venv venv
source venv/bin/activate
echo "  Created: ./venv/"
echo ""

# Step 4: Install dependencies
echo -e "${YELLOW}[4/5] Installing Python dependencies...${NC}"
pip install --upgrade pip --quiet
pip install -r requirements.txt
echo "  All dependencies installed."
echo ""

# Step 5: Test microphone
echo -e "${YELLOW}[5/5] Testing microphone access...${NC}"
python -c "
import pyaudio
pa = pyaudio.PyAudio()
try:
    default = pa.get_default_input_device_info()
    print(f\"  Default microphone: {default['name']}\")
    print(f\"  Channels: {int(default['maxInputChannels'])}, Sample Rate: {int(default['defaultSampleRate'])}\")
except Exception as e:
    print(f\"  Warning: Could not detect microphone: {e}\")
    print(f\"  Make sure your microphone is connected.\")
pa.terminate()
"
echo ""

# Done
echo -e "${GREEN}========================================================"
echo "  Setup complete!"
echo "========================================================"
echo ""
echo "  To start dictating:"
echo ""
echo "    source venv/bin/activate"
echo "    python dictate.py"
echo ""
echo "  First run will download the Whisper model (~500 MB)."
echo ""
echo "  Terminal mode works out of the box (hold SPACE to record)."
echo ""
echo "  For global hotkey mode (--global), grant these permissions:"
echo "    - Microphone (prompted automatically)"
echo "    - Accessibility (System Settings > Privacy > Accessibility)"
echo "    - Input Monitoring (System Settings > Privacy > Input Monitoring)"
echo ""
echo -e "========================================================${NC}"
