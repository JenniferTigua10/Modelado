import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// Verificar que las variables de entorno estén disponibles
console.log('Environment check:', {
  hasSupabaseUrl: !!import.meta.env.VITE_SUPABASE_URL,
  hasSupabaseKey: !!import.meta.env.VITE_SUPABASE_KEY
})

createApp(App).mount('#app')
