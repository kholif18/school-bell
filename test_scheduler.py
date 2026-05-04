# test_scheduler.py (fixed import)
import logging
import time
from datetime import datetime as dt
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

def test_scheduler():
    print("\n" + "="*60)
    print("TESTING SCHEDULER ENGINE")
    print("="*60 + "\n")
    
    from core.scheduler_engine import SchedulerEngine
    
    print("1. Creating scheduler engine...")
    engine = SchedulerEngine()
    print("   ✓ Scheduler engine created\n")
    
    print("2. Loading schedules from database...")
    count = engine.load_jobs()
    print(f"   ✓ Loaded {count} job(s)\n")
    
    print("3. Current jobs in scheduler:")
    for job in engine.scheduler.get_jobs():
        print(f"   📋 Job ID: {job.id}")
        print(f"      Name: {job.name}")
        # Fix: Access next_run_time safely
        next_run = job.next_run_time if hasattr(job, 'next_run_time') else 'Not scheduled yet'
        print(f"      Next run: {next_run}")
        print()
    
    print("4. Starting scheduler...")
    engine.start()
    print(f"   ✓ Scheduler running: {engine.running}")
    print(f"   ✓ Active jobs: {engine.get_jobs_count()}\n")
    
    # Wait a moment for scheduler to initialize
    time.sleep(2)
    
    print("5. Scheduler status:")
    status = engine.get_status()
    print(f"   Running: {status['running']}")
    print(f"   Active jobs: {status['active_jobs']}")
    if status['next_bell']:
        print(f"   Next bell: {status['next_bell'].strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("   Next bell: No upcoming bells")
    print()
    
    print("6. Testing manual bell ring (simulate)...")
    from core.schedule_manager import get_schedule_manager
    manager = get_schedule_manager()
    schedules = manager.get_all_schedules()
    if schedules:
        print(f"   Manually ringing: {schedules[0].name}")
        engine._ring_bell(schedules[0])
    print()
    
    print("7. Waiting 3 seconds for audio to play...")
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    print("\n8. Stopping scheduler...")
    engine.stop()
    print("   ✓ Scheduler stopped\n")
    
    print("9. Final status:")
    status = engine.get_status()
    print(f"   Running: {status['running']}")
    print(f"   Active jobs: {status['active_jobs']}")
    print()
    
    print("="*60)
    print("✅ SCHEDULER TEST COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    # First, ensure we have at least one schedule in database
    from core.schedule_manager import get_schedule_manager
    from datetime import time as tm  # Rename to avoid conflict
    
    manager = get_schedule_manager()
    schedules = manager.get_all_schedules()
    
    if not schedules:
        print("No schedules found. Creating a test schedule...")
        manager.add_schedule(
            name="Test Bell",
            bell_time=tm(7, 0),
            days=[0, 1, 2, 3, 4],
            audio_file=None  # Will use default
        )
        print("✓ Test schedule created\n")
    else:
        print(f"✓ Found {len(schedules)} existing schedule(s)\n")
    
    # Run scheduler test
    test_scheduler()