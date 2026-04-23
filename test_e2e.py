#!/usr/bin/env python3
"""End-to-end test for Whisper Dictate — simulates ESC key press/release via Quartz."""

import os
import subprocess
import sys
import threading
import time

import Quartz


def simulate_key_press(keycode, flags=0):
    """Simulate a key press via Quartz."""
    event = Quartz.CGEventCreateKeyboardEvent(None, keycode, True)
    if flags:
        Quartz.CGEventSetFlags(event, flags)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


def simulate_key_release(keycode, flags=0):
    """Simulate a key release via Quartz."""
    event = Quartz.CGEventCreateKeyboardEvent(None, keycode, False)
    if flags:
        Quartz.CGEventSetFlags(event, flags)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


# macOS keycodes
KEYCODE_ESC = 0x35
KEYCODE_CTRL_R = 0x3E


class OutputCollector:
    """Collects subprocess output in a background thread."""

    def __init__(self, stream):
        self.lines = []
        self.stream = stream
        self._thread = threading.Thread(target=self._read, daemon=True)
        self._thread.start()

    def _read(self):
        for line in self.stream:
            line = line.rstrip("\n")
            self.lines.append(line)
            print(f"    | {line}")

    def wait_for(self, text, timeout=120):
        deadline = time.time() + timeout
        while time.time() < deadline:
            for line in self.lines:
                if text in line:
                    return True
            time.sleep(0.5)
        return False

    def has(self, text):
        return any(text in line for line in self.lines)


def main():
    print("=" * 56)
    print("  Whisper Dictate — E2E Test")
    print("=" * 56)
    print()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    # Test 1: ESC key (default hotkey)
    print("[1] Starting dictate.py with ESC hotkey...")
    proc = subprocess.Popen(
        [sys.executable, "-u", "dictate.py", "--verbose", "--no-auto-paste"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=script_dir,
        env=env,
    )

    output = OutputCollector(proc.stdout)

    print("[2] Waiting for model to load...")
    if not output.wait_for("Ready!", timeout=120):
        print("\nFAIL: dictate.py never became ready.")
        proc.kill()
        proc.wait()
        sys.exit(1)

    print()
    time.sleep(1)

    print("[3] Simulating ESC press (hold 2s)...")
    simulate_key_press(KEYCODE_ESC)
    time.sleep(2)

    print("    Releasing ESC...")
    simulate_key_release(KEYCODE_ESC)
    time.sleep(5)

    # Test 2: also try ctrl_r
    print()
    print("[4] Simulating right Ctrl press (hold 2s)...")
    proc2 = subprocess.Popen(
        [sys.executable, "-u", "dictate.py", "--verbose", "--no-auto-paste", "--hotkey", "ctrl_r"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=script_dir,
        env=env,
    )

    output2 = OutputCollector(proc2.stdout)

    if not output2.wait_for("Ready!", timeout=120):
        print("\nFAIL: second dictate.py never became ready.")
        proc.kill()
        proc2.kill()
        proc.wait()
        proc2.wait()
        sys.exit(1)

    time.sleep(1)
    simulate_key_press(KEYCODE_CTRL_R, Quartz.kCGEventFlagMaskControl)
    time.sleep(2)

    print("    Releasing right Ctrl...")
    simulate_key_release(KEYCODE_CTRL_R, 0)
    time.sleep(5)

    proc.kill()
    proc2.kill()
    proc.wait()
    proc2.wait()

    print()
    print("=" * 56)
    print("  Results")
    print("=" * 56)

    esc_recording = output.has("Recording...")
    esc_processing = output.has("Processing...")
    esc_mic_err = output.has("Microphone error")
    esc_key_seen = output.has("key press")

    ctrl_recording = output2.has("Recording...")
    ctrl_processing = output2.has("Processing...")
    ctrl_mic_err = output2.has("Microphone error")
    ctrl_key_seen = output2.has("key press")

    print(f"  ESC:    key_seen={esc_key_seen}  recording={esc_recording}  processing={esc_processing}  mic_err={esc_mic_err}")
    print(f"  Ctrl_R: key_seen={ctrl_key_seen}  recording={ctrl_recording}  processing={ctrl_processing}  mic_err={ctrl_mic_err}")

    esc_ok = esc_recording or esc_mic_err or esc_processing
    ctrl_ok = ctrl_recording or ctrl_mic_err or ctrl_processing

    if esc_ok and ctrl_ok:
        print("\n  SUCCESS: Both hotkeys working!")
    elif esc_ok:
        print("\n  PARTIAL: ESC works, Ctrl_R failed.")
    elif ctrl_ok:
        print("\n  PARTIAL: Ctrl_R works, ESC failed.")
    else:
        print("\n  FAILED: Neither hotkey triggered recording.")
        if not esc_key_seen and not ctrl_key_seen:
            print("  pynput is not receiving ANY key events.")
            print("  Check: System Settings > Privacy & Security > Input Monitoring")
            print("  Add Terminal (or your terminal app) to the list.")

    print()


if __name__ == "__main__":
    main()
