import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Role, Permission
from datetime import datetime, UTC

def setup_roles():
    """Set up Admin and User roles with appropriate permissions"""
    app = create_app()
    
    with app.app_context():
        # First, ensure all necessary permissions exist
        permissions = {
            # User management
            'user_list': 'Can list all users',
            'user_view': 'Can view user profiles',
            'user_create': 'Can create new users',
            'user_edit': 'Can edit user profiles',
            'user_delete': 'Can delete users',
            
            # Role management
            'role_view': 'Can view roles',
            'role_create': 'Can create new roles',
            'role_edit': 'Can edit roles',
            'role_delete': 'Can delete roles',
            
            # Contact management
            'contact_view': 'Can view contacts',
            'contact_create': 'Can create new contacts',
            'contact_edit': 'Can edit contacts',
            'contact_delete': 'Can delete contacts',
            
            # Organization management
            'org_view': 'Can view organizations',
            'org_create': 'Can create new organizations',
            'org_edit': 'Can edit organizations',
            'org_delete': 'Can delete organizations',
            
            # Project management
            'project_view': 'Can view projects',
            'project_create': 'Can create new projects',
            'project_edit': 'Can edit projects',
            'project_delete': 'Can delete projects',
            
            # Interaction management
            'interaction_view': 'Can view interactions',
            'interaction_create': 'Can create new interactions',
            'interaction_edit': 'Can edit interactions',
            'interaction_delete': 'Can delete interactions',
            
            # Settings management
            'settings_view': 'Can view settings',
            'settings_edit': 'Can edit settings'
        }
        
        # Create permissions if they don't exist
        for name, description in permissions.items():
            permission = Permission.query.filter_by(name=name).first()
            if not permission:
                permission = Permission(
                    name=name,
                    description=description,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC)
                )
                db.session.add(permission)
                print(f"Created permission: {name}")
        
        db.session.commit()
        
        # Create Admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(
                name='admin',
                description='Administrator with full system access',
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            db.session.add(admin_role)
            print("Created admin role")
        
        # Create User role
        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            user_role = Role(
                name='user',
                description='Standard user with access to core features',
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            db.session.add(user_role)
            print("Created user role")
        
        db.session.commit()
        
        # Assign all permissions to admin role
        admin_permissions = Permission.query.all()
        admin_role.permissions = admin_permissions
        print("Assigned all permissions to admin role")
        
        # Assign basic permissions to user role
        user_permissions = [
            'contact_view', 'contact_create', 'contact_edit',
            'org_view', 'org_create', 'org_edit',
            'project_view', 'project_create', 'project_edit',
            'interaction_view', 'interaction_create', 'interaction_edit',
            'settings_view'
        ]
        user_role.permissions = Permission.query.filter(Permission.name.in_(user_permissions)).all()
        print("Assigned basic permissions to user role")
        
        db.session.commit()
        print("Role setup completed successfully!")

if __name__ == '__main__':
    setup_roles() 