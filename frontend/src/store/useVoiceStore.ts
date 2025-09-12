import { create } from 'zustand'
import { apiClient, handleAPIError } from '@/utils/api'
import type { Voice, VoiceStore } from '@/types'
import toast from 'react-hot-toast'

export const useVoiceStore = create<VoiceStore>((set, get) => ({
  voices: [],
  selectedVoice: null,
  isLoading: false,
  error: null,

  fetchVoices: async () => {
    set({ isLoading: true, error: null })
    
    try {
      const voices = await apiClient.getVoices()
      set({ voices, isLoading: false })
    } catch (error) {
      const errorMessage = handleAPIError(error)
      set({ error: errorMessage, isLoading: false })
      toast.error(`Fehler beim Laden der Stimmen: ${errorMessage}`)
    }
  },

  selectVoice: (voice) => {
    set({ selectedVoice: voice })
  },

  deleteVoice: async (voiceId) => {
    const { voices } = get()
    
    try {
      await apiClient.deleteVoice(voiceId)
      
      // Remove from local state
      const updatedVoices = voices.filter(v => v.id !== voiceId)
      set({ voices: updatedVoices })
      
      // Clear selection if deleted voice was selected
      const { selectedVoice } = get()
      if (selectedVoice?.id === voiceId) {
        set({ selectedVoice: null })
      }
      
      toast.success('Stimme erfolgreich gelöscht')
    } catch (error) {
      const errorMessage = handleAPIError(error)
      toast.error(`Fehler beim Löschen: ${errorMessage}`)
      throw error
    }
  },

  cloneVoice: async (request: any) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await apiClient.cloneVoice(request)
      
      // Add new voice to state with processing status
      const newVoice: Voice = {
        id: response.voice_id,
        name: request.name,
        description: request.description,
        status: 'processing',
        created_at: new Date().toISOString(),
        sample_count: request.files.length,
      }
      
      const { voices } = get()
      set({ 
        voices: [newVoice, ...voices],
        isLoading: false 
      })
      
      toast.success(`Voice Cloning für "${request.name}" gestartet`)
      return response.voice_id
      
    } catch (error) {
      const errorMessage = handleAPIError(error)
      set({ error: errorMessage, isLoading: false })
      toast.error(`Fehler beim Voice Cloning: ${errorMessage}`)
      throw error
    }
  },
}))