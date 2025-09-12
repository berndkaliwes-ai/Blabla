import { useState } from 'react'
import { motion } from 'framer-motion'
import { Upload, X, Play, Pause, Loader2 } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import { useVoiceStore } from '@/store/useVoiceStore'
import { validateAudioFile, formatFileSize, getAudioDuration } from '@/utils/api'
import type { AudioFile } from '@/types'
import toast from 'react-hot-toast'

export default function VoiceClonePage() {
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([])
  const [voiceName, setVoiceName] = useState('')
  const [voiceDescription, setVoiceDescription] = useState('')
  const [playingId, setPlayingId] = useState<string | null>(null)
  
  const { cloneVoice, isLoading } = useVoiceStore()

  const onDrop = async (acceptedFiles: File[]) => {
    const newFiles: AudioFile[] = []
    
    for (const file of acceptedFiles) {
      const validation = validateAudioFile(file)
      if (!validation.valid) {
        toast.error(validation.error!)
        continue
      }

      try {
        const duration = await getAudioDuration(file)
        const preview = URL.createObjectURL(file)
        
        const audioFile: AudioFile = {
          id: Math.random().toString(36).substr(2, 9),
          file,
          name: file.name,
          size: file.size,
          duration,
          preview
        }
        
        newFiles.push(audioFile)
      } catch (error) {
        toast.error(`Fehler beim Verarbeiten von ${file.name}`)
      }
    }
    
    setAudioFiles(prev => [...prev, ...newFiles])
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.ogg', '.webm']
    },
    maxFiles: 10,
    maxSize: 50 * 1024 * 1024 // 50MB
  })

  const removeFile = (id: string) => {
    setAudioFiles(prev => {
      const file = prev.find(f => f.id === id)
      if (file?.preview) {
        URL.revokeObjectURL(file.preview)
      }
      return prev.filter(f => f.id !== id)
    })
  }

  const togglePlay = (id: string, _src: string) => {
    if (playingId === id) {
      setPlayingId(null)
    } else {
      setPlayingId(id)
      // Audio would be handled by a proper audio player component
    }
  }

  const handleSubmit = async () => {
    if (!voiceName.trim()) {
      toast.error('Bitte geben Sie einen Namen für die Stimme ein')
      return
    }
    
    if (audioFiles.length === 0) {
      toast.error('Bitte laden Sie mindestens eine Audio-Datei hoch')
      return
    }

    try {
      await cloneVoice({
        name: voiceName,
        description: voiceDescription,
        files: audioFiles.map(af => af.file)
      })
      
      // Reset form
      setVoiceName('')
      setVoiceDescription('')
      setAudioFiles([])
      
    } catch (error) {
      // Error is handled in the store
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <h1 className="text-4xl font-bold gradient-text">Voice Cloning</h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Laden Sie Audio-Dateien hoch, um eine neue Stimme zu klonen. 
          Für beste Ergebnisse verwenden Sie klare, rauschfreie Aufnahmen von 3-30 Sekunden.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-6"
        >
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Audio-Dateien hochladen</h2>
            
            <div
              {...getRootProps()}
              className={`dropzone ${isDragActive ? 'dropzone-active' : ''}`}
            >
              <input {...getInputProps()} />
              <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
              <p className="text-lg font-medium mb-2">
                {isDragActive ? 'Dateien hier ablegen...' : 'Audio-Dateien hochladen'}
              </p>
              <p className="text-slate-400 text-sm">
                WAV, MP3, OGG oder WebM • Max. 50MB pro Datei
              </p>
            </div>
          </div>

          {/* Voice Info */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Stimmen-Informationen</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Name der Stimme *</label>
                <input
                  type="text"
                  value={voiceName}
                  onChange={(e) => setVoiceName(e.target.value)}
                  placeholder="z.B. Meine Stimme"
                  className="input-primary w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Beschreibung (optional)</label>
                <textarea
                  value={voiceDescription}
                  onChange={(e) => setVoiceDescription(e.target.value)}
                  placeholder="Beschreibung der Stimme..."
                  rows={3}
                  className="input-primary w-full resize-none"
                />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Files List */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-6"
        >
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">
                Hochgeladene Dateien ({audioFiles.length})
              </h2>
              {audioFiles.length > 0 && (
                <span className="text-sm text-slate-400">
                  {formatFileSize(audioFiles.reduce((sum, f) => sum + f.size, 0))} gesamt
                </span>
              )}
            </div>
            
            {audioFiles.length === 0 ? (
              <div className="text-center py-8 text-slate-400">
                <Upload className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>Noch keine Dateien hochgeladen</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
                {audioFiles.map((file) => (
                  <motion.div
                    key={file.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="flex items-center space-x-3 p-3 bg-dark-700 rounded-lg"
                  >
                    <button
                      onClick={() => togglePlay(file.id, file.preview!)}
                      className="p-2 bg-primary-500 hover:bg-primary-600 rounded-lg transition-colors"
                    >
                      {playingId === file.id ? (
                        <Pause className="w-4 h-4" />
                      ) : (
                        <Play className="w-4 h-4" />
                      )}
                    </button>
                    
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{file.name}</p>
                      <p className="text-sm text-slate-400">
                        {formatFileSize(file.size)} • {file.duration?.toFixed(1)}s
                      </p>
                    </div>
                    
                    <button
                      onClick={() => removeFile(file.id)}
                      className="p-2 text-slate-400 hover:text-red-400 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </motion.div>
                ))}
              </div>
            )}
          </div>

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={isLoading || !voiceName.trim() || audioFiles.length === 0}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Stimme wird geklont...</span>
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                <span>Stimme klonen</span>
              </>
            )}
          </button>
        </motion.div>
      </div>
    </div>
  )
}