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
        
        // Get UI elements for NEW interface
        const userIconContainer = document.getElementById('user-icon-container');
        const loginIconContainer = document.getElementById('login-icon-container');
        const authDisabledContainer = document.getElementById('auth-disabled-container');
        const userDisplayName = document.getElementById('user-display-name');
        const userIcon = document.getElementById('user-icon');
        
        if (!userIconContainer || !loginIconContainer || !authDisabledContainer) {
            console.log('⚠️ New auth UI elements not found in DOM');
            return;
        }
        
        // Hide all containers first
        userIconContainer.style.display = 'none';
        loginIconContainer.style.display = 'none';
        authDisabledContainer.style.display = 'none';
        
        if (!this.authEnabled) {
            // Auth disabled: show disabled icon
            authDisabledContainer.style.display = 'block';
        } else {
            // Auth is enabled
            if (this.userLoggedIn) {
                // User is logged in: show user icon with dropdown
                userIconContainer.style.display = 'block';
                
                // Update user display name
                if (userDisplayName) {
                    userDisplayName.textContent = this.userName || 'Usuario';
                }
                
                // Add logged-in class for styling
                if (userIcon) {
                    userIcon.classList.add('logged-in');
                }
            } else {
                // User is not logged in: show login button
                loginIconContainer.style.display = 'block';
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
     * Login user (to be called by Keycloak or other auth system)
     */
    login(username = 'Usuario') {
        this.userLoggedIn = true;
        this.userName = username;
        localStorage.setItem('username', username);
        localStorage.setItem('access_token', 'authenticated');
        this.updateUI();
        
        // Show notification
        this.showNotification('Sesión iniciada', 'success');
    }

    /**
     * Logout user
     */
    logout() {
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
    `;
    document.head.appendChild(style);
});