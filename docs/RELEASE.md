# Release Process

## Prerequisites

- macOS on Apple Silicon
- repository checked out locally
- `origin` pointing to `git@github.com-behavio1:behavio1/behavio-dictate.git`
- working Python environment created by `./setup.sh`

## Step 1: Prepare The Build Environment

```bash
chmod +x setup.sh download-model.sh run-whisper-dictate-pl.command scripts/build_macos_dist.sh
./setup.sh
```

## Step 2: Configure The App Defaults

Before building, review `config.yaml` because it is bundled into the app.

Recommended fields to confirm before each release:

- `model`
- `language`
- `hotkey`
- `auto_paste`
- `show_overlay`
- `device`

Recommended model for Behavio Dictate:

```yaml
model: "mlx-community/whisper-large-v3-turbo"
```

## Step 3: Create The Local macOS Release

Build the app on an Apple Silicon Mac:

```bash
./scripts/build_macos_dist.sh
```

What the script does:

1. validates the host OS and CPU architecture
2. uses the project virtual environment
3. installs `PyInstaller` if it is missing
4. builds `Behavio Dictate.app`
5. creates ZIP archives for distribution

Expected outputs:

- `dist/Behavio Dictate.app`
- `dist/Behavio Dictate-macOS.zip`
- `dist/Behavio Dictate-share.zip`

## Step 4: Smoke Test The Build

Before publishing, verify:

1. the app opens
2. permissions prompts work
3. the configured hotkey works
4. the overlay is visible
5. text is copied or pasted correctly

## Step 5: Push Repository Changes

```bash
git status
git add .
git commit -m "Describe the release change"
git push origin main
```

## Step 6: Create And Push A Tag

```bash
git tag -a v0.1.1 -m "Behavio Dictate 0.1.1"
git push origin v0.1.1
```

## Step 7: Publish To GitHub

CLI example:

```bash
gh release create v0.1.1 \
  "dist/Behavio Dictate-share.zip#Behavio Dictate for macOS" \
  "dist/Behavio Dictate-macOS.zip#Behavio Dictate app archive" \
  --repo behavio1/behavio-dictate \
  --title "Behavio Dictate 0.1.1" \
  --notes "Short release notes here"
```

Upload:

1. `dist/Behavio Dictate-share.zip` as the main user-facing asset
2. `dist/Behavio Dictate-macOS.zip` as the raw app-only archive

## Notes

- Build outputs are release artifacts and should not be committed to git.
- The app currently uses an ad-hoc signature, so macOS may require `Open` on first launch.
- The default model is downloaded on first run unless the user configures a local model path.
- `Behavio Dictate-share.zip` is the preferred file to share with end users.
