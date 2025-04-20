import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Role, Permission
from config import config

def init_roles():
    app = create_app('development')
    with app.app_context():
        # Create permissions
        permissions = {
            'admin': 'Full administrative access',
            'manage_users': 'Manage user accounts',
            'manage_roles': 'Manage roles and permissions',
            'manage_contacts': 'Manage contacts and leads',
            'manage_interactions': 'Manage interactions',
            'manage_projects': 'Manage projects',
            'view_reports': 'View reports and analytics'
        }
        
        for name, description in permissions.items():
            permission = Permission.query.filter_by(name=name).first()
            if not permission:
                permission = Permission(name=name, description=description)
                db.session.add(permission)
        
        db.session.commit()
        
        # Create roles
        roles = {
            'admin': {
                'description': 'Administrator with full access',
                'permissions': list(permissions.keys())
            },
            'manager': {
                'description': 'Manager with elevated privileges',
                'permissions': ['manage_contacts', 'manage_interactions', 'manage_projects', 'view_reports']
            },
            'user': {
                'description': 'Standard user',
                'permissions': ['manage_contacts', 'manage_interactions', 'view_reports']
            }
        }
        
        for role_name, role_data in roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=role_data['description'])
                db.session.add(role)
                db.session.commit()
                
                # Assign permissions to role
                for perm_name in role_data['permissions']:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        role.permissions.append(permission)
        
        db.session.commit()
        print("Roles and permissions initialized successfully!")

if __name__ == '__main__':
    init_roles() 