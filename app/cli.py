import click
from flask.cli import with_appcontext
from app import db
from app.models.user import User

def register_commands(app):
    app.cli.add_command(create_test_user)
    app.cli.add_command(init_db)

@click.command('init-db')
@with_appcontext
def init_db():
    """Initialize the database."""
    db.create_all()
    click.echo('Initialized the database.')

@click.command('create-test-user')
@click.option('--email', default='test@example.com', help='Email for the test user')
@click.option('--password', default='password123', help='Password for the test user')
@with_appcontext
def create_test_user(email, password):
    """Create a test user with the given email and password."""
    user = User.query.filter_by(email=email).first()
    if user:
        click.echo(f'User {email} already exists')
        return

    user = User(
        email=email,
        first_name='Test',
        last_name='User'
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    click.echo(f'Created test user {email} with password {password}') 