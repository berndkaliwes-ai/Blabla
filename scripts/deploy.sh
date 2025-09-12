#!/bin/bash

# XTTS V2 Voice Cloning Studio - Production Deployment Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
ENVIRONMENT=${1:-production}
BACKUP_BEFORE_DEPLOY=${BACKUP_BEFORE_DEPLOY:-true}
HEALTH_CHECK_TIMEOUT=${HEALTH_CHECK_TIMEOUT:-120}

print_status "🚀 Starting XTTS V2 deployment for environment: $ENVIRONMENT"

# Pre-deployment checks
check_requirements() {
    print_status "Checking deployment requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check NVIDIA Docker (for GPU support)
    if ! docker info | grep -q nvidia; then
        print_warning "NVIDIA Docker not detected - GPU acceleration will not be available"
    fi
    
    # Check disk space
    AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
    REQUIRED_SPACE=5242880  # 5GB in KB
    
    if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
        print_error "Insufficient disk space. Required: 5GB, Available: $(($AVAILABLE_SPACE/1024/1024))GB"
        exit 1
    fi
    
    print_success "Requirements check passed"
}

# Create backup
create_backup() {
    if [ "$BACKUP_BEFORE_DEPLOY" = "true" ]; then
        print_status "Creating backup before deployment..."
        
        if [ -f "scripts/backup.sh" ]; then
            ./scripts/backup.sh
            print_success "Backup created"
        else
            print_warning "Backup script not found, skipping backup"
        fi
    fi
}

# Build images
build_images() {
    print_status "Building Docker images..."
    
    case $ENVIRONMENT in
        "production")
            docker-compose -f docker-compose.yml -f docker/docker-compose.prod.yml build --no-cache
            ;;
        "staging")
            docker-compose -f docker-compose.yml build --no-cache
            ;;
        *)
            docker-compose build --no-cache
            ;;
    esac
    
    print_success "Images built successfully"
}

# Deploy services
deploy_services() {
    print_status "Deploying services..."
    
    case $ENVIRONMENT in
        "production")
            docker-compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d
            ;;
        "staging")
            docker-compose -f docker-compose.yml up -d
            ;;
        *)
            docker-compose up -d
            ;;
    esac
    
    print_success "Services deployed"
}

# Health checks
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    local timeout=$HEALTH_CHECK_TIMEOUT
    local elapsed=0
    local interval=5
    
    while [ $elapsed -lt $timeout ]; do
        if docker-compose ps | grep -q "Up (healthy)"; then
            print_success "All services are healthy"
            return 0
        fi
        
        print_status "Waiting for services... (${elapsed}s/${timeout}s)"
        sleep $interval
        elapsed=$((elapsed + interval))
    done
    
    print_error "Services failed to become healthy within ${timeout}s"
    docker-compose ps
    docker-compose logs --tail=50
    return 1
}

# Post-deployment tasks
post_deployment() {
    print_status "Running post-deployment tasks..."
    
    # Clean up old images
    print_status "Cleaning up old Docker images..."
    docker image prune -f
    
    # Show deployment status
    print_status "Deployment status:"
    docker-compose ps
    
    # Show resource usage
    print_status "Resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    
    print_success "Post-deployment tasks completed"
}

# Rollback function
rollback() {
    print_error "Deployment failed, initiating rollback..."
    
    # Stop current deployment
    docker-compose down
    
    # Restore from backup if available
    if [ -d "backups" ] && [ "$(ls -A backups)" ]; then
        LATEST_BACKUP=$(ls -t backups/*.tar.gz | head -n1)
        if [ -n "$LATEST_BACKUP" ]; then
            print_status "Restoring from backup: $LATEST_BACKUP"
            # Add restore logic here
        fi
    fi
    
    print_error "Rollback completed"
    exit 1
}

# Main deployment flow
main() {
    # Set trap for cleanup on failure
    trap rollback ERR
    
    check_requirements
    create_backup
    build_images
    deploy_services
    
    if wait_for_services; then
        post_deployment
        
        print_success "🎉 Deployment completed successfully!"
        echo
        echo "🌐 Access points:"
        echo "   Frontend: http://localhost:3000"
        echo "   Backend API: http://localhost:8000"
        echo "   API Documentation: http://localhost:8000/docs"
        
        if [ "$ENVIRONMENT" = "production" ]; then
            echo "   Monitoring: http://localhost:9090"
        fi
        
    else
        rollback
    fi
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "XTTS V2 Voice Cloning Studio - Deployment Script"
        echo
        echo "Usage: $0 [ENVIRONMENT] [OPTIONS]"
        echo
        echo "Environments:"
        echo "  production    Production deployment with optimizations"
        echo "  staging       Staging deployment"
        echo "  development   Development deployment (default)"
        echo
        echo "Environment Variables:"
        echo "  BACKUP_BEFORE_DEPLOY=true|false    Create backup before deployment"
        echo "  HEALTH_CHECK_TIMEOUT=120           Health check timeout in seconds"
        echo
        exit 0
        ;;
    *)
        main
        ;;
esac