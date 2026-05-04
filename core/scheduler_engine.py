# core/scheduler_engine.py (fixed - prevent double loading)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from core.schedule_manager import get_schedule_manager
from core.audio_manager import AudioManager

logger = logging.getLogger(__name__)

class SchedulerEngine:
    """Bell scheduling engine"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.schedule_manager = get_schedule_manager()
        self.audio_manager = AudioManager()
        self.running = False

    def _ring_bell(self, schedule):
        """Internal method to ring bell for a schedule"""
        current_time = datetime.now().strftime('%H:%M:%S')
        logger.info(f"🔔 RINGING BELL: {schedule.name} at {current_time}")

        success = self.audio_manager.play(schedule.audio_file)

        self.schedule_manager.log_bell_event(
            schedule_name=schedule.name,
            audio_played=schedule.audio_file or self.audio_manager.default_audio,
            status="success" if success else "failed",
            schedule_id=schedule.id,
            error_message=None if success else "Audio playback failed"
        )

        if success:
            logger.info(f"✓ Bell completed: {schedule.name}")
        else:
            logger.error(f"✗ Bell failed: {schedule.name}")

    def load_jobs(self):
        """Load all schedules from database into scheduler"""
        # Don't remove jobs if scheduler is running to avoid duplication
        if not self.running:
            self.scheduler.remove_all_jobs()
        
        schedules = self.schedule_manager.get_all_schedules(include_inactive=False)
        
        if not schedules:
            logger.warning("No active schedules found in database")
            return 0

        loaded_count = 0
        
        for schedule in schedules:
            # Check if job already exists
            job_id = f"bell_{schedule.id}"
            if self.running and self.scheduler.get_job(job_id):
                logger.debug(f"Job {job_id} already exists, skipping")
                continue
                
            days = ",".join(str(d) for d in schedule.get_days_list())
            
            # Skip if days string is empty
            if not days:
                logger.warning(f"Schedule '{schedule.name}' has no days configured, skipping")
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
                id=job_id,
                replace_existing=True,
                name=schedule.name
            )

            loaded_count += 1
            logger.info(
                f"  📅 Loaded: {schedule.name} | Time: {schedule.bell_time.strftime('%H:%M')} | Days: {days}"
            )
        
        if loaded_count > 0:
            logger.info(f"✓ Loaded {loaded_count} schedule(s) into scheduler")
        return loaded_count

    def start(self):
        """Start the scheduler"""
        if not self.running:
            # Load jobs first without removing existing ones
            schedules = self.schedule_manager.get_all_schedules(include_inactive=False)
            if schedules:
                for schedule in schedules:
                    job_id = f"bell_{schedule.id}"
                    if not self.scheduler.get_job(job_id):
                        days = ",".join(str(d) for d in schedule.get_days_list())
                        if days:
                            trigger = CronTrigger(
                                day_of_week=days,
                                hour=schedule.bell_time.hour,
                                minute=schedule.bell_time.minute
                            )
                            self.scheduler.add_job(
                                func=self._ring_bell,
                                trigger=trigger,
                                args=[schedule],
                                id=job_id,
                                replace_existing=True,
                                name=schedule.name
                            )
                            logger.info(f"  📅 Loaded: {schedule.name}")
                
                self.scheduler.start()
                self.running = True
                logger.info(f"🚀 Scheduler started with {len(schedules)} active schedule(s)")
            else:
                logger.warning("No schedules loaded, scheduler not started")
                logger.info("Use schedule manager to add schedules first")
        else:
            logger.warning("Scheduler already running")

    def stop(self):
        """Stop the scheduler"""
        if self.running:
            self.scheduler.shutdown(wait=False)
            self.running = False
            logger.info("⏹️ Scheduler stopped")
        else:
            logger.warning("Scheduler not running")

    def reload(self):
        """Reload all schedules (useful after database changes)"""
        if self.running:
            logger.info("Reloading schedules...")
            # Remove all existing jobs
            self.scheduler.remove_all_jobs()
            # Reload from database
            schedules = self.schedule_manager.get_all_schedules(include_inactive=False)
            for schedule in schedules:
                days = ",".join(str(d) for d in schedule.get_days_list())
                if days:
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
                        name=schedule.name
                    )
                    logger.info(f"  📅 Loaded: {schedule.name}")
            logger.info("✓ Scheduler reloaded")
        else:
            logger.warning("Scheduler not running, call start() first")

    def get_jobs_count(self) -> int:
        """Get number of active jobs in scheduler"""
        return len(self.scheduler.get_jobs())
    
    def get_next_bell_time(self):
        """Get next bell time (for display purposes)"""
        if not self.running:
            return None
        
        jobs = self.scheduler.get_jobs()
        if not jobs:
            return None
        
        # Get next run time from earliest job
        next_run = None
        for job in jobs:
            # Check different ways to get next run time
            if hasattr(job, 'next_run_time') and job.next_run_time:
                if next_run is None or job.next_run_time < next_run:
                    next_run = job.next_run_time
        
        return next_run
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        return {
            'running': self.running,
            'active_jobs': self.get_jobs_count(),
            'next_bell': self.get_next_bell_time()
        }