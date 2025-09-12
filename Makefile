# XTTS V2 Voice Cloning Studio - Makefile

.PHONY: help build up down logs clean install dev test lint format

# Default target
help:
	@echo "XTTS V2 Voice Cloning Studio - Available Commands:"
	@echo ""
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  logs      - Show logs from all services"
	@echo "  clean     - Clean up containers, images, and volumes"
	@echo "  install   - Install frontend dependencies"
	@echo "  dev       - Start development environment"
	@echo "  test      - Run tests"
	@echo "  lint      - Run linting"
	@echo "  format    - Format code"
	@echo ""

# Docker commands
build:
	@echo "🔨 Building Docker images..."
	docker-compose build --no-cache

up:
	@echo "🚀 Starting XTTS V2 Voice Cloning Studio..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"

down:
	@echo "🛑 Stopping services..."
	docker-compose down

logs:
	@echo "📋 Showing logs..."
	docker-compose logs -f

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	docker volume prune -f

# Development commands
install:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install

dev:
	@echo "🔧 Starting development environment..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

test:
	@echo "🧪 Running tests..."
	cd backend && python -m pytest tests/
	cd frontend && npm test

lint:
	@echo "🔍 Running linting..."
	cd backend && python -m flake8 .
	cd frontend && npm run lint

format:
	@echo "✨ Formatting code..."
	cd backend && python -m black .
	cd frontend && npm run format

# Quick start
start: build up
	@echo "🎉 XTTS V2 Voice Cloning Studio is ready!"

# Complete reset
reset: clean build up
	@echo "🔄 Complete reset completed!"

# Health check
health:
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/health || echo "❌ Backend not healthy"
	@curl -f http://localhost:3000 || echo "❌ Frontend not accessible"

# Backup data
backup:
	@echo "💾 Creating backup..."
	@mkdir -p backups
	@docker run --rm -v xtts-v2-docker_voices:/data -v $(PWD)/backups:/backup alpine tar czf /backup/voices-$(shell date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "✅ Backup created in backups/"

# Restore data
restore:
	@echo "📥 Restoring from backup..."
	@echo "Available backups:"
	@ls -la backups/
	@echo "Usage: make restore BACKUP=voices-YYYYMMDD-HHMMSS.tar.gz"
ifdef BACKUP
	@docker run --rm -v xtts-v2-docker_voices:/data -v $(PWD)/backups:/backup alpine tar xzf /backup/$(BACKUP) -C /data
	@echo "✅ Backup restored!"
else
	@echo "❌ Please specify BACKUP file"
endif