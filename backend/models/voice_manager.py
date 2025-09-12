"""
Voice Manager für XTTS V2 Voice Cloning
"""

import os
import json
import asyncio
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from schemas.api_models import VoiceInfo, VoiceStatus
from models.audio_processor import AudioProcessor
from utils.logger import get_logger

logger = get_logger(__name__)

class VoiceManager:
    def __init__(self):
        self.voices_dir = Path("voices")
        self.voices_db_path = Path("voices/voices.json")
        self.audio_processor = AudioProcessor()
        self.voices_cache: Dict[str, VoiceInfo] = {}
        
    async def initialize(self):
        """Voice Manager initialisieren"""
        try:
            # Verzeichnisse erstellen
            self.voices_dir.mkdir(exist_ok=True)
            
            # Voices-Datenbank laden
            await self._load_voices_db()
            
            # Cache aktualisieren
            await self._refresh_cache()
            
            logger.info("✅ Voice Manager initialisiert")
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Voice Manager Initialisierung: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Prüfen ob Manager bereit ist"""
        return self.voices_dir.exists()
    
    async def get_all_voices(self) -> List[VoiceInfo]:
        """Alle verfügbaren Stimmen abrufen"""
        await self._refresh_cache()
        return list(self.voices_cache.values())
    
    async def clone_voice(
        self,
        voice_id: str,
        name: str,
        description: str,
        audio_paths: List[Path]
    ):
        """
        Neue Stimme aus Audio-Dateien klonen
        
        Args:
            voice_id: Eindeutige Voice ID
            name: Name der Stimme
            description: Beschreibung
            audio_paths: Liste der Audio-Dateien
        """
        try:
            logger.info(f"🎭 Starte Voice Cloning für '{name}'")
            
            # Voice-Verzeichnis erstellen
            voice_dir = self.voices_dir / voice_id
            voice_dir.mkdir(exist_ok=True)
            
            # Status auf "processing" setzen
            voice_info = VoiceInfo(
                id=voice_id,
                name=name,
                description=description,
                status=VoiceStatus.PROCESSING,
                created_at=datetime.now(),
                sample_count=len(audio_paths)
            )
            
            await self._save_voice_info(voice_info)
            self.voices_cache[voice_id] = voice_info
            
            # Audio-Dateien verarbeiten
            processed_files = []
            total_duration = 0.0
            
            for i, audio_path in enumerate(audio_paths):
                try:
                    # Audio für Voice Cloning optimieren
                    processed_path = await self.audio_processor.process_for_cloning(
                        audio_path, 
                        voice_dir / f"sample_{i:03d}.wav"
                    )
                    
                    # Dauer ermitteln
                    duration = await self.audio_processor.get_duration(processed_path)
                    total_duration += duration
                    
                    processed_files.append(processed_path)
                    
                    # Original-Datei löschen
                    if audio_path != processed_path:
                        audio_path.unlink(missing_ok=True)
                        
                except Exception as e:
                    logger.warning(f"Fehler bei Audio-Verarbeitung {audio_path}: {e}")
                    continue
            
            if not processed_files:
                raise ValueError("Keine Audio-Dateien konnten verarbeitet werden")
            
            # Preview-Audio erstellen (erstes Sample)
            preview_path = voice_dir / "preview.wav"
            if processed_files:
                shutil.copy2(processed_files[0], preview_path)
            
            # Voice-Info aktualisieren
            voice_info.status = VoiceStatus.READY
            voice_info.duration = total_duration
            voice_info.sample_count = len(processed_files)
            voice_info.preview_url = f"/voices/{voice_id}/preview.wav"
            
            await self._save_voice_info(voice_info)
            self.voices_cache[voice_id] = voice_info
            
            logger.info(f"✅ Voice Cloning für '{name}' abgeschlossen")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Voice Cloning: {e}")
            
            # Fehler-Status setzen
            if voice_id in self.voices_cache:
                voice_info = self.voices_cache[voice_id]
                voice_info.status = VoiceStatus.ERROR
                await self._save_voice_info(voice_info)
            
            raise
    
    async def get_voice_status(self, voice_id: str) -> Dict[str, Any]:
        """Status einer Stimme abrufen"""
        if voice_id not in self.voices_cache:
            await self._refresh_cache()
        
        if voice_id not in self.voices_cache:
            raise ValueError(f"Voice {voice_id} nicht gefunden")
        
        voice_info = self.voices_cache[voice_id]
        
        return {
            "voice_id": voice_id,
            "status": voice_info.status.value,
            "name": voice_info.name,
            "description": voice_info.description,
            "sample_count": voice_info.sample_count,
            "duration": voice_info.duration,
            "created_at": voice_info.created_at.isoformat(),
            "preview_url": voice_info.preview_url
        }
    
    async def delete_voice(self, voice_id: str):
        """Stimme löschen"""
        try:
            # Aus Cache entfernen
            if voice_id in self.voices_cache:
                del self.voices_cache[voice_id]
            
            # Verzeichnis löschen
            voice_dir = self.voices_dir / voice_id
            if voice_dir.exists():
                shutil.rmtree(voice_dir)
            
            # Datenbank aktualisieren
            await self._save_voices_db()
            
            logger.info(f"✅ Voice {voice_id} gelöscht")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Löschen der Voice: {e}")
            raise
    
    async def _load_voices_db(self):
        """Voices-Datenbank laden"""
        if self.voices_db_path.exists():
            try:
                with open(self.voices_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for voice_data in data.get('voices', []):
                    voice_info = VoiceInfo(**voice_data)
                    self.voices_cache[voice_info.id] = voice_info
                    
            except Exception as e:
                logger.warning(f"Fehler beim Laden der Voices-DB: {e}")
    
    async def _save_voices_db(self):
        """Voices-Datenbank speichern"""
        try:
            data = {
                'voices': [
                    voice.dict() for voice in self.voices_cache.values()
                ],
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.voices_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Voices-DB: {e}")
    
    async def _save_voice_info(self, voice_info: VoiceInfo):
        """Einzelne Voice-Info speichern"""
        self.voices_cache[voice_info.id] = voice_info
        await self._save_voices_db()
    
    async def _refresh_cache(self):
        """Cache mit Dateisystem abgleichen"""
        try:
            # Alle Voice-Verzeichnisse scannen
            for voice_dir in self.voices_dir.iterdir():
                if voice_dir.is_dir() and voice_dir.name != "voices.json":
                    voice_id = voice_dir.name
                    
                    # Prüfen ob Voice im Cache ist
                    if voice_id not in self.voices_cache:
                        # Voice-Info aus Verzeichnis rekonstruieren
                        await self._reconstruct_voice_info(voice_id, voice_dir)
            
            # Nicht mehr existierende Voices aus Cache entfernen
            existing_dirs = {d.name for d in self.voices_dir.iterdir() if d.is_dir()}
            to_remove = [vid for vid in self.voices_cache.keys() if vid not in existing_dirs]
            
            for voice_id in to_remove:
                del self.voices_cache[voice_id]
            
            if to_remove:
                await self._save_voices_db()
                
        except Exception as e:
            logger.warning(f"Fehler beim Cache-Refresh: {e}")
    
    async def _reconstruct_voice_info(self, voice_id: str, voice_dir: Path):
        """Voice-Info aus Verzeichnis rekonstruieren"""
        try:
            # Audio-Dateien zählen
            audio_files = list(voice_dir.glob("*.wav"))
            sample_count = len([f for f in audio_files if not f.name.startswith("preview")])
            
            # Gesamtdauer berechnen
            total_duration = 0.0
            for audio_file in audio_files:
                if not audio_file.name.startswith("preview"):
                    duration = await self.audio_processor.get_duration(audio_file)
                    total_duration += duration
            
            # Voice-Info erstellen
            voice_info = VoiceInfo(
                id=voice_id,
                name=f"Voice {voice_id[:8]}",
                description="Rekonstruierte Stimme",
                status=VoiceStatus.READY,
                created_at=datetime.fromtimestamp(voice_dir.stat().st_ctime),
                sample_count=sample_count,
                duration=total_duration,
                preview_url=f"/voices/{voice_id}/preview.wav" if (voice_dir / "preview.wav").exists() else None
            )
            
            self.voices_cache[voice_id] = voice_info
            
        except Exception as e:
            logger.warning(f"Fehler bei Voice-Rekonstruktion {voice_id}: {e}")