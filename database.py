#!/usr/bin/env python3
"""
Database models and handlers for district activities
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, Boolean, Index, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()


class Activity(Base):
    """Activity model for storing district events"""
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    location = Column(String(200), nullable=False, index=True)
    severity = Column(String(20), default='low', index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    reported_by = Column(String(100), nullable=False)
    reporter_id = Column(Integer, nullable=False, index=True)
    status = Column(String(20), default='active')  # active, resolved, archived
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_verified = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)

    # Indexes for performance
    __table_args__ = (
        Index('ix_created_at_category', 'created_at', 'category'),
        Index('ix_location_severity', 'location', 'severity'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'description': self.description,
            'location': self.location,
            'severity': self.severity,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'reported_by': self.reported_by,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'is_verified': self.is_verified,
            'view_count': self.view_count
        }


class ActivityUpdate(Base):
    """Track updates/comments on activities"""
    __tablename__ = 'activity_updates'

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, nullable=False, index=True)
    update_text = Column(String(500), nullable=False)
    updated_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class DatabaseHandler:
    """Handle all database operations"""

    def __init__(self, db_url: Optional[str] = None):
        if db_url is None:
            # Use environment variable or default to SQLite
            db_url = os.getenv('DATABASE_URL', 'sqlite:///activities.db')

        # Handle postgresql:// → postgresql+psycopg2://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)

        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(self.engine)
        logger.info("Database initialized")

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    def add_activity(self, category: str, description: str, location: str,
                     severity: str = 'low', reported_by: str = 'Anonymous',
                     reporter_id: int = 0, latitude: Optional[float] = None,
                     longitude: Optional[float] = None) -> Activity:
        """Add new activity to database"""
        session = self.get_session()
        try:
            activity = Activity(
                category=category,
                description=description,
                location=location,
                severity=severity,
                reported_by=reported_by,
                reporter_id=reporter_id,
                latitude=latitude,
                longitude=longitude
            )
            session.add(activity)
            session.commit()
            logger.info(f"Activity added: {activity.id} - {category} at {location}")
            return activity
        finally:
            session.close()

    def get_activities(self, limit: int = 50, category: Optional[str] = None,
                      location: Optional[str] = None, hours: int = 24,
                      severity: Optional[str] = None) -> List[Activity]:
        """Get activities with optional filters"""
        session = self.get_session()
        try:
            query = session.query(Activity)

            # Filter by time
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            query = query.filter(Activity.created_at >= cutoff_time)

            # Optional filters
            if category:
                query = query.filter(Activity.category == category)
            if location:
                query = query.filter(Activity.location.ilike(f"%{location}%"))
            if severity:
                query = query.filter(Activity.severity == severity)

            # Order by creation time
            activities = query.order_by(desc(Activity.created_at)).limit(limit).all()
            return activities
        finally:
            session.close()

    def get_activity_by_id(self, activity_id: int) -> Optional[Activity]:
        """Get activity by ID"""
        session = self.get_session()
        try:
            return session.query(Activity).filter(Activity.id == activity_id).first()
        finally:
            session.close()

    def get_stats(self, hours: int = 24) -> Dict:
        """Get activity statistics"""
        session = self.get_session()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            cutoff_week = datetime.utcnow() - timedelta(days=7)

            # 24h stats
            activities_24h = session.query(Activity).filter(
                Activity.created_at >= cutoff_time
            ).all()

            # Week stats
            activities_week = session.query(Activity).filter(
                Activity.created_at >= cutoff_week
            ).all()

            # Category breakdown
            category_stats = {}
            for activity in activities_24h:
                category_stats[activity.category] = category_stats.get(activity.category, 0) + 1

            # Severity breakdown
            severity_stats = {}
            for activity in activities_24h:
                severity_stats[activity.severity] = severity_stats.get(activity.severity, 0) + 1

            # Top locations
            location_stats = {}
            for activity in activities_24h:
                location_stats[activity.location] = location_stats.get(activity.location, 0) + 1
            top_locations = sorted(location_stats.items(), key=lambda x: x[1], reverse=True)

            return {
                'total_24h': len(activities_24h),
                'total_week': len(activities_week),
                'incidents_24h': sum(1 for a in activities_24h if a.category == 'incident'),
                'events_24h': sum(1 for a in activities_24h if a.category == 'event'),
                'emergencies_24h': sum(1 for a in activities_24h if a.category == 'emergency'),
                'critical_week': sum(1 for a in activities_week if a.severity == 'critical'),
                'category_breakdown': category_stats,
                'severity_24h': severity_stats,
                'top_areas': top_locations
            }
        finally:
            session.close()

    def update_activity_status(self, activity_id: int, status: str, updated_by: str = 'admin'):
        """Update activity status"""
        session = self.get_session()
        try:
            activity = session.query(Activity).filter(Activity.id == activity_id).first()
            if activity:
                activity.status = status
                activity.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Activity {activity_id} status updated to {status}")
        finally:
            session.close()

    def add_activity_update(self, activity_id: int, update_text: str, updated_by: str = 'system'):
        """Add update/comment to activity"""
        session = self.get_session()
        try:
            update = ActivityUpdate(
                activity_id=activity_id,
                update_text=update_text,
                updated_by=updated_by
            )
            session.add(update)
            session.commit()
        finally:
            session.close()

    def get_activity_updates(self, activity_id: int) -> List[ActivityUpdate]:
        """Get updates for specific activity"""
        session = self.get_session()
        try:
            return session.query(ActivityUpdate).filter(
                ActivityUpdate.activity_id == activity_id
            ).order_by(desc(ActivityUpdate.created_at)).all()
        finally:
            session.close()

    def get_trending_locations(self, limit: int = 10) -> List[tuple]:
        """Get trending locations by activity count"""
        session = self.get_session()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            from sqlalchemy import func

            trending = session.query(
                Activity.location,
                func.count(Activity.id).label('count')
            ).filter(
                Activity.created_at >= cutoff_time
            ).group_by(Activity.location).order_by(
                desc(func.count(Activity.id))
            ).limit(limit).all()

            return trending
        finally:
            session.close()


# Global database handler instance
_db_handler: Optional[DatabaseHandler] = None


def get_db_handler() -> DatabaseHandler:
    """Get global database handler instance"""
    global _db_handler
    if _db_handler is None:
        _db_handler = DatabaseHandler()
    return _db_handler


def init_db():
    """Initialize database"""
    get_db_handler().init_db()


def add_activity(category: str, description: str, location: str, **kwargs) -> Activity:
    """Add activity"""
    return get_db_handler().add_activity(category, description, location, **kwargs)


def get_activities(limit: int = 50, **kwargs) -> List[Activity]:
    """Get activities"""
    return get_db_handler().get_activities(limit=limit, **kwargs)


def get_activity(activity_id: int) -> Optional[Activity]:
    """Get single activity"""
    return get_db_handler().get_activity_by_id(activity_id)


def get_stats() -> Dict:
    """Get statistics"""
    return get_db_handler().get_stats()


def update_activity(activity_id: int, status: str, **kwargs):
    """Update activity"""
    get_db_handler().update_activity_status(activity_id, status, **kwargs)


def add_update(activity_id: int, update_text: str, updated_by: str = 'system'):
    """Add activity update"""
    get_db_handler().add_activity_update(activity_id, update_text, updated_by)


def get_updates(activity_id: int) -> List[ActivityUpdate]:
    """Get activity updates"""
    return get_db_handler().get_activity_updates(activity_id)
