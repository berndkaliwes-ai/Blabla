import { Routes, Route } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useLocation } from 'react-router-dom'

// Components
import Layout from '@/components/Layout'
import HomePage from '@/pages/HomePage'
import VoiceClonePage from '@/pages/VoiceClonePage'
import TTSPage from '@/pages/TTSPage'
import VoicesPage from '@/pages/VoicesPage'
import SettingsPage from '@/pages/SettingsPage'

// Page transition variants
const pageVariants = {
  initial: {
    opacity: 0,
    x: -20,
  },
  in: {
    opacity: 1,
    x: 0,
  },
  out: {
    opacity: 0,
    x: 20,
  },
}

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.3,
}

function App() {
  const location = useLocation()

  return (
    <Layout>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route
            path="/"
            element={
              <motion.div
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
              >
                <HomePage />
              </motion.div>
            }
          />
          <Route
            path="/clone"
            element={
              <motion.div
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
              >
                <VoiceClonePage />
              </motion.div>
            }
          />
          <Route
            path="/tts"
            element={
              <motion.div
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
              >
                <TTSPage />
              </motion.div>
            }
          />
          <Route
            path="/voices"
            element={
              <motion.div
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
              >
                <VoicesPage />
              </motion.div>
            }
          />
          <Route
            path="/settings"
            element={
              <motion.div
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
              >
                <SettingsPage />
              </motion.div>
            }
          />
        </Routes>
      </AnimatePresence>
    </Layout>
  )
}

export default App