"""
Unit Tests for Voice Manager
Comprehensive testing of voice management functionality
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import json
from datetime import datetime

from models.voice_manager import VoiceManager
from schemas.api_models import VoiceInfo, VoiceStatus


@pytest.mark.unit
@pytest.mark.voice
class TestVoiceManagerInitialization:
    """Test VoiceManager initialization"""
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, temp_dir):
        """Test successful initialization"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_db_path = voice_manager.voices_dir / "voices.json"
        
        await voice_manager.initialize()
        
        assert voice_manager.voices_dir.exists()
        assert voice_manager.is_ready()
    
    @pytest.mark.asyncio
    async def test_initialize_with_existing_data(self, temp_dir):
        """Test initialization with existing voice data"""
        voices_dir = temp_dir / "voices"
        voices_dir.mkdir(exist_ok=True)
        
        # Create mock voices.json
        voices_data = {
            "voices": [{
                "id": "test-voice-1",
                "name": "Test Voice 1",
                "description": "Test description",
                "status": "ready",
                "created_at": "2023-01-01T00:00:00Z",
                "sample_count": 3,
                "duration": 10.5
            }],
            "updated_at": "2023-01-01T00:00:00Z"
        }
        
        voices_db_path = voices_dir / "voices.json"
        with open(voices_db_path, 'w') as f:
            json.dump(voices_data, f)
        
        voice_manager = VoiceManager()
        voice_manager.voices_dir = voices_dir
        voice_manager.voices_db_path = voices_db_path
        
        await voice_manager.initialize()
        
        assert len(voice_manager.voices_cache) == 1
        assert "test-voice-1" in voice_manager.voices_cache


@pytest.mark.unit
@pytest.mark.voice
class TestVoiceRetrieval:
    """Test voice retrieval functionality"""
    
    @pytest.mark.asyncio
    async def test_get_all_voices_empty(self, temp_dir):
        """Test getting all voices when none exist"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_cache = {}
        
        with patch.object(voice_manager, '_refresh_cache', new_callable=AsyncMock):
            voices = await voice_manager.get_all_voices()
            assert voices == []
    
    @pytest.mark.asyncio
    async def test_get_all_voices_with_data(self, temp_dir, mock_voice_data):
        """Test getting all voices with existing data"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        
        # Create VoiceInfo object
        voice_info = VoiceInfo(**mock_voice_data)
        voice_manager.voices_cache = {voice_info.id: voice_info}
        
        with patch.object(voice_manager, '_refresh_cache', new_callable=AsyncMock):
            voices = await voice_manager.get_all_voices()
            assert len(voices) == 1
            assert voices[0].id == mock_voice_data["id"]
    
    @pytest.mark.asyncio
    async def test_get_voice_status_existing(self, temp_dir, mock_voice_data):
        """Test getting status of existing voice"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        
        voice_info = VoiceInfo(**mock_voice_data)
        voice_manager.voices_cache = {voice_info.id: voice_info}
        
        status = await voice_manager.get_voice_status(voice_info.id)
        
        assert status["voice_id"] == voice_info.id
        assert status["status"] == voice_info.status.value
        assert status["name"] == voice_info.name
    
    @pytest.mark.asyncio
    async def test_get_voice_status_not_found(self, temp_dir):
        """Test getting status of non-existent voice"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_cache = {}
        
        with patch.object(voice_manager, '_refresh_cache', new_callable=AsyncMock):
            with pytest.raises(ValueError, match="Voice .* not found"):
                await voice_manager.get_voice_status("non-existent-voice")


@pytest.mark.unit
@pytest.mark.voice
class TestVoiceCloning:
    """Test voice cloning functionality"""
    
    @pytest.mark.asyncio
    async def test_clone_voice_success(self, temp_dir, multiple_audio_files):
        """Test successful voice cloning"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.audio_processor = MagicMock()
        
        # Mock audio processor methods
        voice_manager.audio_processor.process_for_cloning = AsyncMock(
            side_effect=lambda input_path, output_path: output_path
        )
        voice_manager.audio_processor.get_duration = AsyncMock(return_value=3.0)
        
        voice_id = "test-voice-123"
        name = "Test Voice"
        description = "Test description"
        
        with patch.object(voice_manager, '_save_voice_info', new_callable=AsyncMock):
            await voice_manager.clone_voice(
                voice_id=voice_id,
                name=name,
                description=description,
                audio_paths=multiple_audio_files
            )
        
        # Check that voice was added to cache
        assert voice_id in voice_manager.voices_cache
        voice_info = voice_manager.voices_cache[voice_id]
        assert voice_info.name == name
        assert voice_info.description == description
        assert voice_info.status == VoiceStatus.READY
    
    @pytest.mark.asyncio
    async def test_clone_voice_processing_error(self, temp_dir, multiple_audio_files):
        """Test voice cloning with processing error"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.audio_processor = MagicMock()
        
        # Mock audio processor to raise error
        voice_manager.audio_processor.process_for_cloning = AsyncMock(
            side_effect=Exception("Processing failed")
        )
        
        voice_id = "test-voice-123"
        
        with patch.object(voice_manager, '_save_voice_info', new_callable=AsyncMock):
            await voice_manager.clone_voice(
                voice_id=voice_id,
                name="Test Voice",
                description="Test description",
                audio_paths=multiple_audio_files
            )
        
        # Check that voice status is set to error
        assert voice_id in voice_manager.voices_cache
        voice_info = voice_manager.voices_cache[voice_id]
        assert voice_info.status == VoiceStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_clone_voice_no_files(self, temp_dir):
        """Test voice cloning with no audio files"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.audio_processor = MagicMock()
        
        voice_id = "test-voice-123"
        
        with patch.object(voice_manager, '_save_voice_info', new_callable=AsyncMock):
            with pytest.raises(ValueError, match="Keine Audio-Dateien"):
                await voice_manager.clone_voice(
                    voice_id=voice_id,
                    name="Test Voice",
                    description="Test description",
                    audio_paths=[]
                )


@pytest.mark.unit
@pytest.mark.voice
class TestVoiceDeletion:
    """Test voice deletion functionality"""
    
    @pytest.mark.asyncio
    async def test_delete_voice_success(self, temp_dir, mock_voice_data):
        """Test successful voice deletion"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        
        # Create voice directory and cache entry
        voice_id = mock_voice_data["id"]
        voice_dir = voice_manager.voices_dir / voice_id
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        voice_info = VoiceInfo(**mock_voice_data)
        voice_manager.voices_cache = {voice_id: voice_info}
        
        with patch.object(voice_manager, '_save_voices_db', new_callable=AsyncMock):
            await voice_manager.delete_voice(voice_id)
        
        # Check that voice was removed
        assert voice_id not in voice_manager.voices_cache
        assert not voice_dir.exists()
    
    @pytest.mark.asyncio
    async def test_delete_voice_not_in_cache(self, temp_dir):
        """Test deleting voice not in cache"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_cache = {}
        
        voice_id = "non-existent-voice"
        
        with patch.object(voice_manager, '_save_voices_db', new_callable=AsyncMock):
            # Should not raise error
            await voice_manager.delete_voice(voice_id)


@pytest.mark.unit
@pytest.mark.voice
class TestVoiceDatabase:
    """Test voice database operations"""
    
    @pytest.mark.asyncio
    async def test_save_voices_db(self, temp_dir, mock_voice_data):
        """Test saving voices database"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_dir.mkdir(exist_ok=True)
        voice_manager.voices_db_path = voice_manager.voices_dir / "voices.json"
        
        voice_info = VoiceInfo(**mock_voice_data)
        voice_manager.voices_cache = {voice_info.id: voice_info}
        
        await voice_manager._save_voices_db()
        
        # Check that file was created
        assert voice_manager.voices_db_path.exists()
        
        # Check file contents
        with open(voice_manager.voices_db_path, 'r') as f:
            data = json.load(f)
        
        assert "voices" in data
        assert "updated_at" in data
        assert len(data["voices"]) == 1
        assert data["voices"][0]["id"] == voice_info.id
    
    @pytest.mark.asyncio
    async def test_load_voices_db_corrupted(self, temp_dir):
        """Test loading corrupted voices database"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_dir.mkdir(exist_ok=True)
        voice_manager.voices_db_path = voice_manager.voices_dir / "voices.json"
        
        # Create corrupted JSON file
        with open(voice_manager.voices_db_path, 'w') as f:
            f.write("invalid json content")
        
        # Should not raise error, just log warning
        await voice_manager._load_voices_db()
        
        # Cache should be empty
        assert len(voice_manager.voices_cache) == 0


@pytest.mark.unit
@pytest.mark.voice
class TestVoiceReconstruction:
    """Test voice reconstruction from filesystem"""
    
    @pytest.mark.asyncio
    async def test_reconstruct_voice_info(self, temp_dir):
        """Test reconstructing voice info from directory"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.audio_processor = MagicMock()
        voice_manager.audio_processor.get_duration = AsyncMock(return_value=3.0)
        
        # Create voice directory with audio files
        voice_id = "test-voice-123"
        voice_dir = voice_manager.voices_dir / voice_id
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        # Create mock audio files
        for i in range(3):
            audio_file = voice_dir / f"sample_{i:03d}.wav"
            audio_file.write_text("mock audio data")
        
        # Create preview file
        preview_file = voice_dir / "preview.wav"
        preview_file.write_text("mock preview data")
        
        await voice_manager._reconstruct_voice_info(voice_id, voice_dir)
        
        # Check that voice was added to cache
        assert voice_id in voice_manager.voices_cache
        voice_info = voice_manager.voices_cache[voice_id]
        assert voice_info.sample_count == 3
        assert voice_info.status == VoiceStatus.READY
        assert voice_info.preview_url is not None
    
    @pytest.mark.asyncio
    async def test_refresh_cache_with_orphaned_directories(self, temp_dir):
        """Test cache refresh with orphaned voice directories"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.voices_dir.mkdir(exist_ok=True)
        voice_manager.audio_processor = MagicMock()
        voice_manager.audio_processor.get_duration = AsyncMock(return_value=2.0)
        
        # Create orphaned voice directory
        orphaned_voice_dir = voice_manager.voices_dir / "orphaned-voice"
        orphaned_voice_dir.mkdir()
        
        # Create audio file in orphaned directory
        audio_file = orphaned_voice_dir / "sample_000.wav"
        audio_file.write_text("mock audio data")
        
        with patch.object(voice_manager, '_save_voices_db', new_callable=AsyncMock):
            await voice_manager._refresh_cache()
        
        # Check that orphaned voice was reconstructed
        assert "orphaned-voice" in voice_manager.voices_cache


@pytest.mark.unit
@pytest.mark.voice
@pytest.mark.slow
class TestVoiceManagerPerformance:
    """Test VoiceManager performance"""
    
    @pytest.mark.asyncio
    async def test_get_all_voices_performance(self, temp_dir, benchmark):
        """Benchmark get_all_voices method"""
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        
        # Create multiple voices in cache
        for i in range(100):
            voice_info = VoiceInfo(
                id=f"voice-{i}",
                name=f"Voice {i}",
                description=f"Test voice {i}",
                status=VoiceStatus.READY,
                created_at=datetime.now(),
                sample_count=3,
                duration=10.0
            )
            voice_manager.voices_cache[voice_info.id] = voice_info
        
        with patch.object(voice_manager, '_refresh_cache', new_callable=AsyncMock):
            async def get_voices():
                return await voice_manager.get_all_voices()
            
            result = await benchmark(get_voices)
            assert len(result) == 100
    
    @pytest.mark.asyncio
    async def test_voice_cloning_memory_usage(self, temp_dir, multiple_audio_files):
        """Test memory usage during voice cloning"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        voice_manager = VoiceManager()
        voice_manager.voices_dir = temp_dir / "voices"
        voice_manager.audio_processor = MagicMock()
        voice_manager.audio_processor.process_for_cloning = AsyncMock(
            side_effect=lambda input_path, output_path: output_path
        )
        voice_manager.audio_processor.get_duration = AsyncMock(return_value=3.0)
        
        with patch.object(voice_manager, '_save_voice_info', new_callable=AsyncMock):
            await voice_manager.clone_voice(
                voice_id="memory-test-voice",
                name="Memory Test Voice",
                description="Testing memory usage",
                audio_paths=multiple_audio_files
            )
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024