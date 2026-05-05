# core/schedule_manager.py
from datetime import time
from typing import List, Optional
import logging

from core.database import get_db_manager
from core.models import ScheduleProfile, BellSchedule, BellHistory

logger = logging.getLogger(__name__)


class ScheduleManager:
    """
    Clean data manager for:
    - Profiles
    - Schedules
    - History (lightweight)
    """

    def __init__(self):
        self.db = get_db_manager()

    # ======================
    # SESSION HELPER
    # ======================

    def _session(self):
        return self.db.get_session()

    # ======================
    # PROFILE
    # ======================

    def create_profile(self, name: str, description=None, color="#4CAF50"):
        session = self._session()
        try:
            profile = ScheduleProfile(
                name=name,
                description=description,
                color=color,
                is_active=False,
            )
            session.add(profile)
            session.commit()
            return profile.id
        except Exception as e:
            session.rollback()
            logger.error(f"create_profile error: {e}")
            return None
        finally:
            session.close()

    def get_profiles(self):
        session = self._session()
        try:
            return session.query(ScheduleProfile).order_by(
                ScheduleProfile.is_active.desc(),
                ScheduleProfile.name
            ).all()
        finally:
            session.close()

    def get_active_profile(self):
        session = self._session()
        try:
            return session.query(ScheduleProfile).filter_by(is_active=True).first()
        finally:
            session.close()

    def set_active_profile(self, profile_id: int) -> bool:
        """Atomic active profile switch"""
        session = self._session()
        try:
            session.query(ScheduleProfile).update(
                {ScheduleProfile.is_active: False}
            )

            profile = session.query(ScheduleProfile).get(profile_id)
            if not profile:
                return False

            profile.is_active = True
            session.commit()

            logger.info(f"Active profile: {profile.name}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"set_active_profile error: {e}")
            return False
        finally:
            session.close()

    # ======================
    # SCHEDULE
    # ======================

    def add_schedule(self, profile_id: int, name: str, bell_time: time,
                     days: List[int], audio_file: str = None):

        session = self._session()
        try:
            schedule = BellSchedule(
                profile_id=profile_id,
                name=name,
                bell_time=bell_time,
                days_of_week=",".join(map(str, days)),
                audio_file=audio_file,
            )
            session.add(schedule)
            session.commit()
            return schedule.id

        except Exception as e:
            session.rollback()
            logger.error(f"add_schedule error: {e}")
            return None
        finally:
            session.close()

    def get_schedules_by_profile(self, profile_id: int):
        session = self._session()
        try:
            return session.query(BellSchedule).filter_by(
                profile_id=profile_id,
                is_active=True
            ).order_by(BellSchedule.bell_time).all()
        finally:
            session.close()

    def get_schedule(self, schedule_id: int):
        session = self._session()
        try:
            return session.query(BellSchedule).get(schedule_id)
        finally:
            session.close()

    def delete_schedule(self, schedule_id: int):
        session = self._session()
        try:
            obj = session.query(BellSchedule).get(schedule_id)
            if not obj:
                return False

            session.delete(obj)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"delete_schedule error: {e}")
            return False
        finally:
            session.close()

    # ======================
    # HISTORY (LIGHTWEIGHT)
    # ======================

    def log_bell_event(self, schedule_name, audio_played,
                       status, schedule_id=None, profile_name=None):

        session = self._session()
        try:
            history = BellHistory(
                schedule_id=schedule_id,
                schedule_name=schedule_name,
                audio_played=audio_played,
                status=status,
                profile_name=profile_name,
            )
            session.add(history)
            session.commit()

        except Exception as e:
            session.rollback()
            logger.error(f"log_bell_event error: {e}")
        finally:
            session.close()