# add_sample_history.py
from core.schedule_manager import get_schedule_manager
from datetime import datetime

manager = get_schedule_manager()

# Tambah sample history
samples = [
    ("Morning Assembly", "default", "success", "General Schedule"),
    ("First Period", "custom/bell.mp3", "success", "General Schedule"),
    ("Break Time", "default", "failed", "General Schedule"),
    ("Lunch Break", "default", "success", "General Schedule"),
    ("Afternoon Session", "default", "success", "General Schedule"),
]

for name, audio, status, profile in samples:
    manager.log_bell_event(
        schedule_name=name,
        audio_played=audio,
        status=status,
        profile_name=profile
    )
    print(f"✓ Added: {name} - {status}")

print(f"\nTotal history: {len(manager.get_recent_history(100))}")