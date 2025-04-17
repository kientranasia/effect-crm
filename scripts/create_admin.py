import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User
from config import config

def create_admin_user():
    app = create_app(config['development'])
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists.")
            return
        
        # Create admin user
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('kien@123@')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully.")

if __name__ == '__main__':
    create_admin_user() 