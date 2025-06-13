import { useState } from 'react'
import './App.css'

function App() {
  const [tasks, setTasks] = useState([])
  const [input, setInput] = useState('')
  const [editId, setEditId] = useState(null)
  const [editText, setEditText] = useState('')

  const addTask = (e) => {
    e.preventDefault()
    if (input.trim() === '') return
    setTasks([{ id: Date.now(), text: input, done: false }, ...tasks])
    setInput('')
  }

  const deleteTask = (id) => {
    setTasks(tasks.filter(task => task.id !== id))
  }

  const toggleDone = (id) => {
    setTasks(tasks.map(task =>
      task.id === id ? { ...task, done: !task.done } : task
    ))
  }

  const startEdit = (id, text) => {
    setEditId(id)
    setEditText(text)
  }

  const saveEdit = (id) => {
    if (editText.trim() === '') return
    setTasks(tasks.map(task =>
      task.id === id ? { ...task, text: editText } : task
    ))
    setEditId(null)
    setEditText('')
  }

  return (
    <div className="todo-container">
      <h1>Gestor de Tareas</h1>
      <form onSubmit={addTask} className="todo-form">
        <input
          className="todo-input"
          type="text"
          placeholder="Nueva tarea..."
          value={input}
          onChange={e => setInput(e.target.value)}
        />
        <button className="todo-btn" type="submit">Agregar</button>
      </form>
      <ul className="todo-list">
        {tasks.length === 0 && <li className="empty">No hay tareas</li>}
        {tasks.map(task => (
          <li key={task.id} className={`todo-item${task.done ? ' done' : ''}`}>
            <input type="checkbox" checked={task.done} onChange={() => toggleDone(task.id)} />
            {editId === task.id ? (
              <div style={{ display: 'flex', gap: '0.5rem', flex: 1 }}>
                <input
                  className="edit-input"
                  value={editText}
                  onChange={e => setEditText(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && saveEdit(task.id)}
                  autoFocus
                />
                <button className="todo-btn" onClick={() => saveEdit(task.id)} type="button">Guardar</button>
                <button className="delete-btn" onClick={() => setEditId(null)} type="button">Cancelar</button>
              </div>
            ) : (
              <div style={{ display: 'flex', gap: '0.5rem', flex: 1, alignItems: 'center' }}>
                <span className="task-text" style={{ flex: 1, textDecoration: task.done ? 'line-through' : 'none', cursor: 'pointer' }} onDoubleClick={() => startEdit(task.id, task.text)}>{task.text}</span>
                <button className="todo-btn" onClick={() => startEdit(task.id, task.text)} type="button">Editar</button>
                <button className="delete-btn" onClick={() => deleteTask(task.id)} type="button">Eliminar</button>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default App
