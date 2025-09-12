"""
Unit Tests for XTTS V2 API Endpoints
Tests all FastAPI endpoints with comprehensive coverage
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
import io


@pytest.mark.unit
@pytest.mark.api
class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_success(self, client: TestClient):
        """Test successful health check"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
        assert isinstance(data["services"], dict)
    
    def test_health_check_response_structure(self, client: TestClient):
        """Test health check response structure"""
        response = client.get("/health")
        data = response.json()
        
        required_fields = ["status", "timestamp", "services"]
        for field in required_fields:
            assert field in data
        
        # Check services structure
        services = data["services"]
        expected_services = ["tts", "voice_manager", "audio_processor"]
        for service in expected_services:
            assert service in services
            assert isinstance(services[service], bool)


@pytest.mark.unit
@pytest.mark.api
class TestVoicesEndpoints:
    """Test voice management endpoints"""
    
    def test_get_voices_empty(self, client: TestClient):
        """Test getting voices when none exist"""
        with patch('models.voice_manager.VoiceManager.get_all_voices') as mock_get:
            mock_get.return_value = []
            
            response = client.get("/api/voices")
            assert response.status_code == 200
            assert response.json() == []
    
    def test_get_voices_with_data(self, client: TestClient, mock_voice_data):
        """Test getting voices with existing data"""
        with patch('models.voice_manager.VoiceManager.get_all_voices') as mock_get:
            mock_get.return_value = [mock_voice_data]
            
            response = client.get("/api/voices")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["id"] == mock_voice_data["id"]
    
    def test_get_voice_status_success(self, client: TestClient):
        """Test getting voice status"""
        voice_id = "test-voice-123"
        mock_status = {
            "voice_id": voice_id,
            "status": "ready",
            "name": "Test Voice",
            "sample_count": 3
        }
        
        with patch('models.voice_manager.VoiceManager.get_voice_status') as mock_status_func:
            mock_status_func.return_value = mock_status
            
            response = client.get(f"/api/voices/{voice_id}/status")
            assert response.status_code == 200
            data = response.json()
            assert data["voice_id"] == voice_id
            assert data["status"] == "ready"
    
    def test_get_voice_status_not_found(self, client: TestClient):
        """Test getting status for non-existent voice"""
        voice_id = "non-existent-voice"
        
        with patch('models.voice_manager.VoiceManager.get_voice_status') as mock_status:
            mock_status.side_effect = ValueError(f"Voice {voice_id} not found")
            
            response = client.get(f"/api/voices/{voice_id}/status")
            assert response.status_code == 500
    
    def test_delete_voice_success(self, client: TestClient):
        """Test successful voice deletion"""
        voice_id = "test-voice-123"
        
        with patch('models.voice_manager.VoiceManager.delete_voice') as mock_delete:
            mock_delete.return_value = None
            
            response = client.delete(f"/api/voices/{voice_id}")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert voice_id in data["message"]
    
    def test_delete_voice_not_found(self, client: TestClient):
        """Test deleting non-existent voice"""
        voice_id = "non-existent-voice"
        
        with patch('models.voice_manager.VoiceManager.delete_voice') as mock_delete:
            mock_delete.side_effect = ValueError("Voice not found")
            
            response = client.delete(f"/api/voices/{voice_id}")
            assert response.status_code == 500


@pytest.mark.unit
@pytest.mark.api
class TestVoiceCloneEndpoint:
    """Test voice cloning endpoint"""
    
    def test_clone_voice_success(self, client: TestClient, sample_audio_file):
        """Test successful voice cloning"""
        with patch('models.voice_manager.VoiceManager.clone_voice') as mock_clone:
            mock_clone.return_value = "new-voice-123"
            
            with open(sample_audio_file, 'rb') as audio_file:
                files = [("files", ("test.wav", audio_file, "audio/wav"))]
                data = {
                    "name": "Test Voice",
                    "description": "Test description"
                }
                
                response = client.post("/api/voices/clone", data=data, files=files)
                
                assert response.status_code == 200
                result = response.json()
                assert "voice_id" in result
                assert result["status"] == "processing"
    
    def test_clone_voice_no_files(self, client: TestClient):
        """Test voice cloning without files"""
        data = {
            "name": "Test Voice",
            "description": "Test description"
        }
        
        response = client.post("/api/voices/clone", data=data)
        assert response.status_code == 422  # Validation error
    
    def test_clone_voice_invalid_file_type(self, client: TestClient, temp_dir):
        """Test voice cloning with invalid file type"""
        # Create a text file instead of audio
        text_file = temp_dir / "test.txt"
        text_file.write_text("This is not an audio file")
        
        with open(text_file, 'rb') as file:
            files = [("files", ("test.txt", file, "text/plain"))]
            data = {
                "name": "Test Voice",
                "description": "Test description"
            }
            
            response = client.post("/api/voices/clone", data=data, files=files)
            assert response.status_code == 400
    
    def test_clone_voice_missing_name(self, client: TestClient, sample_audio_file):
        """Test voice cloning without name"""
        with open(sample_audio_file, 'rb') as audio_file:
            files = [("files", ("test.wav", audio_file, "audio/wav"))]
            data = {"description": "Test description"}
            
            response = client.post("/api/voices/clone", data=data, files=files)
            assert response.status_code == 422  # Validation error


@pytest.mark.unit
@pytest.mark.api
class TestTTSEndpoint:
    """Test Text-to-Speech endpoint"""
    
    def test_generate_speech_success(self, client: TestClient, mock_tts_request):
        """Test successful TTS generation"""
        mock_response = {
            "audio_url": "/outputs/test-audio.wav",
            "filename": "test-audio.wav",
            "duration": 5.2,
            "text": mock_tts_request["text"],
            "voice_id": mock_tts_request["voice_id"]
        }
        
        with patch('models.tts_service.XTTSService.generate_speech') as mock_generate:
            mock_generate.return_value = "/outputs/test-audio.wav"
            with patch('models.audio_processor.AudioProcessor.get_duration') as mock_duration:
                mock_duration.return_value = 5.2
                
                response = client.post("/api/tts/generate", json=mock_tts_request)
                
                assert response.status_code == 200
                data = response.json()
                assert data["filename"] == "test-audio.wav"
                assert data["duration"] == 5.2
                assert data["text"] == mock_tts_request["text"]
    
    def test_generate_speech_empty_text(self, client: TestClient):
        """Test TTS generation with empty text"""
        request_data = {
            "text": "",
            "voice_id": "test-voice-123",
            "language": "en",
            "speed": 1.0,
            "temperature": 0.7
        }
        
        response = client.post("/api/tts/generate", json=request_data)
        assert response.status_code == 400
    
    def test_generate_speech_invalid_voice(self, client: TestClient):
        """Test TTS generation with invalid voice ID"""
        request_data = {
            "text": "Test text",
            "voice_id": "non-existent-voice",
            "language": "en",
            "speed": 1.0,
            "temperature": 0.7
        }
        
        with patch('models.tts_service.XTTSService.generate_speech') as mock_generate:
            mock_generate.side_effect = ValueError("Voice not found")
            
            response = client.post("/api/tts/generate", json=request_data)
            assert response.status_code == 500
    
    def test_generate_speech_invalid_parameters(self, client: TestClient):
        """Test TTS generation with invalid parameters"""
        request_data = {
            "text": "Test text",
            "voice_id": "test-voice-123",
            "language": "en",
            "speed": 5.0,  # Invalid speed
            "temperature": 2.0  # Invalid temperature
        }
        
        response = client.post("/api/tts/generate", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.parametrize("speed,temperature", [
        (0.5, 0.1),  # Minimum values
        (2.0, 1.0),  # Maximum values
        (1.0, 0.7),  # Default values
    ])
    def test_generate_speech_parameter_ranges(self, client: TestClient, speed, temperature):
        """Test TTS generation with various parameter ranges"""
        request_data = {
            "text": "Test text",
            "voice_id": "test-voice-123",
            "language": "en",
            "speed": speed,
            "temperature": temperature
        }
        
        with patch('models.tts_service.XTTSService.generate_speech') as mock_generate:
            mock_generate.return_value = "/outputs/test-audio.wav"
            with patch('models.audio_processor.AudioProcessor.get_duration') as mock_duration:
                mock_duration.return_value = 3.0
                
                response = client.post("/api/tts/generate", json=request_data)
                assert response.status_code == 200


@pytest.mark.unit
@pytest.mark.api
class TestLanguagesEndpoint:
    """Test languages endpoint"""
    
    def test_get_languages_success(self, client: TestClient):
        """Test getting supported languages"""
        response = client.get("/api/languages")
        
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert isinstance(data["languages"], list)
        assert len(data["languages"]) > 0
        
        # Check language structure
        for lang in data["languages"]:
            assert "code" in lang
            assert "name" in lang
            assert isinstance(lang["code"], str)
            assert isinstance(lang["name"], str)
    
    def test_get_languages_contains_expected(self, client: TestClient):
        """Test that response contains expected languages"""
        response = client.get("/api/languages")
        data = response.json()
        
        language_codes = [lang["code"] for lang in data["languages"]]
        expected_codes = ["de", "en", "es", "fr", "it", "pt"]
        
        for code in expected_codes:
            assert code in language_codes


@pytest.mark.unit
@pytest.mark.api
class TestErrorHandling:
    """Test API error handling"""
    
    def test_404_endpoint(self, client: TestClient):
        """Test non-existent endpoint"""
        response = client.get("/api/non-existent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client: TestClient):
        """Test wrong HTTP method"""
        response = client.post("/api/languages")  # Should be GET
        assert response.status_code == 405
    
    def test_invalid_json(self, client: TestClient):
        """Test invalid JSON in request body"""
        response = client.post(
            "/api/tts/generate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_large_request_body(self, client: TestClient):
        """Test handling of large request bodies"""
        large_text = "A" * 10000  # 10KB text
        request_data = {
            "text": large_text,
            "voice_id": "test-voice-123",
            "language": "en",
            "speed": 1.0,
            "temperature": 0.7
        }
        
        response = client.post("/api/tts/generate", json=request_data)
        assert response.status_code == 400  # Text too long


@pytest.mark.unit
@pytest.mark.api
class TestCORSHeaders:
    """Test CORS headers"""
    
    def test_cors_headers_present(self, client: TestClient):
        """Test that CORS headers are present"""
        response = client.get("/health")
        
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"
    
    def test_options_request(self, client: TestClient):
        """Test OPTIONS request for CORS preflight"""
        response = client.options("/api/voices")
        assert response.status_code == 200


@pytest.mark.unit
@pytest.mark.api
class TestRequestValidation:
    """Test request validation"""
    
    def test_voice_clone_validation(self, client: TestClient):
        """Test voice clone request validation"""
        # Test missing required fields
        response = client.post("/api/voices/clone", data={})
        assert response.status_code == 422
        
        # Test invalid field types
        response = client.post("/api/voices/clone", data={
            "name": 123,  # Should be string
            "description": "Test"
        })
        assert response.status_code == 422
    
    def test_tts_validation(self, client: TestClient):
        """Test TTS request validation"""
        # Test missing required fields
        response = client.post("/api/tts/generate", json={})
        assert response.status_code == 422
        
        # Test invalid field values
        response = client.post("/api/tts/generate", json={
            "text": "Test",
            "voice_id": "test",
            "language": "invalid-lang",
            "speed": -1,  # Invalid
            "temperature": 5  # Invalid
        })
        assert response.status_code == 422


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.slow
class TestPerformance:
    """Test API performance"""
    
    def test_health_check_performance(self, client: TestClient, benchmark):
        """Benchmark health check endpoint"""
        def health_check():
            response = client.get("/health")
            assert response.status_code == 200
            return response
        
        result = benchmark(health_check)
        assert result.status_code == 200
    
    def test_get_voices_performance(self, client: TestClient, benchmark):
        """Benchmark get voices endpoint"""
        with patch('models.voice_manager.VoiceManager.get_all_voices') as mock_get:
            mock_get.return_value = []
            
            def get_voices():
                response = client.get("/api/voices")
                assert response.status_code == 200
                return response
            
            result = benchmark(get_voices)
            assert result.status_code == 200