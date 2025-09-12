import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiClient, handleAPIError } from '@/utils/api'
import type { SettingsStore, GenerationSettings, Language } from '@/types'
// import toast from 'react-hot-toast'

const defaultSettings: GenerationSettings = {
  temperature: 0.7,
  speed: 1.0,
  language: 'de',
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set, get) => ({
      settings: defaultSettings,
      languages: [],

      updateSettings: (newSettings) => {
        const { settings } = get()
        const updatedSettings = { ...settings, ...newSettings }
        set({ settings: updatedSettings })
      },

      fetchLanguages: async () => {
        try {
          const response = await apiClient.getLanguages()
          set({ languages: response.languages })
        } catch (error) {
          const errorMessage = handleAPIError(error)
          console.error('Failed to fetch languages:', errorMessage)
          
          // Fallback languages
          const fallbackLanguages: Language[] = [
            { code: 'de', name: 'Deutsch' },
            { code: 'en', name: 'English' },
            { code: 'es', name: 'Español' },
            { code: 'fr', name: 'Français' },
            { code: 'it', name: 'Italiano' },
            { code: 'pt', name: 'Português' },
          ]
          set({ languages: fallbackLanguages })
        }
      },
    }),
    {
      name: 'settings-store',
      partialize: (state) => ({ settings: state.settings }),
    }
  )
)