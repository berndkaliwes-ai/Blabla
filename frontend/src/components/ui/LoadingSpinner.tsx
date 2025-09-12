import { motion } from 'framer-motion'
import { cn } from '@/utils/cn'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'primary' | 'accent' | 'white'
  className?: string
}

export default function LoadingSpinner({ 
  size = 'md', 
  variant = 'primary', 
  className 
}: LoadingSpinnerProps) {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  }

  const variants = {
    primary: 'border-primary-500',
    accent: 'border-accent-500',
    white: 'border-white'
  }

  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      className={cn(
        'border-2 border-t-transparent rounded-full',
        sizes[size],
        variants[variant],
        className
      )}
    />
  )
}

// Alternative Pulse Loader
export function PulseLoader({ 
  size = 'md', 
  variant = 'primary', 
  className 
}: LoadingSpinnerProps) {
  const sizes = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4',
    xl: 'w-6 h-6'
  }

  const variants = {
    primary: 'bg-primary-500',
    accent: 'bg-accent-500',
    white: 'bg-white'
  }

  return (
    <div className={cn('flex items-center space-x-1', className)}>
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.7, 1, 0.7]
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            delay: i * 0.2,
            ease: 'easeInOut'
          }}
          className={cn(
            'rounded-full',
            sizes[size],
            variants[variant]
          )}
        />
      ))}
    </div>
  )
}

// Wave Loader for Audio
export function WaveLoader({ className }: { className?: string }) {
  return (
    <div className={cn('flex items-center justify-center space-x-1', className)}>
      {[...Array(5)].map((_, i) => (
        <motion.div
          key={i}
          className="w-1 bg-primary-400 rounded-full"
          animate={{
            height: [4, 20, 4],
            opacity: [0.4, 1, 0.4]
          }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            delay: i * 0.1,
            ease: 'easeInOut'
          }}
        />
      ))}
    </div>
  )
}