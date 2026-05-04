# core/audio_manager.py
import pygame
import os
import threading
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AudioManager:
    """Thread-safe audio playback manager"""

    def __init__(self):
        pygame.mixer.init()
        self._lock = threading.Lock()
        self._is_playing = False
        self.default_audio = "assets/audio/default_bell.wav"

    def play(self, audio_file: Optional[str] = None) -> bool:
        with self._lock:
            try:
                if self._is_playing:
                    logger.warning("Audio already playing, skipping overlap")
                    return False

                target_file = audio_file if audio_file and os.path.exists(audio_file) else self.default_audio

                if not os.path.exists(target_file):
                    logger.error(f"Audio file not found: {target_file}")
                    return False

                pygame.mixer.music.load(target_file)
                pygame.mixer.music.play()
                self._is_playing = True

                logger.info(f"Playing audio: {target_file}")

                watcher = threading.Thread(target=self._watch_playback_end, daemon=True)
                watcher.start()

                return True

            except Exception as e:
                logger.error(f"Audio playback error: {e}")
                self._is_playing = False
                return False

    def _watch_playback_end(self):
        while pygame.mixer.music.get_busy():
            threading.Event().wait(0.1)  # Small delay to reduce CPU usage
        self._is_playing = False

    def stop(self):
        with self._lock:
            pygame.mixer.music.stop()
            self._is_playing = False
            logger.info("Audio stopped")

    def set_volume(self, volume_percent: int):
        volume = max(0, min(100, volume_percent)) / 100
        pygame.mixer.music.set_volume(volume)
        logger.info(f"Volume set to {volume_percent}%")

    def is_playing(self) -> bool:
        return self._is_playing