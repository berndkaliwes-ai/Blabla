import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Trash2, Play, Pause, Clock, User, AlertCircle } from 'lucide-react'
import { useVoiceStore } from '@/store/useVoiceStore'
import { formatDuration } from '@/utils/api'
import type { Voice } from '@/types'

export default function VoicesPage() {
  const { voices, fetchVoices, deleteVoice, selectVoice, selectedVoice } = useVoiceStore()
  const [playingId, setPlayingId] = useState<string | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)

  useEffect(() => {
    fetchVoices()
  }, [fetchVoices])

  const handleDelete = async (voiceId: string) => {
    if (deleteConfirm === voiceId) {
      try {
        await deleteVoice(voiceId)
        setDeleteConfirm(null)
      } catch (error) {
        // Error handled in store
      }
    } else {
      setDeleteConfirm(voiceId)
      setTimeout(() => setDeleteConfirm(null), 3000) // Auto-cancel after 3s
    }
  }

  const togglePlay = (voiceId: string) => {
    if (playingId === voiceId) {
      setPlayingId(null)
    } else {
      setPlayingId(voiceId)
      // Audio playback would be handled here
    }
  }



  const getStatusText = (status: Voice['status']) => {
    switch (status) {
      case 'ready': return 'Bereit'
      case 'processing': return 'Verarbeitung...'
      case 'training': return 'Training...'
      case 'error': return 'Fehler'
      default: return 'Unbekannt'
    }
  }

  const readyVoices = voices.filter(v => v.status === 'ready')
  const processingVoices = voices.filter(v => v.status === 'processing' || v.status === 'training')
  const errorVoices = voices.filter(v => v.status === 'error')

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <h1 className="text-4xl font-bold gradient-text">Meine Stimmen</h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Verwalten Sie Ihre geklonten Stimmen und überwachen Sie den Fortschritt neuer Voice-Clones.
        </p>
      </motion.div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        <div className="card text-center">
          <div className="text-2xl font-bold text-green-400 mb-1">{readyVoices.length}</div>
          <div className="text-sm text-slate-400">Bereit</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-yellow-400 mb-1">{processingVoices.length}</div>
          <div className="text-sm text-slate-400">In Bearbeitung</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-red-400 mb-1">{errorVoices.length}</div>
          <div className="text-sm text-slate-400">Fehler</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-primary-400 mb-1">{voices.length}</div>
          <div className="text-sm text-slate-400">Gesamt</div>
        </div>
      </motion.div>

      {voices.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="card text-center py-12"
        >
          <User className="w-16 h-16 text-slate-400 mx-auto mb-4 opacity-50" />
          <h3 className="text-xl font-semibold mb-2">Noch keine Stimmen</h3>
          <p className="text-slate-400 mb-6">
            Klonen Sie Ihre erste Stimme, um hier zu beginnen.
          </p>
          <button
            onClick={() => window.location.href = '/clone'}
            className="btn-primary"
          >
            Erste Stimme klonen
          </button>
        </motion.div>
      ) : (
        <div className="space-y-6">
          {/* Ready Voices */}
          {readyVoices.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h2 className="text-2xl font-semibold mb-4 flex items-center">
                <div className="w-3 h-3 bg-green-400 rounded-full mr-3"></div>
                Bereite Stimmen ({readyVoices.length})
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {readyVoices.map((voice, index) => (
                  <motion.div
                    key={voice.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 * index }}
                    className={`card-hover cursor-pointer ${
                      selectedVoice?.id === voice.id ? 'ring-2 ring-primary-500' : ''
                    }`}
                    onClick={() => selectVoice(voice)}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg mb-1">{voice.name}</h3>
                        {voice.description && (
                          <p className="text-slate-400 text-sm mb-2 line-clamp-2">
                            {voice.description}
                          </p>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {voice.preview_url && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              togglePlay(voice.id)
                            }}
                            className="p-2 bg-primary-500 hover:bg-primary-600 rounded-lg transition-colors"
                          >
                            {playingId === voice.id ? (
                              <Pause className="w-4 h-4" />
                            ) : (
                              <Play className="w-4 h-4" />
                            )}
                          </button>
                        )}
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDelete(voice.id)
                          }}
                          className={`p-2 rounded-lg transition-colors ${
                            deleteConfirm === voice.id
                              ? 'bg-red-500 hover:bg-red-600'
                              : 'bg-slate-600 hover:bg-red-500'
                          }`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-slate-400">
                      <span>{voice.sample_count} Samples</span>
                      {voice.duration && (
                        <span>{formatDuration(voice.duration)}</span>
                      )}
                    </div>
                    
                    <div className="mt-2 text-xs text-slate-500">
                      Erstellt: {new Date(voice.created_at).toLocaleDateString('de-DE')}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Processing Voices */}
          {processingVoices.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <h2 className="text-2xl font-semibold mb-4 flex items-center">
                <div className="w-3 h-3 bg-yellow-400 rounded-full mr-3 animate-pulse"></div>
                In Bearbeitung ({processingVoices.length})
              </h2>
              
              <div className="space-y-3">
                {processingVoices.map((voice, index) => (
                  <motion.div
                    key={voice.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="card flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-4">
                      <Clock className="w-5 h-5 text-yellow-400 animate-spin" />
                      <div>
                        <h3 className="font-medium">{voice.name}</h3>
                        <p className="text-sm text-slate-400">
                          {getStatusText(voice.status)} • {voice.sample_count} Samples
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-sm text-slate-400">
                      {new Date(voice.created_at).toLocaleTimeString('de-DE')}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Error Voices */}
          {errorVoices.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
            >
              <h2 className="text-2xl font-semibold mb-4 flex items-center">
                <div className="w-3 h-3 bg-red-400 rounded-full mr-3"></div>
                Fehler ({errorVoices.length})
              </h2>
              
              <div className="space-y-3">
                {errorVoices.map((voice, index) => (
                  <motion.div
                    key={voice.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="card flex items-center justify-between border-red-500/20"
                  >
                    <div className="flex items-center space-x-4">
                      <AlertCircle className="w-5 h-5 text-red-400" />
                      <div>
                        <h3 className="font-medium">{voice.name}</h3>
                        <p className="text-sm text-red-400">
                          Verarbeitung fehlgeschlagen
                        </p>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => handleDelete(voice.id)}
                      className={`btn-secondary text-red-400 hover:bg-red-500/20 ${
                        deleteConfirm === voice.id ? 'bg-red-500 text-white' : ''
                      }`}
                    >
                      {deleteConfirm === voice.id ? 'Bestätigen?' : 'Löschen'}
                    </button>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      )}
    </div>
  )
}