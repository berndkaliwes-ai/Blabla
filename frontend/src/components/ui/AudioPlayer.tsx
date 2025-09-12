import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Play, Pause, Volume2, Download, RotateCcw } from 'lucide-react'
import { cn } from '@/utils/cn'
import type { AudioPlayerProps } from '@/types'

export default function AudioPlayer({
  src,
  title,
  onPlay,
  onPause,
  onEnded,
  className
}: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  
  const audioRef = useRef<HTMLAudioElement>(null)
  const progressRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handleLoadedData = () => {
      setDuration(audio.duration)
      setIsLoading(false)
    }

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime)
    }

    const handleEnded = () => {
      setIsPlaying(false)
      setCurrentTime(0)
      onEnded?.()
    }

    const handlePlay = () => {
      setIsPlaying(true)
      onPlay?.()
    }

    const handlePause = () => {
      setIsPlaying(false)
      onPause?.()
    }

    audio.addEventListener('loadeddata', handleLoadedData)
    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)

    return () => {
      audio.removeEventListener('loadeddata', handleLoadedData)
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
    }
  }, [onPlay, onPause, onEnded])

  const togglePlayPause = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
    } else {
      audio.play()
    }
  }

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current
    const progressBar = progressRef.current
    if (!audio || !progressBar) return

    const rect = progressBar.getBoundingClientRect()
    const clickX = e.clientX - rect.left
    const newTime = (clickX / rect.width) * duration
    
    audio.currentTime = newTime
    setCurrentTime(newTime)
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value)
    setVolume(newVolume)
    
    const audio = audioRef.current
    if (audio) {
      audio.volume = newVolume
    }
  }

  const resetAudio = () => {
    const audio = audioRef.current
    if (!audio) return

    audio.currentTime = 0
    setCurrentTime(0)
    if (isPlaying) {
      audio.pause()
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'bg-dark-700 rounded-xl p-4 border border-slate-600',
        className
      )}
    >
      <audio ref={audioRef} src={src} preload="metadata" />
      
      {/* Header */}
      {title && (
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-medium text-white truncate">{title}</h3>
          <div className="flex items-center space-x-2">
            <a
              href={src}
              download
              className="p-2 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-slate-600"
            >
              <Download className="w-4 h-4" />
            </a>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      <div className="mb-4">
        <div
          ref={progressRef}
          onClick={handleProgressClick}
          className="relative h-2 bg-slate-600 rounded-full cursor-pointer group"
        >
          <motion.div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-primary-500 to-primary-400 rounded-full"
            style={{ width: `${progress}%` }}
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          />
          
          {/* Progress Handle */}
          <motion.div
            className="absolute top-1/2 transform -translate-y-1/2 w-4 h-4 bg-primary-400 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
            style={{ left: `${progress}%`, marginLeft: '-8px' }}
            whileHover={{ scale: 1.2 }}
          />
        </div>
        
        <div className="flex justify-between text-xs text-slate-400 mt-1">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {/* Play/Pause Button */}
          <motion.button
            onClick={togglePlayPause}
            disabled={isLoading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center justify-center w-10 h-10 bg-primary-500 hover:bg-primary-600 rounded-full text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : isPlaying ? (
              <Pause className="w-5 h-5" />
            ) : (
              <Play className="w-5 h-5 ml-0.5" />
            )}
          </motion.button>

          {/* Reset Button */}
          <motion.button
            onClick={resetAudio}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-slate-600"
          >
            <RotateCcw className="w-4 h-4" />
          </motion.button>
        </div>

        {/* Volume Control */}
        <div className="flex items-center space-x-2">
          <Volume2 className="w-4 h-4 text-slate-400" />
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={handleVolumeChange}
            className="w-16 accent-primary-500"
          />
        </div>
      </div>

      {/* Waveform Visualization (Optional) */}
      {isPlaying && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center justify-center space-x-1 mt-4"
        >
          {[...Array(12)].map((_, i) => (
            <motion.div
              key={i}
              className="w-1 bg-primary-400 rounded-full"
              animate={{
                height: [4, 20, 4],
                opacity: [0.4, 1, 0.4]
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: i * 0.1,
                ease: 'easeInOut'
              }}
            />
          ))}
        </motion.div>
      )}
    </motion.div>
  )
}