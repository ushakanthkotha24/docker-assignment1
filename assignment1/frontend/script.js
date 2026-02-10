// API configuration
const API_BASE_URL = '/api';

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Application initialized');
    checkApiHealth();
    checkDatabaseStatus();
    loadUsers();
    attachFormListener();
});

// Check API health status
function checkApiHealth() {
    fetch(`${API_BASE_URL}/health`)
        .then(response => response.json())
        .then(data => {
            updateStatusDisplay('api-status', true, 'API is running');
            console.log('API Health:', data);
        })
        .catch(error => {
            updateStatusDisplay('api-status', false, 'API is not responding');
            console.error('Error checking API health:', error);
        });
}

// Check database connection status
function checkDatabaseStatus() {
    fetch(`${API_BASE_URL}/database-status`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'connected') {
                updateStatusDisplay('database-status', true, 'Database connected');
            } else {
                updateStatusDisplay('database-status', false, 'Database disconnected');
            }
            console.log('Database Status:', data);
        })
        .catch(error => {
            updateStatusDisplay('database-status', false, 'Database connection failed');
            console.error('Error checking database status:', error);
        });
}

// Update status display
function updateStatusDisplay(elementId, isSuccess, message) {
    const statusElement = document.getElementById(elementId);
    statusElement.textContent = message;
    statusElement.className = `status-text ${isSuccess ? 'success' : 'error'}`;
}

// Attach form submit listener
function attachFormListener() {
    const userForm = document.getElementById('user-form');
    userForm.addEventListener('submit', handleFormSubmit);
}

// Handle form submission
function handleFormSubmit(event) {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();

    if (!username || !email) {
        showMessage('Please fill in all fields', false);
        return;
    }

    const userData = {
        username: username,
        email: email
    };

    fetch(`${API_BASE_URL}/users`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            showMessage('User created successfully', true);
            document.getElementById('user-form').reset();
            loadUsers();
            console.log('User created:', data);
        })
        .catch(error => {
            console.error('Error creating user:', error);
            if (error.error) {
                showMessage(error.error, false);
            } else {
                showMessage('Error creating user', false);
            }
        });
}

// Show message notification
function showMessage(message, isSuccess) {
    const messageElement = document.getElementById('form-message');
    messageElement.textContent = message;
    messageElement.className = `message ${isSuccess ? 'success' : 'error'}`;

    setTimeout(() => {
        messageElement.className = 'message';
        messageElement.textContent = '';
    }, 5000);
}

// Load and display all users
function loadUsers() {
    const usersContainer = document.getElementById('users-container');
    usersContainer.innerHTML = '<p class="loading">Loading users...</p>';

    fetch(`${API_BASE_URL}/users`)
        .then(response => response.json())
        .then(data => {
            if (data.data && data.data.length > 0) {
                usersContainer.innerHTML = '';
                data.data.forEach(user => {
                    const userCard = createUserCard(user);
                    usersContainer.appendChild(userCard);
                });
            } else {
                usersContainer.innerHTML = '<p class="empty-message">No users found. Create one to get started!</p>';
            }
            console.log('Users loaded:', data.data);
        })
        .catch(error => {
            console.error('Error loading users:', error);
            usersContainer.innerHTML = '<p class="empty-message">Error loading users. Please try again later.</p>';
        });
}

// Create user card element
function createUserCard(user) {
    const card = document.createElement('div');
    card.className = 'user-card';

    const createdDate = new Date(user.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    card.innerHTML = `
        <h3 class="user-id">ID: ${user.id}</h3>
        <p><strong>Username:</strong> <span class="user-username">${escapeHtml(user.username)}</span></p>
        <p><strong>Email:</strong> <span class="user-email">${escapeHtml(user.email)}</span></p>
        <p class="user-date"><strong>Created:</strong> ${createdDate}</p>
        <div class="user-actions">
            <button class="btn btn-danger" onclick="deleteUser(${user.id})">Delete User</button>
        </div>
    `;

    return card;
}

// Delete user
function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user?')) {
        return;
    }

    fetch(`${API_BASE_URL}/users/${userId}`, {
        method: 'DELETE'
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            showMessage('User deleted successfully', true);
            loadUsers();
            console.log('User deleted:', data);
        })
        .catch(error => {
            console.error('Error deleting user:', error);
            showMessage('Error deleting user', false);
        });
}

// Escape HTML special characters
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-refresh users every 30 seconds
setInterval(() => {
    checkApiHealth();
    checkDatabaseStatus();
}, 30000);
