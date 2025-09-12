#!/bin/bash

# XTTS V2 Voice Cloning Studio - Backup Script

set -e

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="xtts-backup-${TIMESTAMP}"

echo "🔄 Creating backup: ${BACKUP_NAME}"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Create temporary directory for backup
TEMP_DIR=$(mktemp -d)
trap "rm -rf ${TEMP_DIR}" EXIT

echo "📦 Backing up voices..."
if docker volume ls | grep -q xtts-v2-docker_voices; then
    docker run --rm -v xtts-v2-docker_voices:/data -v ${TEMP_DIR}:/backup alpine tar czf /backup/voices.tar.gz -C /data .
fi

echo "📦 Backing up data..."
if docker volume ls | grep -q xtts-v2-docker_data; then
    docker run --rm -v xtts-v2-docker_data:/data -v ${TEMP_DIR}:/backup alpine tar czf /backup/data.tar.gz -C /data .
fi

echo "📦 Backing up configuration..."
cp -r . ${TEMP_DIR}/config/ 2>/dev/null || true
rm -rf ${TEMP_DIR}/config/.git ${TEMP_DIR}/config/node_modules ${TEMP_DIR}/config/backups 2>/dev/null || true

echo "🗜️ Creating final backup archive..."
cd ${TEMP_DIR}
tar czf ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz .
cd - > /dev/null

echo "✅ Backup created: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "📊 Backup size: $(du -h ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz | cut -f1)"