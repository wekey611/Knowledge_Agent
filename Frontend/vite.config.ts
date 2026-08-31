import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/login': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/me': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/user': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/organization': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/knowledge-bases': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // ⚠️ RAG 问答要调 LLM，MiniMax 通常 5~30s，必须放长
        timeout: 120000,
      },
    },
  },
})
