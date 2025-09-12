"""
Audio-Verarbeitung für XTTS V2 Voice Cloning
"""

import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import asyncio

from utils.logger import get_logger

logger = get_logger(__name__)

class AudioProcessor:
    def __init__(self):
        self.target_sample_rate = 22050
        self.min_duration = 3.0  # Mindestens 3 Sekunden
        self.max_duration = 30.0  # Maximal 30 Sekunden
        
    async def process_for_cloning(
        self, 
        input_path: Path, 
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Audio-Datei für Voice Cloning optimieren
        
        Args:
            input_path: Eingabe-Audio-Datei
            output_path: Ausgabe-Pfad (optional)
            
        Returns:
            Pfad zur verarbeiteten Audio-Datei
        """
        try:
            if output_path is None:
                output_path = input_path.with_suffix('.processed.wav')
            
            # Audio laden
            audio, sr = await asyncio.get_event_loop().run_in_executor(
                None, librosa.load, str(input_path), None
            )
            
            logger.info(f"🎵 Verarbeite Audio: {input_path.name} ({len(audio)/sr:.1f}s, {sr}Hz)")
            
            # Audio-Verarbeitung
            processed_audio = await self._process_audio(audio, sr)
            
            # Verarbeitetes Audio speichern
            await asyncio.get_event_loop().run_in_executor(
                None,
                sf.write,
                str(output_path),
                processed_audio,
                self.target_sample_rate
            )
            
            logger.info(f"✅ Audio verarbeitet: {output_path.name}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Audio-Verarbeitung: {e}")
            raise
    
    async def _process_audio(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Audio-Verarbeitung durchführen"""
        
        # 1. Resampling auf Ziel-Sample-Rate
        if sr != self.target_sample_rate:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.target_sample_rate)
            sr = self.target_sample_rate
        
        # 2. Mono-Konvertierung
        if len(audio.shape) > 1:
            audio = librosa.to_mono(audio)
        
        # 3. Normalisierung
        audio = librosa.util.normalize(audio)
        
        # 4. Stille am Anfang und Ende entfernen
        audio, _ = librosa.effects.trim(audio, top_db=20)
        
        # 5. Länge prüfen und anpassen
        duration = len(audio) / sr
        
        if duration < self.min_duration:
            # Zu kurz: Padding hinzufügen oder wiederholen
            if duration > 1.0:
                # Wiederholen bis Mindestlänge erreicht
                repeat_count = int(np.ceil(self.min_duration / duration))
                audio = np.tile(audio, repeat_count)
                # Auf exakte Länge kürzen
                target_length = int(self.min_duration * sr)
                audio = audio[:target_length]
            else:
                # Zu kurz für Wiederholung: Padding
                target_length = int(self.min_duration * sr)
                padding = target_length - len(audio)
                audio = np.pad(audio, (0, padding), mode='constant')
        
        elif duration > self.max_duration:
            # Zu lang: Auf maximale Länge kürzen
            target_length = int(self.max_duration * sr)
            audio = audio[:target_length]
        
        # 6. Rauschunterdrückung (einfach)
        audio = self._simple_noise_reduction(audio)
        
        # 7. Finale Normalisierung
        audio = librosa.util.normalize(audio)
        
        return audio
    
    def _simple_noise_reduction(self, audio: np.ndarray) -> np.ndarray:
        """Einfache Rauschunterdrückung"""
        try:
            # Spectral Gating für Rauschunterdrückung
            # Berechne RMS-Energie in kleinen Fenstern
            frame_length = 2048
            hop_length = 512
            
            # RMS-Energie berechnen
            rms = librosa.feature.rms(
                y=audio, 
                frame_length=frame_length, 
                hop_length=hop_length
            )[0]
            
            # Schwellwert für Stille (untere 10% der RMS-Werte)
            threshold = np.percentile(rms, 10)
            
            # Maske für Bereiche über dem Schwellwert
            mask = rms > threshold
            
            # Maske auf Audio-Länge interpolieren
            mask_interp = np.interp(
                np.arange(len(audio)),
                np.arange(len(mask)) * hop_length,
                mask.astype(float)
            )
            
            # Sanfte Maskierung anwenden
            audio = audio * np.maximum(mask_interp, 0.1)
            
            return audio
            
        except Exception as e:
            logger.warning(f"Rauschunterdrückung fehlgeschlagen: {e}")
            return audio
    
    async def get_duration(self, audio_path: Path) -> float:
        """Audio-Dauer ermitteln"""
        try:
            info = await asyncio.get_event_loop().run_in_executor(
                None, sf.info, str(audio_path)
            )
            return info.duration
        except Exception as e:
            logger.warning(f"Fehler bei Dauer-Ermittlung: {e}")
            return 0.0
    
    async def get_audio_info(self, audio_path: Path) -> dict:
        """Detaillierte Audio-Informationen"""
        try:
            info = await asyncio.get_event_loop().run_in_executor(
                None, sf.info, str(audio_path)
            )
            
            return {
                "duration": info.duration,
                "sample_rate": info.samplerate,
                "channels": info.channels,
                "frames": info.frames,
                "format": info.format,
                "subtype": info.subtype
            }
        except Exception as e:
            logger.error(f"Fehler bei Audio-Info: {e}")
            return {}
    
    async def validate_audio(self, audio_path: Path) -> bool:
        """Audio-Datei validieren"""
        try:
            info = await self.get_audio_info(audio_path)
            
            # Mindestanforderungen prüfen
            if info.get("duration", 0) < 1.0:
                logger.warning(f"Audio zu kurz: {info.get('duration', 0)}s")
                return False
            
            if info.get("sample_rate", 0) < 8000:
                logger.warning(f"Sample-Rate zu niedrig: {info.get('sample_rate', 0)}Hz")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Audio-Validierung fehlgeschlagen: {e}")
            return False