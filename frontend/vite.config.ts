import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: '../static/figmalol',
    assetsDir: 'assets',
    sourcemap: false,
  },
  server: {
    port: 5173,
    proxy: {
      '/generate': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/models': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/model-profiles': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/metrics-json': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/security-stats': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/session-analytics': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
})
