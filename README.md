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

## Configure The App Step By Step

### 1. Install dependencies

```bash
chmod +x setup.sh download-model.sh run-whisper-dictate-pl.command scripts/build_macos_dist.sh
./setup.sh
```

### 2. Open `config.yaml`

Main app behavior is configured in `config.yaml`.

Current default configuration:

```yaml
backend: "mlx"
model: "mlx-community/whisper-large-v3-turbo"
language: "pl"
hotkey: "cmd_r"
sound_on_start: true
sound_on_stop: true
auto_paste: true
show_overlay: true
overlay_position: "top_center"
trailing_space: true
device: null
```

### 3. Set the most important parameters

- `backend`: use `mlx` on Apple Silicon Macs
- `model`: Whisper model repo id or local path
- `language`: default spoken language, for example `pl`, `en`, or `auto`
- `hotkey`: key used in global mode to start and stop recording
- `auto_paste`: if `true`, the app pastes the result automatically; if `false`, it only copies to clipboard
- `show_overlay`: shows the floating listening indicator while recording
- `device`: microphone device index, or `null` to use the system default input

### 4. Recommended model setup

Recommended setting for this app:

```yaml
model: "mlx-community/whisper-large-v3-turbo"
```

This is the recommended model for Behavio Dictate because it gives the best overall speed/quality tradeoff.

If you want a local offline model path instead of a remote Hugging Face id:

```bash
./download-model.sh
```

Then update `config.yaml`, for example:

```yaml
model: "models/whisper-large-v3-turbo-mlx"
```

### 5. Configure the hotkey

Use one of these approaches:

- persistent default in `config.yaml`
- one-off override with `python dictate.py --global --hotkey ...`
- launcher-specific override in `run-whisper-dictate-pl.command`

Examples:

```yaml
hotkey: "cmd_r"
hotkey: "ctrl_r"
hotkey: "f8"
hotkey: "r"
```

### 6. Grant macOS permissions

For global mode or the packaged app, enable:

1. `Microphone`
2. `Accessibility`
3. `Input Monitoring`

If you use `fn`, also set:

`System Settings > Keyboard > Press fn key to > Do Nothing`

### 7. Test the configuration

Useful commands:

```bash
source venv/bin/activate
python dictate.py --list-devices
python dictate.py --global --debug-keys
python dictate.py --test
```

### 8. Run the app

From source in terminal mode:

```bash
source venv/bin/activate
python dictate.py
```

From source in global mode:

```bash
source venv/bin/activate
python dictate.py --global
```

With the repository launcher:

```bash
./run-whisper-dictate-pl.command
```

## Build The macOS App

Build a distributable `.app` and release ZIP locally:

```bash
./scripts/build_macos_dist.sh
```

This produces release-ready files in `dist/`.

## Build And Deploy Step By Step

### 1. Prepare the environment

```bash
git clone git@github.com-behavio1:behavio1/behavio-dictate.git
cd behavio-dictate
chmod +x setup.sh download-model.sh run-whisper-dictate-pl.command scripts/build_macos_dist.sh
./setup.sh
```

### 2. Verify the app config before packaging

Make sure `config.yaml` contains the values you want to ship in the app bundle, especially:

- `model`
- `language`
- `hotkey`
- `auto_paste`
- `show_overlay`

The build includes `config.yaml` inside the packaged app, so these defaults become the initial shipped defaults.

### 3. Build the app bundle

```bash
./scripts/build_macos_dist.sh
```

This script:

1. checks that you are on macOS Apple Silicon
2. uses `venv/bin/python`
3. installs PyInstaller if needed
4. builds `Behavio Dictate.app`
5. creates release ZIP archives in `dist/`

### 4. Check the build outputs

Expected files:

- `dist/Behavio Dictate.app`
- `dist/Behavio Dictate-macOS.zip`
- `dist/Behavio Dictate-share.zip`

### 5. Smoke-test the packaged app

Before publishing, test at least this:

1. open `dist/Behavio Dictate.app`
2. confirm microphone permission prompt works
3. confirm overlay appears during recording
4. confirm the selected hotkey starts and stops recording
5. confirm text is copied or pasted as expected

### 6. Push the repository changes

```bash
git status
git add .
git commit -m "Describe your release change"
git push origin main
```

### 7. Create a release tag

```bash
git tag -a v0.1.1 -m "Behavio Dictate 0.1.1"
git push origin v0.1.1
```

### 8. Publish the GitHub Release

Example with GitHub CLI:

```bash
gh release create v0.1.1 \
  "dist/Behavio Dictate-share.zip#Behavio Dictate for macOS" \
  "dist/Behavio Dictate-macOS.zip#Behavio Dictate app archive" \
  --repo behavio1/behavio-dictate \
  --title "Behavio Dictate 0.1.1" \
  --notes "Short release notes here"
```

### 9. Share the correct asset

For end users, the preferred download is usually:

- `Behavio Dictate-share.zip`

It contains the app plus the short macOS usage note.

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
