
// API URL
const API_URL = '/api/tasks';

// Variables globales
let tasks = [];
let currentFilter = 'all';

// Elementos DOM
const taskList = document.getElementById('taskList');
const taskForm = document.getElementById('taskForm');
const titleInput = document.getElementById('titleInput');
const descriptionInput = document.getElementById('descriptionInput');
const editModal = document.getElementById('editModal');
const editForm = document.getElementById('editForm');
const editId = document.getElementById('editId');
const editTitle = document.getElementById('editTitle');
const editDescription = document.getElementById('editDescription');
const editCompleted = document.getElementById('editCompleted');
const closeModal = document.querySelector('.close');
const totalTasksSpan = document.getElementById('totalTasks');
const completedTasksSpan = document.getElementById('completedTasks');
const pendingTasksSpan = document.getElementById('pendingTasks');

// ========== FUNCIONES ==========

// Obtener todas las tareas
async function fetchTasks() {
    try {
        const response = await fetch(API_URL);
        tasks = await response.json();
        renderTasks();
        updateStats();
    } catch (error) {
        console.error('Error al obtener tareas:', error);
        taskList.innerHTML = '<div class="loading">❌ Error al cargar las tareas</div>';
    }
}

// Renderizar tareas según el filtro
function renderTasks() {
    let filteredTasks = tasks;
    
    if (currentFilter === 'pending') {
        filteredTasks = tasks.filter(t => !t.completed);
    } else if (currentFilter === 'completed') {
        filteredTasks = tasks.filter(t => t.completed);
    }
    
    if (filteredTasks.length === 0) {
        taskList.innerHTML = `
            <div class="loading">
                📭 No hay tareas ${currentFilter === 'all' ? '' : currentFilter === 'pending' ? 'pendientes' : 'completadas'}
                <br><small>¡Agrega una nueva tarea!</small>
            </div>
        `;
        return;
    }
    
    taskList.innerHTML = filteredTasks.map(task => `
        <div class="task-card ${task.completed ? 'completed' : ''}">
            <div class="task-info">
                <div class="task-title">${escapeHtml(task.title)}</div>
                ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
                <div class="task-meta">
                    <span>🕒 ${formatDate(task.createdAt)}</span>
                    <span>${task.completed ? '✅ Completada' : '⏳ Pendiente'}</span>
                </div>
            </div>
            <div class="task-actions">
                <button class="btn-toggle" onclick="toggleTask(${task.id})" title="Marcar como ${task.completed ? 'pendiente' : 'completada'}">
                    ${task.completed ? '🔄' : '✅'}
                </button>
                <button class="btn-edit" onclick="openEditModal(${task.id})" title="Editar">
                    ✏️
                </button>
                <button class="btn-delete" onclick="deleteTask(${task.id})" title="Eliminar">
                    🗑️
                </button>
            </div>
        </div>
    `).join('');
}

// Actualizar estadísticas
function updateStats() {
    const total = tasks.length;
    const completed = tasks.filter(t => t.completed).length;
    const pending = total - completed;
    
    totalTasksSpan.textContent = total;
    completedTasksSpan.textContent = completed;
    pendingTasksSpan.textContent = pending;
}

// Crear nueva tarea
async function createTask(title, description) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, description })
        });
        
        if (response.ok) {
            await fetchTasks();
            titleInput.value = '';
            descriptionInput.value = '';
        } else {
            alert('Error al crear la tarea');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al crear la tarea');
    }
}

// Marcar tarea como completada/pendiente
async function toggleTask(id) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;
    
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ completed: !task.completed })
        });
        
        if (response.ok) {
            await fetchTasks();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al actualizar la tarea');
    }
}

// Eliminar tarea
async function deleteTask(id) {
    if (!confirm('¿Estás seguro de eliminar esta tarea?')) return;
    
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await fetchTasks();
        } else {
            alert('Error al eliminar la tarea');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar la tarea');
    }
}

// Abrir modal de edición
function openEditModal(id) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;
    
    editId.value = task.id;
    editTitle.value = task.title;
    editDescription.value = task.description || '';
    editCompleted.checked = task.completed;
    
    editModal.style.display = 'block';
}

// Cerrar modal
function closeEditModal() {
    editModal.style.display = 'none';
}

// Guardar edición
async function saveEdit(event) {
    event.preventDefault();
    
    const id = parseInt(editId.value);
    const title = editTitle.value.trim();
    const description = editDescription.value.trim();
    const completed = editCompleted.checked;
    
    if (!title) {
        alert('El título es obligatorio');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, description, completed })
        });
        
        if (response.ok) {
            await fetchTasks();
            closeEditModal();
        } else {
            alert('Error al actualizar la tarea');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al actualizar la tarea');
    }
}

// ========== UTILIDADES ==========

// Escapar HTML para evitar XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Formatear fecha
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ========== EVENT LISTENERS ==========

// Enviar formulario de nueva tarea
taskForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();
    
    if (!title) {
        alert('El título es obligatorio');
        return;
    }
    
    createTask(title, description);
});

// Filtros
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        renderTasks();
    });
});

// Modal - cerrar con X
closeModal.addEventListener('click', closeEditModal);

// Modal - cerrar al hacer clic fuera
window.addEventListener('click', (event) => {
    if (event.target === editModal) {
        closeEditModal();
    }
});

// Enviar formulario de edición
editForm.addEventListener('submit', saveEdit);

// ========== INICIALIZAR ==========
fetchTasks();