"""
Unit Tests for Audio Processor
Comprehensive testing of audio processing functionality
"""

import pytest
import numpy as np
import soundfile as sf
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

from models.audio_processor import AudioProcessor


@pytest.mark.unit
@pytest.mark.audio
class TestAudioProcessorInitialization:
    """Test AudioProcessor initialization"""
    
    def test_init_default_values(self):
        """Test initialization with default values"""
        processor = AudioProcessor()
        
        assert processor.target_sample_rate == 22050
        assert processor.min_duration == 3.0
        assert processor.max_duration == 30.0
    
    def test_init_custom_values(self):
        """Test initialization with custom values"""
        processor = AudioProcessor()
        processor.target_sample_rate = 44100
        processor.min_duration = 5.0
        processor.max_duration = 60.0
        
        assert processor.target_sample_rate == 44100
        assert processor.min_duration == 5.0
        assert processor.max_duration == 60.0


@pytest.mark.unit
@pytest.mark.audio
class TestAudioProcessing:
    """Test audio processing functionality"""
    
    @pytest.mark.asyncio
    async def test_process_for_cloning_success(self, temp_dir, sample_audio_file):
        """Test successful audio processing for cloning"""
        processor = AudioProcessor()
        output_path = temp_dir / "processed_audio.wav"
        
        with patch('librosa.load') as mock_load, \
             patch('soundfile.write') as mock_write:
            
            # Mock librosa.load to return sample audio data
            mock_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
            mock_load.return_value = (mock_audio, 22050)
            
            result_path = await processor.process_for_cloning(
                sample_audio_file, output_path
            )
            
            assert result_path == output_path
            mock_load.assert_called_once()
            mock_write.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_for_cloning_no_output_path(self, sample_audio_file):
        """Test processing without specifying output path"""
        processor = AudioProcessor()
        
        with patch('librosa.load') as mock_load, \
             patch('soundfile.write') as mock_write:
            
            mock_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
            mock_load.return_value = (mock_audio, 22050)
            
            result_path = await processor.process_for_cloning(sample_audio_file)
            
            # Should create output path with .processed.wav extension
            expected_path = sample_audio_file.with_suffix('.processed.wav')
            assert result_path == expected_path
    
    @pytest.mark.asyncio
    async def test_process_audio_resampling(self, temp_dir):
        """Test audio resampling during processing"""
        processor = AudioProcessor()
        
        # Create mock audio at different sample rate
        original_sr = 44100
        target_sr = 22050
        duration = 3.0
        
        original_audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(original_sr * duration)))
        
        with patch('librosa.resample') as mock_resample:
            mock_resample.return_value = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(target_sr * duration)))
            
            processed_audio = await processor._process_audio(original_audio, original_sr)
            
            mock_resample.assert_called_once_with(
                original_audio, orig_sr=original_sr, target_sr=target_sr
            )
    
    @pytest.mark.asyncio
    async def test_process_audio_normalization(self, temp_dir):
        """Test audio normalization"""
        processor = AudioProcessor()
        
        # Create audio with varying amplitude
        audio = np.array([0.1, 0.5, -0.3, 0.8, -0.9])
        
        with patch('librosa.util.normalize') as mock_normalize, \
             patch('librosa.effects.trim') as mock_trim:
            
            mock_normalize.return_value = audio / np.max(np.abs(audio))
            mock_trim.return_value = (audio, None)
            
            processed_audio = await processor._process_audio(audio, 22050)
            
            mock_normalize.assert_called()
    
    @pytest.mark.asyncio
    async def test_process_audio_duration_too_short(self, temp_dir):
        """Test processing audio that's too short"""
        processor = AudioProcessor()
        
        # Create 1 second audio (below minimum of 3 seconds)
        short_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 22050))
        
        with patch('librosa.util.normalize') as mock_normalize, \
             patch('librosa.effects.trim') as mock_trim:
            
            mock_normalize.return_value = short_audio
            mock_trim.return_value = (short_audio, None)
            
            processed_audio = await processor._process_audio(short_audio, 22050)
            
            # Should be extended to minimum duration
            expected_length = int(processor.min_duration * 22050)
            assert len(processed_audio) >= expected_length
    
    @pytest.mark.asyncio
    async def test_process_audio_duration_too_long(self, temp_dir):
        """Test processing audio that's too long"""
        processor = AudioProcessor()
        
        # Create 60 second audio (above maximum of 30 seconds)
        long_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 60, 22050 * 60))
        
        with patch('librosa.util.normalize') as mock_normalize, \
             patch('librosa.effects.trim') as mock_trim:
            
            mock_normalize.return_value = long_audio
            mock_trim.return_value = (long_audio, None)
            
            processed_audio = await processor._process_audio(long_audio, 22050)
            
            # Should be truncated to maximum duration
            expected_length = int(processor.max_duration * 22050)
            assert len(processed_audio) <= expected_length


@pytest.mark.unit
@pytest.mark.audio
class TestNoiseReduction:
    """Test noise reduction functionality"""
    
    def test_simple_noise_reduction_success(self):
        """Test successful noise reduction"""
        processor = AudioProcessor()
        
        # Create audio with some noise pattern
        audio = np.random.normal(0, 0.1, 22050)  # 1 second of noise
        audio[11000:12000] += np.sin(2 * np.pi * 440 * np.linspace(0, 1, 1000)) * 0.5  # Add signal
        
        with patch('librosa.feature.rms') as mock_rms:
            # Mock RMS to return varying energy levels
            mock_rms.return_value = np.array([np.random.uniform(0.01, 0.3, 100)])
            
            processed_audio = processor._simple_noise_reduction(audio)
            
            assert len(processed_audio) == len(audio)
            mock_rms.assert_called()
    
    def test_simple_noise_reduction_error_handling(self):
        """Test noise reduction error handling"""
        processor = AudioProcessor()
        
        # Create problematic audio
        audio = np.array([])  # Empty audio
        
        # Should not raise error, just return original audio
        processed_audio = processor._simple_noise_reduction(audio)
        assert np.array_equal(processed_audio, audio)


@pytest.mark.unit
@pytest.mark.audio
class TestAudioInfo:
    """Test audio information retrieval"""
    
    @pytest.mark.asyncio
    async def test_get_duration_success(self, sample_audio_file):
        """Test successful duration retrieval"""
        processor = AudioProcessor()
        
        with patch('soundfile.info') as mock_info:
            mock_info.return_value = MagicMock(duration=5.2)
            
            duration = await processor.get_duration(sample_audio_file)
            
            assert duration == 5.2
            mock_info.assert_called_once_with(str(sample_audio_file))
    
    @pytest.mark.asyncio
    async def test_get_duration_error(self, temp_dir):
        """Test duration retrieval with error"""
        processor = AudioProcessor()
        non_existent_file = temp_dir / "non_existent.wav"
        
        with patch('soundfile.info', side_effect=Exception("File not found")):
            duration = await processor.get_duration(non_existent_file)
            
            assert duration == 0.0
    
    @pytest.mark.asyncio
    async def test_get_audio_info_success(self, sample_audio_file):
        """Test successful audio info retrieval"""
        processor = AudioProcessor()
        
        mock_info = MagicMock()
        mock_info.duration = 5.2
        mock_info.samplerate = 22050
        mock_info.channels = 1
        mock_info.frames = 114840
        mock_info.format = 'WAV'
        mock_info.subtype = 'PCM_16'
        
        with patch('soundfile.info', return_value=mock_info):
            info = await processor.get_audio_info(sample_audio_file)
            
            assert info["duration"] == 5.2
            assert info["sample_rate"] == 22050
            assert info["channels"] == 1
            assert info["frames"] == 114840
            assert info["format"] == 'WAV'
            assert info["subtype"] == 'PCM_16'
    
    @pytest.mark.asyncio
    async def test_get_audio_info_error(self, temp_dir):
        """Test audio info retrieval with error"""
        processor = AudioProcessor()
        non_existent_file = temp_dir / "non_existent.wav"
        
        with patch('soundfile.info', side_effect=Exception("File not found")):
            info = await processor.get_audio_info(non_existent_file)
            
            assert info == {}


@pytest.mark.unit
@pytest.mark.audio
class TestAudioValidation:
    """Test audio validation functionality"""
    
    @pytest.mark.asyncio
    async def test_validate_audio_success(self, sample_audio_file):
        """Test successful audio validation"""
        processor = AudioProcessor()
        
        mock_info = {
            "duration": 5.0,
            "sample_rate": 22050,
            "channels": 1
        }
        
        with patch.object(processor, 'get_audio_info', return_value=mock_info):
            is_valid = await processor.validate_audio(sample_audio_file)
            
            assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_audio_too_short(self, sample_audio_file):
        """Test validation of audio that's too short"""
        processor = AudioProcessor()
        
        mock_info = {
            "duration": 0.5,  # Too short
            "sample_rate": 22050,
            "channels": 1
        }
        
        with patch.object(processor, 'get_audio_info', return_value=mock_info):
            is_valid = await processor.validate_audio(sample_audio_file)
            
            assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_validate_audio_low_sample_rate(self, sample_audio_file):
        """Test validation of audio with low sample rate"""
        processor = AudioProcessor()
        
        mock_info = {
            "duration": 5.0,
            "sample_rate": 4000,  # Too low
            "channels": 1
        }
        
        with patch.object(processor, 'get_audio_info', return_value=mock_info):
            is_valid = await processor.validate_audio(sample_audio_file)
            
            assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_validate_audio_error(self, temp_dir):
        """Test audio validation with error"""
        processor = AudioProcessor()
        non_existent_file = temp_dir / "non_existent.wav"
        
        with patch.object(processor, 'get_audio_info', side_effect=Exception("Error")):
            is_valid = await processor.validate_audio(non_existent_file)
            
            assert is_valid is False


@pytest.mark.unit
@pytest.mark.audio
@pytest.mark.slow
class TestAudioProcessorPerformance:
    """Test AudioProcessor performance"""
    
    @pytest.mark.asyncio
    async def test_process_for_cloning_performance(self, sample_audio_file, benchmark):
        """Benchmark audio processing for cloning"""
        processor = AudioProcessor()
        
        with patch('librosa.load') as mock_load, \
             patch('soundfile.write') as mock_write:
            
            mock_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150))
            mock_load.return_value = (mock_audio, 22050)
            
            async def process_audio():
                return await processor.process_for_cloning(sample_audio_file)
            
            result = await benchmark(process_audio)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_noise_reduction_performance(self, benchmark):
        """Benchmark noise reduction"""
        processor = AudioProcessor()
        
        # Create 10 seconds of audio
        audio = np.random.normal(0, 0.1, 220500)
        
        def reduce_noise():
            return processor._simple_noise_reduction(audio)
        
        result = benchmark(reduce_noise)
        assert len(result) == len(audio)
    
    @pytest.mark.asyncio
    async def test_memory_usage_large_audio(self, temp_dir):
        """Test memory usage with large audio files"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        processor = AudioProcessor()
        
        # Create large audio file (10 minutes)
        large_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 600, 22050 * 600))
        
        with patch('librosa.load') as mock_load, \
             patch('soundfile.write') as mock_write:
            
            mock_load.return_value = (large_audio, 22050)
            
            audio_file = temp_dir / "large_audio.wav"
            await processor.process_for_cloning(audio_file)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 500MB)
        assert memory_increase < 500 * 1024 * 1024


@pytest.mark.unit
@pytest.mark.audio
class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_process_empty_audio(self):
        """Test processing empty audio"""
        processor = AudioProcessor()
        
        empty_audio = np.array([])
        
        with patch('librosa.util.normalize', return_value=empty_audio), \
             patch('librosa.effects.trim', return_value=(empty_audio, None)):
            
            # Should handle empty audio gracefully
            processed_audio = await processor._process_audio(empty_audio, 22050)
            
            # Should return audio with minimum duration
            expected_length = int(processor.min_duration * 22050)
            assert len(processed_audio) >= expected_length
    
    @pytest.mark.asyncio
    async def test_process_nan_audio(self):
        """Test processing audio with NaN values"""
        processor = AudioProcessor()
        
        # Create audio with NaN values
        audio_with_nan = np.array([0.1, np.nan, 0.3, np.nan, 0.5])
        
        with patch('librosa.util.normalize') as mock_normalize, \
             patch('librosa.effects.trim') as mock_trim:
            
            # Mock normalize to handle NaN
            mock_normalize.return_value = np.nan_to_num(audio_with_nan)
            mock_trim.return_value = (np.nan_to_num(audio_with_nan), None)
            
            processed_audio = await processor._process_audio(audio_with_nan, 22050)
            
            # Should not contain NaN values
            assert not np.isnan(processed_audio).any()
    
    @pytest.mark.asyncio
    async def test_process_very_quiet_audio(self):
        """Test processing very quiet audio"""
        processor = AudioProcessor()
        
        # Create very quiet audio
        quiet_audio = np.sin(2 * np.pi * 440 * np.linspace(0, 3, 66150)) * 1e-6
        
        with patch('librosa.util.normalize') as mock_normalize, \
             patch('librosa.effects.trim') as mock_trim:
            
            mock_normalize.return_value = quiet_audio / np.max(np.abs(quiet_audio))
            mock_trim.return_value = (quiet_audio, None)
            
            processed_audio = await processor._process_audio(quiet_audio, 22050)
            
            # Should be normalized properly
            assert np.max(np.abs(processed_audio)) > 0.1