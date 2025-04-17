import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User
from config import config

def check_admin_user():
    app = create_app(config['development'])
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"Admin user exists with ID: {admin.id}")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Password hash: {admin.password}")
            
            # Test password verification
            test_password = 'kien@123@'
            is_valid = admin.check_password(test_password)
            print(f"Password verification test: {'Success' if is_valid else 'Failed'}")
        else:
            print("Admin user does not exist in the database.")

if __name__ == '__main__':
    check_admin_user() 