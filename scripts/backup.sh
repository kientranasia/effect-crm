#!/bin/bash

# Effect CRM Database Backup Script
# This script helps with database backups in Docker

# Exit on error
set -e

# Default values
ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Display help
function show_help {
    echo "Effect CRM Database Backup Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -e, --env FILE             Environment file to use (default: .env)"
    echo "  -p, --prod                 Use production configuration"
    echo "  -d, --dir DIR              Backup directory (default: ./backups)"
    echo "  -f, --file FILE            Backup file name (default: backup_TIMESTAMP.sql)"
    echo ""
    echo "Examples:"
    echo "  $0                         Create a backup in the default location"
    echo "  $0 -p                      Create a backup in production"
    echo "  $0 -d /path/to/backups     Create a backup in the specified directory"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
            show_help
            exit 0
            ;;
        -e|--env)
            ENV_FILE="$2"
            shift
            shift
            ;;
        -p|--prod)
            COMPOSE_FILE="docker-compose.prod.yml"
            shift
            ;;
        -d|--dir)
            BACKUP_DIR="$2"
            shift
            shift
            ;;
        -f|--file)
            BACKUP_FILE="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file $ENV_FILE not found."
    echo "Please create it from .env.example: cp .env.example $ENV_FILE"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform the backup
echo "Creating database backup..."
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T db pg_dump -U postgres effect_crm > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_FILE"
    echo "Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
else
    echo "Backup failed!"
    exit 1
fi

# Clean up old backups (keep the 5 most recent)
echo "Cleaning up old backups..."
ls -t "$BACKUP_DIR"/backup_*.sql | tail -n +6 | xargs -r rm

echo "Backup process completed!" 