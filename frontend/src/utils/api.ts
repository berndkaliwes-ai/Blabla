import axios from 'axios'
import type { 
  Voice, 
  TTSRequest, 
  TTSResponse, 
  VoiceCloneRequest, 
  Language, 
  HealthResponse 
} from '@/types'

// API Client Setup
const api = axios.create({
  baseURL: '/api',
  timeout: 60000, // 60 seconds for large file uploads
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// API Functions
export const apiClient = {
  // Health Check
  async getHealth(): Promise<HealthResponse> {
    const response = await api.get('/health')
    return response.data
  },

  // Voices
  async getVoices(): Promise<Voice[]> {
    const response = await api.get('/voices')
    return response.data
  },

  async cloneVoice(request: VoiceCloneRequest): Promise<{ voice_id: string; status: string; message: string }> {
    const formData = new FormData()
    formData.append('name', request.name)
    formData.append('description', request.description)
    
    request.files.forEach((file) => {
      formData.append('files', file)
    })

    const response = await api.post('/voices/clone', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getVoiceStatus(voiceId: string): Promise<any> {
    const response = await api.get(`/voices/${voiceId}/status`)
    return response.data
  },

  async deleteVoice(voiceId: string): Promise<{ message: string }> {
    const response = await api.delete(`/voices/${voiceId}`)
    return response.data
  },

  // Text-to-Speech
  async generateSpeech(request: TTSRequest): Promise<TTSResponse> {
    const response = await api.post('/tts/generate', request)
    return response.data
  },

  // Languages
  async getLanguages(): Promise<{ languages: Language[] }> {
    const response = await api.get('/languages')
    return response.data
  },
}

// Utility functions
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export const validateAudioFile = (file: File): { valid: boolean; error?: string } => {
  const validTypes = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/ogg', 'audio/webm']
  const maxSize = 50 * 1024 * 1024 // 50MB
  
  if (!validTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Nur Audio-Dateien sind erlaubt (WAV, MP3, OGG, WebM)'
    }
  }
  
  if (file.size > maxSize) {
    return {
      valid: false,
      error: 'Datei ist zu groß (max. 50MB)'
    }
  }
  
  return { valid: true }
}

export const createAudioPreview = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

export const getAudioDuration = (file: File): Promise<number> => {
  return new Promise((resolve, reject) => {
    const audio = new Audio()
    const url = URL.createObjectURL(file)
    
    audio.addEventListener('loadedmetadata', () => {
      URL.revokeObjectURL(url)
      resolve(audio.duration)
    })
    
    audio.addEventListener('error', () => {
      URL.revokeObjectURL(url)
      reject(new Error('Could not load audio file'))
    })
    
    audio.src = url
  })
}

// Error handling
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message)
    this.name = 'APIError'
  }
}

export const handleAPIError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail
  }
  
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  
  if (error.message) {
    return error.message
  }
  
  return 'Ein unbekannter Fehler ist aufgetreten'
}