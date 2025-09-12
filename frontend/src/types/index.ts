// API Types
export interface Voice {
  id: string
  name: string
  description: string
  status: 'processing' | 'ready' | 'error' | 'training'
  created_at: string
  language?: string
  sample_count: number
  duration?: number
  preview_url?: string
}

export interface TTSRequest {
  text: string
  voice_id: string
  language: string
  speed: number
  temperature: number
}

export interface TTSResponse {
  audio_url: string
  filename: string
  duration: number
  text: string
  voice_id: string
  generated_at: string
}

export interface VoiceCloneRequest {
  name: string
  description: string
  files: File[]
}

export interface Language {
  code: string
  name: string
}

export interface HealthResponse {
  status: string
  timestamp: string
  services: {
    tts: boolean
    voice_manager: boolean
    audio_processor: boolean
  }
}

// UI Types
export interface AudioFile {
  id: string
  file: File
  name: string
  size: number
  duration?: number
  preview?: string
}

export interface GenerationSettings {
  temperature: number
  speed: number
  language: string
}

export interface VoiceCloneProgress {
  voice_id: string
  status: 'processing' | 'ready' | 'error'
  progress?: number
  message?: string
  error?: string
}

// Store Types
export interface AppState {
  voices: Voice[]
  selectedVoice: Voice | null
  isLoading: boolean
  error: string | null
  settings: GenerationSettings
}

export interface VoiceStore {
  voices: Voice[]
  selectedVoice: Voice | null
  isLoading: boolean
  error: string | null
  fetchVoices: () => Promise<void>
  selectVoice: (voice: Voice | null) => void
  deleteVoice: (voiceId: string) => Promise<void>
  cloneVoice: (request: VoiceCloneRequest) => Promise<string>
}

export interface TTSStore {
  isGenerating: boolean
  currentAudio: TTSResponse | null
  history: TTSResponse[]
  generateSpeech: (request: TTSRequest) => Promise<TTSResponse>
  clearHistory: () => void
}

export interface SettingsStore {
  settings: GenerationSettings
  languages: Language[]
  updateSettings: (settings: Partial<GenerationSettings>) => void
  fetchLanguages: () => Promise<void>
}

// Component Props
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'accent' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  children: React.ReactNode
  onClick?: () => void
  className?: string
}

export interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  glass?: boolean
}

export interface DropzoneProps {
  onDrop: (files: File[]) => void
  accept?: string[]
  maxFiles?: number
  maxSize?: number
  disabled?: boolean
  className?: string
}

export interface AudioPlayerProps {
  src: string
  title?: string
  onPlay?: () => void
  onPause?: () => void
  onEnded?: () => void
  className?: string
}

export interface WaveformProps {
  isPlaying: boolean
  className?: string
}

export interface VoiceCardProps {
  voice: Voice
  onSelect?: (voice: Voice) => void
  onDelete?: (voiceId: string) => void
  selected?: boolean
  className?: string
}