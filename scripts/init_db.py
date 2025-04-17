import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Role
from config import config

def init_db():
    app = create_app(config['development'])
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully.")
        
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
    init_db() 