#!/bin/bash

# Entrypoint script for XTTS V2 backend

set -e

echo "🚀 Starting XTTS V2 Backend..."

# Wait for dependencies (if any)
if [ -n "$WAIT_FOR_SERVICES" ]; then
    echo "⏳ Waiting for dependencies..."
    # Add service waiting logic here if needed
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /app/{data,models,uploads,outputs,voices,logs}

# Set permissions
echo "🔐 Setting permissions..."
chown -R $(id -u):$(id -g) /app/{data,models,uploads,outputs,voices,logs} 2>/dev/null || true

# Download models if not present
if [ ! -d "/app/models/tts_models" ] && [ "${DOWNLOAD_MODELS:-true}" = "true" ]; then
    echo "📥 Downloading XTTS V2 models..."
    python -c "
from TTS.api import TTS
print('Downloading XTTS V2 model...')
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
print('Model download completed!')
" || echo "⚠️ Model download failed, will download on first use"
fi

# Run database migrations or setup if needed
echo "🔧 Running setup tasks..."
# Add any setup tasks here

# Health check
echo "🏥 Running initial health check..."
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA device: {torch.cuda.get_device_name(0)}')
print('✅ Environment check passed')
"

echo "✅ Initialization completed!"

# Execute the main command
exec "$@"