#!/bin/bash

# XTTS V2 Voice Cloning Studio - Setup Script

set -e

echo "🎙️ XTTS V2 Voice Cloning Studio Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
}

# Check if Docker Compose is installed
check_docker_compose() {
    print_status "Checking Docker Compose installation..."
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed"
}

# Check for NVIDIA Docker (optional)
check_nvidia_docker() {
    print_status "Checking NVIDIA Docker support..."
    if command -v nvidia-docker &> /dev/null || docker info | grep -q nvidia; then
        print_success "NVIDIA Docker support detected"
        export GPU_SUPPORT=true
    else
        print_warning "NVIDIA Docker not detected. GPU acceleration will not be available."
        export GPU_SUPPORT=false
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p data models uploads outputs voices logs backups
    print_success "Directories created"
}

# Set up environment file
setup_env() {
    print_status "Setting up environment configuration..."
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success "Environment file created from template"
        print_warning "Please review and update .env file with your settings"
    else
        print_warning ".env file already exists, skipping..."
    fi
}

# Set permissions
set_permissions() {
    print_status "Setting up permissions..."
    
    # Make sure directories are writable
    chmod -R 755 data models uploads outputs voices logs
    
    # Make scripts executable
    chmod +x scripts/*.sh
    
    print_success "Permissions set"
}

# Download default assets (optional)
download_assets() {
    print_status "Setting up default assets..."
    
    # Create favicon and other assets
    mkdir -p frontend/public
    
    # You could download default assets here
    # For now, we'll just create placeholder files
    
    print_success "Assets ready"
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    if [ "$1" = "--no-cache" ]; then
        docker-compose build --no-cache
    else
        docker-compose build
    fi
    
    print_success "Docker images built successfully"
}

# Run initial tests
run_tests() {
    print_status "Running initial tests..."
    
    # Start services temporarily for testing
    docker-compose up -d
    
    # Wait for services to be ready
    sleep 30
    
    # Test backend health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend health check passed"
    else
        print_warning "Backend health check failed"
    fi
    
    # Test frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend accessibility check passed"
    else
        print_warning "Frontend accessibility check failed"
    fi
    
    # Stop services
    docker-compose down
}

# Main setup function
main() {
    echo
    print_status "Starting XTTS V2 Voice Cloning Studio setup..."
    echo
    
    # Run checks
    check_docker
    check_docker_compose
    check_nvidia_docker
    
    echo
    
    # Setup
    create_directories
    setup_env
    set_permissions
    download_assets
    
    echo
    
    # Build
    if [ "$1" = "--skip-build" ]; then
        print_warning "Skipping Docker build as requested"
    else
        build_images $1
    fi
    
    echo
    
    # Test
    if [ "$1" = "--skip-tests" ]; then
        print_warning "Skipping tests as requested"
    else
        print_status "Would you like to run initial tests? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            run_tests
        fi
    fi
    
    echo
    print_success "Setup completed successfully!"
    echo
    echo "🚀 To start the application:"
    echo "   make up"
    echo
    echo "🌐 Access points:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo
    echo "📚 For more commands:"
    echo "   make help"
    echo
}

# Handle command line arguments
case "$1" in
    --help|-h)
        echo "XTTS V2 Voice Cloning Studio Setup Script"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h        Show this help message"
        echo "  --skip-build      Skip Docker image building"
        echo "  --skip-tests      Skip initial tests"
        echo "  --no-cache        Build Docker images without cache"
        echo
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac