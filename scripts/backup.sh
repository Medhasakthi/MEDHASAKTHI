#!/bin/bash

# MEDHASAKTHI Backup Script
# Automated backup for database, uploads, and configurations

set -e

# Configuration
BACKUP_DIR="/opt/backups/medhasakthi"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)
COMPOSE_FILE="/opt/medhasakthi/docker-compose.yml"

# AWS S3 Configuration (optional)
S3_BUCKET="medhasakthi-backups"
AWS_REGION="us-east-1"

# Slack notification (optional)
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Create backup directory
create_backup_dir() {
    log "Creating backup directory: $BACKUP_DIR/$DATE"
    mkdir -p "$BACKUP_DIR/$DATE"
}

# Backup PostgreSQL database
backup_database() {
    log "Starting database backup..."
    
    # Check if PostgreSQL container is running
    if ! docker-compose -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        error "PostgreSQL container is not running"
        return 1
    fi
    
    # Create database backup
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
        -U admin \
        -h localhost \
        -p 5432 \
        --verbose \
        --clean \
        --no-owner \
        --no-privileges \
        medhasakthi > "$BACKUP_DIR/$DATE/database.sql"
    
    if [ $? -eq 0 ]; then
        log "Database backup completed successfully"
        
        # Compress the backup
        gzip "$BACKUP_DIR/$DATE/database.sql"
        log "Database backup compressed"
    else
        error "Database backup failed"
        return 1
    fi
}

# Backup Redis data
backup_redis() {
    log "Starting Redis backup..."
    
    # Check if Redis container is running
    if ! docker-compose -f "$COMPOSE_FILE" ps redis | grep -q "Up"; then
        warn "Redis container is not running, skipping Redis backup"
        return 0
    fi
    
    # Create Redis backup
    docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli \
        --rdb /data/dump.rdb BGSAVE
    
    # Wait for backup to complete
    sleep 5
    
    # Copy Redis dump
    docker cp $(docker-compose -f "$COMPOSE_FILE" ps -q redis):/data/dump.rdb \
        "$BACKUP_DIR/$DATE/redis-dump.rdb"
    
    if [ $? -eq 0 ]; then
        log "Redis backup completed successfully"
        gzip "$BACKUP_DIR/$DATE/redis-dump.rdb"
    else
        warn "Redis backup failed"
    fi
}

# Backup uploaded files
backup_uploads() {
    log "Starting uploads backup..."
    
    UPLOADS_DIR="/opt/medhasakthi/backend/uploads"
    
    if [ -d "$UPLOADS_DIR" ]; then
        tar -czf "$BACKUP_DIR/$DATE/uploads.tar.gz" -C "$UPLOADS_DIR" .
        
        if [ $? -eq 0 ]; then
            log "Uploads backup completed successfully"
        else
            error "Uploads backup failed"
            return 1
        fi
    else
        warn "Uploads directory not found, skipping uploads backup"
    fi
}

# Backup configuration files
backup_configs() {
    log "Starting configuration backup..."
    
    CONFIG_DIR="/opt/medhasakthi"
    
    # Backup important configuration files
    tar -czf "$BACKUP_DIR/$DATE/configs.tar.gz" \
        -C "$CONFIG_DIR" \
        docker-compose.yml \
        .env \
        nginx/nginx.conf \
        monitoring/ \
        --exclude="*.log" \
        --exclude="node_modules" \
        --exclude=".git"
    
    if [ $? -eq 0 ]; then
        log "Configuration backup completed successfully"
    else
        error "Configuration backup failed"
        return 1
    fi
}

# Upload to S3 (if configured)
upload_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        log "S3 backup not configured, skipping upload"
        return 0
    fi
    
    log "Uploading backup to S3..."
    
    # Check if AWS CLI is available
    if ! command -v aws &> /dev/null; then
        warn "AWS CLI not found, skipping S3 upload"
        return 0
    fi
    
    # Upload backup directory to S3
    aws s3 sync "$BACKUP_DIR/$DATE" "s3://$S3_BUCKET/backups/$DATE" \
        --region "$AWS_REGION" \
        --storage-class STANDARD_IA
    
    if [ $? -eq 0 ]; then
        log "Backup uploaded to S3 successfully"
    else
        error "S3 upload failed"
        return 1
    fi
}

# Clean old backups
cleanup_old_backups() {
    log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
    
    # Local cleanup
    find "$BACKUP_DIR" -type d -name "20*" -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
    
    # S3 cleanup (if configured)
    if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
        aws s3 ls "s3://$S3_BUCKET/backups/" | \
        awk '{print $2}' | \
        while read -r backup_date; do
            backup_timestamp=$(date -d "${backup_date%/}" +%s 2>/dev/null || echo 0)
            current_timestamp=$(date +%s)
            age_days=$(( (current_timestamp - backup_timestamp) / 86400 ))
            
            if [ $age_days -gt $RETENTION_DAYS ]; then
                log "Deleting old S3 backup: $backup_date"
                aws s3 rm "s3://$S3_BUCKET/backups/$backup_date" --recursive
            fi
        done
    fi
    
    log "Cleanup completed"
}

# Send notification
send_notification() {
    local status=$1
    local message=$2
    
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        if [ "$status" = "success" ]; then
            color="good"
            emoji=":white_check_mark:"
        else
            color="danger"
            emoji=":x:"
        fi
        
        curl -X POST -H 'Content-type: application/json' \
            --data "{
                \"attachments\": [{
                    \"color\": \"$color\",
                    \"title\": \"$emoji MEDHASAKTHI Backup $status\",
                    \"text\": \"$message\",
                    \"footer\": \"Backup Script\",
                    \"ts\": $(date +%s)
                }]
            }" \
            "$SLACK_WEBHOOK_URL" > /dev/null 2>&1
    fi
}

# Calculate backup size
calculate_backup_size() {
    if [ -d "$BACKUP_DIR/$DATE" ]; then
        du -sh "$BACKUP_DIR/$DATE" | cut -f1
    else
        echo "0B"
    fi
}

# Main backup function
main() {
    log "Starting MEDHASAKTHI backup process..."
    
    local start_time=$(date +%s)
    local errors=0
    
    # Create backup directory
    create_backup_dir || ((errors++))
    
    # Perform backups
    backup_database || ((errors++))
    backup_redis || ((errors++))
    backup_uploads || ((errors++))
    backup_configs || ((errors++))
    
    # Upload to S3
    upload_to_s3 || ((errors++))
    
    # Cleanup old backups
    cleanup_old_backups
    
    # Calculate metrics
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local backup_size=$(calculate_backup_size)
    
    if [ $errors -eq 0 ]; then
        log "Backup completed successfully!"
        log "Duration: ${duration}s, Size: $backup_size"
        send_notification "success" "Backup completed in ${duration}s. Size: $backup_size"
    else
        error "Backup completed with $errors errors"
        send_notification "failed" "Backup completed with $errors errors. Duration: ${duration}s"
        exit 1
    fi
}

# Script execution
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
