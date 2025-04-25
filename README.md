# Partner OS

A modern CRM system built with Flask and SQLAlchemy.

## Features

- Contact Management
- Lead Tracking
- Project Management
- Task Management
- User Management with Role-Based Access Control
- API Integration
- Modern UI with Bootstrap 5
- AI-Powered Interaction Analysis (Claude and OpenAI)

## Setup Instructions

### Local Development Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements/dev.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the setup script:
```bash
python scripts/setup.py
```

This will:
- Create the database
- Initialize roles and permissions
- Create an admin user (email: admin@example.com, password: admin123)

5. Run the application:
```bash
python run.py
```

The application will be available at http://localhost:5000

### Docker Development Setup

1. Build and start the containers:
```bash
docker-compose up -d
```

2. The application will be available at http://localhost:5000

### Docker Production Setup

1. Build the production image:
```bash
docker build -t effect-crm:latest .
```

2. Run the production container:
```bash
docker run -d -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql://user:password@host:5432/dbname \
  -e MAIL_SERVER=smtp.example.com \
  -e MAIL_PORT=587 \
  -e MAIL_USE_TLS=True \
  -e MAIL_USERNAME=your-email@example.com \
  -e MAIL_PASSWORD=your-password \
  effect-crm:latest
```

For more detailed production deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Development

- Database migrations: `flask db migrate -m "message"` and `flask db upgrade`
- Run tests: `python -m pytest`
- Format code: `black .`
- Check code style: `flake8`

## API Documentation

The API documentation is available at `/api/docs` when running the application.

## License

MIT License 