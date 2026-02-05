import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/workflows': { target: 'http://localhost:5000', changeOrigin: true },
      '/workflow-runs': { target: 'http://localhost:5000', changeOrigin: true },
    },
  },
})
