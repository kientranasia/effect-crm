# Partner OS Deployment and Update Guide

This guide provides comprehensive instructions for both initial deployment and platform updates of the Partner OS system.

## Table of Contents
1. [Initial Deployment](#initial-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Platform Updates](#platform-updates)
4. [Common Issues and Solutions](#common-issues-and-solutions)
5. [Database Management](#database-management)
6. [Environment Setup](#environment-setup)

## Initial Deployment

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (recommended)
- Git

### Step 1: Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd effect-crm

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt
```

### Step 2: Configuration
1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update the environment variables in `.env` with your specific configuration.

### Step 3: Database Setup
```bash
# Create instance directory and set permissions
mkdir -p instance
chmod -R 777 instance

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Docker Deployment

### Development Environment

1. Build and start the containers:
```bash
docker-compose up -d
```

2. The application will be available at http://localhost:5000

### Production Environment

#### Option 1: Using docker-compose

1. Create a production environment file:
```bash
cp .env.example .env.production
```

2. Edit `.env.production` with your production settings.

3. Build and start the containers:
```bash
docker-compose -f docker-compose.yml --env-file .env.production up -d
```

#### Option 2: Using Docker directly

1. Build the production image:
```bash
docker build -t effect-crm:latest .
```

2. Run the production container:
```bash
docker run -d -p 5000:5000 \
  --name effect-crm \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/instance:/app/instance \
  -e FLASK_ENV=production \
  -e FLASK_DEBUG=0 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql://user:password@host:5432/dbname \
  -e MAIL_SERVER=smtp.example.com \
  -e MAIL_PORT=587 \
  -e MAIL_USE_TLS=True \
  -e MAIL_USERNAME=your-email@example.com \
  -e MAIL_PASSWORD=your-password \
  -e ANTHROPIC_API_KEY=your-anthropic-key \
  -e OPENAI_API_KEY=your-openai-key \
  effect-crm:latest
```

#### Option 3: Using Docker Swarm

1. Initialize Docker Swarm:
```bash
docker swarm init
```

2. Deploy the stack:
```bash
docker stack deploy -c docker-compose.yml effect-crm
```

### Production Best Practices

1. **Use a reverse proxy**: Set up Nginx or Apache as a reverse proxy in front of the application.
2. **Enable HTTPS**: Configure SSL/TLS certificates for secure communication.
3. **Set up monitoring**: Use tools like Prometheus and Grafana for monitoring.
4. **Implement logging**: Configure proper logging to a centralized system.
5. **Regular backups**: Set up automated database backups.
6. **Use secrets management**: Store sensitive information in Docker secrets or a vault service.

## Platform Updates

### Docker-based Update

1. Pull the latest changes:
```bash
git pull origin main
```

2. Rebuild and restart the containers:
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

3. Apply database migrations:
```bash
docker-compose exec web flask db upgrade
```

## Common Issues and Solutions

### 1. Database Permission Issues
**Symptoms:**
- "unable to open database file" error
- Permission denied errors

**Solution:**
```bash
# Reset database permissions
mkdir -p instance
chmod -R 777 instance
rm -f instance/dev-app.db
touch instance/dev-app.db
chmod 666 instance/dev-app.db
flask db upgrade
```

### 2. Port Conflicts
**Symptoms:**
- "Address already in use" error on port 5000

**Solution:**
1. Change port in `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"
```
2. Or kill the process using port 5000:
```bash
lsof -i :5000
kill -9 <PID>
```

### 3. Migration Errors
**Symptoms:**
- SQLAlchemy errors during migration
- Missing tables or columns

**Solution:**
1. Check migration files in `migrations/versions/`
2. Ensure all model changes are reflected in migrations
3. If needed, reset migrations:
```bash
flask db stamp head
flask db migrate
flask db upgrade
```

### 4. Module Import Errors
**Symptoms:**
- "ModuleNotFoundError" for required packages

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# If specific package is missing
pip install <package-name>
```

## Database Management

### Backup Database
```bash
# Create backup
cp instance/dev-app.db instance/dev-app.db.backup

# Restore from backup
cp instance/dev-app.db.backup instance/dev-app.db
```

### Reset Database
```bash
# Remove existing database
rm -f instance/dev-app.db

# Create new database
touch instance/dev-app.db
chmod 666 instance/dev-app.db

# Reinitialize
flask db upgrade
```

## Environment Setup

### Development Environment
```bash
export FLASK_APP=run.py
export FLASK_ENV=development
export FLASK_CONFIG=development
```

### Production Environment
```bash
export FLASK_APP=run.py
export FLASK_ENV=production
export FLASK_CONFIG=production
```

### Running the Application
```bash
# Development
python run.py

# Production (using gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## Best Practices

1. **Always backup the database before updates**
2. **Test migrations in development before production**
3. **Keep requirements.txt updated**
4. **Use version control for all changes**
5. **Document all configuration changes**
6. **Monitor error logs after updates**
7. **Have a rollback plan ready**

## Troubleshooting

If you encounter issues not covered in this guide:

1. Check the application logs
2. Verify database permissions
3. Ensure all environment variables are set
4. Confirm all dependencies are installed
5. Check for port conflicts
6. Verify migration files are correct
7. Ensure proper file ownership and permissions

For persistent issues, check the GitHub issues or contact the development team. 