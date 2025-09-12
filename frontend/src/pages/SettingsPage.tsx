import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { Settings, Globe, Zap, Info } from 'lucide-react'
import { useSettingsStore } from '@/store/useSettingsStore'
import { useTTSStore } from '@/store/useTTSStore'

export default function SettingsPage() {
  const { settings, updateSettings, languages, fetchLanguages } = useSettingsStore()
  const { clearHistory, history } = useTTSStore()

  useEffect(() => {
    fetchLanguages()
  }, [fetchLanguages])

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <h1 className="text-4xl font-bold gradient-text">Einstellungen</h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Konfigurieren Sie Ihre Präferenzen für optimale Voice Cloning und TTS Ergebnisse.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Generation Settings */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-6"
        >
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-primary-500/20 rounded-xl flex items-center justify-center">
                <Zap className="w-5 h-5 text-primary-400" />
              </div>
              <h2 className="text-xl font-semibold">Generierungs-Einstellungen</h2>
            </div>

            <div className="space-y-6">
              {/* Language */}
              <div>
                <label className="block text-sm font-medium mb-3">
                  <Globe className="w-4 h-4 inline mr-2" />
                  Standard-Sprache
                </label>
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
                <p className="text-xs text-slate-400 mt-2">
                  Die Sprache, die standardmäßig für neue TTS-Generierungen verwendet wird.
                </p>
              </div>

              {/* Speed */}
              <div>
                <label className="block text-sm font-medium mb-3">
                  Sprechgeschwindigkeit: {settings.speed}x
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="2"
                  step="0.1"
                  value={settings.speed}
                  onChange={(e) => updateSettings({ speed: parseFloat(e.target.value) })}
                  className="w-full accent-primary-500"
                />
                <div className="flex justify-between text-xs text-slate-400 mt-1">
                  <span>0.5x (Langsam)</span>
                  <span>1.0x (Normal)</span>
                  <span>2.0x (Schnell)</span>
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  Steuert die Geschwindigkeit der generierten Sprache.
                </p>
              </div>

              {/* Temperature */}
              <div>
                <label className="block text-sm font-medium mb-3">
                  Kreativität/Variabilität: {settings.temperature}
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="1"
                  step="0.1"
                  value={settings.temperature}
                  onChange={(e) => updateSettings({ temperature: parseFloat(e.target.value) })}
                  className="w-full accent-primary-500"
                />
                <div className="flex justify-between text-xs text-slate-400 mt-1">
                  <span>0.1 (Konsistent)</span>
                  <span>0.7 (Ausgewogen)</span>
                  <span>1.0 (Kreativ)</span>
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  Höhere Werte führen zu mehr Variation, niedrigere zu konsistenteren Ergebnissen.
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Data Management */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-6"
        >
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-accent-500/20 rounded-xl flex items-center justify-center">
                <Settings className="w-5 h-5 text-accent-400" />
              </div>
              <h2 className="text-xl font-semibold">Daten-Verwaltung</h2>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-dark-700 rounded-lg">
                <div>
                  <h3 className="font-medium mb-1">TTS-Verlauf</h3>
                  <p className="text-sm text-slate-400">
                    {history.length} generierte Audio-Dateien
                  </p>
                </div>
                <button
                  onClick={clearHistory}
                  disabled={history.length === 0}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Löschen
                </button>
              </div>

              <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                <div className="flex items-start space-x-3">
                  <Info className="w-5 h-5 text-yellow-400 mt-0.5" />
                  <div>
                    <h3 className="font-medium text-yellow-400 mb-1">Hinweis</h3>
                    <p className="text-sm text-slate-300">
                      Das Löschen des Verlaufs entfernt nur die Referenzen. 
                      Die Audio-Dateien bleiben auf dem Server gespeichert.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* System Info */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-emerald-500/20 rounded-xl flex items-center justify-center">
                <Info className="w-5 h-5 text-emerald-400" />
              </div>
              <h2 className="text-xl font-semibold">System-Information</h2>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b border-slate-700">
                <span className="text-slate-400">Version</span>
                <span className="font-mono">1.0.0</span>
              </div>
              
              <div className="flex justify-between py-2 border-b border-slate-700">
                <span className="text-slate-400">XTTS Model</span>
                <span className="font-mono">V2</span>
              </div>
              
              <div className="flex justify-between py-2 border-b border-slate-700">
                <span className="text-slate-400">Unterstützte Sprachen</span>
                <span className="font-mono">{languages.length}</span>
              </div>
              
              <div className="flex justify-between py-2">
                <span className="text-slate-400">GPU-Beschleunigung</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-green-400 text-sm">Aktiv</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Tips */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="glass rounded-2xl p-6"
      >
        <h3 className="text-lg font-semibold mb-4">💡 Tipps für beste Ergebnisse</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-300">
          <div>
            <h4 className="font-medium text-white mb-2">Voice Cloning:</h4>
            <ul className="space-y-1 text-slate-400">
              <li>• Verwenden Sie klare, rauschfreie Aufnahmen</li>
              <li>• 3-30 Sekunden pro Audio-Datei</li>
              <li>• Mindestens 3-5 verschiedene Samples</li>
              <li>• Gleichmäßige Lautstärke und Tempo</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-white mb-2">Text-to-Speech:</h4>
            <ul className="space-y-1 text-slate-400">
              <li>• Niedrige Temperatur für konsistente Ergebnisse</li>
              <li>• Höhere Temperatur für mehr Variation</li>
              <li>• Angepasste Geschwindigkeit je nach Anwendung</li>
              <li>• Korrekte Sprache für beste Aussprache</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  )
}