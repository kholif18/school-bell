# core/audio_engine.py
import pygame
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioEngine:
    def __init__(self):
        pygame.mixer.init()
        self.default_bell_file = "assets/audio/default_bell.wav"
        self.current_playing = None
    
    def play_audio(self, audio_file):
        """Play specific audio file"""
        try:
            if os.path.exists(audio_file):
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                logger.info(f"Playing audio: {audio_file}")
                return True
            else:
                logger.warning(f"Audio file not found: {audio_file}")
                self.play_default_bell()
                return False
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
    
    def play_default_bell(self):
        """Play default bell sound"""
        if os.path.exists(self.default_bell_file):
            self.play_audio(self.default_bell_file)
        else:
            # Create a simple beep if no audio file exists
            self._play_system_beep()
    
    def _play_system_beep(self):
        """Fallback system beep"""
        try:
            import sys
            if sys.platform == "win32":
                import winsound
                winsound.Beep(880, 1000)  # Frequency: 880Hz, Duration: 1000ms
            else:
                print('\a')  # ASCII bell
        except:
            logger.warning("Could not play system beep")
    
    def stop_audio(self):
        """Stop current audio"""
        pygame.mixer.music.stop()
    
    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        pygame.mixer.music.set_volume(volume)