import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiClient, handleAPIError } from '@/utils/api'
import type { TTSStore, TTSRequest } from '@/types'
import toast from 'react-hot-toast'

export const useTTSStore = create<TTSStore>()(
  persist(
    (set, get) => ({
      isGenerating: false,
      currentAudio: null,
      history: [],

      generateSpeech: async (request: TTSRequest) => {
        set({ isGenerating: true })
        
        try {
          const response = await apiClient.generateSpeech(request)
          
          const { history } = get()
          const updatedHistory = [response, ...history.slice(0, 19)] // Keep last 20
          
          set({ 
            currentAudio: response,
            history: updatedHistory,
            isGenerating: false 
          })
          
          toast.success('Audio erfolgreich generiert!')
          return response
          
        } catch (error) {
          const errorMessage = handleAPIError(error)
          set({ isGenerating: false })
          toast.error(`Fehler bei der Audio-Generierung: ${errorMessage}`)
          throw error
        }
      },

      clearHistory: () => {
        set({ history: [], currentAudio: null })
        toast.success('Verlauf gelöscht')
      },
    }),
    {
      name: 'tts-store',
      partialize: (state) => ({ 
        history: state.history.slice(0, 10) // Only persist last 10 items
      }),
    }
  )
)