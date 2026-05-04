# core/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time
from sqlalchemy.sql import func
from core.database import Base
import json
from datetime import time

class BellSchedule(Base):
    __tablename__ = 'bell_schedules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    bell_time = Column(Time, nullable=False)
    days_of_week = Column(String(50), default='0,1,2,3,4')  # JSON string
    audio_file = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  # Fixed
    
    def get_days_list(self):
        """Convert days_of_week string to list of integers"""
        if not self.days_of_week:
            return [0, 1, 2, 3, 4]
        return [int(d) for d in self.days_of_week.split(',') if d.strip()]
    
    def set_days_list(self, days_list):
        """Set days_of_week from list of integers"""
        self.days_of_week = ','.join(str(d) for d in days_list)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'time': self.bell_time.strftime('%H:%M') if self.bell_time else None,
            'hour': self.bell_time.hour if self.bell_time else 0,
            'minute': self.bell_time.minute if self.bell_time else 0,
            'days': self.get_days_list(),
            'days_string': self.days_of_week,
            'audio_file': self.audio_file,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f"<BellSchedule(id={self.id}, name='{self.name}', time={self.bell_time})>"

class SpecialSchedule(Base):
    __tablename__ = 'special_schedules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    schedule_date = Column(DateTime, nullable=False)
    bell_time = Column(Time, nullable=False)
    audio_file = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.schedule_date.strftime('%Y-%m-%d'),
            'time': self.bell_time.strftime('%H:%M'),
            'audio_file': self.audio_file,
            'is_active': self.is_active
        }

class BellHistory(Base):
    __tablename__ = 'bell_history'
    
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, nullable=True)
    schedule_name = Column(String(100))
    rang_at = Column(DateTime, server_default=func.now())
    audio_played = Column(String(255))
    status = Column(String(20))  # 'success', 'failed', 'skipped'
    error_message = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<BellHistory(id={self.id}, name='{self.schedule_name}', status='{self.status}')>"