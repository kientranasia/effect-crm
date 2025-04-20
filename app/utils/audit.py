from flask import request
from app import db
from app.models import AuditLog

def log_audit(user_id, action, entity_type, entity_id, details=None):
    """
    Create an audit log entry
    
    Args:
        user_id (int): ID of the user performing the action
        action (str): The action being performed (create, update, delete, etc.)
        entity_type (str): The type of entity being acted upon (user, role, etc.)
        entity_id (int): The ID of the entity being acted upon
        details (dict, optional): Additional details about the action
    """
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None
    )
    db.session.add(log)
    db.session.commit()
    return log 