import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Mic, 
  MessageSquare, 
  Users, 
  Settings, 
  Home,
  Menu,
  X,
  Zap
} from 'lucide-react'
import { cn } from '@/utils/cn'

interface LayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Voice Cloning', href: '/clone', icon: Mic },
  { name: 'Text-to-Speech', href: '/tts', icon: MessageSquare },
  { name: 'Meine Stimmen', href: '/voices', icon: Users },
  { name: 'Einstellungen', href: '/settings', icon: Settings },
]

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  return (
    <div className="min-h-screen bg-dark-900">
      {/* Mobile sidebar */}
      <motion.div
        initial={false}
        animate={sidebarOpen ? { x: 0 } : { x: '-100%' }}
        transition={{ type: 'tween', duration: 0.3 }}
        className="fixed inset-y-0 left-0 z-50 w-64 bg-dark-800 border-r border-slate-700 lg:hidden"
      >
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold gradient-text">XTTS Studio</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 rounded-lg hover:bg-slate-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <nav className="p-4 space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  'flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200',
                  isActive
                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                    : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                )}
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
              </Link>
            )
          })}
        </nav>
      </motion.div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:z-50 lg:block lg:w-64 lg:bg-dark-800 lg:border-r lg:border-slate-700">
        <div className="flex items-center space-x-2 p-6 border-b border-slate-700">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center animate-pulse-slow">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold gradient-text">XTTS Studio</h1>
            <p className="text-xs text-slate-400">Voice Cloning V2</p>
          </div>
        </div>
        
        <nav className="p-4 space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 group',
                  isActive
                    ? 'bg-gradient-to-r from-primary-500/20 to-accent-500/20 text-primary-400 border border-primary-500/30 shadow-lg'
                    : 'text-slate-300 hover:bg-slate-700 hover:text-white hover:scale-105'
                )}
              >
                <item.icon className={cn(
                  'w-5 h-5 transition-transform duration-200',
                  isActive ? 'scale-110' : 'group-hover:scale-110'
                )} />
                <span className="font-medium">{item.name}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="ml-auto w-2 h-2 bg-primary-400 rounded-full"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
              </Link>
            )
          })}
        </nav>

        {/* Status indicator */}
        <div className="absolute bottom-4 left-4 right-4">
          <div className="glass rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-xs text-slate-400">System Online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile header */}
      <div className="lg:hidden">
        <div className="flex items-center justify-between p-4 bg-dark-800 border-b border-slate-700">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-lg hover:bg-slate-700 transition-colors"
          >
            <Menu className="w-6 h-6" />
          </button>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold gradient-text">XTTS Studio</span>
          </div>
          <div className="w-10"></div> {/* Spacer */}
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        <main className="min-h-screen">
          <div className="p-4 lg:p-8">
            {children}
          </div>
        </main>
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
        />
      )}
    </div>
  )
}