# core/schedule_manager.py
from datetime import time, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, desc
from core.database import get_db_manager
from core.models import BellSchedule, SpecialSchedule, BellHistory
import logging

logger = logging.getLogger(__name__)

class ScheduleManager:
    """Handles all schedule-related database operations"""
    
    def __init__(self):
        self.db = get_db_manager()
    
    def _get_session(self):
        """Get database session with context manager support"""
        return self.db.get_session()
    
    # ============= Bell Schedule CRUD =============
    
    def add_schedule(self, name: str, bell_time: time, days: List[int] = None, 
                     audio_file: str = None) -> Optional[int]:
        """Add new bell schedule"""
        session = self._get_session()
        try:
            if days is None:
                days = [0, 1, 2, 3, 4]
            
            schedule = BellSchedule(
                name=name,
                bell_time=bell_time,
                days_of_week=','.join(str(d) for d in days),
                audio_file=audio_file
            )
            session.add(schedule)
            session.commit()
            logger.info(f"Added schedule: {name} at {bell_time}")
            return schedule.id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add schedule: {e}")
            return None
        finally:
            session.close()
    
    def get_all_schedules(self, include_inactive: bool = False) -> List[BellSchedule]:
        """Get all bell schedules"""
        session = self._get_session()
        try:
            query = session.query(BellSchedule)
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
            
            # Handle special field conversions
            if 'bell_time' in kwargs:
                if isinstance(kwargs['bell_time'], str):
                    time_parts = kwargs['bell_time'].split(':')
                    kwargs['bell_time'] = time(int(time_parts[0]), int(time_parts[1]))
            
            if 'days' in kwargs and isinstance(kwargs['days'], list):
                kwargs['days_of_week'] = ','.join(str(d) for d in kwargs['days'])
                del kwargs['days']
            
            for key, value in kwargs.items():
                if hasattr(schedule, key):
                    setattr(schedule, key, value)
            
            session.commit()
            logger.info(f"Updated schedule {schedule_id}")
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
                logger.info(f"Deleted schedule {schedule_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete schedule: {e}")
            return False
        finally:
            session.close()
    
    def toggle_schedule(self, schedule_id: int) -> bool:
        """Toggle schedule active status"""
        session = self._get_session()
        try:
            schedule = session.query(BellSchedule).filter(
                BellSchedule.id == schedule_id
            ).first()
            if schedule:
                schedule.is_active = not schedule.is_active
                session.commit()
                logger.info(f"Toggled schedule {schedule_id} to {schedule.is_active}")
                return True
            return False
        finally:
            session.close()
    
    # ============= Special Schedule CRUD =============
    
    def add_special_schedule(self, name: str, schedule_date: datetime, 
                             bell_time: time, audio_file: str = None) -> Optional[int]:
        """Add special schedule for specific date"""
        session = self._get_session()
        try:
            special = SpecialSchedule(
                name=name,
                schedule_date=schedule_date,
                bell_time=bell_time,
                audio_file=audio_file
            )
            session.add(special)
            session.commit()
            logger.info(f"Added special schedule: {name} on {schedule_date.date()}")
            return special.id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add special schedule: {e}")
            return None
        finally:
            session.close()
    
    def get_special_schedule_for_date(self, date: datetime) -> List[SpecialSchedule]:
        """Get special schedules for specific date"""
        session = self._get_session()
        try:
            date_start = datetime(date.year, date.month, date.day)
            date_end = datetime(date.year, date.month, date.day, 23, 59, 59)
            return session.query(SpecialSchedule).filter(
                and_(
                    SpecialSchedule.schedule_date >= date_start,
                    SpecialSchedule.schedule_date <= date_end,
                    SpecialSchedule.is_active == True
                )
            ).order_by(SpecialSchedule.bell_time).all()
        finally:
            session.close()
    
    def delete_special_schedule(self, schedule_id: int) -> bool:
        """Delete special schedule by ID"""
        session = self._get_session()
        try:
            schedule = session.query(SpecialSchedule).filter(
                SpecialSchedule.id == schedule_id
            ).first()
            if schedule:
                session.delete(schedule)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    # ============= History =============
    
    def log_bell_event(self, schedule_name: str, audio_played: str, 
                       status: str, error_message: str = None, 
                       schedule_id: int = None):
        """Log bell ringing event"""
        session = self._get_session()
        try:
            history = BellHistory(
                schedule_id=schedule_id,
                schedule_name=schedule_name,
                audio_played=audio_played,
                status=status,
                error_message=error_message
            )
            session.add(history)
            session.commit()
            logger.debug(f"Logged bell event: {schedule_name} - {status}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to log bell event: {e}")
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
    
    def get_history_by_date(self, date: datetime) -> List[BellHistory]:
        """Get history for specific date"""
        session = self._get_session()
        try:
            date_start = datetime(date.year, date.month, date.day)
            date_end = datetime(date.year, date.month, date.day, 23, 59, 59)
            return session.query(BellHistory).filter(
                BellHistory.rang_at >= date_start,
                BellHistory.rang_at <= date_end
            ).order_by(BellHistory.rang_at).all()
        finally:
            session.close()

# Singleton instance
_schedule_manager = None

def get_schedule_manager() -> ScheduleManager:
    """Get singleton schedule manager instance"""
    global _schedule_manager
    if _schedule_manager is None:
        _schedule_manager = ScheduleManager()
    return _schedule_manager