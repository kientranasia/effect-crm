#!/bin/bash

# Effect CRM Database Migration Script
# This script helps with database migrations in Docker

# Exit on error
set -e

# Default values
ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"
ACTION="upgrade"
MESSAGE=""

# Display help
function show_help {
    echo "Effect CRM Database Migration Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -e, --env FILE             Environment file to use (default: .env)"
    echo "  -p, --prod                 Use production configuration"
    echo "  -a, --action ACTION        Action to perform: upgrade, downgrade, migrate, stamp (default: upgrade)"
    echo "  -m, --message MESSAGE      Migration message (required for migrate action)"
    echo ""
    echo "Examples:"
    echo "  $0                         Apply all pending migrations"
    echo "  $0 -p                      Apply all pending migrations in production"
    echo "  $0 -a migrate -m \"Add user table\"  Create a new migration"
    echo "  $0 -a downgrade            Roll back the last migration"
    echo "  $0 -a stamp head           Mark the database as up to date"
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
        -a|--action)
            ACTION="$2"
            shift
            shift
            ;;
        -m|--message)
            MESSAGE="$2"
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

# Check if message is provided for migrate action
if [ "$ACTION" = "migrate" ] && [ -z "$MESSAGE" ]; then
    echo "Error: Migration message is required for migrate action."
    echo "Please provide a message with -m or --message."
    exit 1
fi

# Perform the requested action
if [ "$ACTION" = "upgrade" ]; then
    echo "Applying all pending migrations..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec web flask db upgrade
elif [ "$ACTION" = "downgrade" ]; then
    echo "Rolling back the last migration..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec web flask db downgrade
elif [ "$ACTION" = "migrate" ]; then
    echo "Creating a new migration: $MESSAGE..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec web flask db migrate -m "$MESSAGE"
elif [ "$ACTION" = "stamp" ]; then
    echo "Marking the database as up to date..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec web flask db stamp head
else
    echo "Unknown action: $ACTION"
    exit 1
fi

echo "Migration completed successfully!" 