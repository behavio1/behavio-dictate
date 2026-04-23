# Behavio Dictate

Local voice-to-text dictation for macOS. Hold a hotkey, speak, release, and the text is pasted into the active app. The app runs locally on Apple Silicon using Whisper via MLX.

## What It Does

- Dictates into any macOS app with a global hotkey
- Uses local Whisper inference on Apple Silicon
- Shows a lightweight on-screen listening overlay
- Supports direct transcription and translation-to-English flows
- Can run from source or as a packaged `.app`

## Inspiration

Behavio Dictate was inspired by the original [Whisper Dictate](https://github.com/GuigsEvt/whisper-dictate) project.

## Download

For a ready-to-run macOS build, use the latest GitHub Release:

- `https://github.com/behavio1/behavio-dictate/releases/latest`

Release assets are built for macOS on Apple Silicon.

## Current Defaults

This repository is currently configured with Behavio-specific defaults:

- app name: `Behavio Dictate`
- default language: Polish (`pl`)
- default hotkey: right Command (`cmd_r`)
- default model: `mlx-community/whisper-large-v3-turbo`
- auto-paste: enabled

You can change these values in `config.yaml`.

We recommend `large-v3-turbo` as the default model for this app. It gives the best overall balance of speed and quality and is the recommended model for Behavio Dictate.

## Hotkey Configuration

The hotkey is only relevant in global mode, meaning when you run the app with `--global` or launch the packaged macOS app.

You can configure it in three places:

### 1. Persistent project default: `config.yaml`

Edit the `hotkey` field in `config.yaml`:

```yaml
hotkey: "cmd_r"
```

Use this when you want your preferred shortcut to be the default every time you run the app.

### 2. One-off override from the command line

Pass `--hotkey` together with `--global`:

```bash
python dictate.py --global --hotkey esc
python dictate.py --global --hotkey f6
python dictate.py --global --hotkey r
```

This overrides the value from `config.yaml` only for the current launch.

### 3. Repository launcher script

If you use `run-whisper-dictate-pl.command`, the hotkey is also set there explicitly:

```bash
./run-whisper-dictate-pl.command
```

That script currently runs:

```bash
python dictate.py --config config.yaml --global --language pl --model mlx-community/whisper-large-v3-turbo --hotkey cmd_r
```

If you want that launcher to use another shortcut by default, update the `--hotkey ...` argument in `run-whisper-dictate-pl.command`.

### Supported hotkey values

These values are supported by the app:

- `fn` or `globe`: the fn/Globe key on a Mac keyboard
- `esc` or `escape`: Escape
- `ctrl`, `ctrl_l`, `ctrl_r`: Control key
- `alt`, `alt_l`, `alt_r`, `option`, `option_l`, `option_r`: Option/Alt key
- `cmd`, `cmd_l`, `cmd_r`: Command key
- `shift`, `shift_l`, `shift_r`: Shift key
- `space`, `tab`, `enter`: common keyboard keys
- `f1` to `f12`: function keys
- any single character such as `r`, `t`, or `;`

Examples:

- `hotkey: "cmd_r"`: right Command
- `hotkey: "ctrl_r"`: right Control
- `hotkey: "f8"`: F8
- `hotkey: "r"`: letter R

### Related parameters

- `--global`: enables system-wide hotkey mode
- `--hotkey KEY`: chooses which key starts and stops recording
- `--config FILE`: loads a different config file instead of the default `config.yaml`

Example with all three together:

```bash
python dictate.py --config config.yaml --global --hotkey ctrl_r
```

### macOS note for `fn`

If you use `fn`, macOS should not reserve it for the emoji picker:

`System Settings > Keyboard > Press fn key to > Do Nothing`

## Requirements

- macOS on Apple Silicon (`arm64`)
- Python 3.11+
- Homebrew
- PortAudio: `brew install portaudio`

## First Run

The default model is not committed to the repository and is not embedded in the source tree.

On first launch, the app downloads the configured model from Hugging Face and caches it locally. With the current default model, expect roughly `1.5 GB` to be downloaded once.

After the model is cached, transcription works locally without needing an active internet connection.

## Quick Start From Source

```bash
git clone https://github.com/behavio1/behavio-dictate.git
cd behavio-dictate
chmod +x setup.sh download-model.sh run-whisper-dictate-pl.command scripts/build_macos_dist.sh
./setup.sh
```

Run in terminal mode:

```bash
source venv/bin/activate
python dictate.py
```

Run in global mode:

```bash
source venv/bin/activate
python dictate.py --global
```

Run with the repository defaults:

```bash
./run-whisper-dictate-pl.command
```

## Build The macOS App

Build a distributable `.app` and release ZIP locally:

```bash
./scripts/build_macos_dist.sh
```

This produces release-ready files in `dist/`.

## Model Options

Download a model explicitly for offline-first setup:

```bash
./download-model.sh
```

Note: the repository default uses the remote model id `mlx-community/whisper-large-v3-turbo`. If you download a local copy with `download-model.sh`, the matching local path will be `models/whisper-large-v3-turbo-mlx`.

Common MLX models:

| Model | Size | Remote repo id |
|-------|------|----------------|
| tiny | ~75 MB | `mlx-community/whisper-tiny-mlx` |
| base | ~150 MB | `mlx-community/whisper-base-mlx` |
| small | ~500 MB | `mlx-community/whisper-small-mlx` |
| medium | ~1.5 GB | `mlx-community/whisper-medium-mlx` |
| large-v3 | ~3.0 GB | `mlx-community/whisper-large-v3-mlx` |
| large-v3-turbo | ~1.6 GB | `mlx-community/whisper-large-v3-turbo` |

Recommended for this app: `large-v3-turbo`.

## Configuration

Main settings live in `config.yaml`:

```yaml
backend: "mlx"
model: "mlx-community/whisper-large-v3-turbo"
language: "pl"
hotkey: "cmd_r"
auto_paste: true
show_overlay: true
sound_on_start: true
sound_on_stop: true
trailing_space: true
```

Available hotkeys include `fn`, `esc`, `ctrl_r`, `cmd_r`, `space`, `tab`, `enter`, `f1`-`f12`, and single-character keys.

## macOS Permissions

Global mode requires:

1. `Microphone`
2. `Accessibility`
3. `Input Monitoring`

If macOS blocks the packaged app, open it the first time via right click and `Open`.

## Repository Layout

```text
.
├── README.md
├── LICENSE
├── .github/
├── assets/
├── scripts/
├── sounds/
├── dictate.py
├── overlay.py
├── config.yaml
├── setup.sh
├── download-model.sh
├── run-whisper-dictate-pl.command
└── Whisper Dictate PL.spec
```

Build outputs, local models, virtual environments, and backup copies are intentionally excluded from git.

## Development Notes

- `dictate.py` is the main entry point
- `overlay.py` handles the floating listening indicator
- `Whisper Dictate PL.spec` builds the macOS app via PyInstaller
- `scripts/build_macos_dist.sh` creates the distributable app bundle and ZIP

## Credits

This project builds on the ideas and codebase of the original [Whisper Dictate](https://github.com/GuigsEvt/whisper-dictate) project and has been adapted for the Behavio workflow and macOS app distribution.

## License

MIT
