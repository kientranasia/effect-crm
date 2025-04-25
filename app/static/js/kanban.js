document.addEventListener('DOMContentLoaded', function() {
    // Initialize Kanban board
    initKanbanBoard();
    
    // Initialize task modals
    initTaskModals();
});

/**
 * Initialize the Kanban board with drag and drop functionality
 */
function initKanbanBoard() {
    const kanbanCards = document.querySelectorAll('.kanban-card');
    const kanbanColumns = document.querySelectorAll('.kanban-column-body');
    
    // Add drag and drop event listeners to cards
    kanbanCards.forEach(card => {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
    });
    
    // Add drag and drop event listeners to columns
    kanbanColumns.forEach(column => {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('dragleave', handleDragLeave);
        column.addEventListener('drop', handleDrop);
    });
}

/**
 * Handle drag start event
 * @param {Event} e - The drag event
 */
function handleDragStart(e) {
    this.classList.add('dragging');
    e.dataTransfer.setData('text/plain', this.dataset.taskId);
}

/**
 * Handle drag end event
 */
function handleDragEnd() {
    this.classList.remove('dragging');
}

/**
 * Handle drag over event
 * @param {Event} e - The drag event
 */
function handleDragOver(e) {
    e.preventDefault();
    this.classList.add('drag-over');
}

/**
 * Handle drag leave event
 */
function handleDragLeave() {
    this.classList.remove('drag-over');
}

/**
 * Handle drop event
 * @param {Event} e - The drop event
 */
function handleDrop(e) {
    e.preventDefault();
    this.classList.remove('drag-over');
    
    const taskId = e.dataTransfer.getData('text/plain');
    const newStatus = this.dataset.status;
    
    // Update task status via AJAX
    updateTaskStatus(taskId, newStatus)
        .then(data => {
            if (data.success) {
                // Move the card to the new column
                const card = document.querySelector(`.kanban-card[data-task-id="${taskId}"]`);
                this.appendChild(card);
                
                // Update counters
                updateColumnCounters();
                
                // Show success message
                showToast('Task status updated successfully', 'success');
            } else {
                showToast('Failed to update task status', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('An error occurred while updating the task', 'error');
        });
}

/**
 * Update task status via AJAX
 * @param {number} taskId - The task ID
 * @param {string} status - The new status
 * @returns {Promise} - The fetch promise
 */
function updateTaskStatus(taskId, status) {
    return fetch(`/tasks/${taskId}/update-status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ status })
    })
    .then(response => response.json());
}

/**
 * Update task position via AJAX
 * @param {number} taskId - The task ID
 * @param {number} position - The new position
 * @returns {Promise} - The fetch promise
 */
function updateTaskPosition(taskId, position) {
    return fetch(`/tasks/${taskId}/update-position`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ position })
    })
    .then(response => response.json());
}

/**
 * Update column counters
 */
function updateColumnCounters() {
    const columns = document.querySelectorAll('.kanban-column');
    columns.forEach(column => {
        const counter = column.querySelector('.badge');
        const cards = column.querySelectorAll('.kanban-card');
        counter.textContent = cards.length;
    });
}

/**
 * Initialize task modals
 */
function initTaskModals() {
    // Add task modal
    const addTaskModal = document.getElementById('addTaskModal');
    if (addTaskModal) {
        const addTaskForm = addTaskModal.querySelector('#addTaskForm');
        addTaskForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    showToast('Failed to create task', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('An error occurred while creating the task', 'error');
            });
        });
    }
    
    // Edit task modal
    const editTaskModal = document.getElementById('editTaskModal');
    if (editTaskModal) {
        editTaskModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const taskId = button.getAttribute('data-task-id');
            const form = this.querySelector('#editTaskForm');
            
            // Set form action
            form.action = `/tasks/${taskId}/edit`;
            
            // Fetch task data
            fetch(`/tasks/${taskId}`)
                .then(response => response.json())
                .then(data => {
                    form.querySelector('[name="title"]').value = data.title;
                    form.querySelector('[name="description"]').value = data.description || '';
                    form.querySelector('[name="due_date"]').value = data.due_date || '';
                    form.querySelector('[name="priority"]').value = data.priority;
                    form.querySelector('[name="assigned_to_id"]').value = data.assigned_to_id || '';
                    form.querySelector('[name="status"]').value = data.status;
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Failed to load task data', 'error');
                });
        });
        
        const editTaskForm = editTaskModal.querySelector('#editTaskForm');
        editTaskForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    showToast('Failed to update task', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('An error occurred while updating the task', 'error');
            });
        });
    }
    
    // Delete task modal
    const deleteTaskModal = document.getElementById('deleteTaskModal');
    if (deleteTaskModal) {
        const deleteTaskForm = deleteTaskModal.querySelector('#deleteTaskForm');
        deleteTaskForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    showToast('Failed to delete task', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('An error occurred while deleting the task', 'error');
            });
        });
    }
}

/**
 * Delete task function
 * @param {number} taskId - The task ID
 */
function deleteTask(taskId) {
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteTaskModal'));
    const deleteForm = document.getElementById('deleteTaskForm');
    
    deleteForm.action = `/tasks/${taskId}/delete`;
    deleteModal.show();
}

/**
 * Get CSRF token from meta tag
 * @returns {string} - The CSRF token
 */
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

/**
 * Show toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of toast (success, error, warning, info)
 */
function showToast(message, type = 'info') {
    // Check if toast container exists, if not create it
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.id = toastId;
    
    // Create toast content
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add toast to container
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 3000 });
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
} 