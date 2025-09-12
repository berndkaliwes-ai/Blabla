import { forwardRef } from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/utils/cn'
import type { CardProps } from '@/types'

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ children, className, hover = false, glass = false, ...props }, ref) => {
    const baseClasses = "rounded-xl p-6 shadow-lg"
    
    const variants = {
      default: "bg-dark-800 border border-slate-700",
      glass: "glass border-white/10",
      hover: "bg-dark-800 border border-slate-700 hover:border-slate-600 hover:shadow-xl transition-all duration-300"
    }
    
    const variant = glass ? 'glass' : hover ? 'hover' : 'default'
    
    const CardComponent = hover ? motion.div : 'div'
    const motionProps = hover ? {
      whileHover: { scale: 1.02, y: -2 },
      transition: { type: 'spring', stiffness: 300, damping: 30 }
    } : {}
    
    return (
      <CardComponent
        ref={ref}
        className={cn(baseClasses, variants[variant], className)}
        {...motionProps}
        {...props}
      >
        {children}
      </CardComponent>
    )
  }
)

Card.displayName = 'Card'

export default Card