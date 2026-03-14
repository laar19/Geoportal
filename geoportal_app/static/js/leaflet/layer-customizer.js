/**
 * Layer Customizer Module
 * Provides dynamic styling controls for layers in the Information sidebar.
 * Supports geometry-specific controls (fill disabled for LineString layers).
 */

(function (global) {
    'use strict';

    // Color palette with 11 professional colors
    const COLOR_PRESETS = [
        { name: 'Ocean Blue', hex: '#2563eb' },
        { name: 'Emerald', hex: '#10b981' },
        { name: 'Amber', hex: '#f59e0b' },
        { name: 'Rose', hex: '#f43f5e' },
        { name: 'Violet', hex: '#8b5cf6' },
        { name: 'Slate', hex: '#64748b' },
        { name: 'Orange', hex: '#ea580c' },
        { name: 'Cyan', hex: '#06b6d4' },
        { name: 'Black', hex: '#000000' },
        { name: 'White', hex: '#ffffff' },
        { name: 'Grey', hex: '#6b7280' }
    ];

    const FALLBACK_COLOR = '#3388ff';
    const DEFAULT_STYLES = {
        fillColor: '#3388ff',
        strokeColor: '#0c275a',
        opacity: 80,
        strokeWidth: 2
    };

    class LayerCustomizer {
        constructor(map, geoserverConfig) {
            this._map = map;
            this._geoserverConfig = geoserverConfig;
            this._selectedLayer = null;
            this._selectedLayerData = null;
            this._geometryType = null;
            this._customStyles = {}; // { layerName: { fillColor, strokeColor, opacity, strokeWidth } }
            this._overlayLayers = {}; // { layerName: L.GeoJSON }
            this._wmsLayers = {}; // Reference to original WMS layers
            this._panelElement = null;
            this._isInitialized = false;
        }

        /**
         * Initialize the customizer - create UI panel
         */
        init() {
            if (this._isInitialized) return;
            this._createPanel();
            this._bindEvents();
            this._isInitialized = true;
            console.log('LayerCustomizer initialized');
        }

        /**
         * Register a WMS layer for customization
         */
        registerWMSLayer(layerName, wmsLayer, layerData) {
            this._wmsLayers[layerName] = wmsLayer;
            // Initialize default styles if not set
            if (!this._customStyles[layerName]) {
                this._customStyles[layerName] = { ...DEFAULT_STYLES };
            }
        }

        /**
         * Select a layer for customization
         */
        selectLayer(layerName, layerData, geometryType) {
            this._selectedLayer = layerName;
            this._selectedLayerData = layerData;
            this._geometryType = geometryType || 'Polygon';

            // Update UI
            this._updatePanelForLayer();
            this._showPanel();
        }

        /**
         * Hide the customization panel
         */
        hidePanel() {
            if (this._panelElement) {
                this._panelElement.style.display = 'none';
            }
            this._selectedLayer = null;
        }

        /**
         * Create the customization panel HTML
         */
        _createPanel() {
            const container = document.getElementById('layer-customization-container');
            if (!container) {
                console.warn('LayerCustomizer: #layer-customization-container not found');
                return;
            }

            const panel = document.createElement('div');
            panel.id = 'layer-customization-panel';
            panel.className = 'layer-customization-panel';
            panel.style.display = 'none';

            panel.innerHTML = `
                <div class="customizer-header">
                    <h4 id="customizer-layer-name">Personalizar Capa</h4>
                    <button id="customizer-close-btn" class="customizer-close" title="Cerrar">&times;</button>
                </div>
                
                <div class="customizer-body">
                    <!-- Opacity Control -->
                    <div class="customizer-group">
                        <label for="customizer-opacity">
                            <i class="fas fa-adjust"></i> Opacidad
                            <span id="customizer-opacity-value">80%</span>
                        </label>
                        <input type="range" id="customizer-opacity" min="0" max="100" value="80" class="customizer-slider">
                    </div>

                    <!-- Stroke Color -->
                    <div class="customizer-group">
                        <label><i class="fas fa-pen"></i> Color de Borde</label>
                        <div class="color-picker-row">
                            <div id="stroke-color-swatches" class="color-swatch-grid"></div>
                            <div class="hex-input-group">
                                <span>#</span>
                                <input type="text" id="customizer-stroke-hex" maxlength="6" placeholder="0c275a" class="hex-input">
                            </div>
                        </div>
                    </div>

                    <!-- Stroke Width -->
                    <div class="customizer-group">
                        <label for="customizer-stroke-width">
                            <i class="fas fa-minus"></i> Grosor de Borde
                            <span id="customizer-stroke-width-value">2px</span>
                        </label>
                        <input type="range" id="customizer-stroke-width" min="1" max="10" value="2" class="customizer-slider">
                    </div>

                    <!-- Fill Color (hidden for LineString) -->
                    <div class="customizer-group" id="fill-color-group">
                        <label><i class="fas fa-fill-drip"></i> Color de Relleno</label>
                        <div class="color-picker-row">
                            <div id="fill-color-swatches" class="color-swatch-grid"></div>
                            <div class="hex-input-group">
                                <span>#</span>
                                <input type="text" id="customizer-fill-hex" maxlength="6" placeholder="3388ff" class="hex-input">
                            </div>
                        </div>
                    </div>
                </div>

                <div class="customizer-footer">
                    <button id="customizer-reset-btn" class="customizer-btn customizer-btn-secondary">
                        <i class="fas fa-undo"></i> Restablecer
                    </button>
                    <button id="customizer-apply-btn" class="customizer-btn customizer-btn-primary">
                        <i class="fas fa-check"></i> Aplicar
                    </button>
                </div>
            `;

            container.appendChild(panel);
            this._panelElement = panel;

            // Populate color swatches
            this._populateColorSwatches('stroke-color-swatches', 'stroke');
            this._populateColorSwatches('fill-color-swatches', 'fill');
        }

        /**
         * Populate color swatch grid
         */
        _populateColorSwatches(containerId, type) {
            const container = document.getElementById(containerId);
            if (!container) return;

            container.innerHTML = '';
            COLOR_PRESETS.forEach(color => {
                const swatch = document.createElement('div');
                swatch.className = 'color-swatch';
                swatch.style.backgroundColor = color.hex;
                swatch.title = color.name;
                swatch.dataset.color = color.hex;
                swatch.dataset.type = type;

                // Add border for light colors
                if (color.hex === '#ffffff' || color.hex === '#f59e0b') {
                    swatch.style.border = '1px solid #ccc';
                }

                container.appendChild(swatch);
            });
        }

        /**
         * Bind event listeners
         */
        _bindEvents() {
            const self = this;

            // Close button
            const closeBtn = document.getElementById('customizer-close-btn');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => self.hidePanel());
            }

            // Opacity slider
            const opacitySlider = document.getElementById('customizer-opacity');
            if (opacitySlider) {
                opacitySlider.addEventListener('input', (e) => {
                    document.getElementById('customizer-opacity-value').textContent = e.target.value + '%';
                    self._updateStyleProperty('opacity', parseInt(e.target.value));
                });
            }

            // Stroke width slider
            const strokeWidthSlider = document.getElementById('customizer-stroke-width');
            if (strokeWidthSlider) {
                strokeWidthSlider.addEventListener('input', (e) => {
                    document.getElementById('customizer-stroke-width-value').textContent = e.target.value + 'px';
                    self._updateStyleProperty('strokeWidth', parseInt(e.target.value));
                });
            }

            // Color swatch clicks (using event delegation)
            document.addEventListener('click', (e) => {
                if (e.target.classList.contains('color-swatch')) {
                    const color = e.target.dataset.color;
                    const type = e.target.dataset.type;

                    if (type === 'stroke') {
                        document.getElementById('customizer-stroke-hex').value = color.replace('#', '');
                        self._updateStyleProperty('strokeColor', color);
                        self._highlightSelectedSwatch('stroke-color-swatches', color);
                    } else if (type === 'fill') {
                        document.getElementById('customizer-fill-hex').value = color.replace('#', '');
                        self._updateStyleProperty('fillColor', color);
                        self._highlightSelectedSwatch('fill-color-swatches', color);
                    }
                }
            });

            // Hex input for stroke
            const strokeHex = document.getElementById('customizer-stroke-hex');
            if (strokeHex) {
                strokeHex.addEventListener('change', (e) => {
                    const hex = '#' + e.target.value;
                    if (self._isValidHex(hex)) {
                        self._updateStyleProperty('strokeColor', hex);
                        self._highlightSelectedSwatch('stroke-color-swatches', hex);
                    } else {
                        e.target.value = DEFAULT_STYLES.strokeColor.replace('#', '');
                        self._showWarning('Código hex inválido, usando color por defecto');
                    }
                });
            }

            // Hex input for fill
            const fillHex = document.getElementById('customizer-fill-hex');
            if (fillHex) {
                fillHex.addEventListener('change', (e) => {
                    const hex = '#' + e.target.value;
                    if (self._isValidHex(hex)) {
                        self._updateStyleProperty('fillColor', hex);
                        self._highlightSelectedSwatch('fill-color-swatches', hex);
                    } else {
                        e.target.value = DEFAULT_STYLES.fillColor.replace('#', '');
                        self._showWarning('Código hex inválido, usando color por defecto');
                    }
                });
            }

            // Reset button
            const resetBtn = document.getElementById('customizer-reset-btn');
            if (resetBtn) {
                resetBtn.addEventListener('click', () => self._resetStyle());
            }

            // Apply button
            const applyBtn = document.getElementById('customizer-apply-btn');
            if (applyBtn) {
                applyBtn.addEventListener('click', () => self._applyStyle());
            }
        }

        /**
         * Highlight selected color swatch
         */
        _highlightSelectedSwatch(containerId, color) {
            const container = document.getElementById(containerId);
            if (!container) return;

            container.querySelectorAll('.color-swatch').forEach(swatch => {
                swatch.classList.remove('selected');
                if (swatch.dataset.color.toLowerCase() === color.toLowerCase()) {
                    swatch.classList.add('selected');
                }
            });
        }

        /**
         * Validate hex color code
         */
        _isValidHex(hex) {
            return /^#([0-9A-F]{3}){1,2}$/i.test(hex);
        }

        /**
         * Show warning message
         */
        _showWarning(message) {
            if (typeof showNonBlockingAlert === 'function') {
                showNonBlockingAlert(message, 'warning');
            } else {
                console.warn(message);
            }
        }

        /**
         * Update a style property and apply real-time preview
         */
        _updateStyleProperty(property, value) {
            if (!this._selectedLayer) return;

            if (!this._customStyles[this._selectedLayer]) {
                this._customStyles[this._selectedLayer] = { ...DEFAULT_STYLES };
            }
            this._customStyles[this._selectedLayer][property] = value;

            // Apply real-time preview
            this._applyStylePreview();
        }

        /**
         * Apply style preview (real-time update)
         */
        async _applyStylePreview() {
            if (!this._selectedLayer) return;

            const styles = this._customStyles[this._selectedLayer];
            const wmsLayer = this._wmsLayers[this._selectedLayer];

            // If we have an overlay layer, update its style in real-time
            if (this._overlayLayers[this._selectedLayer]) {
                this._updateOverlayStyle(this._selectedLayer);
            } else if (wmsLayer) {
                // Only opacity can be changed on WMS without overlay
                const opacity = styles.opacity / 100;
                wmsLayer.setOpacity(opacity);
            }
        }

        /**
         * Update overlay layer style
         */
        _updateOverlayStyle(layerName) {
            const overlay = this._overlayLayers[layerName];
            const styles = this._customStyles[layerName];

            if (!overlay || !styles) return;

            const opacity = styles.opacity / 100;

            overlay.setStyle((feature) => {
                const geomType = feature.geometry ? feature.geometry.type : '';
                const isLine = geomType === 'LineString' || geomType === 'MultiLineString';

                return {
                    color: styles.strokeColor,
                    weight: styles.strokeWidth,
                    fillColor: isLine ? undefined : styles.fillColor,
                    fillOpacity: isLine ? 0 : opacity * 0.6,
                    opacity: opacity
                };
            });

            // Also update circle markers for points
            overlay.eachLayer((layer) => {
                if (layer instanceof L.CircleMarker) {
                    layer.setStyle({
                        color: styles.strokeColor,
                        weight: styles.strokeWidth,
                        fillColor: styles.fillColor,
                        fillOpacity: opacity
                    });
                }
            });
        }

        /**
         * Toggle between WMS layer and styled overlay
         */
        _toggleWmsOverlay(layerName, showOverlay) {
            const wmsLayer = this._wmsLayers[layerName];
            const overlay = this._overlayLayers[layerName];

            if (showOverlay && overlay) {
                // Hide WMS, show overlay
                if (wmsLayer && this._map.hasLayer(wmsLayer)) {
                    wmsLayer.setOpacity(0);
                }
                if (!this._map.hasLayer(overlay)) {
                    overlay.addTo(this._map);
                }
            } else {
                // Show WMS, hide overlay
                if (overlay && this._map.hasLayer(overlay)) {
                    this._map.removeLayer(overlay);
                }
                if (wmsLayer) {
                    const styles = this._customStyles[layerName] || DEFAULT_STYLES;
                    wmsLayer.setOpacity(styles.opacity / 100);
                }
            }
        }

        /**
         * Apply the current style (commit changes) - fetches WFS and creates styled overlay
         */
        async _applyStyle() {
            if (!this._selectedLayer) return;

            const styles = this._customStyles[this._selectedLayer];
            console.log('Applying styles for', this._selectedLayer, styles);

            // Show loading indicator
            const applyBtn = document.getElementById('customizer-apply-btn');
            if (applyBtn) {
                applyBtn.disabled = true;
                applyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Aplicando...';
            }

            try {
                // Create overlay if it doesn't exist
                if (!this._overlayLayers[this._selectedLayer]) {
                    await this._createOverlayForLayer(this._selectedLayer);
                }

                // Update overlay styles
                this._updateOverlayStyle(this._selectedLayer);

                // Switch to overlay view
                this._toggleWmsOverlay(this._selectedLayer, true);

                // Show success message
                if (typeof showNonBlockingAlert === 'function') {
                    showNonBlockingAlert('Estilos aplicados correctamente', 'success');
                }
            } catch (error) {
                console.error('Error applying styles:', error);
                if (typeof showNonBlockingAlert === 'function') {
                    showNonBlockingAlert('Error al aplicar estilos: ' + error.message, 'danger');
                }
            } finally {
                // Restore button
                if (applyBtn) {
                    applyBtn.disabled = false;
                    applyBtn.innerHTML = '<i class="fas fa-check"></i> Aplicar';
                }
            }
        }

        /**
         * Reset style to defaults
         */
        _resetStyle() {
            if (!this._selectedLayer) return;

            this._customStyles[this._selectedLayer] = { ...DEFAULT_STYLES };
            this._updatePanelForLayer();

            // Switch back to WMS layer (hide overlay)
            this._toggleWmsOverlay(this._selectedLayer, false);

            // Apply default opacity to WMS
            const wmsLayer = this._wmsLayers[this._selectedLayer];
            if (wmsLayer) {
                wmsLayer.setOpacity(DEFAULT_STYLES.opacity / 100);
            }

            if (typeof showNonBlockingAlert === 'function') {
                showNonBlockingAlert('Estilos restablecidos', 'info');
            }
        }

        /**
         * Show the customization panel
         */
        _showPanel() {
            if (this._panelElement) {
                this._panelElement.style.display = 'block';
            }
        }

        /**
         * Update panel controls based on selected layer
         */
        _updatePanelForLayer() {
            if (!this._selectedLayer || !this._panelElement) return;

            const styles = this._customStyles[this._selectedLayer] || { ...DEFAULT_STYLES };

            // Update layer name
            const nameEl = document.getElementById('customizer-layer-name');
            if (nameEl) {
                nameEl.textContent = this._selectedLayer;
            }

            // Update opacity slider
            const opacitySlider = document.getElementById('customizer-opacity');
            const opacityValue = document.getElementById('customizer-opacity-value');
            if (opacitySlider && opacityValue) {
                opacitySlider.value = styles.opacity;
                opacityValue.textContent = styles.opacity + '%';
            }

            // Update stroke width slider
            const strokeWidthSlider = document.getElementById('customizer-stroke-width');
            const strokeWidthValue = document.getElementById('customizer-stroke-width-value');
            if (strokeWidthSlider && strokeWidthValue) {
                strokeWidthSlider.value = styles.strokeWidth;
                strokeWidthValue.textContent = styles.strokeWidth + 'px';
            }

            // Update hex inputs
            const strokeHex = document.getElementById('customizer-stroke-hex');
            if (strokeHex) {
                strokeHex.value = styles.strokeColor.replace('#', '');
            }

            const fillHex = document.getElementById('customizer-fill-hex');
            if (fillHex) {
                fillHex.value = styles.fillColor.replace('#', '');
            }

            // Highlight selected swatches
            this._highlightSelectedSwatch('stroke-color-swatches', styles.strokeColor);
            this._highlightSelectedSwatch('fill-color-swatches', styles.fillColor);

            // Show/hide fill color group based on geometry type
            const fillGroup = document.getElementById('fill-color-group');
            if (fillGroup) {
                const isLine = this._geometryType === 'LineString' ||
                    this._geometryType === 'MultiLineString';
                fillGroup.style.display = isLine ? 'none' : 'block';
            }
        }

        /**
         * Create a GeoJSON overlay for a layer (for custom styling)
         */
        async _createOverlayForLayer(layerName) {
            if (this._overlayLayers[layerName]) {
                return this._overlayLayers[layerName];
            }

            // Build WFS URL - try different service paths
            const geoserverUrl = this._geoserverConfig.geoserver_url;
            const workspace = this._geoserverConfig.workspace || '';
            const typeName = workspace ? `${workspace}:${layerName}` : layerName;

            // Try multiple WFS endpoint patterns
            const wfsUrls = [
                `${geoserverUrl}/wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=${typeName}&outputFormat=application/json`,
                `${geoserverUrl}/ows?service=WFS&version=1.1.0&request=GetFeature&typeName=${typeName}&outputFormat=application/json`,
                `${geoserverUrl}/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=${layerName}&outputFormat=application/json`
            ];

            let geojson = null;
            let lastError = null;

            for (const wfsUrl of wfsUrls) {
                try {
                    console.log('Trying WFS URL:', wfsUrl);
                    const response = await fetch(wfsUrl);
                    if (response.ok) {
                        const data = await response.json();
                        if (data.features && data.features.length > 0) {
                            geojson = data;
                            break;
                        }
                    }
                } catch (err) {
                    lastError = err;
                    console.warn('WFS fetch failed:', wfsUrl, err);
                }
            }

            if (!geojson) {
                throw new Error('No se pudo obtener los datos de la capa. ' + (lastError ? lastError.message : ''));
            }

            const styles = this._customStyles[layerName] || { ...DEFAULT_STYLES };
            const opacity = styles.opacity / 100;

            const overlay = L.geoJSON(geojson, {
                style: (feature) => {
                    const geomType = feature.geometry ? feature.geometry.type : '';
                    const isLine = geomType === 'LineString' || geomType === 'MultiLineString';

                    return {
                        color: styles.strokeColor,
                        weight: styles.strokeWidth,
                        fillColor: isLine ? undefined : styles.fillColor,
                        fillOpacity: isLine ? 0 : opacity * 0.6,
                        opacity: opacity
                    };
                },
                pointToLayer: (feature, latlng) => {
                    return L.circleMarker(latlng, {
                        radius: 6,
                        color: styles.strokeColor,
                        weight: styles.strokeWidth,
                        fillColor: styles.fillColor,
                        fillOpacity: opacity
                    });
                }
            });

            this._overlayLayers[layerName] = overlay;

            // Detect geometry type from first feature
            if (geojson.features && geojson.features.length > 0) {
                const geomType = geojson.features[0].geometry.type;
                this._geometryType = geomType;
                // Update UI to show/hide fill controls
                const fillGroup = document.getElementById('fill-color-group');
                if (fillGroup) {
                    const isLine = geomType === 'LineString' || geomType === 'MultiLineString';
                    fillGroup.style.display = isLine ? 'none' : 'block';
                }
            }

            return overlay;
        }
        /**
         * Check if a layer has an active customized overlay
         */
        hasActiveOverlay(layerName) {
            // An overlay is "active" if it exists in our registry. 
            // It might currently be hidden if the user toggled it off, 
            // but we want to know if 'this module' owns the representation.
            // However, we only "own" it if we successfully created an overlay.
            // If we just have custom styles but no overlay (only WMS opacity change), 
            // then we don't own the toggle (WMS toggle works fine for just opacity).
            return !!this._overlayLayers[layerName];
        }

        /**
         * Toggle visibility of the customized overlay
         * returns true if visible, false if hidden
         */
        toggleLayerVisibility(layerName) {
            const overlay = this._overlayLayers[layerName];
            if (!overlay) return false;

            if (this._map.hasLayer(overlay)) {
                this._map.removeLayer(overlay);
                return false;
            } else {
                overlay.addTo(this._map);
                return true;
            }
        }
    }

    // Export to global scope
    global.LayerCustomizer = LayerCustomizer;

})(window);
