import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    // Geliştirmede API isteklerini backend'e yönlendir (CORS sorununu önler)
    proxy: {
      '/auth': { target: 'http://localhost:8000', changeOrigin: true },
      '/qr': { target: 'http://localhost:8000', changeOrigin: true },
      '/health': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
  preview: {
    port: 3000,
  },
})
