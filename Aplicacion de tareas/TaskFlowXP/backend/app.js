const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

const db = new sqlite3.Database('./database/taskflow.db');

// Crear tabla si no existe
db.run(`CREATE TABLE IF NOT EXISTS tareas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  titulo TEXT NOT NULL,
  descripcion TEXT,
  fechaLimite TEXT,
  prioridad TEXT,
  completada INTEGER DEFAULT 0
)`);

// Obtener todas las tareas
app.get('/api/tareas', (req, res) => {
  db.all('SELECT * FROM tareas', [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

// Crear tarea
app.post('/api/tareas', (req, res) => {
  const { titulo, descripcion, fechaLimite, prioridad } = req.body;
  db.run(`INSERT INTO tareas (titulo, descripcion, fechaLimite, prioridad) VALUES (?, ?, ?, ?)`,
    [titulo, descripcion, fechaLimite, prioridad],
    function (err) {
      if (err) return res.status(500).json({ error: err.message });
      res.status(201).json({ id: this.lastID });
    });
});

// Actualizar tarea
app.put('/api/tareas/:id', (req, res) => {
  const { id } = req.params;
  const { titulo, descripcion, fechaLimite, prioridad, completada } = req.body;
  db.run(`UPDATE tareas SET titulo = ?, descripcion = ?, fechaLimite = ?, prioridad = ?, completada = ? WHERE id = ?`,
    [titulo, descripcion, fechaLimite, prioridad, completada, id],
    function (err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ actualizado: true });
    });
});

// Eliminar tarea
app.delete('/api/tareas/:id', (req, res) => {
  const { id } = req.params;
  db.run(`DELETE FROM tareas WHERE id = ?`, [id], function (err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ eliminado: true });
  });
});

app.listen(PORT, () => {
  console.log(`Servidor escuchando en http://localhost:${PORT}`);
});
