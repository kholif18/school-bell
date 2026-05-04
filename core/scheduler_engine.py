# core/scheduler_engine.py (updated for profiles)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from core.schedule_manager import get_schedule_manager
from core.audio_manager import AudioManager

logger = logging.getLogger(__name__)

class SchedulerEngine:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.schedule_manager = get_schedule_manager()
        self.audio_manager = AudioManager()
        self.running = False
        self.current_profile_id = None

    def _ring_bell(self, schedule):
        """Ring bell for a schedule"""
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Get active profile name for logging
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
        if not self.running:
            loaded = self.load_jobs_from_active_profile()
            if loaded > 0:
                self.scheduler.start()
                self.running = True
                logger.info(f"🚀 Scheduler started with {loaded} jobs")
            else:
                logger.warning("No schedules loaded, scheduler not started")
        else:
            logger.warning("Scheduler already running")

    def stop(self):
        if self.running:
            self.scheduler.shutdown(wait=False)
            self.running = False
            logger.info("⏹️ Scheduler stopped")
    
    def reload(self):
        """Reload schedules based on current active profile"""
        if self.running:
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
        return len(self.scheduler.get_jobs())
    
    def get_next_bell_time(self):
        if not self.running:
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
        """Get scheduler status with safe profile access"""
        active_profile = self.schedule_manager.get_active_profile()

        profile_dict = None
        if active_profile:
            profile_dict = {
                'id': active_profile.id,
                'name': active_profile.name,
                'description': active_profile.description,
                'is_active': active_profile.is_active,
                'color': active_profile.color,
            }
        
        return {
            'running': self.running,
            'active_jobs': self.get_jobs_count(),
            'next_bell': self.get_next_bell_time(),
            'active_profile': profile_dict
        }