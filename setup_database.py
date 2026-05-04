# setup_database.py
"""One-time script to setup database with profile system"""
from core.database import get_db_manager
from core.models import Base, ScheduleProfile, BellSchedule
from datetime import time
import os

def setup_database():
    # Remove old database if exists
    if os.path.exists("db/school_bell.db"):
        os.remove("db/school_bell.db")
        print("✓ Removed old database")
    
    # Create new database
    db = get_db_manager()
    db.create_tables()
    print("✓ Created new database with profile schema")
    
    session = db.get_session()
    
    # Create default profile
    general = ScheduleProfile(
        name="General Schedule",
        description="Normal school day schedule (Monday-Friday)",
        is_active=True,
        color="#4CAF50"
    )
    session.add(general)
    
    # Create other example profiles
    profiles = [
        ("Ramadan Schedule", "Ramadan / fasting day schedule", False, "#FF9800"),
        ("Exam Schedule", "Final exam period schedule", False, "#F44336"),
        ("Friday Schedule", "Short Friday schedule", False, "#9C27B0"),
    ]
    
    for name, desc, active, color in profiles:
        profile = ScheduleProfile(name=name, description=desc, is_active=active, color=color)
        session.add(profile)
    
    session.flush()  # Get profile IDs
    
    # Add example schedules for General profile
    general_schedules = [
        ("Morning Assembly", time(7, 0), [0, 1, 2, 3, 4]),
        ("First Period", time(7, 15), [0, 1, 2, 3, 4]),
        ("Break Time", time(9, 45), [0, 1, 2, 3, 4]),
        ("Second Period", time(10, 0), [0, 1, 2, 3, 4]),
        ("Lunch Break", time(12, 0), [0, 1, 2, 3, 4]),
        ("Afternoon Session", time(13, 0), [0, 1, 2, 3, 4]),
        ("Dismissal", time(15, 30), [0, 1, 2, 3, 4]),
    ]
    
    for name, bell_time, days in general_schedules:
        schedule = BellSchedule(
            profile_id=general.id,
            name=name,
            bell_time=bell_time,
            days_of_week=','.join(str(d) for d in days)
        )
        session.add(schedule)
    
    session.commit()
    session.close()
    
    print("\n" + "="*40)
    print("✅ DATABASE SETUP COMPLETE")
    print("="*40)
    print(f"Profiles created: {len(profiles) + 1}")
    print(f"Schedules in General: {len(general_schedules)}")
    print("Active profile: General Schedule")
    
    # Verify
    verify = db.get_session()
    profiles = verify.query(ScheduleProfile).all()
    for p in profiles:
        schedule_count = verify.query(BellSchedule).filter(BellSchedule.profile_id == p.id).count()
        print(f"  📁 {p.name} ({schedule_count} schedules) - {'ACTIVE' if p.is_active else 'inactive'}")
    verify.close()

if __name__ == "__main__":
    setup_database()