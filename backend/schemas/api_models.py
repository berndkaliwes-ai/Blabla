"""
API Models und Schemas für XTTS V2 Voice Cloning Studio
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class VoiceStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    TRAINING = "training"

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text zum Sprechen")
    voice_id: str = Field(..., description="ID der zu verwendenden Stimme")
    language: str = Field(default="de", description="Sprache (ISO 639-1 Code)")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Sprechgeschwindigkeit")
    temperature: float = Field(default=0.7, ge=0.1, le=1.0, description="Kreativität/Variabilität")

class VoiceCloneRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name der Stimme")
    description: Optional[str] = Field(default="", max_length=500, description="Beschreibung der Stimme")

class VoiceInfo(BaseModel):
    id: str
    name: str
    description: str
    status: VoiceStatus
    created_at: datetime
    language: Optional[str] = None
    sample_count: int = 0
    duration: Optional[float] = None
    preview_url: Optional[str] = None

class TTSResponse(BaseModel):
    audio_url: str
    filename: str
    duration: float
    text: str
    voice_id: str
    generated_at: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, bool]

class VoiceStatusResponse(BaseModel):
    voice_id: str
    status: VoiceStatus
    progress: Optional[float] = None
    message: Optional[str] = None
    error: Optional[str] = None

class AudioProcessingResult(BaseModel):
    success: bool
    file_path: Optional[str] = None
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    error: Optional[str] = None

class GenerationSettings(BaseModel):
    temperature: float = Field(default=0.7, ge=0.1, le=1.0)
    length_penalty: float = Field(default=1.0, ge=0.5, le=2.0)
    repetition_penalty: float = Field(default=1.0, ge=0.5, le=2.0)
    top_k: int = Field(default=50, ge=1, le=100)
    top_p: float = Field(default=0.8, ge=0.1, le=1.0)