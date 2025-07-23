#!/bin/bash

# MEDHASAKTHI Deployment Script
# Automated deployment with health checks and rollback capability

set -e

# Configuration
DEPLOY_DIR="/opt/medhasakthi"
BACKUP_DIR="/opt/backups/deployments"
DATE=$(date +%Y%m%d_%H%M%S)
COMPOSE_FILE="docker-compose.yml"
HEALTH_CHECK_TIMEOUT=300
ROLLBACK_ENABLED=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running as root or with sudo
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root or with sudo"
        exit 1
    fi
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if deployment directory exists
    if [ ! -d "$DEPLOY_DIR" ]; then
        error "Deployment directory $DEPLOY_DIR does not exist"
        exit 1
    fi
    
    log "Prerequisites check passed"
}

# Create deployment backup
create_deployment_backup() {
    log "Creating deployment backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup current deployment
    tar -czf "$BACKUP_DIR/deployment_backup_$DATE.tar.gz" \
        -C "$DEPLOY_DIR" \
        --exclude="logs" \
        --exclude="uploads" \
        --exclude="node_modules" \
        --exclude=".git" \
        .
    
    if [ $? -eq 0 ]; then
        log "Deployment backup created: $BACKUP_DIR/deployment_backup_$DATE.tar.gz"
    else
        error "Failed to create deployment backup"
        exit 1
    fi
}

# Pull latest code
pull_latest_code() {
    log "Pulling latest code from repository..."
    
    cd "$DEPLOY_DIR"
    
    # Stash any local changes
    git stash push -m "Auto-stash before deployment $DATE"
    
    # Pull latest changes
    git pull origin main
    
    if [ $? -eq 0 ]; then
        log "Code updated successfully"
        CURRENT_COMMIT=$(git rev-parse HEAD)
        log "Current commit: $CURRENT_COMMIT"
    else
        error "Failed to pull latest code"
        exit 1
    fi
}

# Build and pull Docker images
build_images() {
    log "Building and pulling Docker images..."
    
    cd "$DEPLOY_DIR"
    
    # Pull latest base images
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Build custom images
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    if [ $? -eq 0 ]; then
        log "Images built successfully"
    else
        error "Failed to build images"
        exit 1
    fi
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    cd "$DEPLOY_DIR"
    
    # Check if backend container is running
    if docker-compose -f "$COMPOSE_FILE" ps backend | grep -q "Up"; then
        # Run migrations
        docker-compose -f "$COMPOSE_FILE" exec -T backend alembic upgrade head
        
        if [ $? -eq 0 ]; then
            log "Database migrations completed successfully"
        else
            error "Database migrations failed"
            return 1
        fi
    else
        warn "Backend container is not running, skipping migrations"
    fi
}

# Deploy services
deploy_services() {
    log "Deploying services..."
    
    cd "$DEPLOY_DIR"
    
    # Stop services gracefully
    docker-compose -f "$COMPOSE_FILE" down --timeout 30
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    if [ $? -eq 0 ]; then
        log "Services deployed successfully"
    else
        error "Failed to deploy services"
        exit 1
    fi
}

# Health check function
health_check() {
    local service_name=$1
    local health_url=$2
    local max_attempts=30
    local attempt=1
    
    log "Performing health check for $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$health_url" > /dev/null 2>&1; then
            log "$service_name health check passed"
            return 0
        fi
        
        info "Health check attempt $attempt/$max_attempts for $service_name..."
        sleep 10
        ((attempt++))
    done
    
    error "$service_name health check failed after $max_attempts attempts"
    return 1
}

# Comprehensive health checks
run_health_checks() {
    log "Running comprehensive health checks..."
    
    local health_check_failed=false
    
    # Wait for services to start
    sleep 30
    
    # Check backend API
    if ! health_check "Backend API" "http://localhost:8000/health"; then
        health_check_failed=true
    fi
    
    # Check institute portal
    if ! health_check "Institute Portal" "http://localhost:3001"; then
        health_check_failed=true
    fi
    
    # Check student portal
    if ! health_check "Student Portal" "http://localhost:3000"; then
        health_check_failed=true
    fi
    
    # Check database connectivity
    if docker-compose -f "$COMPOSE_FILE" exec -T backend python -c "
from app.core.database import engine
try:
    result = engine.execute('SELECT 1').scalar()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" > /dev/null 2>&1; then
        log "Database connectivity check passed"
    else
        error "Database connectivity check failed"
        health_check_failed=true
    fi
    
    # Check Redis connectivity
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping | grep -q "PONG"; then
        log "Redis connectivity check passed"
    else
        error "Redis connectivity check failed"
        health_check_failed=true
    fi
    
    if [ "$health_check_failed" = true ]; then
        error "Health checks failed"
        return 1
    else
        log "All health checks passed"
        return 0
    fi
}

# Rollback deployment
rollback_deployment() {
    if [ "$ROLLBACK_ENABLED" != true ]; then
        error "Rollback is disabled"
        return 1
    fi
    
    warn "Rolling back deployment..."
    
    cd "$DEPLOY_DIR"
    
    # Find the latest backup
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/deployment_backup_*.tar.gz 2>/dev/null | head -n1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        error "No backup found for rollback"
        return 1
    fi
    
    log "Rolling back to: $LATEST_BACKUP"
    
    # Stop current services
    docker-compose -f "$COMPOSE_FILE" down --timeout 30
    
    # Restore from backup
    tar -xzf "$LATEST_BACKUP" -C "$DEPLOY_DIR"
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    if [ $? -eq 0 ]; then
        log "Rollback completed successfully"
        return 0
    else
        error "Rollback failed"
        return 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up old deployment backups..."
    
    # Keep only the last 10 backups
    ls -t "$BACKUP_DIR"/deployment_backup_*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f
    
    log "Cleanup completed"
}

# Send deployment notification
send_notification() {
    local status=$1
    local message=$2
    
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        if [ "$status" = "success" ]; then
            color="good"
            emoji=":rocket:"
        else
            color="danger"
            emoji=":x:"
        fi
        
        curl -X POST -H 'Content-type: application/json' \
            --data "{
                \"attachments\": [{
                    \"color\": \"$color\",
                    \"title\": \"$emoji MEDHASAKTHI Deployment $status\",
                    \"text\": \"$message\",
                    \"footer\": \"Deployment Script\",
                    \"ts\": $(date +%s)
                }]
            }" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1
    fi
}

# Main deployment function
main() {
    local start_time=$(date +%s)
    
    log "Starting MEDHASAKTHI deployment process..."
    
    # Check prerequisites
    check_prerequisites
    
    # Create backup
    create_deployment_backup
    
    # Pull latest code
    pull_latest_code
    
    # Build images
    build_images
    
    # Deploy services
    deploy_services
    
    # Run migrations
    if ! run_migrations; then
        error "Migration failed, attempting rollback..."
        if rollback_deployment; then
            send_notification "failed" "Deployment failed during migration. Rollback successful."
        else
            send_notification "failed" "Deployment failed during migration. Rollback also failed!"
        fi
        exit 1
    fi
    
    # Run health checks
    if ! run_health_checks; then
        error "Health checks failed, attempting rollback..."
        if rollback_deployment; then
            send_notification "failed" "Deployment failed health checks. Rollback successful."
        else
            send_notification "failed" "Deployment failed health checks. Rollback also failed!"
        fi
        exit 1
    fi
    
    # Cleanup
    cleanup_old_backups
    
    # Calculate deployment time
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "Deployment completed successfully in ${duration}s!"
    send_notification "success" "Deployment completed successfully in ${duration}s. Commit: $CURRENT_COMMIT"
}

# Script execution
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
