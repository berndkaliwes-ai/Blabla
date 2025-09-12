"""
Audio-Analyse für XTTS V2 Voice Cloning
Erweiterte Funktionen zur Audio-Qualitätsbewertung
"""

import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import asyncio
from dataclasses import dataclass

from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class AudioQualityMetrics:
    """Audio-Qualitäts-Metriken"""
    snr: float  # Signal-to-Noise Ratio
    spectral_centroid: float
    spectral_rolloff: float
    zero_crossing_rate: float
    mfcc_variance: float
    rms_energy: float
    silence_ratio: float
    quality_score: float  # 0-100

class AudioAnalyzer:
    def __init__(self):
        self.sample_rate = 22050
        self.frame_length = 2048
        self.hop_length = 512
        
    async def analyze_audio_quality(self, audio_path: Path) -> AudioQualityMetrics:
        """
        Umfassende Audio-Qualitätsanalyse
        
        Args:
            audio_path: Pfad zur Audio-Datei
            
        Returns:
            AudioQualityMetrics mit detaillierten Metriken
        """
        try:
            # Audio laden
            audio, sr = await asyncio.get_event_loop().run_in_executor(
                None, librosa.load, str(audio_path), self.sample_rate
            )
            
            # Verschiedene Metriken berechnen
            metrics = await self._calculate_metrics(audio, sr)
            
            # Gesamtqualitätsscore berechnen
            quality_score = self._calculate_quality_score(metrics)
            metrics['quality_score'] = quality_score
            
            return AudioQualityMetrics(**metrics)
            
        except Exception as e:
            logger.error(f"Fehler bei Audio-Analyse: {e}")
            raise
    
    async def _calculate_metrics(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Berechne verschiedene Audio-Metriken"""
        
        # Signal-to-Noise Ratio
        snr = self._calculate_snr(audio)
        
        # Spektrale Features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(
            y=audio, sr=sr, hop_length=self.hop_length
        )[0])
        
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(
            y=audio, sr=sr, hop_length=self.hop_length
        )[0])
        
        # Zero Crossing Rate
        zcr = np.mean(librosa.feature.zero_crossing_rate(
            audio, frame_length=self.frame_length, hop_length=self.hop_length
        )[0])
        
        # MFCC Varianz (Indikator für Sprachvielfalt)
        mfccs = librosa.feature.mfcc(
            y=audio, sr=sr, n_mfcc=13, hop_length=self.hop_length
        )
        mfcc_variance = np.mean(np.var(mfccs, axis=1))
        
        # RMS Energy
        rms = np.mean(librosa.feature.rms(
            y=audio, frame_length=self.frame_length, hop_length=self.hop_length
        )[0])
        
        # Stille-Verhältnis
        silence_ratio = self._calculate_silence_ratio(audio)
        
        return {
            'snr': float(snr),
            'spectral_centroid': float(spectral_centroid),
            'spectral_rolloff': float(spectral_rolloff),
            'zero_crossing_rate': float(zcr),
            'mfcc_variance': float(mfcc_variance),
            'rms_energy': float(rms),
            'silence_ratio': float(silence_ratio)
        }
    
    def _calculate_snr(self, audio: np.ndarray) -> float:
        """Signal-to-Noise Ratio berechnen"""
        try:
            # Einfache SNR-Schätzung basierend auf RMS-Werten
            # Obere 50% als Signal, untere 10% als Rauschen betrachten
            rms_values = librosa.feature.rms(y=audio, frame_length=2048)[0]
            
            signal_threshold = np.percentile(rms_values, 50)
            noise_threshold = np.percentile(rms_values, 10)
            
            if noise_threshold > 0:
                snr = 20 * np.log10(signal_threshold / noise_threshold)
                return max(0, min(60, snr))  # Begrenzen auf 0-60 dB
            else:
                return 60.0  # Maximaler SNR wenn kein Rauschen detektiert
                
        except Exception:
            return 30.0  # Fallback-Wert
    
    def _calculate_silence_ratio(self, audio: np.ndarray) -> float:
        """Verhältnis von Stille zu Sprache berechnen"""
        try:
            # RMS-basierte Stille-Detektion
            rms = librosa.feature.rms(y=audio, frame_length=2048)[0]
            threshold = np.percentile(rms, 20)  # Untere 20% als Stille
            
            silence_frames = np.sum(rms < threshold)
            total_frames = len(rms)
            
            return silence_frames / total_frames if total_frames > 0 else 1.0
            
        except Exception:
            return 0.5  # Fallback-Wert
    
    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """
        Gesamtqualitätsscore basierend auf verschiedenen Metriken
        Score von 0-100, wobei 100 die beste Qualität ist
        """
        try:
            score = 0.0
            
            # SNR (30% Gewichtung)
            snr_score = min(100, max(0, metrics['snr'] * 2))  # 0-30 dB -> 0-60 Punkte
            score += snr_score * 0.3
            
            # Stille-Verhältnis (20% Gewichtung)
            # Optimal: 10-30% Stille
            silence_ratio = metrics['silence_ratio']
            if 0.1 <= silence_ratio <= 0.3:
                silence_score = 100
            elif silence_ratio < 0.1:
                silence_score = silence_ratio * 1000  # Zu wenig Stille
            else:
                silence_score = max(0, 100 - (silence_ratio - 0.3) * 200)  # Zu viel Stille
            score += silence_score * 0.2
            
            # RMS Energy (15% Gewichtung)
            # Normalisierte Energie sollte im mittleren Bereich liegen
            rms_score = min(100, max(0, metrics['rms_energy'] * 500))
            score += rms_score * 0.15
            
            # MFCC Varianz (15% Gewichtung)
            # Höhere Varianz deutet auf mehr Sprachvielfalt hin
            mfcc_score = min(100, metrics['mfcc_variance'] * 10)
            score += mfcc_score * 0.15
            
            # Spektrale Features (20% Gewichtung)
            spectral_score = min(100, max(0, 
                (metrics['spectral_centroid'] / 4000) * 50 +  # Normalisiert auf 0-2000 Hz
                (metrics['spectral_rolloff'] / 8000) * 50     # Normalisiert auf 0-4000 Hz
            ))
            score += spectral_score * 0.2
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.warning(f"Fehler bei Qualitätsscore-Berechnung: {e}")
            return 50.0  # Fallback-Score
    
    async def get_audio_recommendations(self, metrics: AudioQualityMetrics) -> List[str]:
        """
        Empfehlungen zur Verbesserung der Audio-Qualität
        
        Args:
            metrics: Audio-Qualitäts-Metriken
            
        Returns:
            Liste von Empfehlungen
        """
        recommendations = []
        
        if metrics.quality_score < 30:
            recommendations.append("⚠️ Sehr niedrige Audio-Qualität - Aufnahme wiederholen empfohlen")
        elif metrics.quality_score < 50:
            recommendations.append("⚠️ Niedrige Audio-Qualität - Verbesserungen möglich")
        elif metrics.quality_score < 70:
            recommendations.append("✅ Akzeptable Audio-Qualität")
        else:
            recommendations.append("🎉 Hervorragende Audio-Qualität!")
        
        # Spezifische Empfehlungen
        if metrics.snr < 15:
            recommendations.append("🔇 Zu viel Hintergrundrauschen - ruhigere Umgebung verwenden")
        
        if metrics.silence_ratio > 0.5:
            recommendations.append("🤫 Zu viel Stille - kürzere Pausen zwischen Wörtern")
        elif metrics.silence_ratio < 0.05:
            recommendations.append("🗣️ Zu wenig Pausen - natürlichere Sprechweise verwenden")
        
        if metrics.rms_energy < 0.01:
            recommendations.append("📢 Audio zu leise - Aufnahmelautstärke erhöhen")
        elif metrics.rms_energy > 0.3:
            recommendations.append("🔊 Audio zu laut - Aufnahmelautstärke reduzieren")
        
        if metrics.mfcc_variance < 0.5:
            recommendations.append("🎭 Wenig Sprachvariation - expressiver sprechen")
        
        return recommendations
    
    async def compare_audio_files(self, audio_paths: List[Path]) -> Dict[str, any]:
        """
        Vergleiche mehrere Audio-Dateien und gebe Konsistenz-Metriken zurück
        
        Args:
            audio_paths: Liste von Audio-Dateien
            
        Returns:
            Vergleichsstatistiken
        """
        if len(audio_paths) < 2:
            return {"error": "Mindestens 2 Audio-Dateien für Vergleich erforderlich"}
        
        try:
            metrics_list = []
            
            # Alle Dateien analysieren
            for path in audio_paths:
                metrics = await self.analyze_audio_quality(path)
                metrics_list.append(metrics)
            
            # Konsistenz berechnen
            consistency_score = self._calculate_consistency(metrics_list)
            
            # Durchschnittswerte
            avg_quality = np.mean([m.quality_score for m in metrics_list])
            avg_snr = np.mean([m.snr for m in metrics_list])
            
            return {
                "file_count": len(audio_paths),
                "average_quality": float(avg_quality),
                "average_snr": float(avg_snr),
                "consistency_score": float(consistency_score),
                "quality_range": {
                    "min": float(min(m.quality_score for m in metrics_list)),
                    "max": float(max(m.quality_score for m in metrics_list))
                },
                "recommendations": await self._get_consistency_recommendations(
                    metrics_list, consistency_score
                )
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Audio-Vergleich: {e}")
            return {"error": str(e)}
    
    def _calculate_consistency(self, metrics_list: List[AudioQualityMetrics]) -> float:
        """Berechne Konsistenz zwischen Audio-Dateien"""
        try:
            # Standardabweichungen verschiedener Metriken
            quality_std = np.std([m.quality_score for m in metrics_list])
            snr_std = np.std([m.snr for m in metrics_list])
            rms_std = np.std([m.rms_energy for m in metrics_list])
            
            # Konsistenz-Score (niedrigere Standardabweichung = höhere Konsistenz)
            consistency = 100 - min(100, (quality_std + snr_std * 2 + rms_std * 100) / 3)
            
            return max(0, consistency)
            
        except Exception:
            return 50.0
    
    async def _get_consistency_recommendations(
        self, 
        metrics_list: List[AudioQualityMetrics], 
        consistency_score: float
    ) -> List[str]:
        """Empfehlungen für bessere Konsistenz"""
        recommendations = []
        
        if consistency_score < 50:
            recommendations.append("⚠️ Niedrige Konsistenz zwischen Audio-Dateien")
            recommendations.append("💡 Verwenden Sie das gleiche Mikrofon und die gleiche Umgebung")
            recommendations.append("💡 Halten Sie Abstand und Lautstärke konstant")
        elif consistency_score < 70:
            recommendations.append("✅ Akzeptable Konsistenz")
            recommendations.append("💡 Kleine Verbesserungen bei Aufnahmequalität möglich")
        else:
            recommendations.append("🎉 Sehr konsistente Audio-Qualität!")
        
        # Spezifische Inkonsistenzen
        quality_range = max(m.quality_score for m in metrics_list) - min(m.quality_score for m in metrics_list)
        if quality_range > 30:
            recommendations.append("📊 Große Qualitätsunterschiede zwischen Dateien")
        
        return recommendations