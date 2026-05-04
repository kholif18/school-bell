# test_database.py
from datetime import time, datetime
from core.database import get_db_manager
from core.schedule_manager import get_schedule_manager
import logging

# Setup logging to see details
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

def test_database():
    print("\n" + "="*50)
    print("TESTING DATABASE LAYER")
    print("="*50 + "\n")
    
    # Initialize database
    print("1. Initializing database...")
    db = get_db_manager()
    db.create_tables()
    print("   ✓ Database tables created")
    
    # Get schedule manager
    manager = get_schedule_manager()
    
    # Add test schedule
    print("\n2. Adding test schedule...")
    schedule_id = manager.add_schedule(
        name="Morning Bell",
        bell_time=time(7, 0),
        days=[0, 1, 2, 3, 4],  # Monday to Friday
        audio_file="assets/audio/morning.wav"
    )
    print(f"   ✓ Added schedule with ID: {schedule_id}")
    
    # Add another schedule
    schedule_id2 = manager.add_schedule(
        name="Afternoon Bell",
        bell_time=time(13, 0),
        days=[0, 1, 2, 3, 4],
        audio_file="assets/audio/afternoon.wav"
    )
    print(f"   ✓ Added schedule with ID: {schedule_id2}")
    
    # Get all schedules
    print("\n3. Retrieving all schedules...")
    schedules = manager.get_all_schedules()
    print(f"   ✓ Found {len(schedules)} active schedules:")
    for s in schedules:
        print(f"      - {s.name}: {s.bell_time} on days {s.get_days_list()} (active: {s.is_active})")
    
    # Test schedule retrieval
    print("\n4. Testing schedule retrieval by ID...")
    retrieved = manager.get_schedule_by_id(schedule_id)
    if retrieved:
        print(f"   ✓ Retrieved: {retrieved.name} at {retrieved.bell_time}")
    
    # Test schedule update
    print("\n5. Testing schedule update...")
    success = manager.update_schedule(schedule_id, name="Morning Assembly Bell")
    if success:
        updated = manager.get_schedule_by_id(schedule_id)
        print(f"   ✓ Updated name to: {updated.name}")
    
    # Test toggle schedule
    print("\n6. Testing toggle schedule...")
    manager.toggle_schedule(schedule_id2)
    schedules_after_toggle = manager.get_all_schedules()
    print(f"   ✓ Active schedules after toggle: {len(schedules_after_toggle)}")
    
    # Test history logging
    print("\n7. Testing bell history logging...")
    manager.log_bell_event(
        schedule_name="Test Bell",
        audio_played="default",
        status="success",
        schedule_id=schedule_id
    )
    manager.log_bell_event(
        schedule_name="Failed Bell",
        audio_played="custom.wav",
        status="failed",
        error_message="Audio file not found"
    )
    print("   ✓ Logged test events")
    
    # Get recent history
    print("\n8. Retrieving recent history...")
    history = manager.get_recent_history(limit=10)
    print(f"   ✓ Found {len(history)} history entries:")
    for h in history[:3]:  # Show last 3
        print(f"      - {h.schedule_name}: {h.status} at {h.rang_at}")
    
    # Test special schedule
    print("\n9. Testing special schedule...")
    special_id = manager.add_special_schedule(
        name="Holiday Bell",
        schedule_date=datetime(2026, 12, 25),
        bell_time=time(10, 0),
        audio_file="assets/audio/holiday.wav"
    )
    print(f"   ✓ Added special schedule with ID: {special_id}")
    
    # Test delete
    print("\n10. Testing delete schedule...")
    manager.delete_schedule(schedule_id2)
    remaining = manager.get_all_schedules()
    print(f"    ✓ Remaining schedules: {len(remaining)}")
    
    print("\n" + "="*50)
    print("✅ ALL DATABASE TESTS PASSED!")
    print("="*50 + "\n")
    
    # Show database file info
    import os
    if os.path.exists("db/school_bell.db"):
        size = os.path.getsize("db/school_bell.db")
        print(f"📁 Database created at: db/school_bell.db")
        print(f"📊 File size: {size:,} bytes")
        print(f"📅 Last modified: {datetime.fromtimestamp(os.path.getmtime('db/school_bell.db'))}")

if __name__ == "__main__":
    test_database()