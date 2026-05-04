# create_default_bell.py
import wave
import struct
import os
import math

def create_default_bell():
    """Create a simple default bell sound (beep)"""
    filename = "assets/audio/default_bell.wav"
    
    # Create directory if not exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Parameters
    sample_rate = 44100
    duration = 0.5  # seconds
    frequency = 880  # Hz (A5 note)
    
    # Generate sine wave
    samples = []
    for i in range(int(sample_rate * duration)):
        t = float(i) / sample_rate
        # Simple sine wave
        value = int(32767 * math.sin(2 * math.pi * frequency * t))
        # Add fade in/out to avoid popping
        if i < 1000:
            value = int(value * (i / 1000))
        if i > int(sample_rate * duration) - 1000:
            value = int(value * ((sample_rate * duration - i) / 1000))
        samples.append(struct.pack('<h', value))
    
    # Write WAV file
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 2 bytes per sample
        wav.setframerate(sample_rate)
        wav.writeframes(b''.join(samples))
    
    print(f"✓ Default bell sound created at: {filename}")
    print(f"  Duration: {duration}s, Frequency: {frequency}Hz")

if __name__ == "__main__":
    create_default_bell()