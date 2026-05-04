# test_app_core.py
import time
import logging

# Disable pygame logging for cleaner output
logging.getLogger('pygame').setLevel(logging.WARNING)

def test_app_core():
    print("\n" + "="*60)
    print("TESTING APP CORE")
    print("="*60 + "\n")
    
    from core.app_core import get_app
    
    print("1. Getting app instance...")
    app = get_app()
    print("   ✓ App instance created\n")
    
    print("2. Initializing app...")
    app.initialize()
    print(f"   ✓ Initialized: {app._initialized}\n")
    
    print("3. App status before start:")
    status = app.get_status()
    print(f"   App name: {status['config']['app_name']}")
    print(f"   Version: {status['config']['version']}")
    print(f"   Volume: {status['config']['volume']}%")
    print(f"   Scheduler running: {status['scheduler']['running']}")
    print()
    
    print("4. Starting app...")
    app.start()
    print(f"   ✓ Scheduler running: {app.scheduler.running}")
    print(f"   ✓ Active jobs: {app.scheduler.get_jobs_count()}\n")
    
    print("5. Adding new schedule through app...")
    schedule_id = app.add_schedule(
        name="Lunch Bell",
        hour=12,
        minute=0,
        days=[0, 1, 2, 3, 4],
        audio_file=None
    )
    print(f"   ✓ Schedule added with ID: {schedule_id}\n")
    
    print("6. Reloading schedules...")
    app.reload_schedules()
    print(f"   ✓ Active jobs after reload: {app.scheduler.get_jobs_count()}\n")
    
    print("7. Final status:")
    status = app.get_status()
    print(f"   Scheduler running: {status['scheduler']['running']}")
    print(f"   Active jobs: {status['scheduler']['active_jobs']}")
    if status['scheduler']['next_bell']:
        print(f"   Next bell: {status['scheduler']['next_bell'].strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("8. Stopping app...")
    app.stop()
    print("   ✓ App stopped\n")
    
    print("="*60)
    print("✅ APP CORE TEST COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_app_core()