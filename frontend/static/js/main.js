/**
 * TaskFlowAI - Main JavaScript
 * API Integration and UI Utilities
 */

// ==================== API REQUEST HELPER ====================

/**
 * Make authenticated API requests
 * @param {string} url - API endpoint
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
 * @param {Object} body - Request body (optional)
 * @returns {Promise<any>} - Parsed JSON response
 */
async function apiRequest(url, method = 'GET', body = null) {
    const token = localStorage.getItem('authToken');
    
    const headers = {
        'Content-Type': 'application/json'
    };
    
    // Add JWT token if available
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        method,
        headers
    };
    
    if (body && method !== 'GET') {
        config.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(url, config);
        
        // Handle 401 Unauthorized - redirect to login
        if (response.status === 401) {
            localStorage.removeItem('authToken');
            localStorage.removeItem('currentUser');
            window.location.href = '/login';
            throw new Error('Unauthorized');
        }
        
        // Handle other error responses
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
        }
        
        // Return parsed JSON
        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// ==================== AUTH FUNCTIONS ====================

/**
 * Login user
 * @param {string} identifier - Username or email
 * @param {string} password - User password
 * @returns {Promise<Object>} - User data with token
 */
async function login(identifier, password) {
    try {
        const response = await apiRequest('/api/auth/login', 'POST', {
            identifier,
            password
        });
        
        // Save token to localStorage
        if (response.access_token) {
            localStorage.setItem('authToken', response.access_token);
        }
        
        // Save user data
        if (response.user) {
            localStorage.setItem('currentUser', JSON.stringify(response.user));
        }
        
        return response;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

/**
 * Register new user
 * @param {string} username - Username
 * @param {string} email - Email address
 * @param {string} password - Password
 * @param {string} full_name - Full name (optional)
 * @returns {Promise<Object>} - Created user data
 */
async function register(username, email, password, full_name = '') {
    try {
        const response = await apiRequest('/api/auth/register', 'POST', {
            username,
            email,
            password,
            full_name
        });
        
        return response;
    } catch (error) {
        console.error('Registration error:', error);
        throw error;
    }
}

/**
 * Logout current user
 */
function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    window.location.href = '/login';
}

/**
 * Get current authenticated user
 * @returns {Promise<Object>} - User data
 */
async function getCurrentUser() {
    try {
        const response = await apiRequest('/api/auth/me');
        localStorage.setItem('currentUser', JSON.stringify(response));
        return response;
    } catch (error) {
        console.error('Get current user error:', error);
        throw error;
    }
}

/**
 * Check if user is authenticated
 * @returns {boolean} - True if token exists
 */
function checkAuth() {
    const token = localStorage.getItem('authToken');
    return !!token;
}

/**
 * Get stored user data from localStorage
 * @returns {Object|null} - User object or null
 */
function getStoredUser() {
    const userData = localStorage.getItem('currentUser');
    return userData ? JSON.parse(userData) : null;
}

// ==================== UI UTILITIES ====================

/**
 * Show Bootstrap alert/toast message
 * @param {string} message - Message to display
 * @param {string} type - Alert type (success, danger, warning, info)
 */
function showAlert(message, type = 'info') {
    // Remove any existing alerts
    const existingAlerts = document.querySelectorAll('.alert-toast');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show alert-toast`;
    alertDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 150);
    }, 5000);
}

/**
 * Show loading spinner overlay
 */
function showLoading() {
    // Remove existing loader if any
    hideLoading();
    
    const loader = document.createElement('div');
    loader.id = 'loadingOverlay';
    loader.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
    `;
    loader.innerHTML = `
        <div class="spinner-border text-light" role="status" style="width: 3rem; height: 3rem;">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    
    document.body.appendChild(loader);
}

/**
 * Hide loading spinner overlay
 */
function hideLoading() {
    const loader = document.getElementById('loadingOverlay');
    if (loader) {
        loader.remove();
    }
}

/**
 * Format ISO date string to readable format
 * @param {string} isoString - ISO date string
 * @param {boolean} includeTime - Include time in format
 * @returns {string} - Formatted date
 */
function formatDate(isoString, includeTime = false) {
    if (!isoString) return 'N/A';
    
    const date = new Date(isoString);
    
    if (isNaN(date.getTime())) return 'Invalid Date';
    
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return date.toLocaleDateString('pt-BR', options);
}

/**
 * Show Bootstrap modal
 * @param {string} modalId - Modal element ID
 */
function showModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    }
}

/**
 * Hide Bootstrap modal
 * @param {string} modalId - Modal element ID
 */
function hideModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        }
    }
}

/**
 * Debounce function for search inputs
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== SIDEBAR TOGGLE ====================

/**
 * Toggle sidebar for mobile view
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    
    if (sidebar) {
        sidebar.classList.toggle('show');
    }
    
    if (mainContent) {
        mainContent.classList.toggle('sidebar-open');
    }
}

/**
 * Close sidebar when clicking outside (mobile)
 */
function setupSidebarClose() {
    const mainContent = document.getElementById('mainContent');
    const sidebar = document.getElementById('sidebar');
    
    if (mainContent && sidebar) {
        mainContent.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
                mainContent.classList.remove('sidebar-open');
            }
        });
    }
}

// ==================== USER DISPLAY ====================

/**
 * Update user display in navbar/sidebar
 */
function updateUserDisplay() {
    const user = getStoredUser();
    
    if (user) {
        const userNameElements = document.querySelectorAll('.user-name');
        const userEmailElements = document.querySelectorAll('.user-email');
        const userAvatarElements = document.querySelectorAll('.user-avatar');
        
        userNameElements.forEach(el => {
            el.textContent = user.full_name || user.username || 'User';
        });
        
        userEmailElements.forEach(el => {
            el.textContent = user.email || '';
        });
        
        userAvatarElements.forEach(el => {
            const initials = (user.full_name || user.username || 'U')
                .split(' ')
                .map(n => n[0])
                .join('')
                .toUpperCase()
                .substring(0, 2);
            el.textContent = initials;
        });
    }
}

// ==================== FORM VALIDATION ====================

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} - True if valid
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {Object} - Validation result
 */
function validatePassword(password) {
    const result = {
        valid: true,
        errors: []
    };
    
    if (password.length < 6) {
        result.valid = false;
        result.errors.push('Senha deve ter no mínimo 6 caracteres');
    }
    
    return result;
}

// ==================== INITIALIZATION ====================

/**
 * Initialize application on DOMContentLoaded
 */
document.addEventListener('DOMContentLoaded', async function() {
    // Check if on public page (login/register)
    const isPublicPage = window.location.pathname === '/login' || 
                         window.location.pathname === '/register' ||
                         window.location.pathname === '/';
    
    // If not on public page, check authentication
    if (!isPublicPage) {
        if (!checkAuth()) {
            window.location.href = '/login';
            return;
        }
        
        // Load current user if not in localStorage
        const storedUser = getStoredUser();
        if (!storedUser) {
            try {
                showLoading();
                await getCurrentUser();
                hideLoading();
            } catch (error) {
                hideLoading();
                console.error('Failed to load user:', error);
                logout();
                return;
            }
        }
        
        // Update user display
        updateUserDisplay();
        
        // Setup sidebar
        setupSidebarClose();
    }
    
    // Setup logout buttons
    const logoutButtons = document.querySelectorAll('[data-action="logout"]');
    logoutButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    });
    
    // Setup sidebar toggle buttons
    const sidebarToggleButtons = document.querySelectorAll('[data-action="toggle-sidebar"]');
    sidebarToggleButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            toggleSidebar();
        });
    });
    
    console.log('TaskFlowAI initialized successfully');
});

// ==================== EXPORT FOR MODULE USE ====================

// If using modules, export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        apiRequest,
        login,
        register,
        logout,
        getCurrentUser,
        checkAuth,
        getStoredUser,
        showAlert,
        showLoading,
        hideLoading,
        formatDate,
        showModal,
        hideModal,
        debounce,
        toggleSidebar,
        updateUserDisplay,
        isValidEmail,
        validatePassword
    };
}
