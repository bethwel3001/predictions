import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    dedupe: ['react', 'react-dom']
  },
  server: {
    port: 3000,
  },
  optimizeDeps: {
    include: ['lucide-react']
  }
})