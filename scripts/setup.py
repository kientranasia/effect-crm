from app import create_app, db
from app.models import User, Role
from scripts.init_roles import init_roles

def setup():
    app = create_app('development')
    with app.app_context():
        # Initialize database
        db.create_all()
        
        # Initialize roles and permissions
        init_roles()
        
        # Create admin user if it doesn't exist
        admin_role = Role.query.filter_by(name='admin').first()
        admin = User.query.filter_by(email='admin@example.com').first()
        
        if not admin:
            admin = User(
                email='admin@example.com',
                first_name='System',
                last_name='Administrator',
                role_id=admin_role.id,
                is_active=True
            )
            admin.set_password('admin123')  # Change this in production
            db.session.add(admin)
            db.session.commit()
            print("Created admin user")
        else:
            print("Admin user already exists")
        
        print("Setup completed successfully!")

if __name__ == '__main__':
    setup() 