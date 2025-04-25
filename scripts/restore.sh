#!/bin/bash

# Partner OS Database Restore Script
# This script helps with database restoration in Docker

# Exit on error
set -e

# Default values
ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"
BACKUP_FILE=""

# Display help
function show_help {
    echo "Partner OS Database Restore Script"
    echo ""
    echo "Usage: $0 [options] BACKUP_FILE"
    echo ""
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -e, --env FILE             Environment file to use (default: .env)"
    echo "  -p, --prod                 Use production configuration"
    echo ""
    echo "Examples:"
    echo "  $0 backup_20230101_120000.sql  Restore from the specified backup file"
    echo "  $0 -p backup_20230101_120000.sql  Restore in production"
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
        *)
            BACKUP_FILE="$1"
            shift
            ;;
    esac
done

# Check if backup file is provided
if [ -z "$BACKUP_FILE" ]; then
    echo "Error: Backup file is required."
    show_help
    exit 1
fi

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file $ENV_FILE not found."
    echo "Please create it from .env.example: cp .env.example $ENV_FILE"
    exit 1
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file $BACKUP_FILE not found."
    exit 1
fi

# Confirm restoration
echo "WARNING: This will restore the database from $BACKUP_FILE."
echo "This operation will overwrite the current database."
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restoration cancelled."
    exit 1
fi

# Perform the restoration
echo "Restoring database from $BACKUP_FILE..."
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T db psql -U postgres -d effect_crm -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T db psql -U postgres effect_crm < "$BACKUP_FILE"

# Check if restoration was successful
if [ $? -eq 0 ]; then
    echo "Restoration completed successfully!"
else
    echo "Restoration failed!"
    exit 1
fi

echo "Database restoration process completed!" 