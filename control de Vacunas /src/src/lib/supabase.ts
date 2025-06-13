import { createClient } from '@supabase/supabase-js'
import { supabaseConfig } from './config.js'

// Intentar usar variables de entorno primero, luego usar configuración embebida
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || supabaseConfig.url
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY || supabaseConfig.key

if (!supabaseUrl || !supabaseKey) {
  throw new Error('Faltan variables de entorno de Supabase. Verifica tu archivo .env')
}

console.log('Supabase initialized with URL:', supabaseUrl.substring(0, 30) + '...')

export const supabase = createClient(supabaseUrl, supabaseKey)
