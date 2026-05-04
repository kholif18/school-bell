# core/audio_manager.py
import pygame
import os
import threading
import logging
from typing import Optional
from core.path_helper import app_path

logger = logging.getLogger(__name__)

class AudioManager:
    """Thread-safe audio playback manager - NON-BLOCKING"""
    
    def __init__(self):
        pygame.mixer.init()
        self._lock = threading.RLock()
        self._is_playing = False
        self.audio_dir = app_path("assets", "audio")
        self.default_audio = app_path("assets", "audio", "default_bell.wav")
        self._ensure_default_bell()

    def _ensure_default_bell(self):
        if not os.path.exists(self.default_audio):
            self._create_default_bell()

    def _create_default_bell(self):
        import wave
        import struct
        import math
        
        os.makedirs(self.audio_dir, exist_ok=True)
        
        try:
            sample_rate = 44100
            duration = 0.5
            frequency = 880
            
            samples = []
            for i in range(int(sample_rate * duration)):
                t = float(i) / sample_rate
                value = int(32767 * math.sin(2 * math.pi * frequency * t))
                if i < 1000:
                    value = int(value * (i / 1000))
                if i > int(sample_rate * duration) - 1000:
                    value = int(value * ((sample_rate * duration - i) / 1000))
                samples.append(struct.pack('<h', value))
            
            with wave.open(self.default_audio, 'w') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                wav.writeframes(b''.join(samples))
            logger.info(f"Created default bell: {self.default_audio}")
        except Exception as e:
            logger.warning(f"Could not create default bell: {e}")

    def play(self, audio_file: Optional[str] = None) -> bool:
        """Play audio - non-blocking, returns immediately"""
        with self._lock:
            if self._is_playing:
                logger.warning("Audio already playing, skipping overlap")
                return False

            target_file = audio_file if audio_file and os.path.exists(audio_file) else self.default_audio

            if not os.path.exists(target_file):
                logger.error(f"Audio file not found: {target_file}")
                return False

            self._is_playing = True

        # Play in separate thread to avoid blocking
        threading.Thread(target=self._play_worker, args=(target_file,), daemon=True).start()
        return True

    def _play_worker(self, target_file):
        """Worker thread for actual audio playback"""
        try:
            pygame.mixer.music.load(target_file)
            pygame.mixer.music.play()
            logger.info(f"Playing audio: {target_file}")

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                threading.Event().wait(0.1)

        except Exception as e:
            logger.error(f"Audio playback error: {e}")

        finally:
            with self._lock:
                self._is_playing = False

    def stop(self):
        """Stop current audio playback"""
        with self._lock:
            pygame.mixer.music.stop()
            self._is_playing = False
            logger.debug("Audio stopped")

    def set_volume(self, volume_percent: int):
        volume = max(0, min(100, volume_percent)) / 100
        pygame.mixer.music.set_volume(volume)
        logger.info(f"Volume set to {volume_percent}%")

    def is_playing(self) -> bool:
        return self._is_playing
    
# ========== SINGLETON ==========
_audio_manager = None
_audio_lock = threading.Lock()

def get_audio_manager() -> AudioManager:
    """Get singleton audio manager instance"""
    global _audio_manager
    with _audio_lock:
        if _audio_manager is None:
            _audio_manager = AudioManager()
    return _audio_manager