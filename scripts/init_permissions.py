from app import create_app, db
from app.models import Permission, Role
from datetime import datetime
from sqlalchemy.exc import IntegrityError

def init_permissions():
    """Initialize the default permissions"""
    print("Starting permissions initialization...")
    
    app = create_app()
    
    with app.app_context():
        # Define default permissions
        default_permissions = {
            # User management permissions
            'user_list': 'Can list all user accounts',
            'user_view': 'Can view user profiles',
            'user_create': 'Can create new users',
            'user_edit': 'Can edit user profiles',
            'user_delete': 'Can delete users',
            
            # Account management permissions
            'account_list': 'Can list all accounts',
            'account_view': 'Can view account details',
            'account_create': 'Can create new accounts',
            'account_edit': 'Can edit account details',
            'account_delete': 'Can delete accounts',
            'account_approve': 'Can approve new accounts',
            'account_suspend': 'Can suspend accounts',
            
            # Role management permissions
            'role_view': 'Can view roles',
            'role_create': 'Can create new roles',
            'role_edit': 'Can edit roles',
            'role_delete': 'Can delete roles',
            
            # Customer management permissions
            'customer_view': 'Can view customers',
            'customer_create': 'Can create new customers',
            'customer_edit': 'Can edit customers',
            'customer_delete': 'Can delete customers',
            
            # Lead management permissions
            'lead_view': 'Can view leads',
            'lead_create': 'Can create new leads',
            'lead_edit': 'Can edit leads',
            'lead_delete': 'Can delete leads',
            
            # Settings management permissions
            'settings_view': 'Can view system settings',
            'settings_edit': 'Can edit system settings'
        }
        
        # Create permissions
        created_permissions = []
        for name, description in default_permissions.items():
            permission = Permission.query.filter_by(name=name).first()
            if not permission:
                permission = Permission(
                    name=name,
                    description=description,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(permission)
                print(f"Created permission: {name}")
            created_permissions.append(permission)
        
        # Commit the permissions
        db.session.commit()
        
        # Assign all permissions to admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            for permission in created_permissions:
                if permission not in admin_role.assigned_permissions:
                    admin_role.assigned_permissions.append(permission)
            try:
                db.session.commit()
                print("\nAssigned all permissions to admin role")
            except IntegrityError:
                db.session.rollback()
                print("Some permissions were already assigned to admin role")
        
        # Assign basic permissions to user role
        user_role = Role.query.filter_by(name='user').first()
        if user_role:
            basic_permissions = [
                'customer_view', 'customer_create', 'customer_edit',
                'lead_view', 'lead_create', 'lead_edit',
                'account_view'  # Users can view their own account details
            ]
            for perm_name in basic_permissions:
                perm = Permission.query.filter_by(name=perm_name).first()
                if perm and perm not in user_role.assigned_permissions:
                    user_role.assigned_permissions.append(perm)
            try:
                db.session.commit()
                print("Assigned basic permissions to user role")
            except IntegrityError:
                db.session.rollback()
                print("Some permissions were already assigned to user role")
        
        print("\nPermissions initialization completed successfully!")

if __name__ == '__main__':
    init_permissions() 