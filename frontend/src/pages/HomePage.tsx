import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Mic, 
  MessageSquare, 
  Users, 
  Zap, 
  ArrowRight,
  Play,
  Upload,
  Sparkles
} from 'lucide-react'
import { useVoiceStore } from '@/store/useVoiceStore'
import { useTTSStore } from '@/store/useTTSStore'

const features = [
  {
    icon: Mic,
    title: 'Voice Cloning',
    description: 'Klonen Sie jede Stimme mit nur wenigen Audio-Samples',
    href: '/clone',
    color: 'from-primary-500 to-primary-600',
    action: 'Stimme klonen'
  },
  {
    icon: MessageSquare,
    title: 'Text-to-Speech',
    description: 'Verwandeln Sie Text in natürlich klingende Sprache',
    href: '/tts',
    color: 'from-accent-500 to-accent-600',
    action: 'Text sprechen'
  },
  {
    icon: Users,
    title: 'Stimmen-Bibliothek',
    description: 'Verwalten Sie Ihre geklonten Stimmen',
    href: '/voices',
    color: 'from-emerald-500 to-emerald-600',
    action: 'Stimmen verwalten'
  }
]

const stats = [
  { label: 'Geklonte Stimmen', value: '0', icon: Mic },
  { label: 'Generierte Audios', value: '0', icon: Play },
  { label: 'Sprachen', value: '16+', icon: Sparkles },
]

export default function HomePage() {
  const { voices, fetchVoices } = useVoiceStore()
  const { history } = useTTSStore()

  useEffect(() => {
    fetchVoices()
  }, [fetchVoices])

  // Update stats with real data
  const updatedStats = stats.map(stat => {
    if (stat.label === 'Geklonte Stimmen') {
      return { ...stat, value: voices.length.toString() }
    }
    if (stat.label === 'Generierte Audios') {
      return { ...stat, value: history.length.toString() }
    }
    return stat
  })

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center space-y-6"
      >
        <div className="inline-flex items-center space-x-2 bg-primary-500/10 border border-primary-500/20 rounded-full px-4 py-2 text-primary-400">
          <Zap className="w-4 h-4" />
          <span className="text-sm font-medium">XTTS V2 Powered</span>
        </div>
        
        <h1 className="text-4xl lg:text-6xl font-bold">
          <span className="gradient-text">Voice Cloning</span>
          <br />
          <span className="text-white">Studio</span>
        </h1>
        
        <p className="text-xl text-slate-400 max-w-2xl mx-auto">
          Erstellen Sie realistische Stimmen-Klone und generieren Sie natürlich klingende Sprache 
          mit der neuesten XTTS V2 Technologie von Coqui AI.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/clone"
            className="btn-primary inline-flex items-center space-x-2"
          >
            <Upload className="w-5 h-5" />
            <span>Stimme klonen</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          
          <Link
            to="/tts"
            className="btn-secondary inline-flex items-center space-x-2"
          >
            <Play className="w-5 h-5" />
            <span>Text sprechen</span>
          </Link>
        </div>
      </motion.div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        {updatedStats.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: 0.1 * index }}
            className="card-hover text-center"
          >
            <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-500/20 rounded-xl mb-4">
              <stat.icon className="w-6 h-6 text-primary-400" />
            </div>
            <div className="text-3xl font-bold text-white mb-2">{stat.value}</div>
            <div className="text-slate-400">{stat.label}</div>
          </motion.div>
        ))}
      </motion.div>

      {/* Features */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="space-y-6"
      >
        <div className="text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Leistungsstarke Features
          </h2>
          <p className="text-slate-400 max-w-2xl mx-auto">
            Alles was Sie für professionelles Voice Cloning und Text-to-Speech benötigen
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.1 * index }}
              whileHover={{ scale: 1.02 }}
              className="group"
            >
              <Link to={feature.href} className="block">
                <div className="card-hover h-full">
                  <div className={`inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br ${feature.color} rounded-xl mb-6 group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className="w-7 h-7 text-white" />
                  </div>
                  
                  <h3 className="text-xl font-semibold text-white mb-3 group-hover:text-primary-400 transition-colors">
                    {feature.title}
                  </h3>
                  
                  <p className="text-slate-400 mb-6 leading-relaxed">
                    {feature.description}
                  </p>
                  
                  <div className="flex items-center text-primary-400 font-medium group-hover:text-primary-300 transition-colors">
                    <span>{feature.action}</span>
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        className="glass rounded-2xl p-8"
      >
        <div className="flex flex-col lg:flex-row items-center justify-between space-y-6 lg:space-y-0">
          <div>
            <h3 className="text-2xl font-bold text-white mb-2">
              Bereit loszulegen?
            </h3>
            <p className="text-slate-400">
              Starten Sie mit dem Klonen Ihrer ersten Stimme oder generieren Sie sofort Sprache.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              to="/clone"
              className="btn-primary inline-flex items-center space-x-2"
            >
              <Mic className="w-5 h-5" />
              <span>Erste Stimme klonen</span>
            </Link>
            
            <Link
              to="/tts"
              className="btn-accent inline-flex items-center space-x-2"
            >
              <MessageSquare className="w-5 h-5" />
              <span>Text sprechen</span>
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}