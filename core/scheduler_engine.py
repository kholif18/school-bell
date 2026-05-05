# core/scheduler_engine.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import threading
import time as time_sleep
from zoneinfo import ZoneInfo

from core.schedule_manager import get_schedule_manager
from core.audio_manager import get_audio_manager
from core.config_manager import get_config

logger = logging.getLogger(__name__)

class SchedulerEngine:
    """Bell scheduling engine - with industrial-grade lifecycle management"""
    
    def __init__(self):
        self.schedule_manager = get_schedule_manager()
        self.audio_manager = get_audio_manager()
        self.scheduler = None
        self.running = False
        self.current_profile_id = None
        self._scheduler_lock = threading.RLock()
        self._create_scheduler()
        self._job_lock = threading.RLock()
        self._watchdog = None
        self._watchdog_running = False
    
    def start_watchdog(self):
        """Start watchdog thread to monitor scheduler health"""
        if self._watchdog is not None:
            return
        
        self._watchdog_running = True
        
        def worker():
            while self._watchdog_running:
                threading.Event().wait(15)  # Check every 15 seconds
                if self.running and self.scheduler:
                    try:
                        # Test scheduler health
                        self.scheduler.get_jobs()
                    except Exception as e:
                        logger.error(f"Scheduler watchdog detected failure: {e}")
                        logger.info("Attempting self-healing restart...")
                        with self._scheduler_lock:
                            try:
                                self.scheduler.shutdown(wait=False)
                            except:
                                pass
                            self.running = False
                            self._create_scheduler()
                            self.start()
                        break
        
        self._watchdog = threading.Thread(target=worker, daemon=True)
        self._watchdog.start()
        logger.info("Scheduler watchdog started")

    def stop_watchdog(self):
        """Stop watchdog thread"""
        self._watchdog_running = False
        self._watchdog = None
        
    def _create_scheduler(self):
        """Create new scheduler instance with production defaults"""
        config = get_config()
        tz_str = config.get("scheduler.timezone", "Asia/Jakarta")
        
        self.scheduler = BackgroundScheduler(
            timezone=ZoneInfo(tz_str),
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 30
            }
        )
    
    def _ensure_scheduler(self):
        """Ensure scheduler exists (recreate if needed)"""
        if self.scheduler is None:
            self._create_scheduler()
    
    def _ring_bell(self, schedule):
        """Ring bell for a schedule - protected by job lock"""
        with self._job_lock:
            with self.audio_manager._lock:
                current_time = datetime.now().strftime('%H:%M:%S')
                
                active_profile = self.schedule_manager.get_active_profile()
                profile_name = active_profile.name if active_profile else "Unknown"
                
                logger.info(f"🔔 [{profile_name}] {schedule.name} at {current_time}")

                success = self.audio_manager.play(schedule.audio_file)

                self.schedule_manager.log_bell_event(
                    schedule_name=schedule.name,
                    audio_played=schedule.audio_file or self.audio_manager.default_audio,
                    status="success" if success else "failed",
                    schedule_id=schedule.id,
                    profile_name=profile_name,
                    error_message=None if success else "Audio playback failed"
                )

    def load_jobs_from_active_profile(self):
        """Load schedules from currently active profile only"""
        with self._job_lock:
            self._ensure_scheduler()
            self.scheduler.remove_all_jobs()
            
            active_profile = self.schedule_manager.get_active_profile()
            if not active_profile:
                logger.warning("No active profile found")
                return 0
            
            self.current_profile_id = active_profile.id
            schedules = self.schedule_manager.get_schedules_by_profile(active_profile.id)
            
            if not schedules:
                logger.warning(f"No schedules in profile '{active_profile.name}'")
                return 0

            loaded_count = 0
            for schedule in schedules:
                days = ",".join(str(d) for d in schedule.get_days_list())
                if not days:
                    continue

                trigger = CronTrigger(
                    day_of_week=days,
                    hour=schedule.bell_time.hour,
                    minute=schedule.bell_time.minute
                )

                self.scheduler.add_job(
                    func=self._ring_bell,
                    trigger=trigger,
                    args=[schedule],
                    id=f"bell_{schedule.id}",
                    replace_existing=True,
                    name=f"[{active_profile.name}] {schedule.name}"
                )
                loaded_count += 1
            
            logger.info(f"✓ Loaded {loaded_count} schedules from profile '{active_profile.name}'")
            return loaded_count

    def start(self):
        """Start the scheduler - thread-safe"""
        with self._scheduler_lock:
            if self.running:
                logger.warning("Scheduler already running")
                return False

            # Pastikan ada active profile
            active_profile = self.schedule_manager.get_active_profile()
            if not active_profile:
                logger.error("No active profile found. Please activate a profile first.")
                return False

            self._ensure_scheduler()
            loaded = self.load_jobs_from_active_profile()

            if loaded <= 0:
                logger.error(f"No schedules in profile '{active_profile.name}'. Please add schedules first.")
                return False

            self.scheduler.start()
            self.running = True
            self.start_watchdog()
            logger.info(f"🚀 Scheduler started with {loaded} jobs")
            return True

    def stop(self):
        """Stop the scheduler and ensure clean shutdown"""
        with self._scheduler_lock:
            if not self.running:
                logger.warning("Scheduler not running")
                return False

            self.stop_watchdog()

            try:
                self.scheduler.shutdown(wait=False)
            except Exception as e:
                logger.error(f"Scheduler shutdown error: {e}")

            self.running = False
            self.scheduler = None
            time_sleep.sleep(0.2)
            self._create_scheduler()
            logger.info("⏹️ Scheduler stopped")
            return True
    
    def reload(self):
        """Reload schedules based on current active profile"""
        if self.running:
            with self._job_lock:
                logger.info("Reloading schedules...")
                self.load_jobs_from_active_profile()
                logger.info("✓ Scheduler reloaded")
    
    def switch_profile(self, profile_id: int) -> bool:
        """Switch to a different profile and reload"""
        success = self.schedule_manager.set_active_profile(profile_id)
        if success and self.running:
            self.reload()
        return success
    
    def get_jobs_count(self) -> int:
        if not self.scheduler or not self.running:
            return 0
        return len(self.scheduler.get_jobs())
    
    def get_next_bell_time(self):
        if not self.running or not self.scheduler:
            return None
        jobs = self.scheduler.get_jobs()
        if not jobs:
            return None
        next_run = None
        for job in jobs:
            if hasattr(job, 'next_run_time') and job.next_run_time:
                if next_run is None or job.next_run_time < next_run:
                    next_run = job.next_run_time
        return next_run
    
    def get_status(self) -> dict:
        active_profile = self.schedule_manager.get_active_profile()
        return {
            'running': self.running,
            'active_jobs': self.get_jobs_count(),
            'next_bell': self.get_next_bell_time(),
            'active_profile': {
                'id': active_profile.id,
                'name': active_profile.name,
                'is_active': active_profile.is_active
            } if active_profile else None
        }