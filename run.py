import os
from app import create_app, db
from config import config

app = create_app('default')

if __name__ == '__main__':
    # Ensure instance directory exists
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, port=5000) 