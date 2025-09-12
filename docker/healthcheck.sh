#!/bin/bash

# Health check script for XTTS V2 containers

set -e

SERVICE_TYPE=${1:-backend}
TIMEOUT=${2:-30}

case $SERVICE_TYPE in
  "backend")
    echo "🏥 Checking backend health..."
    
    # Check if the service is responding
    if curl -f -s --max-time $TIMEOUT http://localhost:8000/health > /dev/null; then
      echo "✅ Backend is healthy"
      exit 0
    else
      echo "❌ Backend health check failed"
      exit 1
    fi
    ;;
    
  "frontend")
    echo "🏥 Checking frontend health..."
    
    # Check if nginx is serving files
    if curl -f -s --max-time $TIMEOUT http://localhost:3000 > /dev/null; then
      echo "✅ Frontend is healthy"
      exit 0
    else
      echo "❌ Frontend health check failed"
      exit 1
    fi
    ;;
    
  *)
    echo "❌ Unknown service type: $SERVICE_TYPE"
    exit 1
    ;;
esac