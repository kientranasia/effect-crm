#!/bin/bash

# Partner OS Database Initialization Script
# This script helps with initializing the database in Docker

# Exit on error
set -e

# Default values
ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"
SEED_DATA=false

# Display help
function show_help {
    echo "Partner OS Database Initialization Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -e, --env FILE             Environment file to use (default: .env)"
    echo "  -p, --prod                 Use production configuration"
    echo "  -s, --seed                 Seed the database with example data"
    echo ""
    echo "Examples:"
    echo "  $0                         Initialize the database"
    echo "  $0 -p                      Initialize the database in production"
    echo "  $0 -s                      Initialize the database and seed with example data"
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
        -s|--seed)
            SEED_DATA=true
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

# Create necessary directories
mkdir -p instance logs

# Initialize the database
echo "Initializing the database..."
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T web flask db init
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T web flask db migrate -m "Initial migration"
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T web flask db upgrade

# Seed the database with example data if requested
if [ "$SEED_DATA" = true ]; then
    echo "Seeding the database with example data..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T web flask seed
fi

echo "Database initialization completed successfully!" 