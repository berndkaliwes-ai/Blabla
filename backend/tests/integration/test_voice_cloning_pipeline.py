"""
Integration Tests for Voice Cloning Pipeline
Tests the complete end-to-end voice cloning workflow
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient
from httpx import AsyncClient

from models.voice_manager import VoiceManager
from models.audio_processor import AudioProcessor
from models.audio_analyzer import AudioAnalyzer
from models.voice_trainer import VoiceTrainer, TrainingConfig
from schemas.api_models import VoiceStatus


@pytest.mark.integration
@pytest.mark.voice
class TestVoiceClonePipeline:
    """Test complete voice cloning pipeline"""
    
    @pytest.mark.asyncio
    async def test_complete_voice_clone_workflow(self, temp_dir, multiple_audio_files):
        """Test complete voice cloning workflow from upload to ready"""
        # Initialize components
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_dir.mkdir(exist_ok=True)
        
        audio_processor = AudioProcessor()
        voice_manager.audio_processor = audio_processor
        
        # Mock audio processing
        with patch.object(audio_processor, 'process_for_cloning') as mock_process, \
             patch.object(audio_processor, 'get_duration') as mock_duration, \
             patch.object(audio_processor, 'validate_audio') as mock_validate:
            
            mock_process.side_effect = lambda input_path, output_path: output_path
            mock_duration.return_value = 3.5
            mock_validate.return_value = True
            
            # Start voice cloning
            voice_id = "integration-test-voice"
            await voice_manager.clone_voice(
                voice_id=voice_id,
                name="Integration Test Voice",
                description="Voice created during integration testing",
                audio_paths=multiple_audio_files
            )
            
            # Verify voice was created
            assert voice_id in voice_manager.voices_cache
            voice_info = voice_manager.voices_cache[voice_id]
            
            assert voice_info.name == "Integration Test Voice"
            assert voice_info.status == VoiceStatus.READY
            assert voice_info.sample_count == len(multiple_audio_files)
            assert voice_info.duration > 0
            
            # Verify voice directory was created
            voice_dir = voice_manager.voices_dir / voice_id
            assert voice_dir.exists()
            
            # Verify processed files exist
            processed_files = list(voice_dir.glob("*.wav"))
            assert len(processed_files) >= len(multiple_audio_files)
    
    @pytest.mark.asyncio
    async def test_voice_clone_with_quality_analysis(self, temp_dir, multiple_audio_files):
        """Test voice cloning with audio quality analysis"""
        # Initialize components
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_dir.mkdir(exist_ok=True)
        
        audio_analyzer = AudioAnalyzer()
        audio_processor = AudioProcessor()
        voice_manager.audio_processor = audio_processor
        
        # Mock quality analysis
        with patch.object(audio_analyzer, 'analyze_audio_quality') as mock_analyze, \
             patch.object(audio_analyzer, 'compare_audio_files') as mock_compare, \
             patch.object(audio_processor, 'process_for_cloning') as mock_process, \
             patch.object(audio_processor, 'get_duration') as mock_duration:
            
            # Mock quality metrics
            from models.audio_analyzer import AudioQualityMetrics
            mock_analyze.return_value = AudioQualityMetrics(
                snr=25.0,
                spectral_centroid=2000.0,
                spectral_rolloff=4000.0,
                zero_crossing_rate=0.1,
                mfcc_variance=1.5,
                rms_energy=0.15,
                silence_ratio=0.2,
                quality_score=85.0
            )
            
            mock_compare.return_value = {
                "file_count": len(multiple_audio_files),
                "average_quality": 85.0,
                "consistency_score": 90.0,
                "recommendations": ["🎉 Sehr konsistente Audio-Qualität!"]
            }
            
            mock_process.side_effect = lambda input_path, output_path: output_path
            mock_duration.return_value = 3.0
            
            # Perform quality analysis before cloning
            quality_results = []
            for audio_file in multiple_audio_files:
                metrics = await audio_analyzer.analyze_audio_quality(audio_file)
                quality_results.append(metrics)
            
            # All files should have good quality
            assert all(metrics.quality_score > 80 for metrics in quality_results)
            
            # Compare files for consistency
            comparison = await audio_analyzer.compare_audio_files(multiple_audio_files)
            assert comparison["consistency_score"] > 85
            
            # Proceed with cloning
            voice_id = "quality-test-voice"
            await voice_manager.clone_voice(
                voice_id=voice_id,
                name="Quality Test Voice",
                description="Voice with quality analysis",
                audio_paths=multiple_audio_files
            )
            
            # Verify successful cloning
            assert voice_id in voice_manager.voices_cache
            voice_info = voice_manager.voices_cache[voice_id]
            assert voice_info.status == VoiceStatus.READY
    
    @pytest.mark.asyncio
    async def test_voice_clone_with_training_pipeline(self, temp_dir, multiple_audio_files):
        """Test voice cloning with advanced training pipeline"""
        # Initialize training components
        voice_trainer = VoiceTrainer()
        voice_trainer.audio_analyzer = AudioAnalyzer()
        voice_trainer.audio_processor = AudioProcessor()
        
        # Create training configuration
        config = TrainingConfig(
            voice_id="training-test-voice",
            name="Training Test Voice",
            description="Voice with advanced training",
            audio_files=multiple_audio_files,
            quality_threshold=70.0,
            min_duration=10.0,
            enable_quality_filter=True,
            enable_preprocessing=True
        )
        
        # Mock training components
        with patch.object(voice_trainer.audio_analyzer, 'analyze_audio_quality') as mock_analyze, \
             patch.object(voice_trainer.audio_analyzer, 'compare_audio_files') as mock_compare, \
             patch.object(voice_trainer.audio_processor, 'process_for_cloning') as mock_process, \
             patch.object(voice_trainer.audio_processor, 'get_duration') as mock_duration:
            
            # Mock quality analysis
            from models.audio_analyzer import AudioQualityMetrics
            mock_analyze.return_value = AudioQualityMetrics(
                snr=30.0,
                spectral_centroid=2200.0,
                spectral_rolloff=4200.0,
                zero_crossing_rate=0.12,
                mfcc_variance=1.8,
                rms_energy=0.18,
                silence_ratio=0.15,
                quality_score=88.0
            )
            
            mock_compare.return_value = {
                "file_count": len(multiple_audio_files),
                "average_quality": 88.0,
                "consistency_score": 92.0,
                "recommendations": ["🎉 Hervorragende Audio-Qualität!"]
            }
            
            mock_process.side_effect = lambda input_path, output_path: output_path
            mock_duration.return_value = 4.0
            
            # Start training
            session_id = await voice_trainer.start_training(config)
            
            # Wait for training to complete (mocked)
            await asyncio.sleep(0.1)  # Simulate training time
            
            # Check training progress
            progress = await voice_trainer.get_training_progress(session_id)
            assert progress is not None
            assert progress.voice_id == config.voice_id
            
            # Cleanup training session
            await voice_trainer.cleanup_session(session_id)
    
    @pytest.mark.asyncio
    async def test_voice_clone_error_recovery(self, temp_dir, multiple_audio_files):
        """Test voice cloning error recovery mechanisms"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_dir.mkdir(exist_ok=True)
        
        audio_processor = AudioProcessor()
        voice_manager.audio_processor = audio_processor
        
        # Simulate processing error on second file
        def mock_process_with_error(input_path, output_path):
            if "sample_audio_1" in str(input_path):
                raise Exception("Simulated processing error")
            return output_path
        
        with patch.object(audio_processor, 'process_for_cloning', side_effect=mock_process_with_error), \
             patch.object(audio_processor, 'get_duration', return_value=3.0):
            
            voice_id = "error-recovery-voice"
            await voice_manager.clone_voice(
                voice_id=voice_id,
                name="Error Recovery Voice",
                description="Testing error recovery",
                audio_paths=multiple_audio_files
            )
            
            # Voice should still be created but with fewer samples
            assert voice_id in voice_manager.voices_cache
            voice_info = voice_manager.voices_cache[voice_id]
            
            # Should have processed some files despite error
            assert voice_info.sample_count < len(multiple_audio_files)
            assert voice_info.sample_count > 0


@pytest.mark.integration
@pytest.mark.api
class TestVoiceCloneAPIIntegration:
    """Test voice cloning API integration"""
    
    @pytest.mark.asyncio
    async def test_api_voice_clone_complete_workflow(self, async_client: AsyncClient, multiple_audio_files):
        """Test complete API workflow for voice cloning"""
        # Prepare multipart form data
        files = []
        for i, audio_file in enumerate(multiple_audio_files):
            with open(audio_file, 'rb') as f:
                files.append(("files", (f"audio_{i}.wav", f.read(), "audio/wav")))
        
        data = {
            "name": "API Test Voice",
            "description": "Voice created via API integration test"
        }
        
        # Mock the voice cloning process
        with patch('models.voice_manager.VoiceManager.clone_voice') as mock_clone:
            mock_clone.return_value = "api-test-voice-123"
            
            # Start voice cloning
            response = await async_client.post(
                "/api/voices/clone",
                data=data,
                files=files
            )
            
            assert response.status_code == 200
            result = response.json()
            
            assert "voice_id" in result
            assert result["status"] == "processing"
            assert "API Test Voice" in result["message"]
            
            voice_id = result["voice_id"]
            
            # Check voice status
            with patch('models.voice_manager.VoiceManager.get_voice_status') as mock_status:
                mock_status.return_value = {
                    "voice_id": voice_id,
                    "status": "ready",
                    "name": "API Test Voice",
                    "sample_count": len(multiple_audio_files)
                }
                
                status_response = await async_client.get(f"/api/voices/{voice_id}/status")
                assert status_response.status_code == 200
                
                status_data = status_response.json()
                assert status_data["voice_id"] == voice_id
                assert status_data["status"] == "ready"
    
    @pytest.mark.asyncio
    async def test_api_voice_clone_with_validation_errors(self, async_client: AsyncClient):
        """Test API voice cloning with validation errors"""
        # Test missing name
        response = await async_client.post(
            "/api/voices/clone",
            data={"description": "Test description"}
        )
        assert response.status_code == 422
        
        # Test missing files
        response = await async_client.post(
            "/api/voices/clone",
            data={"name": "Test Voice", "description": "Test description"}
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_api_voice_clone_large_files(self, async_client: AsyncClient, temp_dir):
        """Test API voice cloning with large files"""
        # Create a large audio file (simulated)
        large_audio_file = temp_dir / "large_audio.wav"
        
        # Create 30 seconds of audio data
        sample_rate = 22050
        duration = 30.0
        audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
        sf.write(large_audio_file, audio_data, sample_rate)
        
        with open(large_audio_file, 'rb') as f:
            files = [("files", ("large_audio.wav", f.read(), "audio/wav"))]
        
        data = {
            "name": "Large File Test Voice",
            "description": "Testing large file upload"
        }
        
        with patch('models.voice_manager.VoiceManager.clone_voice') as mock_clone:
            mock_clone.return_value = "large-file-voice-123"
            
            response = await async_client.post(
                "/api/voices/clone",
                data=data,
                files=files
            )
            
            assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.voice
class TestVoiceCloneDataPersistence:
    """Test voice cloning data persistence"""
    
    @pytest.mark.asyncio
    async def test_voice_data_persistence_across_restarts(self, temp_dir, multiple_audio_files):
        """Test that voice data persists across application restarts"""
        # First instance - create voice
        voice_manager1 = VoiceManager()
        voice_manager1.voices_dir = temp_dir / "voices"
        voice_manager1.voices_dir.mkdir(exist_ok=True)
        voice_manager1.voices_db_path = voice_manager1.voices_dir / "voices.json"
        
        audio_processor = AudioProcessor()
        voice_manager1.audio_processor = audio_processor
        
        with patch.object(audio_processor, 'process_for_cloning') as mock_process, \
             patch.object(audio_processor, 'get_duration') as mock_duration:
            
            mock_process.side_effect = lambda input_path, output_path: output_path
            mock_duration.return_value = 3.0
            
            voice_id = "persistence-test-voice"
            await voice_manager1.clone_voice(
                voice_id=voice_id,
                name="Persistence Test Voice",
                description="Testing data persistence",
                audio_paths=multiple_audio_files
            )
            
            # Verify voice was created
            assert voice_id in voice_manager1.voices_cache
            
            # Save to database
            await voice_manager1._save_voices_db()
        
        # Second instance - load existing data (simulating restart)
        voice_manager2 = VoiceManager()
        voice_manager2.voices_dir = temp_dir / "voices"
        voice_manager2.voices_db_path = voice_manager2.voices_dir / "voices.json"
        
        await voice_manager2.initialize()
        
        # Verify voice was loaded
        assert voice_id in voice_manager2.voices_cache
        voice_info = voice_manager2.voices_cache[voice_id]
        assert voice_info.name == "Persistence Test Voice"
        assert voice_info.status == VoiceStatus.READY
    
    @pytest.mark.asyncio
    async def test_voice_directory_reconstruction(self, temp_dir):
        """Test voice reconstruction from directory structure"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_dir.mkdir(exist_ok=True)
        voice_manager.audio_processor = AudioProcessor()
        
        # Create orphaned voice directory (without database entry)
        orphaned_voice_id = "orphaned-voice"
        orphaned_dir = voice_manager.voices_dir / orphaned_voice_id
        orphaned_dir.mkdir()
        
        # Create mock audio files in orphaned directory
        for i in range(3):
            audio_file = orphaned_dir / f"sample_{i:03d}.wav"
            audio_file.write_text("mock audio data")
        
        # Create preview file
        preview_file = orphaned_dir / "preview.wav"
        preview_file.write_text("mock preview data")
        
        with patch.object(voice_manager.audio_processor, 'get_duration', return_value=2.5):
            await voice_manager.initialize()
        
        # Verify orphaned voice was reconstructed
        assert orphaned_voice_id in voice_manager.voices_cache
        voice_info = voice_manager.voices_cache[orphaned_voice_id]
        assert voice_info.sample_count == 3
        assert voice_info.status == VoiceStatus.READY


@pytest.mark.integration
@pytest.mark.voice
@pytest.mark.slow
class TestVoiceClonePerformance:
    """Test voice cloning performance under various conditions"""
    
    @pytest.mark.asyncio
    async def test_concurrent_voice_cloning(self, temp_dir):
        """Test concurrent voice cloning operations"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_dir.mkdir(exist_ok=True)
        
        audio_processor = AudioProcessor()
        voice_manager.audio_processor = audio_processor
        
        # Create multiple sets of audio files
        audio_file_sets = []
        for i in range(3):
            file_set = []
            for j in range(2):
                audio_file = temp_dir / f"concurrent_audio_{i}_{j}.wav"
                # Create mock audio data
                audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
                sf.write(audio_file, audio_data, 22050)
                file_set.append(audio_file)
            audio_file_sets.append(file_set)
        
        with patch.object(audio_processor, 'process_for_cloning') as mock_process, \
             patch.object(audio_processor, 'get_duration') as mock_duration:
            
            mock_process.side_effect = lambda input_path, output_path: output_path
            mock_duration.return_value = 3.0
            
            # Start concurrent voice cloning operations
            tasks = []
            for i, file_set in enumerate(audio_file_sets):
                task = voice_manager.clone_voice(
                    voice_id=f"concurrent-voice-{i}",
                    name=f"Concurrent Voice {i}",
                    description=f"Concurrent test voice {i}",
                    audio_paths=file_set
                )
                tasks.append(task)
            
            # Wait for all operations to complete
            await asyncio.gather(*tasks)
            
            # Verify all voices were created
            for i in range(3):
                voice_id = f"concurrent-voice-{i}"
                assert voice_id in voice_manager.voices_cache
                voice_info = voice_manager.voices_cache[voice_id]
                assert voice_info.status == VoiceStatus.READY
    
    @pytest.mark.asyncio
    async def test_voice_cloning_memory_efficiency(self, temp_dir):
        """Test memory efficiency during voice cloning"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_dir.mkdir(exist_ok=True)
        
        audio_processor = AudioProcessor()
        voice_manager.audio_processor = audio_processor
        
        # Create multiple large audio files
        large_audio_files = []
        for i in range(5):
            audio_file = temp_dir / f"large_audio_{i}.wav"
            # Create 60 seconds of audio
            audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 60, 22050 * 60))
            sf.write(audio_file, audio_data, 22050)
            large_audio_files.append(audio_file)
        
        with patch.object(audio_processor, 'process_for_cloning') as mock_process, \
             patch.object(audio_processor, 'get_duration') as mock_duration:
            
            mock_process.side_effect = lambda input_path, output_path: output_path
            mock_duration.return_value = 60.0
            
            await voice_manager.clone_voice(
                voice_id="memory-test-voice",
                name="Memory Test Voice",
                description="Testing memory efficiency",
                audio_paths=large_audio_files
            )
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 1GB)
        assert memory_increase < 1024 * 1024 * 1024
    
    @pytest.mark.asyncio
    async def test_voice_cloning_with_many_files(self, temp_dir):
        """Test voice cloning with many audio files"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_dir.mkdir(exist_ok=True)
        
        audio_processor = AudioProcessor()
        voice_manager.audio_processor = audio_processor
        
        # Create many small audio files
        many_audio_files = []
        for i in range(50):
            audio_file = temp_dir / f"many_audio_{i}.wav"
            # Create 2 seconds of audio
            audio_data = np.sin(2 * np.pi * (440 + i * 10) * np.linspace(0, 2, 44100))
            sf.write(audio_file, audio_data, 22050)
            many_audio_files.append(audio_file)
        
        with patch.object(audio_processor, 'process_for_cloning') as mock_process, \
             patch.object(audio_processor, 'get_duration') as mock_duration:
            
            mock_process.side_effect = lambda input_path, output_path: output_path
            mock_duration.return_value = 2.0
            
            start_time = asyncio.get_event_loop().time()
            
            await voice_manager.clone_voice(
                voice_id="many-files-voice",
                name="Many Files Voice",
                description="Testing with many files",
                audio_paths=many_audio_files
            )
            
            end_time = asyncio.get_event_loop().time()
            processing_time = end_time - start_time
            
            # Should complete within reasonable time (less than 30 seconds)
            assert processing_time < 30.0
            
            # Verify voice was created successfully
            assert "many-files-voice" in voice_manager.voices_cache
            voice_info = voice_manager.voices_cache["many-files-voice"]
            assert voice_info.sample_count == len(many_audio_files)
            assert voice_info.status == VoiceStatus.READY