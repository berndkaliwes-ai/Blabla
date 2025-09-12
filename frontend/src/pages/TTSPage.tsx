import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Play, Download, Loader2, Volume2, Settings } from 'lucide-react'
import { useVoiceStore } from '@/store/useVoiceStore'
import { useTTSStore } from '@/store/useTTSStore'
import { useSettingsStore } from '@/store/useSettingsStore'
import type { TTSRequest } from '@/types'
import toast from 'react-hot-toast'

export default function TTSPage() {
  const [text, setText] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  
  const { voices, selectedVoice, selectVoice, fetchVoices } = useVoiceStore()
  const { generateSpeech, isGenerating, currentAudio } = useTTSStore()
  const { settings, updateSettings, languages, fetchLanguages } = useSettingsStore()

  useEffect(() => {
    fetchVoices()
    fetchLanguages()
  }, [fetchVoices, fetchLanguages])

  const handleGenerate = async () => {
    if (!text.trim()) {
      toast.error('Bitte geben Sie einen Text ein')
      return
    }
    
    if (!selectedVoice) {
      toast.error('Bitte wählen Sie eine Stimme aus')
      return
    }

    const request: TTSRequest = {
      text: text.trim(),
      voice_id: selectedVoice.id,
      language: settings.language,
      speed: settings.speed,
      temperature: settings.temperature
    }

    try {
      await generateSpeech(request)
    } catch (error) {
      // Error handled in store
    }
  }

  const readyVoices = voices.filter(v => v.status === 'ready')

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <h1 className="text-4xl font-bold gradient-text">Text-to-Speech</h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Verwandeln Sie jeden Text in natürlich klingende Sprache mit Ihren geklonten Stimmen.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Text Input */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2 space-y-6"
        >
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Text eingeben</h2>
              <span className="text-sm text-slate-400">
                {text.length}/5000 Zeichen
              </span>
            </div>
            
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Geben Sie hier den Text ein, der gesprochen werden soll..."
              rows={8}
              maxLength={5000}
              className="input-primary w-full resize-none"
            />
            
            <div className="flex items-center justify-between mt-4">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="btn-secondary inline-flex items-center space-x-2"
              >
                <Settings className="w-4 h-4" />
                <span>Einstellungen</span>
              </button>
              
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !text.trim() || !selectedVoice}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Generiere...</span>
                  </>
                ) : (
                  <>
                    <Volume2 className="w-5 h-5" />
                    <span>Sprechen</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Settings Panel */}
          {showSettings && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="card"
            >
              <h3 className="text-lg font-semibold mb-4">Generierungs-Einstellungen</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Sprache</label>
                  <select
                    value={settings.language}
                    onChange={(e) => updateSettings({ language: e.target.value })}
                    className="input-primary w-full"
                  >
                    {languages.map((lang) => (
                      <option key={lang.code} value={lang.code}>
                        {lang.name}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Geschwindigkeit: {settings.speed}x
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    value={settings.speed}
                    onChange={(e) => updateSettings({ speed: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Kreativität: {settings.temperature}
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1"
                    step="0.1"
                    value={settings.temperature}
                    onChange={(e) => updateSettings({ temperature: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                </div>
              </div>
            </motion.div>
          )}

          {/* Generated Audio */}
          {currentAudio && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <h3 className="text-lg font-semibold mb-4">Generiertes Audio</h3>
              
              <div className="bg-dark-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-medium">{currentAudio.filename}</span>
                  <span className="text-sm text-slate-400">
                    {currentAudio.duration.toFixed(1)}s
                  </span>
                </div>
                
                <audio
                  controls
                  src={currentAudio.audio_url}
                  className="w-full mb-3"
                />
                
                <div className="flex items-center space-x-2">
                  <a
                    href={currentAudio.audio_url}
                    download={currentAudio.filename}
                    className="btn-secondary inline-flex items-center space-x-2"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download</span>
                  </a>
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>

        {/* Voice Selection */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-6"
        >
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Stimme auswählen</h2>
            
            {readyVoices.length === 0 ? (
              <div className="text-center py-8 text-slate-400">
                <Volume2 className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="mb-2">Keine Stimmen verfügbar</p>
                <p className="text-sm">Klonen Sie zuerst eine Stimme</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
                {readyVoices.map((voice) => (
                  <motion.button
                    key={voice.id}
                    onClick={() => selectVoice(voice)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                      selectedVoice?.id === voice.id
                        ? 'border-primary-500 bg-primary-500/10'
                        : 'border-slate-600 hover:border-slate-500 bg-dark-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{voice.name}</h3>
                      {voice.preview_url && (
                        <Play className="w-4 h-4 text-slate-400" />
                      )}
                    </div>
                    
                    {voice.description && (
                      <p className="text-sm text-slate-400 mb-2">
                        {voice.description}
                      </p>
                    )}
                    
                    <div className="flex items-center space-x-4 text-xs text-slate-500">
                      <span>{voice.sample_count} Samples</span>
                      {voice.duration && (
                        <span>{voice.duration.toFixed(1)}s</span>
                      )}
                    </div>
                  </motion.button>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}