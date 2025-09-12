import { forwardRef } from 'react'
import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import { cn } from '@/utils/cn'
import type { ButtonProps } from '@/types'

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    variant = 'primary', 
    size = 'md', 
    loading = false, 
    disabled = false, 
    children, 
    onClick, 
    className,
    ...props 
  }, ref) => {
    const baseClasses = "inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-900 disabled:opacity-50 disabled:cursor-not-allowed"
    
    const variants = {
      primary: "bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white shadow-lg hover:shadow-xl focus:ring-primary-500",
      secondary: "bg-slate-700 hover:bg-slate-600 text-white border border-slate-600 hover:border-slate-500 focus:ring-slate-500",
      accent: "bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 text-white shadow-lg hover:shadow-xl focus:ring-accent-500",
      ghost: "text-slate-300 hover:text-white hover:bg-slate-700 focus:ring-slate-500"
    }
    
    const sizes = {
      sm: "px-3 py-2 text-sm space-x-1.5",
      md: "px-6 py-3 text-base space-x-2",
      lg: "px-8 py-4 text-lg space-x-2.5"
    }
    
    const isDisabled = disabled || loading
    
    return (
      <motion.button
        ref={ref}
        whileHover={!isDisabled ? { scale: 1.02 } : {}}
        whileTap={!isDisabled ? { scale: 0.98 } : {}}
        onClick={onClick}
        disabled={isDisabled}
        className={cn(
          baseClasses,
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {loading && (
          <Loader2 className="w-4 h-4 animate-spin" />
        )}
        {children}
      </motion.button>
    )
  }
)

Button.displayName = 'Button'

export default Button