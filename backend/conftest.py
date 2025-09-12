"""
Global pytest configuration and fixtures for XTTS V2 Backend
"""

import asyncio
import os
import tempfile
import shutil
from pathlib import Path
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import numpy as np
import soundfile as sf

# Import your app
from main import app

# Test Configuration
TEST_DATA_DIR = Path(__file__).parent / "tests" / "fixtures"
TEMP_DIR = Path(tempfile.gettempdir()) / "xtts_tests"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """FastAPI test client"""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def temp_dir() -> Generator[Path, None, None]:
    """Temporary directory for test files"""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    yield TEMP_DIR
    shutil.rmtree(TEMP_DIR, ignore_errors=True)


@pytest.fixture
def clean_temp_dir(temp_dir: Path) -> Generator[Path, None, None]:
    """Clean temporary directory for each test"""
    # Clean before test
    for item in temp_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    
    yield temp_dir
    
    # Clean after test
    for item in temp_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


@pytest.fixture
def sample_audio_file(temp_dir: Path) -> Path:
    """Generate a sample audio file for testing"""
    # Generate 3 seconds of sine wave at 22050 Hz
    sample_rate = 22050
    duration = 3.0
    frequency = 440.0  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t) * 0.5
    
    audio_file = temp_dir / "sample_audio.wav"
    sf.write(audio_file, audio_data, sample_rate)
    
    return audio_file


@pytest.fixture
def multiple_audio_files(temp_dir: Path) -> list[Path]:
    """Generate multiple sample audio files"""
    files = []
    frequencies = [220, 440, 880]  # Different frequencies
    
    for i, freq in enumerate(frequencies):
        sample_rate = 22050
        duration = 2.0 + i  # Different durations
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * freq * t) * 0.3
        
        audio_file = temp_dir / f"sample_audio_{i}.wav"
        sf.write(audio_file, audio_data, sample_rate)
        files.append(audio_file)
    
    return files


@pytest.fixture
def mock_voice_data():
    """Mock voice data for testing"""
    return {
        "id": "test-voice-123",
        "name": "Test Voice",
        "description": "A test voice for unit testing",
        "status": "ready",
        "created_at": "2023-01-01T00:00:00Z",
        "sample_count": 3,
        "duration": 15.5,
        "language": "en"
    }


@pytest.fixture
def mock_tts_request():
    """Mock TTS request data"""
    return {
        "text": "Hello, this is a test message for text-to-speech.",
        "voice_id": "test-voice-123",
        "language": "en",
        "speed": 1.0,
        "temperature": 0.7
    }


@pytest.fixture
def mock_voice_clone_request():
    """Mock voice cloning request"""
    return {
        "name": "New Test Voice",
        "description": "A voice cloned for testing purposes"
    }


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, temp_dir):
    """Setup test environment variables"""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("UPLOAD_DIR", str(temp_dir / "uploads"))
    monkeypatch.setenv("OUTPUT_DIR", str(temp_dir / "outputs"))
    monkeypatch.setenv("VOICES_DIR", str(temp_dir / "voices"))
    monkeypatch.setenv("MODELS_DIR", str(temp_dir / "models"))
    
    # Create test directories
    (temp_dir / "uploads").mkdir(exist_ok=True)
    (temp_dir / "outputs").mkdir(exist_ok=True)
    (temp_dir / "voices").mkdir(exist_ok=True)
    (temp_dir / "models").mkdir(exist_ok=True)


@pytest.fixture
def mock_xtts_model():
    """Mock XTTS model for testing"""
    class MockXTTSModel:
        def __init__(self):
            self.is_loaded = True
        
        def tts(self, text: str, speaker_wav: str, language: str = "en", **kwargs):
            # Return mock audio data
            sample_rate = 22050
            duration = len(text) * 0.1  # Rough estimate
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            return np.sin(2 * np.pi * 440 * t) * 0.3
        
        def to(self, device: str):
            return self
    
    return MockXTTSModel()


@pytest.fixture
def mock_audio_analyzer():
    """Mock audio analyzer for testing"""
    class MockAudioAnalyzer:
        async def analyze_audio_quality(self, audio_path):
            from models.audio_analyzer import AudioQualityMetrics
            return AudioQualityMetrics(
                snr=25.0,
                spectral_centroid=2000.0,
                spectral_rolloff=4000.0,
                zero_crossing_rate=0.1,
                mfcc_variance=1.5,
                rms_energy=0.15,
                silence_ratio=0.2,
                quality_score=85.0
            )
        
        async def get_audio_recommendations(self, metrics):
            return ["✅ Hervorragende Audio-Qualität!"]
        
        async def compare_audio_files(self, audio_paths):
            return {
                "file_count": len(audio_paths),
                "average_quality": 85.0,
                "consistency_score": 90.0,
                "recommendations": ["🎉 Sehr konsistente Audio-Qualität!"]
            }
    
    return MockAudioAnalyzer()


# Pytest markers for test categorization
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "audio: Audio processing tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "voice: Voice cloning tests")
    config.addinivalue_line("markers", "tts: Text-to-speech tests")


# Test data cleanup
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Cleanup test data after each test"""
    yield
    # Cleanup logic here if needed
    pass


# Performance testing fixtures
@pytest.fixture
def benchmark_config():
    """Configuration for benchmark tests"""
    return {
        "min_rounds": 5,
        "max_time": 10.0,
        "warmup": True
    }


# Database fixtures (if using database)
@pytest.fixture
def db_session():
    """Database session for testing"""
    # Mock database session
    class MockDBSession:
        def __init__(self):
            self.data = {}
        
        def add(self, obj):
            pass
        
        def commit(self):
            pass
        
        def rollback(self):
            pass
        
        def close(self):
            pass
    
    return MockDBSession()


# Error simulation fixtures
@pytest.fixture
def simulate_network_error():
    """Simulate network errors for testing"""
    def _simulate_error(error_type="timeout"):
        if error_type == "timeout":
            raise TimeoutError("Simulated network timeout")
        elif error_type == "connection":
            raise ConnectionError("Simulated connection error")
        else:
            raise Exception(f"Simulated {error_type} error")
    
    return _simulate_error