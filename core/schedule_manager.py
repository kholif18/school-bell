# core/schedule_manager.py

from datetime import time, datetime
from typing import List, Optional
from sqlalchemy import and_, desc
from core.database import get_db_manager
from core.models import ScheduleProfile, BellSchedule, BellHistory
import logging
import threading

logger = logging.getLogger(__name__)

class ScheduleManager:
    def __init__(self):
        self.db = get_db_manager()
    
    def _get_session(self):
        return self.db.get_session()
    
    # ============= Profile CRUD =============
    
    def create_profile(self, name: str, description: str = None, color: str = "#4CAF50") -> Optional[int]:
        """Create new schedule profile"""
        session = self._get_session()
        try:
            profile = ScheduleProfile(
                name=name,
                description=description,
                color=color
            )
            session.add(profile)
            session.commit()
            logger.info(f"Created profile: {name}")
            return profile.id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create profile: {e}")
            return None
        finally:
            session.close()
    
    def get_all_profiles(self) -> List[ScheduleProfile]:
        """Get all profiles"""
        session = self._get_session()
        try:
            return session.query(ScheduleProfile).order_by(
                ScheduleProfile.is_active.desc(),
                ScheduleProfile.name
            ).all()
        finally:
            session.close()
    
    def get_active_profile(self) -> Optional[ScheduleProfile]:
        """Get currently active profile"""
        session = self._get_session()
        try:
            return session.query(ScheduleProfile).filter(
                ScheduleProfile.is_active == True
            ).first()
        finally:
            session.close()
    
    def set_active_profile(self, profile_id: int) -> bool:
        """Set which profile is active"""
        session = self._get_session()
        try:
            # Deactivate all profiles
            session.query(ScheduleProfile).update({ScheduleProfile.is_active: False})
            # Activate selected profile
            profile = session.query(ScheduleProfile).filter(
                ScheduleProfile.id == profile_id
            ).first()
            if profile:
                profile.is_active = True
                session.commit()
                # HAPUS: self._active_profile_id = profile_id
                logger.info(f"Active profile switched to: {profile.name}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to set active profile: {e}")
            return False
        finally:
            session.close()
    
    def delete_profile(self, profile_id: int) -> bool:
        """Delete profile and all its schedules"""
        session = self._get_session()
        try:
            profile = session.query(ScheduleProfile).filter(
                ScheduleProfile.id == profile_id
            ).first()
            if profile:
                session.delete(profile)
                session.commit()
                logger.info(f"Deleted profile: {profile.name}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete profile: {e}")
            return False
        finally:
            session.close()
    
    # ============= Schedule CRUD with Profile =============
    
    def add_schedule(self, profile_id: int, name: str, bell_time: time, 
                    days: List[int] = None, audio_file: str = None) -> Optional[int]:
        """Add new bell schedule to profile"""
        session = self._get_session()
        try:
            if days is None:
                days = [0, 1, 2, 3, 4]
            
            schedule = BellSchedule(
                profile_id=profile_id,
                name=name,
                bell_time=bell_time,
                days_of_week=','.join(str(d) for d in days),
                audio_file=audio_file
            )
            session.add(schedule)
            session.commit()
            logger.info(f"Added schedule '{name}' to profile {profile_id}")
            return schedule.id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add schedule: {e}")
            return None
        finally:
            session.close()
    
    def get_schedules_by_profile(self, profile_id: int = None, include_inactive: bool = False) -> List[BellSchedule]:
        session = self._get_session()
        try:
            if profile_id is None:
                active = session.query(ScheduleProfile).filter(
                    ScheduleProfile.is_active == True
                ).first()
                target_profile_id = active.id if active else None
            else:
                target_profile_id = profile_id

            if not target_profile_id:
                return []

            query = session.query(BellSchedule).filter(
                BellSchedule.profile_id == target_profile_id
            )

            if not include_inactive:
                query = query.filter(BellSchedule.is_active == True)

            return query.order_by(BellSchedule.bell_time).all()
        finally:
            session.close()
    
    def get_schedule_by_id(self, schedule_id: int) -> Optional[BellSchedule]:
        """Get single schedule by ID"""
        session = self._get_session()
        try:
            return session.query(BellSchedule).filter(
                BellSchedule.id == schedule_id
            ).first()
        finally:
            session.close()
    
    def update_schedule(self, schedule_id: int, **kwargs) -> bool:
        """Update schedule fields"""
        session = self._get_session()
        try:
            schedule = session.query(BellSchedule).filter(
                BellSchedule.id == schedule_id
            ).first()
            
            if not schedule:
                return False
            
            if 'bell_time' in kwargs and isinstance(kwargs['bell_time'], str):
                time_parts = kwargs['bell_time'].split(':')
                kwargs['bell_time'] = time(int(time_parts[0]), int(time_parts[1]))
            
            if 'days' in kwargs and isinstance(kwargs['days'], list):
                kwargs['days_of_week'] = ','.join(str(d) for d in kwargs['days'])
                del kwargs['days']
            
            for key, value in kwargs.items():
                if hasattr(schedule, key):
                    setattr(schedule, key, value)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update schedule: {e}")
            return False
        finally:
            session.close()
    
    def delete_schedule(self, schedule_id: int) -> bool:
        """Delete schedule by ID"""
        session = self._get_session()
        try:
            schedule = session.query(BellSchedule).filter(
                BellSchedule.id == schedule_id
            ).first()
            if schedule:
                session.delete(schedule)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def get_schedule_count_by_profile(self, profile_id: int) -> int:
        """Get schedule count for a profile without lazy loading"""
        session = self._get_session()
        try:
            return session.query(BellSchedule).filter(
                BellSchedule.profile_id == profile_id
            ).count()
        finally:
            session.close()
    
    # ============= History =============
    
    def log_bell_event(self, schedule_name: str, audio_played: str, 
                    status: str, error_message: str = None, 
                    schedule_id: int = None, profile_name: str = None):
        """Log bell ringing event with profile context"""
        session = self._get_session()
        try:
            if profile_name is None:
                active_profile = self.get_active_profile()
                profile_name = active_profile.name if active_profile else "Unknown"
            
            history = BellHistory(
                schedule_id=schedule_id,
                profile_name=profile_name,
                schedule_name=schedule_name,
                audio_played=audio_played,
                status=status,
                error_message=error_message
            )
            session.add(history)
            session.commit()
        finally:
            session.close()
    
    def get_recent_history(self, limit: int = 100) -> List[BellHistory]:
        """Get recent bell history"""
        session = self._get_session()
        try:
            return session.query(BellHistory).order_by(
                desc(BellHistory.rang_at)
            ).limit(limit).all()
        finally:
            session.close()

_schedule_manager = None
_schedule_lock = threading.Lock()

def get_schedule_manager() -> ScheduleManager:
    global _schedule_manager
    with _schedule_lock:
        if _schedule_manager is None:
            _schedule_manager = ScheduleManager()
    return _schedule_manager