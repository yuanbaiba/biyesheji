import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  server: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:30000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  plugins: [
    vue()
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'echarts': ['echarts'],
          'vue-vendor': ['vue', 'vue-router']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  optimizeDeps: {
    include: ['element-plus', 'axios', 'vue', 'vue-router', 'pinia']
  }
})