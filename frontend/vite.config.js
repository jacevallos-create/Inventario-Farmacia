import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  base:'/static/frontend/',
  plugins:[react()],
  build:{outDir:'../static/frontend',emptyOutDir:true},
  server:{host:'127.0.0.1',port:5173}
})
