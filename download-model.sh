#!/bin/bash
# Whisper Dictate — Model Downloader
# Downloads the Whisper model to ./models/ for local use.

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

MODELS_DIR="$(cd "$(dirname "$0")" && pwd)/models"

echo ""
echo -e "${BOLD}========================================================"
echo "  Whisper Dictate — Model Downloader"
echo -e "========================================================${NC}"
echo ""

# ---------------------------------------------------------------------------
# Step 1: Choose backend
# ---------------------------------------------------------------------------

echo -e "${CYAN}Which backend will you use?${NC}"
echo ""
echo "  1) MLX     — Apple Silicon (M1/M2/M3/M4), fastest on Mac"
echo "  2) NVIDIA  — CUDA GPU (Linux/Windows), or CPU fallback"
echo ""
read -rp "  Enter choice [1/2]: " BACKEND_CHOICE
echo ""

case "$BACKEND_CHOICE" in
    1) BACKEND="mlx" ;;
    2) BACKEND="nvidia" ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

# ---------------------------------------------------------------------------
# Step 2: Choose model
# ---------------------------------------------------------------------------

echo -e "${CYAN}Choose a model:${NC}"
echo ""

if [[ "$BACKEND" == "mlx" ]]; then
    echo "  1) tiny              ~75 MB   — fastest, good accuracy"
    echo "  2) base             ~150 MB   — fast, better accuracy"
    echo "  3) small            ~500 MB   — great accuracy (recommended)"
    echo "  4) medium           ~1.5 GB   — excellent accuracy"
    echo "  5) large-v3         ~3.0 GB   — best accuracy"
    echo "  6) large-v3-turbo   ~1.6 GB   — best speed/accuracy balance"
    echo ""
    read -rp "  Enter choice [1-6] (default: 3): " MODEL_CHOICE
    MODEL_CHOICE="${MODEL_CHOICE:-3}"

    case "$MODEL_CHOICE" in
        1) REPO="mlx-community/whisper-tiny-mlx";          MODEL_NAME="whisper-tiny-mlx" ;;
        2) REPO="mlx-community/whisper-base-mlx";          MODEL_NAME="whisper-base-mlx" ;;
        3) REPO="mlx-community/whisper-small-mlx";         MODEL_NAME="whisper-small-mlx" ;;
        4) REPO="mlx-community/whisper-medium-mlx";        MODEL_NAME="whisper-medium-mlx" ;;
        5) REPO="mlx-community/whisper-large-v3-mlx";      MODEL_NAME="whisper-large-v3-mlx" ;;
        6) REPO="mlx-community/whisper-large-v3-turbo-mlx"; MODEL_NAME="whisper-large-v3-turbo-mlx" ;;
        *)
            echo -e "${RED}Invalid choice. Exiting.${NC}"
            exit 1
            ;;
    esac
else
    echo "  1) tiny              ~75 MB   — fastest, good accuracy"
    echo "  2) base             ~150 MB   — fast, better accuracy"
    echo "  3) small            ~500 MB   — great accuracy (recommended)"
    echo "  4) medium           ~1.5 GB   — excellent accuracy"
    echo "  5) large-v3         ~3.0 GB   — best accuracy"
    echo "  6) large-v3-turbo   ~1.6 GB   — best speed/accuracy balance"
    echo ""
    read -rp "  Enter choice [1-6] (default: 3): " MODEL_CHOICE
    MODEL_CHOICE="${MODEL_CHOICE:-3}"

    case "$MODEL_CHOICE" in
        1) REPO="Systran/faster-whisper-tiny";          MODEL_NAME="faster-whisper-tiny" ;;
        2) REPO="Systran/faster-whisper-base";          MODEL_NAME="faster-whisper-base" ;;
        3) REPO="Systran/faster-whisper-small";         MODEL_NAME="faster-whisper-small" ;;
        4) REPO="Systran/faster-whisper-medium";        MODEL_NAME="faster-whisper-medium" ;;
        5) REPO="Systran/faster-whisper-large-v3";      MODEL_NAME="faster-whisper-large-v3" ;;
        6) REPO="Systran/faster-whisper-large-v3-turbo"; MODEL_NAME="faster-whisper-large-v3-turbo" ;;
        *)
            echo -e "${RED}Invalid choice. Exiting.${NC}"
            exit 1
            ;;
    esac
fi

echo ""
echo -e "${YELLOW}Downloading: ${BOLD}${REPO}${NC}"
echo -e "${YELLOW}Destination: ${BOLD}${MODELS_DIR}/${MODEL_NAME}/${NC}"
echo ""

# ---------------------------------------------------------------------------
# Step 3: Ensure huggingface-cli is available
# ---------------------------------------------------------------------------

if command -v hf &>/dev/null; then
    HF_CMD="hf"
elif command -v huggingface-cli &>/dev/null; then
    HF_CMD="huggingface-cli"
else
    echo -e "${YELLOW}Installing huggingface-hub CLI...${NC}"
    pip install --quiet huggingface-hub
    HF_CMD="huggingface-cli"
    # Check if hf is available after install (newer versions)
    if command -v hf &>/dev/null; then
        HF_CMD="hf"
    fi
fi

# ---------------------------------------------------------------------------
# Step 4: Download
# ---------------------------------------------------------------------------

mkdir -p "$MODELS_DIR"

$HF_CMD download "$REPO" --local-dir "$MODELS_DIR/$MODEL_NAME"

echo ""
echo -e "${GREEN}========================================================"
echo "  Download complete!"
echo "========================================================"
echo ""
echo "  Model saved to: models/${MODEL_NAME}/"
echo ""
echo "  To use it, update config.yaml:"
echo ""
if [[ "$BACKEND" == "mlx" ]]; then
    echo "    backend: \"mlx\""
    echo "    model: \"models/${MODEL_NAME}\""
else
    echo "    backend: \"faster-whisper\""
    echo "    model: \"models/${MODEL_NAME}\""
fi
echo ""
echo "  Or pass it on the command line:"
echo ""
echo "    python dictate.py --backend ${BACKEND} --model models/${MODEL_NAME}"
echo ""
echo -e "========================================================${NC}"
