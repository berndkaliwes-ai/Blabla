import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, AlertCircle, CheckCircle } from 'lucide-react'
import { cn } from '@/utils/cn'
import type { DropzoneProps } from '@/types'

export default function Dropzone({
  onDrop,
  accept = ['audio/*'],
  maxFiles = 10,
  maxSize = 50 * 1024 * 1024, // 50MB
  disabled = false,
  className,
  ...props
}: DropzoneProps) {
  const handleDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    if (rejectedFiles.length > 0) {
      console.warn('Rejected files:', rejectedFiles)
    }
    
    if (acceptedFiles.length > 0) {
      onDrop(acceptedFiles)
    }
  }, [onDrop])

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject,
    fileRejections
  } = useDropzone({
    onDrop: handleDrop,
    accept: accept.reduce((acc, type) => ({ ...acc, [type]: [] }), {}),
    maxFiles,
    maxSize,
    disabled,
    ...props
  })

  const getDropzoneState = () => {
    if (isDragReject) return 'reject'
    if (isDragAccept) return 'accept'
    if (isDragActive) return 'active'
    return 'default'
  }

  const state = getDropzoneState()

  const stateClasses = {
    default: 'border-slate-600 bg-dark-800/50',
    active: 'border-primary-500 bg-primary-500/10',
    accept: 'border-green-500 bg-green-500/10',
    reject: 'border-red-500 bg-red-500/10'
  }

  const StateIcon = state === 'accept' ? CheckCircle : 
                   state === 'reject' ? AlertCircle : Upload

  return (
    <div className={cn('w-full', className)}>
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300',
          stateClasses[state],
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <input {...getInputProps()} />
        
        <StateIcon 
          className={cn(
            'w-12 h-12 mx-auto mb-4 transition-colors duration-200',
            state === 'accept' ? 'text-green-400' :
            state === 'reject' ? 'text-red-400' :
            state === 'active' ? 'text-primary-400' : 'text-slate-400'
          )} 
        />
        
        <AnimatePresence mode="wait">
          <motion.div
            key={state}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {state === 'reject' && (
              <>
                <p className="text-lg font-medium text-red-400 mb-2">
                  Ungültige Dateien
                </p>
                <p className="text-sm text-red-300">
                  Nur Audio-Dateien bis {Math.round(maxSize / 1024 / 1024)}MB sind erlaubt
                </p>
              </>
            )}
            
            {state === 'accept' && (
              <>
                <p className="text-lg font-medium text-green-400 mb-2">
                  Dateien hier ablegen
                </p>
                <p className="text-sm text-green-300">
                  Bereit zum Upload
                </p>
              </>
            )}
            
            {state === 'active' && (
              <>
                <p className="text-lg font-medium text-primary-400 mb-2">
                  Dateien hier ablegen...
                </p>
                <p className="text-sm text-primary-300">
                  Lassen Sie die Dateien los
                </p>
              </>
            )}
            
            {state === 'default' && (
              <>
                <p className="text-lg font-medium mb-2">
                  Audio-Dateien hochladen
                </p>
                <p className="text-sm text-slate-400 mb-4">
                  Ziehen Sie Dateien hierher oder klicken Sie zum Auswählen
                </p>
                <div className="flex items-center justify-center space-x-4 text-xs text-slate-500">
                  <span>WAV, MP3, OGG</span>
                  <span>•</span>
                  <span>Max. {Math.round(maxSize / 1024 / 1024)}MB</span>
                  <span>•</span>
                  <span>Bis zu {maxFiles} Dateien</span>
                </div>
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* File Rejections */}
      <AnimatePresence>
        {fileRejections.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg"
          >
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <h4 className="font-medium text-red-400 mb-2">
                  Einige Dateien konnten nicht verarbeitet werden:
                </h4>
                <ul className="space-y-1 text-sm text-red-300">
                  {fileRejections.map(({ file, errors }) => (
                    <li key={file.name}>
                      <span className="font-medium">{file.name}:</span>{' '}
                      {errors.map(e => e.message).join(', ')}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}