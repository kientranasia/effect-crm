from app import create_app, db
import os

app = create_app(os.getenv('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 