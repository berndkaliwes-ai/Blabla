"""
Voice Training Manager für XTTS V2
Erweiterte Funktionen für Voice Cloning Training
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

from models.audio_analyzer import AudioAnalyzer, AudioQualityMetrics
from models.audio_processor import AudioProcessor
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class TrainingProgress:
    """Training-Fortschritt für Voice Cloning"""
    voice_id: str
    stage: str  # 'preprocessing', 'analysis', 'training', 'validation', 'completed', 'error'
    progress: float  # 0.0 - 1.0
    message: str
    started_at: datetime
    updated_at: datetime
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None

@dataclass
class TrainingConfig:
    """Konfiguration für Voice Training"""
    voice_id: str
    name: str
    description: str
    audio_files: List[Path]
    quality_threshold: float = 50.0
    min_duration: float = 10.0  # Mindest-Gesamtdauer in Sekunden
    max_files: int = 20
    enable_quality_filter: bool = True
    enable_preprocessing: bool = True

class VoiceTrainer:
    def __init__(self):
        self.audio_analyzer = AudioAnalyzer()
        self.audio_processor = AudioProcessor()
        self.training_sessions: Dict[str, TrainingProgress] = {}
        self.progress_callbacks: Dict[str, List[Callable]] = {}
        
    async def start_training(
        self, 
        config: TrainingConfig,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """
        Starte Voice Training mit erweiterten Features
        
        Args:
            config: Training-Konfiguration
            progress_callback: Callback für Fortschritts-Updates
            
        Returns:
            Training Session ID
        """
        session_id = str(uuid.uuid4())
        
        # Progress tracking initialisieren
        progress = TrainingProgress(
            voice_id=config.voice_id,
            stage='preprocessing',
            progress=0.0,
            message='Training wird vorbereitet...',
            started_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.training_sessions[session_id] = progress
        
        if progress_callback:
            if session_id not in self.progress_callbacks:
                self.progress_callbacks[session_id] = []
            self.progress_callbacks[session_id].append(progress_callback)
        
        # Training im Hintergrund starten
        asyncio.create_task(self._run_training(session_id, config))
        
        return session_id
    
    async def _run_training(self, session_id: str, config: TrainingConfig):
        """Führe das komplette Training durch"""
        try:
            # Stage 1: Audio-Analyse und Qualitätsprüfung
            await self._update_progress(
                session_id, 'analysis', 0.1, 
                'Analysiere Audio-Qualität...'
            )
            
            quality_results = await self._analyze_audio_quality(config)
            
            if config.enable_quality_filter:
                filtered_files = await self._filter_by_quality(
                    config.audio_files, config.quality_threshold
                )
                config.audio_files = filtered_files
            
            # Stage 2: Audio-Preprocessing
            await self._update_progress(
                session_id, 'preprocessing', 0.3,
                'Verarbeite Audio-Dateien...'
            )
            
            if config.enable_preprocessing:
                processed_files = await self._preprocess_audio_files(config)
                config.audio_files = processed_files
            
            # Stage 3: Validierung
            await self._update_progress(
                session_id, 'validation', 0.6,
                'Validiere Training-Daten...'
            )
            
            validation_result = await self._validate_training_data(config)
            if not validation_result['valid']:
                raise ValueError(validation_result['error'])
            
            # Stage 4: Voice Model Training (simuliert)
            await self._update_progress(
                session_id, 'training', 0.7,
                'Trainiere Voice Model...'
            )
            
            await self._simulate_model_training(session_id, config)
            
            # Stage 5: Abschluss
            await self._update_progress(
                session_id, 'completed', 1.0,
                'Training erfolgreich abgeschlossen!'
            )
            
            # Training-Ergebnisse speichern
            await self._save_training_results(session_id, config, quality_results)
            
        except Exception as e:
            logger.error(f"Training-Fehler für Session {session_id}: {e}")
            await self._update_progress(
                session_id, 'error', 0.0,
                f'Training fehlgeschlagen: {str(e)}',
                error_message=str(e)
            )
    
    async def _analyze_audio_quality(self, config: TrainingConfig) -> Dict:
        """Analysiere Qualität aller Audio-Dateien"""
        results = {
            'files': [],
            'average_quality': 0.0,
            'consistency_score': 0.0,
            'recommendations': []
        }
        
        try:
            # Einzelne Dateien analysieren
            quality_scores = []
            for i, audio_file in enumerate(config.audio_files):
                metrics = await self.audio_analyzer.analyze_audio_quality(audio_file)
                recommendations = await self.audio_analyzer.get_audio_recommendations(metrics)
                
                results['files'].append({
                    'file': str(audio_file),
                    'quality_score': metrics.quality_score,
                    'snr': metrics.snr,
                    'recommendations': recommendations
                })
                
                quality_scores.append(metrics.quality_score)
            
            # Gesamtstatistiken
            if quality_scores:
                results['average_quality'] = sum(quality_scores) / len(quality_scores)
                
                # Konsistenz-Analyse
                comparison = await self.audio_analyzer.compare_audio_files(config.audio_files)
                results['consistency_score'] = comparison.get('consistency_score', 0.0)
                results['recommendations'] = comparison.get('recommendations', [])
            
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei Audio-Qualitäts-Analyse: {e}")
            return results
    
    async def _filter_by_quality(
        self, 
        audio_files: List[Path], 
        threshold: float
    ) -> List[Path]:
        """Filtere Audio-Dateien nach Qualität"""
        filtered_files = []
        
        for audio_file in audio_files:
            try:
                metrics = await self.audio_analyzer.analyze_audio_quality(audio_file)
                if metrics.quality_score >= threshold:
                    filtered_files.append(audio_file)
                else:
                    logger.info(f"Datei {audio_file.name} gefiltert (Qualität: {metrics.quality_score:.1f})")
            except Exception as e:
                logger.warning(f"Fehler bei Qualitätsprüfung für {audio_file}: {e}")
        
        return filtered_files
    
    async def _preprocess_audio_files(self, config: TrainingConfig) -> List[Path]:
        """Erweiterte Audio-Vorverarbeitung"""
        processed_files = []
        voice_dir = Path(f"voices/{config.voice_id}")
        
        for i, audio_file in enumerate(config.audio_files):
            try:
                # Verarbeitete Datei speichern
                output_path = voice_dir / f"processed_{i:03d}.wav"
                
                # Erweiterte Verarbeitung
                processed_path = await self.audio_processor.process_for_cloning(
                    audio_file, output_path
                )
                
                processed_files.append(processed_path)
                
            except Exception as e:
                logger.warning(f"Fehler bei Verarbeitung von {audio_file}: {e}")
        
        return processed_files
    
    async def _validate_training_data(self, config: TrainingConfig) -> Dict:
        """Validiere Training-Daten"""
        try:
            # Mindestanzahl Dateien
            if len(config.audio_files) < 3:
                return {
                    'valid': False,
                    'error': 'Mindestens 3 Audio-Dateien erforderlich'
                }
            
            # Gesamtdauer prüfen
            total_duration = 0.0
            for audio_file in config.audio_files:
                duration = await self.audio_processor.get_duration(audio_file)
                total_duration += duration
            
            if total_duration < config.min_duration:
                return {
                    'valid': False,
                    'error': f'Gesamtdauer zu kurz: {total_duration:.1f}s (min: {config.min_duration}s)'
                }
            
            # Maximale Anzahl Dateien
            if len(config.audio_files) > config.max_files:
                return {
                    'valid': False,
                    'error': f'Zu viele Dateien: {len(config.audio_files)} (max: {config.max_files})'
                }
            
            return {
                'valid': True,
                'total_duration': total_duration,
                'file_count': len(config.audio_files)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validierungsfehler: {str(e)}'
            }
    
    async def _simulate_model_training(self, session_id: str, config: TrainingConfig):
        """Simuliere Model-Training mit realistischen Fortschritts-Updates"""
        training_steps = [
            (0.7, "Initialisiere Training..."),
            (0.75, "Lade Basis-Model..."),
            (0.8, "Verarbeite Audio-Features..."),
            (0.85, "Trainiere Voice Embeddings..."),
            (0.9, "Optimiere Model-Parameter..."),
            (0.95, "Validiere Model-Qualität..."),
            (0.98, "Speichere trainiertes Model..."),
        ]
        
        for progress, message in training_steps:
            await self._update_progress(session_id, 'training', progress, message)
            # Simuliere Verarbeitungszeit
            await asyncio.sleep(2)
    
    async def _save_training_results(
        self, 
        session_id: str, 
        config: TrainingConfig, 
        quality_results: Dict
    ):
        """Speichere Training-Ergebnisse"""
        try:
            voice_dir = Path(f"voices/{config.voice_id}")
            results_file = voice_dir / "training_results.json"
            
            results = {
                'session_id': session_id,
                'voice_id': config.voice_id,
                'name': config.name,
                'description': config.description,
                'training_config': asdict(config),
                'quality_analysis': quality_results,
                'completed_at': datetime.now().isoformat(),
                'file_count': len(config.audio_files),
                'total_duration': sum([
                    await self.audio_processor.get_duration(f) 
                    for f in config.audio_files
                ])
            }
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Training-Ergebnisse gespeichert: {results_file}")
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Training-Ergebnisse: {e}")
    
    async def _update_progress(
        self, 
        session_id: str, 
        stage: str, 
        progress: float, 
        message: str,
        error_message: Optional[str] = None
    ):
        """Aktualisiere Training-Fortschritt"""
        if session_id in self.training_sessions:
            session = self.training_sessions[session_id]
            session.stage = stage
            session.progress = progress
            session.message = message
            session.updated_at = datetime.now()
            
            if error_message:
                session.error_message = error_message
            
            # Geschätzte Fertigstellung berechnen
            if progress > 0 and stage != 'error':
                elapsed = (datetime.now() - session.started_at).total_seconds()
                estimated_total = elapsed / progress
                remaining = estimated_total - elapsed
                session.estimated_completion = datetime.now().timestamp() + remaining
            
            # Callbacks benachrichtigen
            if session_id in self.progress_callbacks:
                for callback in self.progress_callbacks[session_id]:
                    try:
                        await callback(session)
                    except Exception as e:
                        logger.warning(f"Callback-Fehler: {e}")
    
    async def get_training_progress(self, session_id: str) -> Optional[TrainingProgress]:
        """Hole Training-Fortschritt"""
        return self.training_sessions.get(session_id)
    
    async def cancel_training(self, session_id: str) -> bool:
        """Breche Training ab"""
        if session_id in self.training_sessions:
            await self._update_progress(
                session_id, 'error', 0.0, 
                'Training abgebrochen', 
                error_message='Training wurde vom Benutzer abgebrochen'
            )
            return True
        return False
    
    async def cleanup_session(self, session_id: str):
        """Räume Training-Session auf"""
        if session_id in self.training_sessions:
            del self.training_sessions[session_id]
        
        if session_id in self.progress_callbacks:
            del self.progress_callbacks[session_id]