import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // rewrite: (path) => path.replace(/^\/api/, '')
      },
      // 文章正文里的图片是相对路径 /uploads/xxx.webp，由服务器托管，
      // 不代理的话会请求到 vite 自己的 5173 端口，导致图片 404 渲染不出来
      '/uploads': {
        target: 'https://106.14.254.44',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
