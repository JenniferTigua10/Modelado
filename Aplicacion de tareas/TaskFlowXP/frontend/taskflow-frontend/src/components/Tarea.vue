<template>
  <div class="tarea" :class="{ completada: tarea.completada }">
    <h3>{{ tarea.titulo }}</h3>
    <p>{{ tarea.descripcion }}</p>
    <p><strong>Fecha límite:</strong> {{ tarea.fechaLimite }}</p>
    <p><strong>Prioridad:</strong> {{ tarea.prioridad }}</p>
    <button @click="$emit('completar', tarea.id)">
      {{ tarea.completada ? 'Desmarcar' : 'Completar' }}
    </button>
    <button @click="$emit('eliminar', tarea.id)">Eliminar</button>
  </div>
</template>

<script setup>
defineProps(['tarea'])
</script>

<style scoped>
.tarea {
  border: 1px solid #ccc;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 8px;
}
.completada {
  background-color: #d4edda;
}
</style>

