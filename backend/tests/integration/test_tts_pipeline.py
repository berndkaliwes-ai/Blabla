"""
Integration Tests for Text-to-Speech Pipeline
Tests the complete TTS workflow from text input to audio output
"""

import pytest
import asyncio
import numpy as np
import soundfile as sf
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient

from models.tts_service import XTTSService
from models.voice_manager import VoiceManager
from models.audio_processor import AudioProcessor
from schemas.api_models import VoiceInfo, VoiceStatus


@pytest.mark.integration
@pytest.mark.tts
class TestTTSPipeline:
    """Test complete Text-to-Speech pipeline"""
    
    @pytest.mark.asyncio
    async def test_complete_tts_workflow(self, temp_dir, mock_voice_data):
        """Test complete TTS workflow from text to audio"""
        # Initialize TTS service
        tts_service = XTTSService()
        tts_service.device = "cpu"  # Use CPU for testing
        
        # Mock XTTS model
        mock_model = MagicMock()
        mock_model.tts.return_value = np.sin(2 * np.pi * 440 * np.linspace(0, 5, 110250))  # 5 seconds of audio
        tts_service.model = mock_model
        tts_service.is_initialized = True
        
        # Create voice reference
        voice_id = mock_voice_data["id"]
        voice_dir = temp_dir / "voices" / voice_id
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        # Create mock reference audio
        reference_audio = voice_dir / "sample_000.wav"
        audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
        sf.write(reference_audio, audio_data, 22050)
        
        # Create outputs directory
        outputs_dir = temp_dir / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            # Generate speech
            output_path = await tts_service.generate_speech(
                text="Hello, this is a test message for text-to-speech generation.",
                voice_id=voice_id,
                language="en",
                speed=1.0,
                temperature=0.7
            )
            
            # Verify output file was created
            assert Path(output_path).exists()
            
            # Verify audio properties
            audio_info = sf.info(output_path)
            assert audio_info.samplerate == 22050
            assert audio_info.duration > 0
    
    @pytest.mark.asyncio
    async def test_tts_with_different_languages(self, temp_dir, mock_voice_data):
        """Test TTS generation with different languages"""
        tts_service = XTTSService()
        tts_service.device = "cpu"
        
        # Mock XTTS model
        mock_model = MagicMock()
        mock_model.tts.return_value = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
        tts_service.model = mock_model
        tts_service.is_initialized = True
        
        # Create voice reference
        voice_id = mock_voice_data["id"]
        voice_dir = temp_dir / "voices" / voice_id
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        reference_audio = voice_dir / "sample_000.wav"
        audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
        sf.write(reference_audio, audio_data, 22050)
        
        outputs_dir = temp_dir / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        # Test different languages
        languages = ["en", "de", "es", "fr", "it"]
        texts = {
            "en": "Hello, how are you today?",
            "de": "Hallo, wie geht es dir heute?",
            "es": "Hola, ¿cómo estás hoy?",
            "fr": "Bonjour, comment allez-vous aujourd'hui?",
            "it": "Ciao, come stai oggi?"
        }
        
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            for language in languages:
                output_path = await tts_service.generate_speech(
                    text=texts[language],
                    voice_id=voice_id,
                    language=language,
                    speed=1.0,
                    temperature=0.7
                )
                
                # Verify output was created
                assert Path(output_path).exists()
                
                # Verify model was called with correct language
                mock_model.tts.assert_called()
                call_args = mock_model.tts.call_args
                assert call_args[1]["language"] == language
    
    @pytest.mark.asyncio
    async def test_tts_with_speed_variations(self, temp_dir, mock_voice_data):
        """Test TTS generation with different speed settings"""
        tts_service = XTTSService()
        tts_service.device = "cpu"
        
        # Mock XTTS model and audio processing
        mock_model = MagicMock()
        mock_model.tts.return_value = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
        tts_service.model = mock_model
        tts_service.is_initialized = True
        
        # Create voice reference
        voice_id = mock_voice_data["id"]
        voice_dir = temp_dir / "voices" / voice_id
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        reference_audio = voice_dir / "sample_000.wav"
        audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
        sf.write(reference_audio, audio_data, 22050)
        
        outputs_dir = temp_dir / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        # Test different speeds
        speeds = [0.5, 0.8, 1.0, 1.5, 2.0]
        
        with patch('pathlib.Path.cwd', return_value=temp_dir), \
             patch.object(tts_service, '_adjust_speed', new_callable=AsyncMock) as mock_adjust:
            
            for speed in speeds:
                output_path = await tts_service.generate_speech(
                    text="This is a speed test message.",
                    voice_id=voice_id,
                    language="en",
                    speed=speed,
                    temperature=0.7
                )
                
                # Verify output was created
                assert Path(output_path).exists()
                
                # Verify speed adjustment was called for non-default speeds
                if speed != 1.0:
                    mock_adjust.assert_called()
    
    @pytest.mark.asyncio
    async def test_tts_error_handling(self, temp_dir, mock_voice_data):
        """Test TTS error handling scenarios"""
        tts_service = XTTSService()
        tts_service.device = "cpu"
        
        # Test with uninitialized service
        tts_service.is_initialized = False
        
        with pytest.raises(RuntimeError, match="XTTS Service ist nicht bereit"):
            await tts_service.generate_speech(
                text="Test text",
                voice_id=mock_voice_data["id"],
                language="en",
                speed=1.0,
                temperature=0.7
            )
        
        # Test with non-existent voice
        tts_service.is_initialized = True
        tts_service.model = MagicMock()
        
        with pytest.raises(ValueError, match="Voice-Referenz.*nicht gefunden"):
            await tts_service.generate_speech(
                text="Test text",
                voice_id="non-existent-voice",
                language="en",
                speed=1.0,
                temperature=0.7
            )
    
    @pytest.mark.asyncio
    async def test_tts_with_long_text(self, temp_dir, mock_voice_data):
        """Test TTS generation with long text input"""
        tts_service = XTTSService()
        tts_service.device = "cpu"
        
        # Mock XTTS model
        mock_model = MagicMock()
        # Return longer audio for longer text
        mock_model.tts.return_value = np.sin(2 * np.pi * 440 * np.linspace(0, 30, 661500))  # 30 seconds
        tts_service.model = mock_model
        tts_service.is_initialized = True
        
        # Create voice reference
        voice_id = mock_voice_data["id"]
        voice_dir = temp_dir / "voices" / voice_id
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        reference_audio = voice_dir / "sample_000.wav"
        audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
        sf.write(reference_audio, audio_data, 22050)
        
        outputs_dir = temp_dir / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        # Create long text (multiple sentences)
        long_text = " ".join([
            "This is a very long text that will be used to test the text-to-speech system.",
            "It contains multiple sentences and should generate a longer audio file.",
            "The system should handle this gracefully and produce high-quality speech output.",
            "This test ensures that the TTS pipeline can process extended text inputs effectively."
        ])
        
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            output_path = await tts_service.generate_speech(
                text=long_text,
                voice_id=voice_id,
                language="en",
                speed=1.0,
                temperature=0.7
            )
            
            # Verify output was created
            assert Path(output_path).exists()
            
            # Verify audio duration is appropriate for long text
            audio_info = sf.info(output_path)
            assert audio_info.duration > 10  # Should be longer than 10 seconds


@pytest.mark.integration
@pytest.mark.tts
@pytest.mark.api
class TestTTSAPIIntegration:
    """Test TTS API integration"""
    
    @pytest.mark.asyncio
    async def test_api_tts_complete_workflow(self, async_client: AsyncClient, mock_voice_data):
        """Test complete TTS API workflow"""
        request_data = {
            "text": "Hello, this is an API integration test for text-to-speech.",
            "voice_id": mock_voice_data["id"],
            "language": "en",
            "speed": 1.0,
            "temperature": 0.7
        }
        
        # Mock TTS service
        with patch('models.tts_service.XTTSService.generate_speech') as mock_generate, \
             patch('models.audio_processor.AudioProcessor.get_duration') as mock_duration:
            
            mock_generate.return_value = "/outputs/api_test_audio.wav"
            mock_duration.return_value = 8.5
            
            response = await async_client.post("/api/tts/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "audio_url" in data
            assert "filename" in data
            assert "duration" in data
            assert data["duration"] == 8.5
            assert data["text"] == request_data["text"]
            assert data["voice_id"] == request_data["voice_id"]
    
    @pytest.mark.asyncio
    async def test_api_tts_validation_errors(self, async_client: AsyncClient):
        """Test TTS API validation errors"""
        # Test empty text
        response = await async_client.post("/api/tts/generate", json={
            "text": "",
            "voice_id": "test-voice",
            "language": "en",
            "speed": 1.0,
            "temperature": 0.7
        })
        assert response.status_code == 400
        
        # Test invalid speed
        response = await async_client.post("/api/tts/generate", json={
            "text": "Test text",
            "voice_id": "test-voice",
            "language": "en",
            "speed": 5.0,  # Invalid
            "temperature": 0.7
        })
        assert response.status_code == 422
        
        # Test invalid temperature
        response = await async_client.post("/api/tts/generate", json={
            "text": "Test text",
            "voice_id": "test-voice",
            "language": "en",
            "speed": 1.0,
            "temperature": 2.0  # Invalid
        })
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_api_tts_with_different_parameters(self, async_client: AsyncClient, mock_voice_data):
        """Test TTS API with various parameter combinations"""
        base_request = {
            "text": "Parameter test message",
            "voice_id": mock_voice_data["id"],
            "language": "en"
        }
        
        # Test parameter combinations
        parameter_sets = [
            {"speed": 0.5, "temperature": 0.1},
            {"speed": 1.0, "temperature": 0.7},
            {"speed": 2.0, "temperature": 1.0},
        ]
        
        with patch('models.tts_service.XTTSService.generate_speech') as mock_generate, \
             patch('models.audio_processor.AudioProcessor.get_duration') as mock_duration:
            
            mock_generate.return_value = "/outputs/param_test_audio.wav"
            mock_duration.return_value = 5.0
            
            for params in parameter_sets:
                request_data = {**base_request, **params}
                
                response = await async_client.post("/api/tts/generate", json=request_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["text"] == request_data["text"]
                assert data["voice_id"] == request_data["voice_id"]


@pytest.mark.integration
@pytest.mark.tts
class TestTTSVoiceIntegration:
    """Test TTS integration with voice management"""
    
    @pytest.mark.asyncio
    async def test_tts_with_cloned_voice(self, temp_dir, multiple_audio_files):
        """Test TTS generation using a cloned voice"""
        # First, create a cloned voice
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_dir.mkdir(exist_ok=True)
        
        audio_processor = AudioProcessor()
        voice_manager.audio_processor = audio_processor
        
        with patch.object(audio_processor, 'process_for_cloning') as mock_process, \
             patch.object(audio_processor, 'get_duration') as mock_duration:
            
            mock_process.side_effect = lambda input_path, output_path: output_path
            mock_duration.return_value = 3.0
            
            voice_id = "tts-integration-voice"
            await voice_manager.clone_voice(
                voice_id=voice_id,
                name="TTS Integration Voice",
                description="Voice for TTS integration testing",
                audio_paths=multiple_audio_files
            )
        
        # Now use the cloned voice for TTS
        tts_service = XTTSService()
        tts_service.device = "cpu"
        
        mock_model = MagicMock()
        mock_model.tts.return_value = np.sin(2 * np.pi * 440 * np.linspace(0, 5, 110250))
        tts_service.model = mock_model
        tts_service.is_initialized = True
        
        outputs_dir = temp_dir / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            output_path = await tts_service.generate_speech(
                text="This message uses a cloned voice for generation.",
                voice_id=voice_id,
                language="en",
                speed=1.0,
                temperature=0.7
            )
            
            # Verify TTS generation succeeded
            assert Path(output_path).exists()
            
            # Verify the correct voice reference was used
            voice_dir = temp_dir / "voices" / voice_id
            assert voice_dir.exists()
            
            # Check that processed audio files exist
            processed_files = list(voice_dir.glob("*.wav"))
            assert len(processed_files) > 0
    
    @pytest.mark.asyncio
    async def test_tts_voice_not_found_handling(self, temp_dir):
        """Test TTS handling when voice is not found"""
        tts_service = XTTSService()
        tts_service.device = "cpu"
        tts_service.model = MagicMock()
        tts_service.is_initialized = True
        
        outputs_dir = temp_dir / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            with pytest.raises(ValueError, match="Voice-Referenz.*nicht gefunden"):
                await tts_service.generate_speech(
                    text="This should fail due to missing voice.",
                    voice_id="non-existent-voice",
                    language="en",
                    speed=1.0,
                    temperature=0.7
                )


@pytest.mark.integration
@pytest.mark.tts
@pytest.mark.slow
class TestTTSPerformance:
    """Test TTS performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_tts_generation_performance(self, temp_dir, mock_voice_data, benchmark):
        """Benchmark TTS generation performance"""
        tts_service = XTTSService()
        tts_service.device = "cpu"
        
        mock_model = MagicMock()
        mock_model.tts.return_value = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
        tts_service.model = mock_model
        tts_service.is_initialized = True
        
        # Create voice reference
        voice_id = mock_voice_data["id"]
        voice_dir = temp_dir / "voices" / voice_id
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        reference_audio = voice_dir / "sample_000.wav"
        audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
        sf.write(reference_audio, audio_data, 22050)
        
        outputs_dir = temp_dir / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            async def generate_tts():
                return await tts_service.generate_speech(
                    text="This is a performance benchmark test message.",
                    voice_id=voice_id,
                    language="en",
                    speed=1.0,
                    temperature=0.7
                )
            
            result = await benchmark(generate_tts)
            assert Path(result).exists()
    
    @pytest.mark.asyncio
    async def test_concurrent_tts_generation(self, temp_dir, mock_voice_data):
        """Test concurrent TTS generation"""
        tts_service = XTTSService()
        tts_service.device = "cpu"
        
        mock_model = MagicMock()
        mock_model.tts.return_value = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
        tts_service.model = mock_model
        tts_service.is_initialized = True
        
        # Create voice reference
        voice_id = mock_voice_data["id"]
        voice_dir = temp_dir / "voices" / voice_id
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        reference_audio = voice_dir / "sample_000.wav"
        audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
        sf.write(reference_audio, audio_data, 22050)
        
        outputs_dir = temp_dir / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        # Generate multiple TTS requests concurrently
        texts = [
            "First concurrent TTS generation test.",
            "Second concurrent TTS generation test.",
            "Third concurrent TTS generation test.",
        ]
        
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            tasks = []
            for i, text in enumerate(texts):
                task = tts_service.generate_speech(
                    text=text,
                    voice_id=voice_id,
                    language="en",
                    speed=1.0,
                    temperature=0.7
                )
                tasks.append(task)
            
            # Wait for all generations to complete
            results = await asyncio.gather(*tasks)
            
            # Verify all outputs were created
            for result in results:
                assert Path(result).exists()
    
    @pytest.mark.asyncio
    async def test_tts_memory_usage(self, temp_dir, mock_voice_data):
        """Test TTS memory usage"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        tts_service = XTTSService()
        tts_service.device = "cpu"
        
        mock_model = MagicMock()
        # Return large audio array to test memory handling
        large_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 60, 22050 * 60))  # 60 seconds
        mock_model.tts.return_value = large_audio
        tts_service.model = mock_model
        tts_service.is_initialized = True
        
        # Create voice reference
        voice_id = mock_voice_data["id"]
        voice_dir = temp_dir / "voices" / voice_id
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        reference_audio = voice_dir / "sample_000.wav"
        audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
        sf.write(reference_audio, audio_data, 22050)
        
        outputs_dir = temp_dir / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        
        with patch('pathlib.Path.cwd', return_value=temp_dir):
            # Generate long audio
            long_text = " ".join(["This is a memory usage test."] * 50)
            
            output_path = await tts_service.generate_speech(
                text=long_text,
                voice_id=voice_id,
                language="en",
                speed=1.0,
                temperature=0.7
            )
            
            assert Path(output_path).exists()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 500MB)
        assert memory_increase < 500 * 1024 * 1024