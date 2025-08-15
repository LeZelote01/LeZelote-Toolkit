import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuration portable avec support ports dynamiques - CORRIGÉ POUR COHÉRENCE
const isPortableMode = process.env.PORTABLE_MODE === 'true'
const backendPort = process.env.BACKEND_PORT || 8000  // ✅ Déjà correct
const frontendPort = process.env.FRONTEND_PORT || 8002  // ✅ 8002

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: parseInt(process.env.VITE_DEV_SERVER_PORT || process.env.FRONTEND_PORT || frontendPort),
    open: false,
    strictPort: true,  // Force utilisation du port configuré
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '*.preview.emergentagent.com',
      'dev-roadmap-guide.preview.emergentagent.com',
      '*.emergentagent.com',
      'emergentagent.com'
    ],
    fs: {
      strict: false
    },
    proxy: {
      '/api': {
        target: `http://localhost:${backendPort}`,
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  },
  define: {
    // Variables pour le mode portable - injecter REACT_APP_BACKEND_URL dans l'environnement Vite
    'import.meta.env.REACT_APP_BACKEND_URL': JSON.stringify(process.env.REACT_APP_BACKEND_URL || ''),
    'import.meta.env.VITE_BACKEND_URL': JSON.stringify(process.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL || `http://localhost:${backendPort}`),
    'import.meta.env.VITE_PORTABLE_MODE': JSON.stringify(isPortableMode.toString())
  }
})