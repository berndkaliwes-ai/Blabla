import { motion } from 'framer-motion'
import { cn } from '@/utils/cn'

interface ProgressBarProps {
  progress: number // 0-100
  variant?: 'primary' | 'accent' | 'success' | 'warning' | 'error'
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  label?: string
  animated?: boolean
  className?: string
}

export default function ProgressBar({
  progress,
  variant = 'primary',
  size = 'md',
  showLabel = false,
  label,
  animated = true,
  className
}: ProgressBarProps) {
  const clampedProgress = Math.max(0, Math.min(100, progress))

  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  }

  const variants = {
    primary: 'from-primary-500 to-primary-400',
    accent: 'from-accent-500 to-accent-400',
    success: 'from-green-500 to-green-400',
    warning: 'from-yellow-500 to-yellow-400',
    error: 'from-red-500 to-red-400'
  }

  return (
    <div className={cn('w-full', className)}>
      {(showLabel || label) && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-slate-300">
            {label || 'Fortschritt'}
          </span>
          <span className="text-sm text-slate-400">
            {Math.round(clampedProgress)}%
          </span>
        </div>
      )}
      
      <div className={cn(
        'w-full bg-slate-700 rounded-full overflow-hidden',
        sizes[size]
      )}>
        <motion.div
          className={cn(
            'h-full bg-gradient-to-r rounded-full',
            variants[variant]
          )}
          initial={{ width: 0 }}
          animate={{ width: `${clampedProgress}%` }}
          transition={animated ? {
            type: 'spring',
            stiffness: 100,
            damping: 20
          } : { duration: 0 }}
        >
          {animated && clampedProgress > 0 && (
            <motion.div
              className="h-full w-full bg-gradient-to-r from-transparent via-white/20 to-transparent"
              animate={{ x: ['-100%', '100%'] }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'linear'
              }}
            />
          )}
        </motion.div>
      </div>
    </div>
  )
}

// Circular Progress Bar
export function CircularProgress({
  progress,
  size = 80,
  strokeWidth = 8,
  variant = 'primary',
  showLabel = true,
  className
}: {
  progress: number
  size?: number
  strokeWidth?: number
  variant?: 'primary' | 'accent' | 'success' | 'warning' | 'error'
  showLabel?: boolean
  className?: string
}) {
  const clampedProgress = Math.max(0, Math.min(100, progress))
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const strokeDasharray = circumference
  const strokeDashoffset = circumference - (clampedProgress / 100) * circumference

  const variants = {
    primary: '#3b82f6',
    accent: '#d946ef',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444'
  }

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#374151"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={variants[variant]}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeLinecap="round"
          strokeDasharray={strokeDasharray}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: 'easeInOut' }}
        />
      </svg>
      
      {showLabel && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-sm font-semibold text-white">
            {Math.round(clampedProgress)}%
          </span>
        </div>
      )}
    </div>
  )
}