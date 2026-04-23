#!/usr/bin/env python3
"""Standalone microphone-driven overlay test for Whisper Dictate PL."""

import os
import signal
import subprocess
import sys
import time

import numpy as np
import pyaudio


SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16


def main():
    env = os.environ.copy()
    env.setdefault("WHISPER_OVERLAY_POSITION", "bottom_center")
    env.setdefault("WHISPER_OVERLAY_MARGIN_Y", "36")

    overlay_proc = subprocess.Popen(
        [sys.executable, os.path.join(os.path.dirname(__file__), "overlay.py")],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )

    pa = pyaudio.PyAudio()
    stream = None

    def cleanup(*_args):
        try:
            if overlay_proc.stdin:
                overlay_proc.stdin.close()
        except Exception:
            pass
        try:
            overlay_proc.terminate()
        except Exception:
            pass
        try:
            if stream is not None:
                stream.stop_stream()
                stream.close()
        except Exception:
            pass
        pa.terminate()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
    )

    try:
        while True:
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            if len(samples) == 0:
                level = 0.0
            else:
                rms = float(np.sqrt(np.mean(np.square(samples / 32768.0))))
                level = min(1.0, rms * 18.0)
            if overlay_proc.stdin is not None:
                overlay_proc.stdin.write(f"{level:.4f}\n".encode("ascii"))
                overlay_proc.stdin.flush()
            time.sleep(0.01)
    finally:
        cleanup()


if __name__ == "__main__":
    main()
