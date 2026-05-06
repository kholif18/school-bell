import threading
import queue
import os
import logging
import time
from typing import Optional

import pygame

from core.paths import get_paths
from core.config import get_config

logger = logging.getLogger(__name__)


class AudioService:

    def __init__(self):
        self.paths = get_paths()
        self.config = get_config()

        self.audio_dir = self.paths.AUDIO_DIR
        self.default_audio = self.paths.DEFAULT_AUDIO

        self._queue = queue.Queue()
        self._running = True
        self._stop_flag = False
        self._lock = threading.RLock()

        self._init_mixer()
        self._ensure_default_audio()

        self._worker = threading.Thread(target=self._loop, daemon=True)
        self._worker.start()

        logger.info("AudioService initialized")

    # =====================================================
    # INIT
    # =====================================================

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            logger.error(f"Pygame mixer init failed: {e}")

    def _ensure_default_audio(self):
        if not os.path.exists(self.default_audio):
            logger.warning("Default audio missing")

    # =====================================================
    # PUBLIC API
    # =====================================================

    def play(self, file: Optional[str] = None):
        target = file if file and os.path.exists(file) else self.default_audio

        # interrupt current playback
        self.stop()

        self._stop_flag = False
        self._queue.put(target)

    def stop(self):
        self._stop_flag = True

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except:
            pass

        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except:
                break

    def set_volume(self, volume: int):
        volume = max(0, min(100, volume)) / 100
        pygame.mixer.music.set_volume(volume)

    def is_busy(self):
        try:
            return pygame.mixer.music.get_busy()
        except:
            return False

    # =====================================================
    # WORKER
    # =====================================================

    def _loop(self):
        while self._running:
            try:
                audio = self._queue.get(timeout=0.2)
                self._play(audio)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Audio worker error: {e}")

    def _play(self, audio_file):
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if self._stop_flag:
                    pygame.mixer.music.stop()
                    break

                time.sleep(0.05)

        except Exception as e:
            logger.error(f"Playback error: {e}")

    # =====================================================
    # CLOSE
    # =====================================================

    def shutdown(self):
        self._running = False
        self.stop()
        logger.info("AudioService shutdown")


_audio_service = None
_lock = threading.Lock()


def get_audio_service():
    global _audio_service
    with _lock:
        if _audio_service is None:
            _audio_service = AudioService()
        return _audio_service