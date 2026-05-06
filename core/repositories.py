# core/repositories.py
from datetime import time
from typing import List, Optional

import logging

from core.database import get_db_manager
from core.models import ScheduleProfile, BellSchedule, BellHistory

logger = logging.getLogger(__name__)


class ScheduleRepository:
    """
    PURE DATA ACCESS LAYER

    Rules:
    - NO business logic
    - NO scheduler/audio
    - ONLY CRUD SQLAlchemy
    """

    def __init__(self):
        self.db = get_db_manager()

    # =========================
    # SESSION
    # =========================

    def _session(self):
        return self.db.get_session()

    # =========================
    # PROFILE
    # =========================

    def create_profile(self, name: str, description: str = None, color: str = "#4CAF50") -> Optional[int]:
        session = self._session()
        try:
            obj = ScheduleProfile(
                name=name,
                description=description,
                color=color,
                is_active=False
            )
            session.add(obj)
            session.commit()
            return obj.id
        except Exception as e:
            session.rollback()
            logger.error(f"create_profile error: {e}")
            return None
        finally:
            session.close()

    def get_profiles(self) -> List[ScheduleProfile]:
        session = self._session()
        try:
            return session.query(ScheduleProfile)\
                .order_by(ScheduleProfile.is_active.desc(), ScheduleProfile.name)\
                .all()
        finally:
            session.close()

    def get_active_profile(self) -> Optional[ScheduleProfile]:
        session = self._session()
        try:
            return session.query(ScheduleProfile)\
                .filter(ScheduleProfile.is_active == True)\
                .first()
        finally:
            session.close()

    def set_active_profile(self, profile_id: int) -> bool:
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
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"set_active_profile error: {e}")
            return False
        finally:
            session.close()

    def delete_profile(self, profile_id: int) -> bool:
        session = self._session()
        try:
            obj = session.query(ScheduleProfile).get(profile_id)
            if not obj:
                return False

            session.delete(obj)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"delete_profile error: {e}")
            return False
        finally:
            session.close()

    # =========================
    # SCHEDULE
    # =========================

    def create_schedule(
        self,
        profile_id: int,
        name: str,
        bell_time: time,
        days: List[int],
        audio_file: str = None
    ) -> Optional[int]:

        session = self._session()
        try:
            obj = BellSchedule(
                profile_id=profile_id,
                name=name,
                bell_time=bell_time,
                days_of_week=",".join(map(str, days)),
                audio_file=audio_file,
                is_active=True
            )
            session.add(obj)
            session.commit()
            return obj.id

        except Exception as e:
            session.rollback()
            logger.error(f"create_schedule error: {e}")
            return None
        finally:
            session.close()

    def update_schedule(self, schedule_id: int, **kwargs) -> bool:
        session = self._session()
        try:
            obj = session.query(BellSchedule).get(schedule_id)
            if not obj:
                return False

            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            session.commit()
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"update_schedule error: {e}")
            return False
        finally:
            session.close()
            
    def get_schedules_by_profile(self, profile_id: int) -> List[BellSchedule]:
        session = self._session()
        try:
            return session.query(BellSchedule)\
                .filter_by(profile_id=profile_id, is_active=True)\
                .order_by(BellSchedule.bell_time)\
                .all()
        finally:
            session.close()

    def get_schedule(self, schedule_id: int) -> Optional[BellSchedule]:
        session = self._session()
        try:
            return session.query(BellSchedule).get(schedule_id)
        finally:
            session.close()

    def delete_schedule(self, schedule_id: int) -> bool:
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

    # =========================
    # HISTORY
    # =========================

    def log_bell_event(
        self,
        schedule_name: str,
        audio_played: str,
        status: str,
        schedule_id: int = None,
        profile_name: str = None,
        error_message: str = None,
    ):
        session = self._session()
        try:
            obj = BellHistory(
                schedule_id=schedule_id,
                schedule_name=schedule_name,
                audio_played=audio_played,
                status=status,
                profile_name=profile_name,
                error_message=error_message
            )
            session.add(obj)
            session.commit()

        except Exception as e:
            session.rollback()
            logger.error(f"log_bell_event error: {e}")
        finally:
            session.close()


# =========================
# SINGLETON
# =========================

_repository = None


def get_repository() -> ScheduleRepository:
    global _repository
    if _repository is None:
        _repository = ScheduleRepository()
    return _repository