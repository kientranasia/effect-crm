import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Permission
from datetime import datetime, UTC

def update_permissions():
    """Update permission descriptions to be more meaningful"""
    app = create_app()
    
    with app.app_context():
        permission_updates = {
            # User Management
            'user_list': 'View list of all system users and their basic information',
            'user_view': 'View detailed user profiles and activity history',
            'user_create': 'Create new user accounts and set initial roles',
            'user_edit': 'Modify existing user profiles, roles, and permissions',
            'user_delete': 'Deactivate or permanently remove user accounts',
            
            # Role Management
            'role_view': 'View available roles and their assigned permissions',
            'role_create': 'Create new roles and assign permissions',
            'role_edit': 'Modify existing roles and their permission sets',
            'role_delete': 'Remove roles from the system',
            
            # Contact Management
            'contact_view': 'View contact details, history, and related interactions',
            'contact_create': 'Add new contacts and their initial information',
            'contact_edit': 'Update contact information and status',
            'contact_delete': 'Remove contacts from the system',
            
            # Organization Management
            'org_view': 'View organization details, contacts, and activity history',
            'org_create': 'Add new organizations and their initial setup',
            'org_edit': 'Update organization information and relationships',
            'org_delete': 'Remove organizations and their associations',
            
            # Project Management
            'project_view': 'View project details, team members, and progress',
            'project_create': 'Create new projects and assign team members',
            'project_edit': 'Update project status, details, and team composition',
            'project_delete': 'Archive or remove projects from the system',
            
            # Interaction Management
            'interaction_view': 'View all interactions with contacts and organizations',
            'interaction_create': 'Record new interactions and schedule follow-ups',
            'interaction_edit': 'Update interaction details and outcomes',
            'interaction_delete': 'Remove incorrect or duplicate interactions',
            
            # Settings Management
            'settings_view': 'View system configuration and preferences',
            'settings_edit': 'Modify system settings and configurations'
        }
        
        for name, description in permission_updates.items():
            permission = Permission.query.filter_by(name=name).first()
            if permission:
                permission.description = description
                permission.updated_at = datetime.now(UTC)
                print(f"Updated permission: {name}")
            else:
                new_permission = Permission(
                    name=name,
                    description=description,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC)
                )
                db.session.add(new_permission)
                print(f"Created new permission: {name}")
        
        db.session.commit()
        print("\nPermission descriptions have been updated successfully!")

if __name__ == '__main__':
    update_permissions() 