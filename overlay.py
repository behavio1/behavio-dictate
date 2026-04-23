#!/usr/bin/env python3
# pyright: reportAny=false, reportAttributeAccessIssue=false, reportMissingParameterType=false, reportMissingTypeStubs=false, reportUnannotatedClassAttribute=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownVariableType=false, reportUntypedBaseClass=false, reportUnusedParameter=false
"""Floating cyberpunk listening overlay for Whisper Dictate on macOS."""

import math
import os
import sys
import threading
import time

import AppKit
import objc
from Foundation import NSString
from Foundation import NSDefaultRunLoopMode, NSRunLoop, NSTimer


POSITION_ALIASES = {
    "top-left": "top_left",
    "top-center": "top_center",
    "top-right": "top_right",
    "bottom-left": "bottom_left",
    "bottom-center": "bottom_center",
    "bottom-right": "bottom_right",
}


def _read_int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        return default


def get_overlay_settings() -> tuple[str, int, int]:
    position = os.environ.get("WHISPER_OVERLAY_POSITION", "top_center").strip().lower()
    position = POSITION_ALIASES.get(position, position)
    if position not in {
        "top_left",
        "top_center",
        "top_right",
        "bottom_left",
        "bottom_center",
        "bottom_right",
    }:
        position = "top_center"
    return (
        position,
        _read_int_env("WHISPER_OVERLAY_MARGIN_X", 16),
        _read_int_env("WHISPER_OVERLAY_MARGIN_Y", 12),
    )


def get_target_screen():
    mouse = AppKit.NSEvent.mouseLocation()
    for screen in AppKit.NSScreen.screens():
        frame = screen.frame()
        if (
            frame.origin.x <= mouse.x <= frame.origin.x + frame.size.width
            and frame.origin.y <= mouse.y <= frame.origin.y + frame.size.height
        ):
            return screen
    return AppKit.NSScreen.mainScreen() or AppKit.NSScreen.screens()[0]


def calculate_window_origin(screen, win_w: int, win_h: int) -> tuple[float, float]:
    position, margin_x, margin_y = get_overlay_settings()
    frame = screen.visibleFrame()

    if position.endswith("left"):
        x = frame.origin.x + margin_x
    elif position.endswith("right"):
        x = frame.origin.x + frame.size.width - win_w - margin_x
    else:
        x = frame.origin.x + (frame.size.width - win_w) / 2

    if position.startswith("bottom"):
        y = frame.origin.y + margin_y
    else:
        y = frame.origin.y + frame.size.height - win_h - margin_y

    return x, y


class OverlayWindow:
    """A small floating window with a subtle cyberpunk listening HUD."""

    def __init__(self):
        self.app = AppKit.NSApplication.sharedApplication()
        self.app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory)

        # Window size and position on the screen under the cursor
        screen = get_target_screen()
        win_w, win_h = 292, 68
        x, y = calculate_window_origin(screen, win_w, win_h)

        style = AppKit.NSWindowStyleMaskBorderless
        window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            ((x, y), (win_w, win_h)),
            style,
            AppKit.NSBackingStoreBuffered,
            False,
        )
        window.setLevel_(AppKit.NSFloatingWindowLevel + 1)
        window.setOpaque_(False)
        window.setAlphaValue_(0.9)
        window.setBackgroundColor_(AppKit.NSColor.clearColor())
        window.setHasShadow_(True)
        window.setIgnoresMouseEvents_(True)
        window.setCollectionBehavior_(
            AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces
            | AppKit.NSWindowCollectionBehaviorStationary
        )

        content = CyberpunkOverlayView.alloc().initWithFrame_(((0, 0), (win_w, win_h)))
        window.setContentView_(content)

        content.setNeedsDisplay_(True)
        window.makeKeyAndOrderFront_(None)
        self.app.activateIgnoringOtherApps_(True)
        window.display()
        self.window = window
        self.content = content

        # Animation timer
        self.timer = (
            NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                0.05, self, "tick:", None, True
            )
        )
        NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)

        # Watch for parent process death in a thread
        self._parent_pid = os.getppid()
        watcher = threading.Thread(target=self._watch_parent, daemon=True)
        watcher.start()

        level_watcher = threading.Thread(target=self._watch_levels, daemon=True)
        level_watcher.start()

    def _watch_parent(self):
        """Terminate when parent process dies."""
        while True:
            time.sleep(0.5)
            # Check if parent changed (reparented to init/launchd = parent died)
            if os.getppid() != self._parent_pid:
                self.app.performSelectorOnMainThread_withObject_waitUntilDone_(
                    objc.selector(None, selector=b"terminate:", signature=b"v@:@"),
                    None,
                    False,
                )
                break

    def _watch_levels(self):
        stream = getattr(sys.stdin, "buffer", sys.stdin)
        while True:
            line = stream.readline()
            if not line:
                break
            try:
                if isinstance(line, bytes):
                    text = line.decode("ascii", errors="ignore").strip()
                else:
                    text = line.strip()
                self.content.set_level(float(text))
            except Exception:
                continue

    def tick_(self, _timer):
        self.content.tick()

    def run(self):
        self.app.run()


class CyberpunkOverlayView(AppKit.NSView):
    """A compact HUD with subtle neon bars and label."""

    def initWithFrame_(self, frame):
        self = objc.super(CyberpunkOverlayView, self).initWithFrame_(frame)
        if self is None:
            return None
        self.phase = 0.0
        self.blink_phase = 0.0
        self.started_at = time.monotonic()
        self.target_level = 0.0
        self.live_level = 0.0
        self.peak_level = 0.0
        self.bar_levels = [0.1, 0.14, 0.2, 0.28, 0.22, 0.16, 0.1]
        self.bar_offsets = [0.0, 0.55, 1.1, 1.65, 2.2, 2.75, 3.3]
        return self

    def set_level(self, level: float):
        incoming = max(0.0, min(1.0, level))
        self.target_level = max(self.target_level * 0.55, incoming)
        self.peak_level = max(self.peak_level, self.target_level)

    def tick(self):
        self.phase += 0.42
        self.blink_phase += 0.24
        self.live_level += (self.target_level - self.live_level) * 0.86
        self.target_level *= 0.45
        self.peak_level *= 0.72
        for index, offset in enumerate(self.bar_offsets):
            wave = 0.12 + 0.88 * abs(math.sin(self.phase + offset))
            shimmer = 0.12 * abs(math.sin((self.phase * 1.15) + offset * 1.8))
            emphasis = 0.18 * abs(math.sin((self.phase * 0.9) + index * 0.95))
            signal = max(self.live_level, self.peak_level * 0.72)
            energy = min(
                1.0, 0.02 + wave * (0.08 + signal * 1.85) + shimmer + emphasis * signal
            )
            self.bar_levels[index] = (self.bar_levels[index] * 0.14) + (energy * 0.86)
        self.setNeedsDisplay_(True)

    def _format_elapsed(self) -> str:
        elapsed = int(max(0, time.monotonic() - self.started_at))
        minutes, seconds = divmod(elapsed, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def drawRect_(self, _rect):
        bounds = self.bounds()
        bg_rect = AppKit.NSInsetRect(bounds, 1, 1)

        shell = AppKit.NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
            bg_rect, 16, 16
        )
        AppKit.NSColor.colorWithRed_green_blue_alpha_(0.03, 0.11, 0.08, 0.8).setFill()
        shell.fill()

        border = AppKit.NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
            bg_rect, 16, 16
        )
        AppKit.NSColor.colorWithRed_green_blue_alpha_(0.44, 0.9, 0.72, 0.18).setStroke()
        border.setLineWidth_(1.0)
        border.stroke()

        dot_rect = ((18, 26), (8, 8))
        dot = AppKit.NSBezierPath.bezierPathWithOvalInRect_(dot_rect)
        AppKit.NSColor.colorWithRed_green_blue_alpha_(0.58, 0.98, 0.96, 0.95).setFill()
        dot.fill()

        pulse_alpha = 0.42 + 0.58 * abs(math.sin(self.blink_phase))

        label_attrs = {
            AppKit.NSFontAttributeName: AppKit.NSFont.monospacedSystemFontOfSize_weight_(
                11, AppKit.NSFontWeightBold
            ),
            AppKit.NSForegroundColorAttributeName: AppKit.NSColor.colorWithRed_green_blue_alpha_(
                0.78, 0.97, 1.0, pulse_alpha
            ),
        }
        NSString.stringWithString_("LISTEN").drawAtPoint_withAttributes_(
            (34, 18), label_attrs
        )

        timer_attrs = {
            AppKit.NSFontAttributeName: AppKit.NSFont.monospacedSystemFontOfSize_weight_(
                10, AppKit.NSFontWeightMedium
            ),
            AppKit.NSForegroundColorAttributeName: AppKit.NSColor.colorWithRed_green_blue_alpha_(
                0.98, 0.83, 0.42, 0.92
            ),
        }
        NSString.stringWithString_(self._format_elapsed()).drawAtPoint_withAttributes_(
            (34, 36), timer_attrs
        )

        track_x = 144
        track_y = 10
        bar_width = 11
        bar_gap = 8
        max_height = 44
        corner = 5

        for index, level in enumerate(self.bar_levels):
            height = max(6, max_height * level)
            bar_x = track_x + index * (bar_width + bar_gap)
            bar_y = track_y + (max_height - height) / 2
            bar_rect = ((bar_x, bar_y), (bar_width, height))
            bar = AppKit.NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                bar_rect, corner, corner
            )

            if index < 4:
                color = AppKit.NSColor.colorWithRed_green_blue_alpha_(
                    0.44, 0.95, 0.98, 0.9
                )
            else:
                color = AppKit.NSColor.colorWithRed_green_blue_alpha_(
                    0.91, 0.46, 0.98, 0.88
                )
            color.setFill()
            bar.fill()

            glow_rect = ((bar_x, bar_y + height - 4), (bar_width, 4))
            glow = AppKit.NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                glow_rect, 2, 2
            )
            AppKit.NSColor.colorWithRed_green_blue_alpha_(
                0.98, 1.0, 1.0, 0.35
            ).setFill()
            glow.fill()


def main():
    overlay = OverlayWindow()
    overlay.run()


if __name__ == "__main__":
    main()
