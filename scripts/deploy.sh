#!/bin/bash

# Partner OS Deployment Script
# This script helps deploy the Partner OS application using Docker

# Exit on error
set -e

# Default values
ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"
PROD_COMPOSE_FILE="docker-compose.prod.yml"
ACTION="up"
SWARM_MODE=false

# Display help
function show_help {
    echo "Partner OS Deployment Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -e, --env FILE             Environment file to use (default: .env)"
    echo "  -p, --prod                 Use production configuration"
    echo "  -s, --swarm                Deploy in Docker Swarm mode"
    echo "  -a, --action ACTION        Action to perform: up, down, build, restart (default: up)"
    echo ""
    echo "Examples:"
    echo "  $0                         Deploy in development mode"
    echo "  $0 -p                      Deploy in production mode"
    echo "  $0 -p -s                   Deploy in production mode with Docker Swarm"
    echo "  $0 -a down                 Stop the application"
    echo "  $0 -a restart              Restart the application"
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
            COMPOSE_FILE="$PROD_COMPOSE_FILE"
            shift
            ;;
        -s|--swarm)
            SWARM_MODE=true
            shift
            ;;
        -a|--action)
            ACTION="$2"
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

# Create necessary directories
mkdir -p logs instance nginx/conf.d nginx/ssl

# Generate self-signed SSL certificate if it doesn't exist
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    echo "Generating self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

# Perform the requested action
if [ "$SWARM_MODE" = true ]; then
    # Initialize Docker Swarm if not already initialized
    if ! docker info | grep -q "Swarm: active"; then
        echo "Initializing Docker Swarm..."
        docker swarm init
    fi
    
    # Deploy the stack
    if [ "$ACTION" = "up" ]; then
        echo "Deploying stack in Swarm mode..."
        docker stack deploy -c "$COMPOSE_FILE" --env-file "$ENV_FILE" effect-crm
    elif [ "$ACTION" = "down" ]; then
        echo "Removing stack..."
        docker stack rm effect-crm
    elif [ "$ACTION" = "restart" ]; then
        echo "Restarting stack..."
        docker stack rm effect-crm
        sleep 5
        docker stack deploy -c "$COMPOSE_FILE" --env-file "$ENV_FILE" effect-crm
    else
        echo "Unknown action: $ACTION"
        exit 1
    fi
else
    # Regular Docker Compose deployment
    if [ "$ACTION" = "up" ]; then
        echo "Starting containers..."
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    elif [ "$ACTION" = "down" ]; then
        echo "Stopping containers..."
        docker-compose -f "$COMPOSE_FILE" down
    elif [ "$ACTION" = "build" ]; then
        echo "Building containers..."
        docker-compose -f "$COMPOSE_FILE" build
    elif [ "$ACTION" = "restart" ]; then
        echo "Restarting containers..."
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    else
        echo "Unknown action: $ACTION"
        exit 1
    fi
fi

echo "Deployment completed successfully!" 