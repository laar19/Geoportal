/**
 * Leaflet Context Menu Manager for Geoportal
 * Implements right-click context menu with conditional options based on auth state
 */

class ContextMenuManager {
    constructor(map) {
        this.map = map;
        this.contextMenu = null;
        this.authEnabled = false;
        this.userLoggedIn = false;
        this.init();
    }

    /**
     * Initialize context menu
     */
    init() {
        console.log('🖱️ ContextMenuManager initializing...');
        
        // Wait for map to be fully initialized
        if (!this.map) {
            console.error('❌ Map not available for context menu');
            return;
        }
        
        // Create context menu with basic options
        this.createContextMenu();
        
        // Listen for auth state changes
        this.setupAuthListeners();
    }

    /**
     * Create Leaflet context menu
     */
    createContextMenu() {
        // Basic menu items (always available)
        const basicItems = [
            {
                text: '<i class="fa-solid fa-ruler"></i> Medir distancia desde aquí',
                callback: () => this.measureDistance(),
                index: 0
            },
            {
                text: '<i class="fa-solid fa-draw-polygon"></i> Medir área desde aquí',
                callback: () => this.measureArea(),
                index: 1
            },
            {
                text: '<i class="fa-solid fa-location-crosshairs"></i> Obtener coordenadas',
                callback: (e) => this.getCoordinates(e),
                index: 2
            },
            {
                separator: true,
                index: 3
            },
            {
                text: '<i class="fa-solid fa-layer-group"></i> Cambiar capa base',
                callback: () => this.changeBaseLayer(),
                index: 4
            },
            {
                text: '<i class="fa-solid fa-arrows-rotate"></i> Centrar mapa aquí',
                callback: (e) => this.centerMap(e),
                index: 5
            }
        ];

        // Auth-related items (conditional)
        const authItems = [
            {
                separator: true,
                index: 6,
                hide: () => !this.authEnabled
            },
            {
                text: '<i class="fa-solid fa-sign-in-alt"></i> Iniciar sesión',
                callback: () => this.login(),
                index: 7,
                hide: () => !this.authEnabled || this.userLoggedIn
            },
            {
                text: '<i class="fa-solid fa-user"></i> Mi perfil',
                callback: () => this.showProfile(),
                index: 8,
                hide: () => !this.authEnabled || !this.userLoggedIn
            },
            {
                text: '<i class="fa-solid fa-download"></i> Descargar datos',
                callback: () => this.downloadData(),
                index: 9,
                hide: () => !this.authEnabled || !this.userLoggedIn
            },
            {
                text: '<i class="fa-solid fa-sign-out-alt" style="color: #ff6b6b;"></i> Cerrar sesión',
                callback: () => this.logout(),
                index: 10,
                hide: () => !this.authEnabled || !this.userLoggedIn
            }
        ];

        // Combine all items
        const allItems = [...basicItems, ...authItems];

        // Create context menu
        this.contextMenu = this.map.contextmenu;
        
        if (!this.contextMenu) {
            this.contextMenu = L.popup();
        }

        // Add context menu to map
        this.map.contextmenu = this.contextMenu;
        
        // Set up context menu items
        this.updateMenuItems(allItems);
        
        console.log('✅ Context menu created');
    }

    /**
     * Update menu items based on current auth state
     */
    updateMenuItems(items) {
        // Clear existing items
        if (this.map.contextmenu && this.map.contextmenu.removeAllItems) {
            this.map.contextmenu.removeAllItems();
        }
        
        // Filter items based on hide conditions
        const visibleItems = items.filter(item => {
            if (item.hide && typeof item.hide === 'function') {
                return !item.hide();
            }
            return true;
        });
        
        // Add items to context menu
        visibleItems.forEach(item => {
            if (item.separator) {
                this.map.contextmenu.addSeparator();
            } else {
                this.map.contextmenu.addItem({
                    text: item.text,
                    callback: item.callback,
                    index: item.index
                });
            }
        });
    }

    /**
     * Set up listeners for auth state changes
     */
    setupAuthListeners() {
        // Listen for custom auth state change events
        document.addEventListener('authStateChanged', (e) => {
            if (e.detail) {
                this.authEnabled = e.detail.enabled || false;
                this.userLoggedIn = e.detail.loggedIn || false;
                this.updateMenu();
            }
        });
        
        // Also listen to window.geoportalAuthUI if available
        if (window.geoportalAuthUI) {
            const authState = window.geoportalAuthUI.getAuthState();
            this.authEnabled = authState.enabled;
            this.userLoggedIn = authState.loggedIn;
            this.updateMenu();
            
            // Update when auth UI changes
            setInterval(() => {
                if (window.geoportalAuthUI) {
                    const currentState = window.geoportalAuthUI.getAuthState();
                    if (currentState.enabled !== this.authEnabled || 
                        currentState.loggedIn !== this.userLoggedIn) {
                        this.authEnabled = currentState.enabled;
                        this.userLoggedIn = currentState.loggedIn;
                        this.updateMenu();
                    }
                }
            }, 1000);
        }
    }

    /**
     * Update menu based on current auth state
     */
    updateMenu() {
        console.log(`🔄 Updating context menu: authEnabled=${this.authEnabled}, userLoggedIn=${this.userLoggedIn}`);
        
        // Recreate menu with updated items
        this.createContextMenu();
        
        // Dispatch event for other components
        this.dispatchUpdateEvent();
    }

    /**
     * Dispatch event when menu is updated
     */
    dispatchUpdateEvent() {
        const event = new CustomEvent('contextMenuUpdated', {
            detail: {
                authEnabled: this.authEnabled,
                userLoggedIn: this.userLoggedIn,
                timestamp: new Date().toISOString()
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * Update auth state from external source
     */
    updateAuthState(loggedIn) {
        this.userLoggedIn = loggedIn;
        this.updateMenu();
    }

    /**
     * Menu item callbacks
     */
    
    measureDistance() {
        console.log('📏 Measure distance from context menu');
        // Trigger distance measurement tool
        if (window.measureTool) {
            window.measureTool.startDistanceMeasurement();
        } else {
            alert('Herramienta de medición de distancia activada. Haz clic en el mapa para empezar a medir.');
        }
    }

    measureArea() {
        console.log('📐 Measure area from context menu');
        // Trigger area measurement tool
        if (window.measureTool) {
            window.measureTool.startAreaMeasurement();
        } else {
            alert('Herramienta de medición de área activada. Haz clic en el mapa para empezar a medir.');
        }
    }

    getCoordinates(e) {
        if (e && e.latlng) {
            const lat = e.latlng.lat.toFixed(6);
            const lng = e.latlng.lng.toFixed(6);
            console.log(`📍 Coordinates: ${lat}, ${lng}`);
            
            // Show coordinates in a popup
            L.popup()
                .setLatLng(e.latlng)
                .setContent(`
                    <div style="text-align: center;">
                        <strong>Coordenadas</strong><br>
                        Lat: ${lat}<br>
                        Lng: ${lng}<br>
                        <button onclick="navigator.clipboard.writeText('${lat}, ${lng}')" 
                                style="margin-top: 5px; padding: 2px 8px; font-size: 12px;">
                            Copiar
                        </button>
                    </div>
                `)
                .openOn(this.map);
        }
    }

    changeBaseLayer() {
        console.log('🗺️ Change base layer from context menu');
        // Show layer switcher if available
        if (window.layerControl) {
            // Toggle layer control visibility
            const control = document.querySelector('.leaflet-control-layers');
            if (control) {
                control.style.display = control.style.display === 'none' ? 'block' : 'none';
            }
        } else {
            alert('Usa el selector de capas en la esquina superior derecha para cambiar la capa base.');
        }
    }

    centerMap(e) {
        if (e && e.latlng) {
            console.log('🎯 Center map at:', e.latlng);
            this.map.setView(e.latlng, this.map.getZoom());
            
            // Visual feedback
            L.circle(e.latlng, {
                radius: 10,
                color: '#3388ff',
                fillColor: '#3388ff',
                fillOpacity: 0.5
            }).addTo(this.map).bindPopup('Centrado aquí').openPopup();
            
            setTimeout(() => {
                this.map.eachLayer(layer => {
                    if (layer instanceof L.Circle && layer.getRadius() === 10) {
                        this.map.removeLayer(layer);
                    }
                });
            }, 2000);
        }
    }

    login() {
        console.log('🔐 Login from context menu');
        // Redirect to login page
        window.location.href = '/login';
    }

    showProfile() {
        console.log('👤 Show profile from context menu');
        // Show user profile modal or page
        alert('Perfil de usuario (funcionalidad en desarrollo)');
    }

    downloadData() {
        console.log('📥 Download data from context menu');
        // Show download options modal
        alert('Descarga de datos (funcionalidad en desarrollo)\n\nEsta opción solo está disponible para usuarios autenticados.');
    }

    logout() {
        console.log('🚪 Logout from context menu');
        // Confirm logout
        if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
            // Redirect to logout endpoint
            window.location.href = '/logout';
        }
    }

    /**
     * Get current context menu state
     */
    getState() {
        return {
            authEnabled: this.authEnabled,
            userLoggedIn: this.userLoggedIn,
            menuItems: this.contextMenu ? this.contextMenu._items.length : 0
        };
    }
}

// Initialize context menu when map is available
function initContextMenu() {
    // Wait for map to be available
    const checkMap = setInterval(() => {
        if (window.map) {
            clearInterval(checkMap);
            
            // Initialize context menu manager
            window.geoportalContextMenu = new ContextMenuManager(window.map);
            
            console.log('✅ Context menu initialized on map');
            
            // Make it available globally
            window.geoportalContextMenu = window.geoportalContextMenu;
            
            // Dispatch event
            document.dispatchEvent(new CustomEvent('contextMenuInitialized', {
                detail: { map: window.map }
            }));
        }
    }, 100);
}

// Start initialization when DOM is ready
document.addEventListener('DOMContentLoaded', initContextMenu);

// Also try to initialize if map becomes available later
if (window.map) {
    initContextMenu();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ContextMenuManager };
}