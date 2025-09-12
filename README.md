# XTTS V2 Voice Cloning Studio 🎙️

Ein professioneller Docker-Container für XTTS V2 (Coqui AI) mit einer modernen, intuitiven Benutzeroberfläche für Voice Cloning und Text-to-Speech.

## Features

- 🎯 **Voice Cloning**: Klonen Sie Stimmen mit nur wenigen Audiodateien
- 🗣️ **Text-to-Speech**: Generieren Sie natürlich klingende Sprache
- 🎨 **Moderne UI**: Ansprechende, responsive Benutzeroberfläche
- 🐳 **Docker Ready**: Vollständig containerisiert und einfach zu deployen
- ⚡ **GPU Support**: Optimiert für CUDA-beschleunigte Inferenz
- 📱 **Responsive**: Funktioniert auf Desktop und mobilen Geräten

## Quick Start

```bash
# Setup ausführen (empfohlen für erste Installation)
./scripts/setup.sh

# Oder manuell starten
make up

# UI öffnen
open http://localhost:3000
```

## Installation

### Voraussetzungen

- Docker & Docker Compose
- NVIDIA Docker (für GPU-Beschleunigung, optional)
- Mindestens 8GB RAM
- 10GB freier Speicherplatz

### Automatische Installation

```bash
# Repository klonen
git clone <repository-url>
cd xtts-v2-docker

# Setup-Script ausführen
./scripts/setup.sh

# Services starten
make up
```

### Manuelle Installation

```bash
# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env nach Bedarf anpassen

# Images bauen
docker-compose build

# Services starten
docker-compose up -d
```

## Verwendung

### Voice Cloning

1. Navigieren Sie zu **Voice Cloning** (http://localhost:3000/clone)
2. Laden Sie 3-10 Audio-Dateien hoch (WAV, MP3, OGG)
3. Geben Sie einen Namen und Beschreibung ein
4. Klicken Sie auf "Stimme klonen"
5. Warten Sie auf die Verarbeitung (kann einige Minuten dauern)

### Text-to-Speech

1. Navigieren Sie zu **Text-to-Speech** (http://localhost:3000/tts)
2. Wählen Sie eine geklonte Stimme aus
3. Geben Sie den gewünschten Text ein
4. Passen Sie Einstellungen an (Sprache, Geschwindigkeit, Kreativität)
5. Klicken Sie auf "Sprechen"
6. Laden Sie das generierte Audio herunter

## Konfiguration

### Umgebungsvariablen

Wichtige Einstellungen in der `.env` Datei:

```bash
# GPU-Unterstützung
CUDA_VISIBLE_DEVICES=0

# Audio-Verarbeitung
MAX_AUDIO_SIZE=52428800  # 50MB
TARGET_SAMPLE_RATE=22050

# Performance
MAX_CONCURRENT_GENERATIONS=2
```

### Docker Compose Profiles

```bash
# Entwicklung
docker-compose up -d

# Produktion
docker-compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d

# Mit Monitoring
docker-compose --profile monitoring up -d
```

## Architektur

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + XTTS V2
- **Container**: Docker + Docker Compose
- **Audio Processing**: librosa, soundfile
- **UI Components**: Framer Motion, React DnD

## Verfügbare Befehle

```bash
# Makefile Befehle
make help          # Zeige alle verfügbaren Befehle
make build         # Baue Docker Images
make up            # Starte Services
make down          # Stoppe Services
make logs          # Zeige Logs
make clean         # Räume auf
make backup        # Erstelle Backup
make health        # Prüfe Service-Status

# Scripts
./scripts/setup.sh     # Automatische Installation
./scripts/deploy.sh    # Produktions-Deployment
./scripts/backup.sh    # Backup erstellen
```

## Troubleshooting

### Häufige Probleme

**GPU nicht erkannt:**
```bash
# NVIDIA Docker installieren
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

**Speicherplatz-Probleme:**
```bash
# Docker aufräumen
docker system prune -a
docker volume prune
```

**Port bereits belegt:**
```bash
# Ports in docker-compose.yml ändern
ports:
  - "3001:3000"  # Frontend
  - "8001:8000"  # Backend
```

### Logs anzeigen

```bash
# Alle Services
docker-compose logs -f

# Spezifischer Service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Performance-Optimierung

### GPU-Optimierung

- Verwenden Sie CUDA 11.8+ für beste Performance
- Mindestens 6GB VRAM empfohlen
- RTX 3060 oder besser für optimale Ergebnisse

### CPU-Optimierung

- Mindestens 4 CPU-Kerne
- 8GB RAM für Backend
- SSD-Speicher empfohlen

### Audio-Qualität

- Verwenden Sie WAV-Dateien für beste Qualität
- Sample-Rate: 22050 Hz oder höher
- Mono-Audio bevorzugt
- Rauschfreie Aufnahmen

## API-Dokumentation

Die vollständige API-Dokumentation ist verfügbar unter:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Wichtige Endpoints

```bash
# Gesundheitsstatus
GET /health

# Stimmen verwalten
GET /api/voices
POST /api/voices/clone
DELETE /api/voices/{voice_id}

# Text-to-Speech
POST /api/tts/generate

# Unterstützte Sprachen
GET /api/languages
```

## Entwicklung

### Entwicklungsumgebung

```bash
# Development Mode starten
make dev

# Frontend entwickeln
cd frontend
npm install
npm run dev

# Backend entwickeln
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Tests ausführen

```bash
# Alle Tests
make test

# Backend Tests
cd backend && python -m pytest

# Frontend Tests
cd frontend && npm test
```

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) für Details.

## Beitragen

Beiträge sind willkommen! Bitte lesen Sie [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

## Support

- 📧 **Issues:** GitHub Issues für Bug-Reports und Feature-Requests
- 💬 **Diskussionen:** GitHub Discussions für Fragen und Ideen
- 📖 **Dokumentation:** Siehe `/docs` Verzeichnis

## Entwickelt mit ❤️ für die Voice AI Community

**Powered by:**
- 🤖 XTTS V2 (Coqui AI)
- ⚛️ React + TypeScript
- 🚀 FastAPI + Python
- 🐳 Docker + Docker Compose
- 🎨 Tailwind CSS + Framer Motion