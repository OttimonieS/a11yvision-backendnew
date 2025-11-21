from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any
import models


def log_activity(
    db: Session,
    user_id: str,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """
    Log user activity to the database

    Args:
        db: Database session
        user_id: ID of the user performing the action
        action: Action being performed (e.g., 'login', 'scan_created', 'settings_updated')
        resource_type: Type of resource (e.g., 'scan', 'settings', 'api_key')
        resource_id: ID of the resource being acted upon
        details: Additional context as JSON
        ip_address: IP address of the request
        user_agent: User agent string
    """
    activity = models.ActivityLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.utcnow()
    )
    db.add(activity)
    db.commit()
    return activity


def get_user_activities(
    db: Session,
    user_id: str,
    limit: int = 100,
    offset: int = 0,
    action_filter: Optional[str] = None
):
    """
    Retrieve user activity logs

    Args:
        db: Database session
        user_id: ID of the user
        limit: Maximum number of records to return
        offset: Number of records to skip
        action_filter: Filter by specific action type
    """
    query = db.query(models.ActivityLog).filter(
        models.ActivityLog.user_id == user_id
    )

    if action_filter:
        query = query.filter(models.ActivityLog.action == action_filter)

    query = query.order_by(models.ActivityLog.created_at.desc())

    return query.offset(offset).limit(limit).all()


def get_all_activities(
    db: Session,
    limit: int = 100,
    offset: int = 0,
    action_filter: Optional[str] = None
):
    """
    Retrieve all activity logs (admin function)

    Args:
        db: Database session
        limit: Maximum number of records to return
        offset: Number of records to skip
        action_filter: Filter by specific action type
    """
    query = db.query(models.ActivityLog)

    if action_filter:
        query = query.filter(models.ActivityLog.action == action_filter)

    query = query.order_by(models.ActivityLog.created_at.desc())

    return query.offset(offset).limit(limit).all()


def get_activity_stats(db: Session, user_id: Optional[str] = None):
    """
    Get activity statistics

    Args:
        db: Database session
        user_id: Optional user ID to filter by
    """
    from sqlalchemy import func

    query = db.query(
        models.ActivityLog.action,
        func.count(models.ActivityLog.id).label('count')
    )

    if user_id:
        query = query.filter(models.ActivityLog.user_id == user_id)

    results = query.group_by(models.ActivityLog.action).all()

    return {action: count for action, count in results}
