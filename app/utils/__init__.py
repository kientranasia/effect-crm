# This file is intentionally empty to make the directory a Python package. 

from flask import current_app, request
from app.models import AuditLog
from app import db
from datetime import datetime
from .audit import log_audit

def log_audit(user_id, action, entity_type, entity_id, details=None):
    """
    Log an audit event to the database.
    
    Args:
        user_id (int): The ID of the user performing the action
        action (str): The type of action (create, update, delete, etc.)
        entity_type (str): The type of entity being affected (user, organization, etc.)
        entity_id (int): The ID of the entity being affected
        details (dict, optional): Additional details about the action
    """
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=request.remote_addr if request else None,
            user_agent=request.user_agent.string if request and request.user_agent else None,
            created_at=datetime.utcnow()
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error logging audit: {str(e)}")
        db.session.rollback()
        return False 

__all__ = ['log_audit'] 