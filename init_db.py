from app import create_app, db
from app.models import User, Role
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
import sys

def init_db():
    """Initialize the database with required tables and admin user."""
    print("Starting database initialization...")
    
    # Create application context
    app = create_app()
    
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        print("Dropped all existing tables")
        
        # Create all tables
        db.create_all()
        print("Created all tables")
        
        # Create admin role
        admin_role = Role(
            name='admin',
            description='Administrator with full access',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(admin_role)
        db.session.commit()
        print("Created admin role")
        
        # Create admin user
        admin = User(
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            first_name='Admin',
            last_name='User',
            is_active=True,
            is_admin=True,
            is_approved=True,
            created_at=datetime.utcnow(),
            role_id=admin_role.id
        )
        db.session.add(admin)
        db.session.commit()
        print("Created admin user")
        
        # Create user role
        user_role = Role(
            name='user',
            description='Regular user',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(user_role)
        db.session.commit()
        print("Created user role")
        
        print("\nDatabase initialization completed successfully!")
        print("\nAdmin credentials:")
        print("Username: admin")
        print("Password: admin123")

if __name__ == '__main__':
    init_db() 