# Release Process

## Local macOS Release

Build the app on an Apple Silicon Mac:

```bash
./scripts/build_macos_dist.sh
```

Expected outputs:

- `dist/Behavio Dictate.app`
- `dist/Behavio Dictate-macOS.zip`
- `dist/Behavio Dictate-share.zip`

## Publish To GitHub

1. Create or update a tag.
2. Create a GitHub Release.
3. Upload `dist/Behavio Dictate-share.zip` as the main macOS asset.
4. Optionally upload `dist/Behavio Dictate-macOS.zip` as the raw app-only archive.

## Notes

- Build outputs are release artifacts and should not be committed to git.
- The app currently uses an ad-hoc signature, so macOS may require `Open` on first launch.
- The default model is downloaded on first run unless the user configures a local model path.
