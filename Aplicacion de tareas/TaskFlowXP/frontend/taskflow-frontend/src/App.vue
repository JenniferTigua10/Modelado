<template>
  <div class="app">
    <h1>TaskFlowXP</h1>

    <form @submit.prevent="agregarTarea">
      <input v-model="nuevaTarea.titulo" placeholder="Título" required />
      <input v-model="nuevaTarea.descripcion" placeholder="Descripción" required />
      <input type="date" v-model="nuevaTarea.fechaLimite" required />
      <select v-model="nuevaTarea.prioridad" required>
        <option disabled value="">Selecciona prioridad</option>
        <option>Alta</option>
        <option>Media</option>
        <option>Baja</option>
      </select>
      <button type="submit">Agregar tarea</button>
    </form>

    <Tarea
      v-for="tarea in tareas"
      :key="tarea.id"
      :tarea="tarea"
      @completar="completarTarea"
      @eliminar="eliminarTarea"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Tarea from './components/Tarea.vue'

// Estado de las tareas
const tareas = ref([])

const nuevaTarea = ref({
  titulo: '',
  descripcion: '',
  fechaLimite: '',
  prioridad: '',
})

// Función para agregar tarea
const agregarTarea = () => {
  if (
    nuevaTarea.value.titulo &&
    nuevaTarea.value.descripcion &&
    nuevaTarea.value.fechaLimite &&
    nuevaTarea.value.prioridad
  ) {
    const nueva = {
      ...nuevaTarea.value,
      id: Date.now(),
      completada: false,
    }
    tareas.value.push(nueva)
    // Resetear campos
    nuevaTarea.value = {
      titulo: '',
      descripcion: '',
      fechaLimite: '',
      prioridad: '',
    }
  }
}

// Función para completar una tarea
const completarTarea = (id) => {
  const tarea = tareas.value.find(t => t.id === id)
  if (tarea) tarea.completada = !tarea.completada
}

// Función para eliminar una tarea
const eliminarTarea = (id) => {
  tareas.value = tareas.value.filter(t => t.id !== id)
}
</script>

<style scoped>
/* Estilo sencillo */
.app {
  max-width: 600px;
  margin: auto;
  padding: 2rem;
}
form {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>

