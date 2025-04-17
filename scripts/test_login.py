import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User
from config import config
from flask_login import login_user
from flask import session

def test_login():
    app = create_app(config['development'])
    
    with app.app_context():
        # 1. Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("ERROR: Admin user does not exist in the database.")
            return
        
        print(f"Admin user exists with ID: {admin.id}")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        
        # 2. Test password verification
        test_password = 'kien@123@'
        is_valid = admin.check_password(test_password)
        print(f"Password verification test: {'Success' if is_valid else 'Failed'}")
        
        if not is_valid:
            print("ERROR: Password verification failed. This is the root cause of the login issue.")
            return
        
        # 3. Test login_user function
        with app.test_request_context():
            login_user(admin)
            print(f"Login successful: {session.get('user_id') == admin.id}")
            print(f"Session user_id: {session.get('user_id')}")
            print(f"Admin user_id: {admin.id}")
            
            # 4. Check if user is authenticated
            from flask_login import current_user
            print(f"Current user authenticated: {current_user.is_authenticated}")
            if current_user.is_authenticated:
                print(f"Current user ID: {current_user.id}")
                print(f"Current user username: {current_user.username}")
            else:
                print("ERROR: User is not authenticated after login_user()")

if __name__ == '__main__':
    test_login() 