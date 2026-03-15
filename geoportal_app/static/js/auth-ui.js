/**
 * Authentication UI Manager for Geoportal
 * Handles showing/hiding auth elements based on login state and ENABLE_KEYCLOAK_AUTH
 */

class AuthUI {
    constructor() {
        this.authEnabled = false;
        this.userLoggedIn = false;
        this.userName = '';
        this.init();
    }

    /**
     * Initialize auth UI
     */
    init() {
        console.log('🔐 AuthUI initializing...');
        
        // Check if auth is enabled from Flask template variable or API
        this.checkAuthStatus();
        
        // Set up periodic status checks (every 30 seconds)
        setInterval(() => this.checkAuthStatus(), 30000);
        
        // Update UI based on initial state
        this.updateUI();
    }

    /**
     * Check authentication status from server
     */
    async checkAuthStatus() {
        try {
            // Try to get auth status from API endpoint if available
            const response = await fetch('/api/auth/status');
            if (response.ok) {
                const data = await response.json();
                this.authEnabled = data.auth_enabled || false;
                this.userLoggedIn = data.logged_in || false;
                this.userName = data.username || '';
            } else {
                // Fallback: check for session cookie or localStorage
                this.checkLocalAuthState();
            }
        } catch (error) {
            console.log('⚠️ Auth status API not available, using fallback');
            this.checkLocalAuthState();
        }
        
        this.updateUI();
    }

    /**
     * Fallback method to check auth state locally
     */
    checkLocalAuthState() {
        // Check if ENABLE_KEYCLOAK_AUTH is set (from Flask template)
        const authEnabledElement = document.getElementById('auth-enabled');
        if (authEnabledElement) {
            this.authEnabled = authEnabledElement.dataset.enabled === 'true';
        } else {
            // Default: assume auth is disabled for easier testing
            this.authEnabled = false;
        }
        
        // Check for session indicators
        const hasAccessToken = this.getCookie('session') || localStorage.getItem('access_token');
        this.userLoggedIn = hasAccessToken ? true : false;
        
        // Try to get username from session
        this.userName = localStorage.getItem('username') || '';
    }

    /**
     * Get cookie value by name
     */
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    /**
     * Update UI elements based on auth state
     */
    updateUI() {
        console.log(`🔄 Updating auth UI: enabled=${this.authEnabled}, loggedIn=${this.userLoggedIn}, user=${this.userName}`);
        
        // Get UI elements
        const userInfo = document.getElementById('auth-user-info');
        const loginBtn = document.getElementById('auth-login-btn');
        const logoutBtn = document.getElementById('auth-logout-btn');
        const authDot = document.getElementById('auth-dot');
        
        if (!userInfo || !loginBtn || !logoutBtn || !authDot) {
            console.log('⚠️ Auth UI elements not found in DOM');
            return;
        }
        
        if (!this.authEnabled) {
            // Auth disabled: hide all auth elements
            userInfo.style.display = 'none';
            loginBtn.style.display = 'none';
            logoutBtn.style.display = 'none';
            authDot.style.display = 'none';
        } else {
            // Auth is enabled, show appropriate elements
            authDot.style.display = 'inline-block';
            
            if (this.userLoggedIn) {
                // User is logged in
                userInfo.style.display = 'block';
                loginBtn.style.display = 'none';
                logoutBtn.style.display = 'block';
                
                // Update username
                const usernameSpan = userInfo.querySelector('.auth-username');
                if (usernameSpan) {
                    usernameSpan.textContent = this.userName || 'Usuario';
                }
                
                // Set auth dot to green
                authDot.className = 'dot ok';
                authDot.title = 'Autenticado';
            } else {
                // User is not logged in
                userInfo.style.display = 'none';
                loginBtn.style.display = 'block';
                logoutBtn.style.display = 'none';
                
                // Set auth dot to red
                authDot.className = 'dot fail';
                authDot.title = 'No autenticado';
            }
        }
        
        // Notify context menu about auth state change
        this.notifyAuthStateChange();
    }
    
    /**
     * Notify other components about auth state change
     */
    notifyAuthStateChange() {
        // Dispatch custom event
        const event = new CustomEvent('authStateChanged', {
            detail: {
                enabled: this.authEnabled,
                loggedIn: this.userLoggedIn,
                username: this.userName,
                timestamp: new Date().toISOString()
            }
        });
        document.dispatchEvent(event);
        
        // Also update context menu directly if available
        if (window.geoportalContextMenu) {
            window.geoportalContextMenu.updateAuthState(this.userLoggedIn);
        }
    }

    /**
     * Simulate login (for testing without Keycloak)
     */
    simulateLogin(username = 'Usuario de prueba') {
        this.userLoggedIn = true;
        this.userName = username;
        localStorage.setItem('username', username);
        localStorage.setItem('access_token', 'simulated_token');
        this.updateUI();
        
        // Show notification
        this.showNotification('Sesión iniciada', 'success');
    }

    /**
     * Simulate logout
     */
    simulateLogout() {
        this.userLoggedIn = false;
        this.userName = '';
        localStorage.removeItem('username');
        localStorage.removeItem('access_token');
        this.updateUI();
        
        // Show notification
        this.showNotification('Sesión cerrada', 'info');
        
        // Redirect to home page
        window.location.href = '/';
    }

    /**
     * Update context menu based on auth state
     */
    updateContextMenu() {
        // This will be implemented when context menu is added
        if (window.geoportalContextMenu) {
            window.geoportalContextMenu.updateAuthState(this.userLoggedIn);
        }
    }

    /**
     * Show notification message
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `auth-notification auth-notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button class="auth-notification-close">&times;</button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
        
        // Close button handler
        notification.querySelector('.auth-notification-close').addEventListener('click', () => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        });
    }

    /**
     * Get current auth state
     */
    getAuthState() {
        return {
            enabled: this.authEnabled,
            loggedIn: this.userLoggedIn,
            username: this.userName
        };
    }
}

// Initialize auth UI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.geoportalAuthUI = new AuthUI();
    
    // Add CSS for notifications
    const style = document.createElement('style');
    style.textContent = `
        .auth-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-width: 300px;
            max-width: 400px;
            transition: opacity 0.3s ease;
        }
        .auth-notification-info {
            background-color: #2196F3;
        }
        .auth-notification-success {
            background-color: #4CAF50;
        }
        .auth-notification-warning {
            background-color: #FF9800;
        }
        .auth-notification-error {
            background-color: #F44336;
        }
        .auth-notification-close {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            margin-left: 15px;
            padding: 0 5px;
        }
        .auth-notification.fade-out {
            opacity: 0;
        }
        
        /* Auth elements in sidebar */
        .auth-element a {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .auth-username {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 80px;
        }
    `;
    document.head.appendChild(style);
    
    // Add debug controls if in development mode
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        this.addDebugControls();
    }
});

/**
 * Add debug controls for testing auth without Keycloak
 */
function addDebugControls() {
    const debugDiv = document.createElement('div');
    debugDiv.id = 'auth-debug-controls';
    debugDiv.style.cssText = `
        position: fixed;
        bottom: 10px;
        right: 10px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-size: 12px;
        z-index: 9999;
    `;
    
    debugDiv.innerHTML = `
        <strong>🔐 Auth Debug</strong><br>
        <button onclick="window.geoportalAuthUI.simulateLogin('Test User')">Simular Login</button>
        <button onclick="window.geoportalAuthUI.simulateLogout()">Simular Logout</button>
        <button onclick="console.log(window.geoportalAuthUI.getAuthState())">Estado</button>
    `;
    
    document.body.appendChild(debugDiv);
}