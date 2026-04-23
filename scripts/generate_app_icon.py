#!/usr/bin/env python3
"""Generate the Behavio Dictate macOS app icon."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ICONSET_DIR = ROOT / "assets" / "behavio-dictate.iconset"


def build_master_icon(size: int = 1024) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for y in range(size):
        t = y / (size - 1)
        r = int(8 + (18 - 8) * t)
        g = int(34 + (72 - 34) * t)
        b = int(24 + (52 - 24) * t)
        draw.line((0, y, size, y), fill=(r, g, b, 255))

    pad = 86
    radius = 228

    shell = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shell_draw = ImageDraw.Draw(shell)
    shell_draw.rounded_rectangle(
        (pad, pad, size - pad, size - pad),
        radius=radius,
        fill=(8, 38, 28, 244),
        outline=(126, 229, 185, 74),
        width=8,
    )
    img.alpha_composite(shell)

    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle(
        (pad + 20, pad + 20, size - pad - 20, size - pad - 20),
        radius=radius - 22,
        outline=(164, 255, 221, 28),
        width=6,
    )
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)))

    accent = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    accent_draw = ImageDraw.Draw(accent)
    accent_draw.rounded_rectangle(
        (206, 214, 818, 230),
        radius=8,
        fill=(110, 255, 214, 112),
    )
    img.alpha_composite(accent.filter(ImageFilter.GaussianBlur(2)))

    # Equalizer bars
    bars = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bars_draw = ImageDraw.Draw(bars)
    bar_w = 64
    gap = 34
    heights = [220, 340, 470, 350, 520, 390, 250]
    start_x = 248
    bottom = 724
    colors = [
        (118, 255, 214, 232),
        (110, 249, 205, 236),
        (100, 242, 194, 240),
        (141, 251, 214, 242),
        (189, 255, 230, 246),
        (118, 240, 198, 238),
        (92, 229, 181, 230),
    ]
    for index, height in enumerate(heights):
        x0 = start_x + index * (bar_w + gap)
        y0 = bottom - height
        x1 = x0 + bar_w
        y1 = bottom
        bars_draw.rounded_rectangle(
            (x0, y0, x1, y1),
            radius=24,
            fill=colors[index],
        )
        bars_draw.rounded_rectangle(
            (x0, y0, x1, y0 + 40),
            radius=18,
            fill=(235, 255, 246, 88),
        )
    img.alpha_composite(bars.filter(ImageFilter.GaussianBlur(1)))

    pulse = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pulse_draw = ImageDraw.Draw(pulse)
    pulse_draw.ellipse((186, 585, 238, 637), fill=(145, 255, 220, 250))
    img.alpha_composite(pulse.filter(ImageFilter.GaussianBlur(1)))

    # Behavio-style B monogram.
    mono = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mono_draw = ImageDraw.Draw(mono)
    mono_draw.rounded_rectangle(
        (184, 318, 252, 566), radius=30, fill=(228, 255, 241, 214)
    )
    mono_draw.rounded_rectangle(
        (236, 320, 372, 420),
        radius=50,
        outline=(228, 255, 241, 214),
        width=34,
    )
    mono_draw.rounded_rectangle(
        (236, 438, 392, 574),
        radius=58,
        outline=(228, 255, 241, 214),
        width=34,
    )
    img.alpha_composite(mono.filter(ImageFilter.GaussianBlur(0.5)))

    return img


def main() -> None:
    ICONSET_DIR.mkdir(parents=True, exist_ok=True)
    master = build_master_icon()

    sizes = {
        "icon_16x16.png": 16,
        "icon_16x16@2x.png": 32,
        "icon_32x32.png": 32,
        "icon_32x32@2x.png": 64,
        "icon_128x128.png": 128,
        "icon_128x128@2x.png": 256,
        "icon_256x256.png": 256,
        "icon_256x256@2x.png": 512,
        "icon_512x512.png": 512,
        "icon_512x512@2x.png": 1024,
    }
    for filename, size in sizes.items():
        master.resize((size, size), Image.Resampling.LANCZOS).save(
            ICONSET_DIR / filename
        )


if __name__ == "__main__":
    main()
