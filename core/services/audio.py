# core/services/audio.py

import threading
import queue
import os
import logging
from typing import Optional

import pygame

from core.paths import get_paths
from core.config import get_config

logger = logging.getLogger(__name__)


class AudioService:
    """
    Clean Audio Service (Production Ready)

    Rules:
    - single worker thread
    - queue-based playback
    - pygame safe init
    - NO business logic
    """

    def __init__(self):
        self.paths = get_paths()
        self.config = get_config()

        self._queue = queue.Queue()
        self._lock = threading.RLock()
        self._running = True

        self.audio_dir = self.paths.AUDIO_DIR
        self.default_audio = self.paths.DEFAULT_AUDIO

        self._init_mixer()
        self._ensure_default_audio()

        self._worker = threading.Thread(
            target=self._loop,
            daemon=True
        )
        self._worker.start()

        logger.info("AudioService initialized")

    # =========================
    # INIT
    # =========================

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            logger.error(f"Pygame init failed: {e}")

    def _ensure_default_audio(self):
        if not os.path.exists(self.default_audio):
            logger.warning("Default audio missing")

    # =========================
    # PUBLIC API
    # =========================

    def play(self, file: Optional[str] = None):
        """
        Enqueue audio safely
        """
        target = file if file and os.path.exists(file) else self.default_audio
        self._queue.put(target)

    def stop(self):
        """
        Stop playback + clear queue
        """
        with self._lock:
            pygame.mixer.music.stop()

        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except:
                break

    def set_volume(self, volume: int):
        volume = max(0, min(100, volume)) / 100
        pygame.mixer.music.set_volume(volume)

    def is_busy(self):
        return pygame.mixer.music.get_busy()

    # =========================
    # WORKER LOOP
    # =========================

    def _loop(self):
        while self._running:
            try:
                audio = self._queue.get(timeout=0.5)
                self._play(audio)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Audio loop error: {e}")

    def _play(self, audio_file: str):
        with self._lock:
            try:
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()

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
        logger.info("AudioService shutdown")


# =========================
# SINGLETON
# =========================

_audio_service = None
_lock = threading.Lock()


def get_audio_service():
    global _audio_service
    with _lock:
        if _audio_service is None:
            _audio_service = AudioService()
        return _audio_service