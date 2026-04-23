# -*- mode: python ; coding: utf-8 -*-

from importlib.util import find_spec
import os
from pathlib import Path
import sysconfig

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


PROJECT_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
APP_NAME = "Behavio Dictate"
APP_VERSION = os.environ.get("BEHAVIO_DICTATE_VERSION", "0.1.0")


def resolve_libjaccl() -> str:
    candidates: list[Path] = []

    mlx_spec = find_spec("mlx")
    if mlx_spec is not None and mlx_spec.submodule_search_locations is not None:
        candidates.extend(
            Path(location) / "lib" / "libjaccl.dylib"
            for location in mlx_spec.submodule_search_locations
        )

    site_packages = Path(sysconfig.get_paths()["platlib"])
    candidates.extend(site_packages.glob("mlx/lib/libjaccl.dylib"))

    for candidate in candidates:
        if candidate.exists():
            return str(candidate.resolve())

    raise FileNotFoundError("Could not locate mlx/lib/libjaccl.dylib for PyInstaller build.")


LIBJACCL = resolve_libjaccl()
DATA_FILES = [('config.yaml', '.'), ('sounds', 'sounds')] + collect_data_files('mlx') + collect_data_files('mlx_whisper')
MLX_WHISPER_IMPORTS = [
    'mlx_whisper.audio',
    'mlx_whisper.decoding',
    'mlx_whisper.load_models',
    'mlx_whisper.transcribe',
    'mlx_whisper.tokenizer',
    'mlx_whisper.timing',
    'mlx_whisper.whisper',
    'mlx_whisper.version',
    'mlx_whisper.writers',
]
HIDDEN_IMPORTS = ['overlay'] + collect_submodules('mlx') + MLX_WHISPER_IMPORTS


a = Analysis(
    ['dictate.py'],
    pathex=[],
    binaries=[(LIBJACCL, '.')],
    datas=DATA_FILES,
    hiddenimports=HIDDEN_IMPORTS,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'mlx_whisper.torch_whisper'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)
app = BUNDLE(
    coll,
    name=f'{APP_NAME}.app',
    icon='assets/behavio-dictate.icns',
    bundle_identifier='one.behavio.dictate',
    info_plist={
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleVersion': APP_VERSION,
        'CFBundleShortVersionString': APP_VERSION,
        'NSHighResolutionCapable': True,
        'NSMicrophoneUsageDescription': 'Behavio Dictate needs microphone access to transcribe your speech locally.',
        'NSAppleEventsUsageDescription': 'Behavio Dictate needs automation access to paste transcribed text into the active app.',
    },
)
