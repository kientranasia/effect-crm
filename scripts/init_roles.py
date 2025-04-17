import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Role
from config import config

def init_roles_and_admin():
    app = create_app(config['development'])
    with app.app_context():
        # Create roles if they don't exist
        roles = {
            'admin': 'Full system administrator access',
            'manager': 'Can manage all CRM data and view reports',
            'user': 'Can view and manage assigned CRM data'
        }
        
        for role_name, description in roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=description)
                db.session.add(role)
                print(f"Created role: {role_name}")
        
        db.session.commit()
        
        # Create admin user if it doesn't exist
        admin_role = Role.query.filter_by(name='admin').first()
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                first_name='System',
                last_name='Administrator',
                role_id=admin_role.id,
                is_active=True
            )
            admin.set_password('kien@123@')
            db.session.add(admin)
            db.session.commit()
            print("Created admin user")
        else:
            print("Admin user already exists")

if __name__ == '__main__':
    init_roles_and_admin() 