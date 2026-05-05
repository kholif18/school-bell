# core/audio_manager.py
import pygame
import threading
import queue
import os
import logging
from typing import Optional

from core.paths import app_path

logger = logging.getLogger(__name__)


class AudioManager:
    """
    Clean Audio Manager:
    - Single worker thread
    - Queue-based playback
    - Thread-safe
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._queue = queue.Queue()
        self._running = True

        self.audio_dir = app_path("assets", "audio")
        self.default_audio = app_path("assets", "audio", "default_bell.wav")

        self._init_mixer()
        self._ensure_default_audio()

        # start worker once
        self._worker_thread = threading.Thread(
            target=self._worker,
            daemon=True
        )
        self._worker_thread.start()

        logger.info("AudioManager initialized")

    # =========================
    # INIT
    # =========================

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            logger.error(f"Pygame mixer init failed: {e}")

    def _ensure_default_audio(self):
        if not os.path.exists(self.default_audio):
            self._create_default_bell()

    def _create_default_bell(self):
        import wave
        import struct
        import math

        os.makedirs(self.audio_dir, exist_ok=True)

        try:
            sample_rate = 44100
            duration = 0.3
            freq = 880

            samples = []

            for i in range(int(sample_rate * duration)):
                t = i / sample_rate
                value = int(32767 * math.sin(2 * math.pi * freq * t))
                samples.append(struct.pack("<h", value))

            with wave.open(self.default_audio, "w") as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(sample_rate)
                f.writeframes(b"".join(samples))

            logger.info("Default bell created")

        except Exception as e:
            logger.error(f"Failed to create bell: {e}")

    # =========================
    # PUBLIC API
    # =========================

    def play(self, audio_file: Optional[str] = None):
        """
        Non-blocking enqueue playback
        """
        target = audio_file if audio_file and os.path.exists(audio_file) else self.default_audio
        self._queue.put(target)

    def stop(self):
        """
        Stop current playback + clear queue
        """
        with self._lock:
            pygame.mixer.music.stop()

        # clear queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except:
                break

        logger.info("Audio stopped & queue cleared")

    def set_volume(self, volume: int):
        volume = max(0, min(100, volume)) / 100
        pygame.mixer.music.set_volume(volume)

    def is_busy(self):
        return pygame.mixer.music.get_busy()

    # =========================
    # WORKER LOOP
    # =========================

    def _worker(self):
        """
        Single audio worker (NO THREAD SPAM)
        """
        while self._running:
            try:
                audio_file = self._queue.get(timeout=0.5)

                if not audio_file:
                    continue

                self._play(audio_file)

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Audio worker error: {e}")

    # =========================
    # PLAYBACK CORE
    # =========================

    def _play(self, audio_file: str):
        with self._lock:
            try:
                if not os.path.exists(audio_file):
                    logger.error(f"Audio not found: {audio_file}")
                    return

                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()

                logger.info(f"Playing: {audio_file}")

                # wait until finish
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)

            except Exception as e:
                logger.error(f"Playback error: {e}")

    # =========================
    # LIFECYCLE
    # =========================

    def shutdown(self):
        self._running = False
        self.stop()
        logger.info("AudioManager shutdown")