"""
XTTS V2 Service für Text-to-Speech Generierung
"""

import os
import torch
import torchaudio
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

from utils.logger import get_logger

logger = get_logger(__name__)

class XTTSService:
    def __init__(self):
        self.model = None
        self.config = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_path = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.is_initialized = False
        
    async def initialize(self):
        """XTTS V2 Model initialisieren"""
        try:
            logger.info(f"🔄 XTTS V2 wird auf {self.device} initialisiert...")
            
            # Model laden
            self.model = TTS(self.model_path).to(self.device)
            
            # Erweiterte Konfiguration für bessere Qualität
            if hasattr(self.model, 'synthesizer') and hasattr(self.model.synthesizer.tts_model, 'config'):
                config = self.model.synthesizer.tts_model.config
                # Optimierungen für bessere Audioqualität
                config.do_trim_silence = True
                config.length_penalty = 1.0
                config.repetition_penalty = 5.0
                config.temperature = 0.7
            
            self.is_initialized = True
            logger.info("✅ XTTS V2 erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"❌ Fehler bei XTTS V2 Initialisierung: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Prüfen ob Service bereit ist"""
        return self.is_initialized and self.model is not None
    
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        language: str = "de",
        speed: float = 1.0,
        temperature: float = 0.7
    ) -> str:
        """
        Text zu Sprache konvertieren
        
        Args:
            text: Zu sprechender Text
            voice_id: ID der Stimme oder Pfad zu Referenz-Audio
            language: Sprache (ISO 639-1)
            speed: Sprechgeschwindigkeit
            temperature: Kreativität/Variabilität
            
        Returns:
            Pfad zur generierten Audio-Datei
        """
        if not self.is_ready():
            raise RuntimeError("XTTS Service ist nicht bereit")
        
        try:
            logger.info(f"🎙️ Generiere Sprache für Text: '{text[:50]}...'")
            
            # Voice-Referenz laden
            speaker_wav = await self._get_voice_reference(voice_id)
            
            # Eindeutigen Dateinamen generieren
            output_filename = f"tts_{uuid.uuid4()}.wav"
            output_path = Path("outputs") / output_filename
            
            # Text-to-Speech generieren
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._generate_audio,
                text,
                speaker_wav,
                str(output_path),
                language,
                temperature
            )
            
            # Geschwindigkeit anpassen falls nötig
            if speed != 1.0:
                await self._adjust_speed(output_path, speed)
            
            logger.info(f"✅ Audio erfolgreich generiert: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Fehler bei TTS-Generierung: {e}")
            raise
    
    def _generate_audio(
        self,
        text: str,
        speaker_wav: str,
        output_path: str,
        language: str,
        temperature: float
    ):
        """Synchrone Audio-Generierung"""
        try:
            # XTTS V2 Inferenz
            wav = self.model.tts(
                text=text,
                speaker_wav=speaker_wav,
                language=language,
                temperature=temperature
            )
            
            # Audio speichern
            torchaudio.save(
                output_path,
                torch.tensor(wav).unsqueeze(0),
                22050
            )
            
        except Exception as e:
            logger.error(f"Fehler bei Audio-Generierung: {e}")
            raise
    
    async def _get_voice_reference(self, voice_id: str) -> str:
        """Voice-Referenz-Audio abrufen"""
        # Prüfen ob es eine geklonte Stimme ist
        voice_dir = Path(f"voices/{voice_id}")
        if voice_dir.exists():
            # Erste verfügbare Audio-Datei verwenden
            audio_files = list(voice_dir.glob("*.wav"))
            if audio_files:
                return str(audio_files[0])
        
        # Fallback: Standard-Stimme oder Fehler
        if voice_id == "default":
            # Standard-Referenz-Audio (sollte vorhanden sein)
            default_path = Path("assets/default_voice.wav")
            if default_path.exists():
                return str(default_path)
        
        raise ValueError(f"Voice-Referenz für {voice_id} nicht gefunden")
    
    async def _adjust_speed(self, audio_path: Path, speed: float):
        """Sprechgeschwindigkeit anpassen"""
        try:
            # Audio laden
            waveform, sample_rate = torchaudio.load(audio_path)
            
            # Geschwindigkeit anpassen (Time-stretching)
            if speed != 1.0:
                # Einfache Resampling-basierte Geschwindigkeitsanpassung
                new_sample_rate = int(sample_rate * speed)
                resampler = torchaudio.transforms.Resample(
                    orig_freq=sample_rate,
                    new_freq=new_sample_rate
                )
                waveform = resampler(waveform)
                
                # Zurück speichern
                torchaudio.save(audio_path, waveform, sample_rate)
                
        except Exception as e:
            logger.warning(f"Geschwindigkeitsanpassung fehlgeschlagen: {e}")
            # Nicht kritisch, Original-Audio bleibt erhalten
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Model-Informationen abrufen"""
        if not self.is_ready():
            return {"status": "not_ready"}
        
        return {
            "status": "ready",
            "model_name": self.model_path,
            "device": self.device,
            "languages": [
                "de", "en", "es", "fr", "it", "pt", "pl", "tr", "ru", 
                "nl", "cs", "ar", "zh", "ja", "hu", "ko"
            ]
        }