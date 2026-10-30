import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En desarrollo, /api se manda al backend local (puerto 8000, o BACKEND_PORT si está ocupado)
export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/api': `http://127.0.0.1:${process.env.BACKEND_PORT ?? 8000}` } },
})
