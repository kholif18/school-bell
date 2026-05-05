# core/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class ScheduleProfile(Base):
    __tablename__ = 'schedule_profiles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=False)
    color = Column(String(20), default="#4CAF50")
    created_at = Column(DateTime, server_default=func.now())
    
    schedules = relationship("BellSchedule", back_populates="profile", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'color': self.color,
        }
    
    def __repr__(self):
        return f"<ScheduleProfile(name='{self.name}', active={self.is_active})>"

class SchedulerState(Base):
    __tablename__ = 'scheduler_state'
    
    id = Column(Integer, primary_key=True, default=1)
    is_running = Column(Boolean, default=False)
    active_jobs = Column(Integer, default=0)
    next_bell = Column(DateTime, nullable=True)
    last_started = Column(DateTime, nullable=True)
    last_stopped = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<SchedulerState(running={self.is_running})>"

class BellSchedule(Base):
    __tablename__ = 'bell_schedules'
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('schedule_profiles.id', ondelete='CASCADE'))
    name = Column(String(100), nullable=False)
    bell_time = Column(Time, nullable=False)
    days_of_week = Column(String(50), default='0,1,2,3,4')
    audio_file = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    profile = relationship("ScheduleProfile", back_populates="schedules")
    
    def get_days_list(self):
        if not self.days_of_week:
            return [0, 1, 2, 3, 4]
        return [int(d) for d in self.days_of_week.split(',') if d.strip()]
    
    def set_days_list(self, days_list):
        self.days_of_week = ','.join(str(d) for d in days_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'name': self.name,
            'time': self.bell_time.strftime('%H:%M') if self.bell_time else None,
            'hour': self.bell_time.hour if self.bell_time else 0,
            'minute': self.bell_time.minute if self.bell_time else 0,
            'days': self.get_days_list(),
            'audio_file': self.audio_file,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f"<BellSchedule(name='{self.name}', time={self.bell_time})>"

class BellHistory(Base):
    __tablename__ = 'bell_history'
    
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, nullable=True)
    profile_name = Column(String(100), nullable=True)
    schedule_name = Column(String(100))
    rang_at = Column(DateTime, server_default=func.now())
    audio_played = Column(String(255))
    status = Column(String(20))
    error_message = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<BellHistory(name='{self.schedule_name}', status='{self.status}')>"