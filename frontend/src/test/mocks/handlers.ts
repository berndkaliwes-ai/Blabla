import { http, HttpResponse } from 'msw'
import type { Voice, TTSResponse, Language } from '@/types'

// Mock data
const mockVoices: Voice[] = [
  {
    id: 'voice-1',
    name: 'Test Voice 1',
    description: 'A test voice for unit testing',
    status: 'ready',
    created_at: '2023-01-01T00:00:00Z',
    sample_count: 3,
    duration: 15.5,
    language: 'en',
    preview_url: '/voices/voice-1/preview.wav'
  },
  {
    id: 'voice-2',
    name: 'Test Voice 2',
    description: 'Another test voice',
    status: 'processing',
    created_at: '2023-01-02T00:00:00Z',
    sample_count: 5,
    duration: 22.3,
    language: 'de'
  }
]

const mockLanguages: Language[] = [
  { code: 'de', name: 'Deutsch' },
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Español' },
  { code: 'fr', name: 'Français' },
  { code: 'it', name: 'Italiano' },
  { code: 'pt', name: 'Português' }
]

export const handlers = [
  // Health check
  http.get('/health', () => {
    return HttpResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        tts: true,
        voice_manager: true,
        audio_processor: true
      }
    })
  }),

  // Get voices
  http.get('/api/voices', () => {
    return HttpResponse.json(mockVoices)
  }),

  // Get voice status
  http.get('/api/voices/:voiceId/status', ({ params }) => {
    const { voiceId } = params
    const voice = mockVoices.find(v => v.id === voiceId)
    
    if (!voice) {
      return new HttpResponse(null, { status: 404 })
    }

    return HttpResponse.json({
      voice_id: voice.id,
      status: voice.status,
      name: voice.name,
      description: voice.description,
      sample_count: voice.sample_count,
      duration: voice.duration,
      created_at: voice.created_at,
      preview_url: voice.preview_url
    })
  }),

  // Clone voice
  http.post('/api/voices/clone', async ({ request }) => {
    const formData = await request.formData()
    const name = formData.get('name') as string
    const description = formData.get('description') as string
    const files = formData.getAll('files') as File[]

    if (!name || files.length === 0) {
      return new HttpResponse(null, { status: 400 })
    }

    const newVoiceId = `voice-${Date.now()}`
    
    return HttpResponse.json({
      voice_id: newVoiceId,
      status: 'processing',
      message: `Voice Cloning für "${name}" gestartet`
    })
  }),

  // Delete voice
  http.delete('/api/voices/:voiceId', ({ params }) => {
    const { voiceId } = params
    const voiceIndex = mockVoices.findIndex(v => v.id === voiceId)
    
    if (voiceIndex === -1) {
      return new HttpResponse(null, { status: 404 })
    }

    mockVoices.splice(voiceIndex, 1)
    
    return HttpResponse.json({
      message: `Stimme ${voiceId} erfolgreich gelöscht`
    })
  }),

  // Generate TTS
  http.post('/api/tts/generate', async ({ request }) => {
    const body = await request.json() as any
    
    if (!body.text || !body.voice_id) {
      return new HttpResponse(null, { status: 400 })
    }

    const response: TTSResponse = {
      audio_url: `/outputs/tts-${Date.now()}.wav`,
      filename: `tts-${Date.now()}.wav`,
      duration: Math.random() * 10 + 2, // 2-12 seconds
      text: body.text,
      voice_id: body.voice_id,
      generated_at: new Date().toISOString()
    }

    return HttpResponse.json(response)
  }),

  // Get languages
  http.get('/api/languages', () => {
    return HttpResponse.json({
      languages: mockLanguages
    })
  }),

  // Error simulation handlers
  http.get('/api/error/500', () => {
    return new HttpResponse(null, { status: 500 })
  }),

  http.get('/api/error/404', () => {
    return new HttpResponse(null, { status: 404 })
  }),

  http.post('/api/error/timeout', () => {
    return new Promise(() => {}) // Never resolves (timeout simulation)
  })
]