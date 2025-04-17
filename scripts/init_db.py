from app import create_app, db
from app.models.user import User
from app.models.customer import Customer

app = create_app('development')

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create test user if not exists
        if not User.query.filter_by(username='admin').first():
            user = User(
                username='admin',
                password='admin123',  # In production, use proper password hashing
                email='admin@example.com'
            )
            db.session.add(user)
            db.session.commit()
            
            # Create some test customers
            customers = [
                Customer(
                    name='Test Customer 1',
                    email='customer1@example.com',
                    phone='123-456-7890',
                    status='Lead',
                    user_id=user.id
                ),
                Customer(
                    name='Test Customer 2',
                    email='customer2@example.com',
                    phone='098-765-4321',
                    status='Active',
                    user_id=user.id
                )
            ]
            db.session.add_all(customers)
            db.session.commit()
            
            print('Database initialized with test data')
        else:
            print('Database already initialized')

if __name__ == '__main__':
    init_db() 