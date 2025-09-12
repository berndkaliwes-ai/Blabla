#!/usr/bin/env python3
"""
Einfache XTTS V2 Backend Version zum Testen
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime

# FastAPI App
app = FastAPI(
    title="XTTS V2 Voice Cloning Studio",
    description="Backend für Voice Cloning und Text-to-Speech",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "🎙️ XTTS V2 Voice Cloning Studio Backend",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": True,
            "tts": False,  # Wird später implementiert
            "voice_manager": False,
            "audio_processor": False
        }
    }

@app.get("/api/voices")
async def get_voices():
    """Alle verfügbaren Stimmen abrufen"""
    return {
        "voices": [],
        "count": 0,
        "message": "Noch keine Stimmen verfügbar"
    }

@app.get("/api/languages")
async def get_languages():
    """Unterstützte Sprachen"""
    return {
        "languages": [
            {"code": "de", "name": "Deutsch"},
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Español"},
            {"code": "fr", "name": "Français"},
            {"code": "it", "name": "Italiano"},
            {"code": "pt", "name": "Português"}
        ]
    }

@app.post("/api/voices/clone")
async def clone_voice():
    """Voice Cloning (Demo)"""
    return {
        "voice_id": "demo-voice-123",
        "status": "processing",
        "message": "Voice Cloning Demo - würde in echter Version starten"
    }

@app.post("/api/tts/generate")
async def generate_tts():
    """Text-to-Speech (Demo)"""
    return {
        "audio_url": "/demo-audio.wav",
        "filename": "demo-audio.wav",
        "duration": 5.2,
        "message": "TTS Demo - würde in echter Version Audio generieren"
    }

@app.get("/status")
async def get_status():
    """System Status"""
    return {
        "system": "XTTS V2 Voice Cloning Studio",
        "backend_status": "running",
        "api_endpoints": [
            "GET /",
            "GET /health", 
            "GET /api/voices",
            "GET /api/languages",
            "POST /api/voices/clone",
            "POST /api/tts/generate",
            "GET /status"
        ],
        "directories": {
            "uploads": os.path.exists("uploads"),
            "outputs": os.path.exists("outputs"), 
            "voices": os.path.exists("voices"),
            "models": os.path.exists("models")
        }
    }

if __name__ == "__main__":
    print("🚀 Starte XTTS V2 Backend...")
    print("📡 API wird verfügbar unter: http://localhost:8000")
    print("📚 Dokumentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )