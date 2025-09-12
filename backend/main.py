"""
XTTS V2 Voice Cloning Studio - FastAPI Backend
Professionelle API für Voice Cloning und Text-to-Speech
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
import asyncio
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime
import shutil

from models.tts_service import XTTSService
from models.voice_manager import VoiceManager
from models.audio_processor import AudioProcessor
from utils.logger import setup_logger
from schemas.api_models import (
    TTSRequest, 
    VoiceCloneRequest, 
    VoiceInfo, 
    TTSResponse,
    HealthResponse
)

# Logger setup
logger = setup_logger()

# FastAPI App
app = FastAPI(
    title="XTTS V2 Voice Cloning Studio",
    description="Professionelle API für Voice Cloning und Text-to-Speech mit XTTS V2",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion spezifische Origins verwenden
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services initialisieren
tts_service = XTTSService()
voice_manager = VoiceManager()
audio_processor = AudioProcessor()

# Verzeichnisse erstellen
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("voices", exist_ok=True)

# Statische Dateien
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.on_event("startup")
async def startup_event():
    """Initialisierung beim Start"""
    logger.info("🚀 XTTS V2 Voice Cloning Studio startet...")
    
    try:
        # TTS Service initialisieren
        await tts_service.initialize()
        logger.info("✅ XTTS V2 Service erfolgreich initialisiert")
        
        # Voice Manager initialisieren
        await voice_manager.initialize()
        logger.info("✅ Voice Manager erfolgreich initialisiert")
        
        logger.info("🎉 Backend erfolgreich gestartet!")
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Starten: {e}")
        raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health Check Endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        services={
            "tts": tts_service.is_ready(),
            "voice_manager": voice_manager.is_ready(),
            "audio_processor": True
        }
    )

@app.get("/api/voices", response_model=List[VoiceInfo])
async def get_voices():
    """Alle verfügbaren Stimmen abrufen"""
    try:
        voices = await voice_manager.get_all_voices()
        return voices
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Stimmen: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voices/clone")
async def clone_voice(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    description: str = Form(""),
    files: List[UploadFile] = File(...)
):
    """Neue Stimme aus Audio-Dateien klonen"""
    try:
        if len(files) < 1:
            raise HTTPException(status_code=400, detail="Mindestens eine Audio-Datei erforderlich")
        
        # Eindeutige Voice ID generieren
        voice_id = str(uuid.uuid4())
        voice_dir = Path(f"voices/{voice_id}")
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        # Audio-Dateien speichern und verarbeiten
        audio_paths = []
        for file in files:
            if not file.content_type.startswith("audio/"):
                raise HTTPException(status_code=400, detail=f"Datei {file.filename} ist keine Audio-Datei")
            
            file_path = voice_dir / f"{uuid.uuid4()}_{file.filename}"
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Audio verarbeiten und validieren
            processed_path = await audio_processor.process_for_cloning(file_path)
            audio_paths.append(processed_path)
        
        # Voice Cloning im Hintergrund starten
        background_tasks.add_task(
            voice_manager.clone_voice,
            voice_id=voice_id,
            name=name,
            description=description,
            audio_paths=audio_paths
        )
        
        return {
            "voice_id": voice_id,
            "status": "processing",
            "message": f"Voice Cloning für '{name}' gestartet"
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Voice Cloning: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts/generate", response_model=TTSResponse)
async def generate_speech(request: TTSRequest):
    """Text zu Sprache konvertieren"""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text darf nicht leer sein")
        
        # Audio generieren
        output_path = await tts_service.generate_speech(
            text=request.text,
            voice_id=request.voice_id,
            language=request.language,
            speed=request.speed,
            temperature=request.temperature
        )
        
        # Datei-URL generieren
        filename = os.path.basename(output_path)
        audio_url = f"/outputs/{filename}"
        
        return TTSResponse(
            audio_url=audio_url,
            filename=filename,
            duration=await audio_processor.get_duration(output_path),
            text=request.text,
            voice_id=request.voice_id
        )
        
    except Exception as e:
        logger.error(f"Fehler bei TTS-Generierung: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/voices/{voice_id}/status")
async def get_voice_status(voice_id: str):
    """Status einer Stimme abrufen"""
    try:
        status = await voice_manager.get_voice_status(voice_id)
        return status
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Voice-Status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/voices/{voice_id}")
async def delete_voice(voice_id: str):
    """Stimme löschen"""
    try:
        await voice_manager.delete_voice(voice_id)
        return {"message": f"Stimme {voice_id} erfolgreich gelöscht"}
    except Exception as e:
        logger.error(f"Fehler beim Löschen der Stimme: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/languages")
async def get_supported_languages():
    """Unterstützte Sprachen abrufen"""
    return {
        "languages": [
            {"code": "de", "name": "Deutsch"},
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Español"},
            {"code": "fr", "name": "Français"},
            {"code": "it", "name": "Italiano"},
            {"code": "pt", "name": "Português"},
            {"code": "pl", "name": "Polski"},
            {"code": "tr", "name": "Türkçe"},
            {"code": "ru", "name": "Русский"},
            {"code": "nl", "name": "Nederlands"},
            {"code": "cs", "name": "Čeština"},
            {"code": "ar", "name": "العربية"},
            {"code": "zh", "name": "中文"},
            {"code": "ja", "name": "日本語"},
            {"code": "hu", "name": "Magyar"},
            {"code": "ko", "name": "한국어"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)