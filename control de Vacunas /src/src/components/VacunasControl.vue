<script setup>
import { ref, onMounted } from 'vue'
import { supabase } from '../lib/supabase'

const vacunas = ref([])
const loading = ref(false)
const error = ref('')

// Formulario
const form = ref({
  paciente: '',
  vacuna: '',
  fecha: '',
  observaciones: ''
})

const editId = ref(null)

async function cargarVacunas() {
  loading.value = true
  const { data, error: err } = await supabase.from('vacunas').select('*').order('fecha', { ascending: false })
  if (err) error.value = err.message
  else vacunas.value = data
  loading.value = false
}

async function guardarVacuna() {
  error.value = ''
  if (!form.value.paciente || !form.value.vacuna || !form.value.fecha) {
    error.value = 'Paciente, vacuna y fecha son obligatorios.'
    return
  }
  let res
  if (editId.value) {
    res = await supabase.from('vacunas').update({ ...form.value }).eq('id', editId.value)
  } else {
    res = await supabase.from('vacunas').insert([{ ...form.value }])
  }
  if (res.error) error.value = res.error.message
  else {
    form.value = { paciente: '', vacuna: '', fecha: '', observaciones: '' }
    editId.value = null
    cargarVacunas()
  }
}

function editarVacuna(vacuna) {
  form.value = { ...vacuna }
  editId.value = vacuna.id
}

async function eliminarVacuna(id) {
  if (!confirm('¿Eliminar este registro?')) return
  const { error: err } = await supabase.from('vacunas').delete().eq('id', id)
  if (err) error.value = err.message
  else cargarVacunas()
}

onMounted(cargarVacunas)
</script>

<template>
  <div class="header">
    <h1>🏥 Sistema de Control de Vacunas para mi cachetistos de pan</h1>
    <p>Gestiona y controla el registro de vacunación de pacientes</p>
  </div>
  
  <div class="card">
    <h2>📝 Registro de Vacunas Thiago1</h2>
    <form @submit.prevent="guardarVacuna">
      <input v-model="form.paciente" placeholder="Nombre del paciente" required />
      <input v-model="form.vacuna" placeholder="Tipo de vacuna" required />
      <input v-model="form.fecha" type="date" required />
      <input v-model="form.observaciones" placeholder="Observaciones (opcional)" />
      
      <div class="form-buttons">
        <button type="submit" class="btn-primary">
          {{ editId ? '✏️ Actualizar' : '💉 Registrar' }}
        </button>
        <button v-if="editId" type="button" class="btn-secondary" @click="() => { form = { paciente: '', vacuna: '', fecha: '', observaciones: '' }; editId = null }">
          ❌ Cancelar
        </button>
      </div>
    </form>
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
  <div class="card">
    <h2>📋 Vacunas Registradas</h2>
    <div v-if="loading" class="loading">🔄 Cargando registros...</div>
    <div v-else-if="vacunas.length === 0" class="no-records">
      📝 No hay registros de vacunas aún. ¡Registra la primera vacuna!
    </div>
    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th>👤 Paciente</th>
            <th>💉 Vacuna</th>
            <th>📅 Fecha</th>
            <th>📝 Observaciones</th>
            <th>⚙️ Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="v in vacunas" :key="v.id">
            <td>{{ v.paciente }}</td>
            <td>{{ v.vacuna }}</td>
            <td>{{ v.fecha }}</td>
            <td>{{ v.observaciones || 'Sin observaciones' }}</td>
            <td class="actions">
              <button @click="editarVacuna(v)" class="btn-edit">✏️ Editar</button>
              <button @click="eliminarVacuna(v.id)" class="btn-delete">🗑️ Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.header {
  text-align: center;
  margin: 0 auto 3em auto;
  padding: 3em 2em;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  color: white;
  max-width: 800px;
}

.header h1 {
  margin: 0;
  font-size: 3em;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.header p {
  margin: 1em 0 0 0;
  font-size: 1.2em;
  opacity: 0.9;
}

.card {
  margin: 0 auto 3em auto;
  padding: 2.5em;
  border: none;
  border-radius: 16px;
  background: white;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
  max-width: 900px;
}

.card h2 {
  color: #333;
  margin-bottom: 1.5em;
  font-size: 1.8em;
  font-weight: 600;
}

form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5em;
  max-width: 800px;
  margin: 0 auto 1.5em auto;
}

input {
  padding: 1em 1.2em;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 1em;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

input[type="date"] {
  cursor: pointer;
}

.form-buttons {
  grid-column: 1 / -1;
  display: flex;
  gap: 1em;
  justify-content: flex-start;
  margin-top: 1em;
}

button {
  padding: 1em 2em;
  border: none;
  border-radius: 12px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.btn-secondary {
  background: linear-gradient(135deg, #868f96 0%, #596164 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(134, 143, 150, 0.4);
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(134, 143, 150, 0.5);
}

.error-message {
  color: #dc3545;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  padding: 1em;
  margin-top: 1em;
  font-weight: 500;
}

.loading {
  text-align: center;
  padding: 3em;
  font-size: 1.2em;
  color: #667eea;
}

.table-container {
  overflow-x: auto;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

th {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 1.2em;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border: none;
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

td {
  padding: 1.2em;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

tbody tr {
  transition: all 0.2s ease;
}

tbody tr:hover {
  background: #f8f9fa;
  transform: scale(1.01);
}

.actions {
  white-space: nowrap;
}

.actions button {
  padding: 0.6em 1.2em;
  margin-right: 0.5em;
  font-size: 0.85em;
  font-weight: 500;
  border-radius: 8px;
  text-transform: none;
  letter-spacing: normal;
}

.btn-edit {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.btn-edit:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
}

.btn-delete {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
}

.btn-delete:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4);
}

.no-records {
  text-align: center;
  padding: 3em;
  color: #6c757d;
  font-size: 1.1em;
  font-style: italic;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 2em;
  }
  
  .header {
    padding: 2em 1.5em;
    margin: 0 auto 2em auto;
  }
  
  .card {
    padding: 1.5em;
    margin: 0 auto 2em auto;
  }
  
  form {
    grid-template-columns: 1fr;
    max-width: none;
  }
  
  .form-buttons {
    flex-direction: column;
  }
  
  .table-container {
    font-size: 0.9em;
  }
  
  th, td {
    padding: 0.8em;
  }
}
</style>
