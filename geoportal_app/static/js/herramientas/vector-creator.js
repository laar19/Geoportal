// lib/vector-creator.js

// === SIMPLIFICACIÓN: Eliminar UMD wrapper y L.Control.extend ===
// Asumimos que Leaflet y Leaflet.draw ya están cargados globalmente.
// Este script se ejecuta después de leaflet.js y leaflet.draw.js.

// Verificación inicial para asegurar que L y L.Control.Draw están disponibles
if (typeof L === 'undefined' || typeof L.Control === 'undefined' || typeof L.Control.Draw === 'undefined') {
    console.error("vector-creator: Error crítico. Leaflet o Leaflet.draw no están cargados correctamente.");
    console.error("Asegúrate de que 'leaflet.js' y 'leaflet.draw.js' se carguen ANTES de este script.");
    throw new Error("Leaflet o Leaflet.draw no disponibles.");
}

// Definir la clase principal (NO extiende L.Control)
L.VectorCreator = L.Class.extend({

    options: {
        // position: 'topright', // <-- Ya no es relevante
        title: 'Vector Creator',
        defaultPointStyle: {
            radius: 6,
            fillColor: "#1E90FF",
            color: "#00008B",
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        },
        defaultPathOptions: {
            color: '#3388ff',
            weight: 3,
            opacity: 0.8
        }
    },

    // initialize ahora recibe el mapa directamente
    initialize: function (map, options) {
        L.Util.setOptions(this, options);
        this._map = map; // <-- Recibimos el mapa aquí
        this._drawnItems = new L.FeatureGroup();
        this._map.addLayer(this._drawnItems); // <-- Añadimos el FG al mapa principal
        this._drawControl = null; // <-- Se inicializará al activar
        this._selectedLayers = new Set();
        this._highlightStyle = {
            color: '#ff0000',
            weight: 4,
            fillColor: '#ffcccc',
            fillOpacity: 0.5
        };
        this._uiContainer = null; // <-- Contenedor del UI para el sidebar
    },

    // Método para crear el panel de UI (HTML) del sidebar
    createUI: function () {
        if (this._uiContainer) {
            // Si ya existe, devolverlo
            return this._uiContainer;
        }

        const container = L.DomUtil.create('div', 'vector-creator-panel');
        container.innerHTML = `
            <h4>${this.options.title}</h4>
            <div class="vector-creator-actions">
                <button class="btn btn-sm" id="vector-creator-load-btn-sidebar">Cargar GeoJSON</button>
                <button class="btn btn-sm" id="vector-creator-style-btn-sidebar">Editar estilo</button>
                <button class="btn btn-sm" id="vector-creator-save-btn-sidebar">Guardar seleccionadas</button>
            </div>
            <div id="vector-creator-status-sidebar">0 capas seleccionadas.</div>
            <div id="vector-creator-style-panel-sidebar">
                <div class="style-group">
                    <label for="vector-creator-stroke-color-sidebar">Color de línea:</label>
                    <input type="color" id="vector-creator-stroke-color-sidebar" value="#3388ff">
                </div>
                <div class="style-group">
                    <label for="vector-creator-stroke-weight-sidebar">Grosor de línea (px):</label>
                    <input type="range" id="vector-creator-stroke-weight-sidebar" min="1" max="10" value="3">
                    <span id="vector-creator-weight-value-sidebar">3</span>
                </div>
                <div class="style-group">
                    <label for="vector-creator-fill-color-sidebar">Color de relleno:</label>
                    <input type="color" id="vector-creator-fill-color-sidebar" value="#3388ff">
                </div>
                <div class="style-group">
                    <label for="vector-creator-fill-opacity-sidebar">Opacidad de relleno:</label>
                    <input type="range" id="vector-creator-fill-opacity-sidebar" min="0" max="1" step="0.1" value="0.2">
                    <span id="vector-creator-opacity-value-sidebar">0.2</span>
                </div>
                <div class="style-group" id="vector-creator-radius-group-sidebar" style="display:none;">
                    <label for="vector-creator-point-radius-sidebar">Radio del punto (px):</label>
                    <input type="range" id="vector-creator-point-radius-sidebar" min="2" max="15" value="6">
                    <span id="vector-creator-radius-value-sidebar">6</span>
                </div>
            </div>
            <!-- Opcional: Mini contenedor para mostrar capas dibujadas -->
            <div id="vector-creator-drawn-layers-container-sidebar" style="margin-top: 10px; max-height: 150px; overflow-y: auto; border: 1px solid #ccc; padding: 5px;">
                <h5>Capas dibujadas:</h5>
                <ul id="vector-creator-drawn-list-sidebar"></ul>
            </div>
        `;

        this._uiContainer = container;
        this._initUIEvents(container); // Inicializar eventos del UI
        return container;
    },

    // Inicializar eventos del UI del sidebar (botones, sliders)
    _initUIEvents: function (container) {
        const self = this;

        // Cargar GeoJSON
        container.querySelector('#vector-creator-load-btn-sidebar').addEventListener('click', function () {
            self._showFileInput();
        });

        // Editar estilo
        container.querySelector('#vector-creator-style-btn-sidebar').addEventListener('click', function () {
            if (self._selectedLayers.size === 0) {
                alert("Selecciona al menos una capa para editar su estilo.");
                return;
            }
            container.querySelector('#vector-creator-style-panel-sidebar').style.display = 'block';
            self._updateStylePanel(); // Usa el método existente, pero actualiza los elementos del sidebar
        });

        // --- BOTÓN GUARDAR: AÑADIMOS DEBUGGING ---
        const saveBtn = container.querySelector('#vector-creator-save-btn-sidebar');
        if (saveBtn) {
            saveBtn.addEventListener('click', function () {
                console.log("🔍 Botón 'Guardar seleccionadas' clicado.");
                console.log("🔍 Cantidad de capas seleccionadas (antes del if):", self._selectedLayers.size);
                console.log("🔍 Capas en _selectedLayers (antes del if):", Array.from(self._selectedLayers));
                if (self._selectedLayers.size === 0) {
                    console.log("⚠️ No hay capas seleccionadas. Mostrando alerta.");
                    alert("No hay capas seleccionadas.");
                    return;
                }
                console.log("✅ Hay capas seleccionadas. Verificando si _showMetadataModal existe...");
                if (typeof self._showMetadataModal === 'function') {
                    console.log("✅ _showMetadataModal es una función. Llamando...");
                    try {
                        self._showMetadataModal();
                        console.log("✅ _showMetadataModal llamada exitosamente.");
                    } catch (error) {
                        console.error("❌ Error al llamar a _showMetadataModal:", error);
                    }
                } else {
                    console.error("❌ _showMetadataModal NO es una función:", typeof self._showMetadataModal);
                }
            });
        } else {
            console.error("❌ Botón #vector-creator-save-btn-sidebar no encontrado en el contenedor.");
        }
        // ---

        // Eventos del panel de estilo (sidebar)
        container.querySelector('#vector-creator-stroke-weight-sidebar').addEventListener('input', function(e) {
            container.querySelector('#vector-creator-weight-value-sidebar').textContent = e.target.value;
            self._applyStyleToSelection();
        });
        container.querySelector('#vector-creator-fill-opacity-sidebar').addEventListener('input', function(e) {
            container.querySelector('#vector-creator-opacity-value-sidebar').textContent = e.target.value;
            self._applyStyleToSelection();
        });
        container.querySelector('#vector-creator-point-radius-sidebar').addEventListener('input', function(e) {
            container.querySelector('#vector-creator-radius-value-sidebar').textContent = e.target.value;
            self._applyStyleToSelection();
        });
        container.querySelector('#vector-creator-stroke-color-sidebar').addEventListener('input', function() {
            self._applyStyleToSelection();
        });
        container.querySelector('#vector-creator-fill-color-sidebar').addEventListener('input', function() {
            self._applyStyleToSelection();
        });
    },

    // --- LÓGICA DE DIBUJO Y EDICIÓN (interactúa con _map) ---

    // Método para activar la funcionalidad de dibujo en el mapa
    enableDrawing: function () {
        if (this._drawControl) {
            // Ya está activo, no hacer nada o manejar el caso
            console.warn("L.VectorCreator: Dibujo ya activo.");
            return;
        }

        const vertexIcon = L.divIcon({
            className: 'leaflet-div-icon leaflet-editing-icon',
            iconSize: new L.Point(8, 8),
            iconAnchor: new L.Point(4, 4),
            html: '<div style="width:8px;height:8px;background:#fff;border:2px solid #3388ff;border-radius:50%;"></div>'
        });

        this._drawControl = new L.Control.Draw({
            edit: {
                featureGroup: this._drawnItems,
                edit: true,
                remove: true,
                vertexIcon: vertexIcon
            },
            draw: {
                polyline: { shapeOptions: this.options.defaultPathOptions },
                polygon: { shapeOptions: { ...this.options.defaultPathOptions, fillOpacity: 0.2, fillColor: '#3388ff' } },
                rectangle: { shapeOptions: { ...this.options.defaultPathOptions, fillOpacity: 0.2, fillColor: '#3388ff' } },
                circle: { shapeOptions: { ...this.options.defaultPathOptions, fillOpacity: 0.2, fillColor: '#3388ff' } },
                marker: true,
                circlemarker: false
            }
        });

        this._map.addControl(this._drawControl); // <-- Añadir al mapa principal

        // Añadir eventos del mapa para dibujo y selección
        this._map.on('click', this._onMapClick, this);
        this._map.on(L.Draw.Event.CREATED, this._onCreated, this);
        this._map.on(L.Draw.Event.EDITED, this._onEdited, this);
        this._map.on(L.Draw.Event.DELETED, this._onDeleted, this);
    },

    // Método para desactivar la funcionalidad de dibujo en el mapa
    disableDrawing: function () {
        if (this._drawControl) {
            this._map.removeControl(this._drawControl); // <-- Remover del mapa principal
            this._drawControl = null;
        }

        // Remover eventos del mapa
        this._map.off('click', this._onMapClick, this);
        this._map.off(L.Draw.Event.CREATED, this._onCreated, this);
        this._map.off(L.Draw.Event.EDITED, this._onEdited, this);
        this._map.off(L.Draw.Event.DELETED, this._onDeleted, this);

        // Limpiar selección
        this._selectedLayers.forEach(l => this._removeHighlight(l));
        this._selectedLayers.clear();
        this._updateStatus(); // Actualizar el estado en el sidebar
    },

    _onCreated: function (e) {
        let layer = e.layer;
        if (e.layerType === 'marker') {
             const latlng = layer.getLatLng();
             this._map.removeLayer(layer); // Remover el marker original
             layer = L.circleMarker(latlng, this.options.defaultPointStyle);
        }
        this._drawnItems.addLayer(layer);
        layer.on('click', this._onLayerClick, this);
        this._updateDrawnLayersList(); // Actualizar la lista en el sidebar
    },

    _onEdited: function (e) {
        // Opcional: manejar edición
        this._updateDrawnLayersList(); // Actualizar la lista en el sidebar si cambia algo
    },

    _onDeleted: function (e) {
        // Opcional: manejar eliminación
        const layers = e.layers;
        layers.eachLayer(layer => {
            if (this._selectedLayers.has(layer)) {
                this._selectedLayers.delete(layer);
            }
            this._updateDrawnLayersList(); // Actualizar la lista en el sidebar
        });
        this._updateStatus(); // Actualizar el estado en el sidebar
    },

    _onLayerClick: function (e) {
        console.log("🔍 Capa clicada en el mapa.");
        L.DomEvent.stopPropagation(e);
        const layer = e.target;
        const wasSelected = this._selectedLayers.has(layer);
        const multiSelect = e.originalEvent.ctrlKey || e.originalEvent.metaKey;

        if (multiSelect) {
            if (wasSelected) {
                console.log("🔍 Deseleccionando capa (multi-select).");
                this._selectedLayers.delete(layer);
                this._removeHighlight(layer);
            } else {
                console.log("🔍 Seleccionando capa (multi-select).");
                this._selectedLayers.add(layer);
                this._applyHighlight(layer);
            }
        } else {
            console.log("🔍 Modo single-select.");
            this._selectedLayers.forEach(l => this._removeHighlight(l));
            this._selectedLayers.clear();
            if (wasSelected) {
                console.log("🔍 Deseleccionando capa (single-select).");
                this._removeHighlight(layer);
            } else {
                console.log("🔍 Seleccionando capa (single-select).");
                this._selectedLayers.add(layer);
                this._applyHighlight(layer);
            }
        }
        this._updateStatus(); // Actualizar el estado en el sidebar
    },

    _onMapClick: function () {
        console.log("🔍 Clic en el mapa fuera de una capa. Deseleccionando todas.");
        this._selectedLayers.forEach(l => this._removeHighlight(l));
        this._selectedLayers.clear();
        this._updateStatus(); // Actualizar el estado en el sidebar
    },

    _applyHighlight: function (layer) {
        if (!layer._savedStyle) {
            layer._savedStyle = {
                color: layer.options.color,
                weight: layer.options.weight,
                fillColor: layer.options.fillColor,
                fillOpacity: layer.options.fillOpacity,
                radius: layer.options.radius
            };
        }

        if (layer instanceof L.CircleMarker) {
            layer.setStyle({
                color: '#ff0000',
                fillColor: '#ffcccc'
            });
        } else {
            layer.setStyle(this._highlightStyle);
        }
    },

    _removeHighlight: function (layer) {
        if (layer._savedStyle) {
            const s = layer._savedStyle;
            const style = {};
            if (s.color !== undefined) style.color = s.color;
            if (s.weight !== undefined) style.weight = s.weight;
            if (s.fillColor !== undefined) style.fillColor = s.fillColor;
            if (s.fillOpacity !== undefined) style.fillOpacity = s.fillOpacity;
            if (s.radius !== undefined) style.radius = s.radius;
            layer.setStyle(style);
        }
    },

    _updateStatus: function () {
        const count = this._selectedLayers.size;
        // Actualizar el elemento en el sidebar, no en el contenedor del mapa
        const statusEl = this._uiContainer ? this._uiContainer.querySelector('#vector-creator-status-sidebar') : null;
        if (statusEl) {
            statusEl.textContent =
                count === 0 ? 'Ninguna capa seleccionada.' :
                count === 1 ? '1 capa seleccionada.' :
                `${count} capas seleccionadas.`;
        }

        if (count === 0 && this._uiContainer) {
            this._uiContainer.querySelector('#vector-creator-style-panel-sidebar').style.display = 'none';
        }
    },

    // Actualiza el panel de estilo en el sidebar con el estilo de la primera capa seleccionada
    _updateStylePanel: function () {
        if (!this._uiContainer) return; // No hay UI para actualizar

        const layers = Array.from(this._selectedLayers);
        if (layers.length === 0) return;

        const layer = layers[0];
        const opts = layer.options;

        let strokeColor = opts.color !== undefined ? opts.color : '#3388ff';
        let strokeWeight = opts.weight !== undefined ? opts.weight : 3;
        let fillColor = opts.fillColor !== undefined ? opts.fillColor : '#3388ff';
        let fillOpacity = opts.fillOpacity !== undefined ? opts.fillOpacity : (layer instanceof L.CircleMarker ? 0.8 : 0.2);
        let radius = opts.radius !== undefined ? opts.radius : 6;

        const isPoint = layer instanceof L.CircleMarker;
        this._uiContainer.querySelector('#vector-creator-radius-group-sidebar').style.display = isPoint ? 'block' : 'none';

        this._uiContainer.querySelector('#vector-creator-stroke-color-sidebar').value = strokeColor;
        this._uiContainer.querySelector('#vector-creator-stroke-weight-sidebar').value = strokeWeight;
        this._uiContainer.querySelector('#vector-creator-weight-value-sidebar').textContent = strokeWeight;
        this._uiContainer.querySelector('#vector-creator-fill-color-sidebar').value = fillColor;
        this._uiContainer.querySelector('#vector-creator-fill-opacity-sidebar').value = fillOpacity;
        this._uiContainer.querySelector('#vector-creator-opacity-value-sidebar').textContent = fillOpacity;

        if (isPoint) {
            this._uiContainer.querySelector('#vector-creator-point-radius-sidebar').value = radius;
            this._uiContainer.querySelector('#vector-creator-radius-value-sidebar').textContent = radius;
        }
    },

    _applyStyleToSelection: function () {
        const layers = Array.from(this._selectedLayers);
        if (layers.length === 0 || !this._uiContainer) return; // Asegurar UI

        const strokeColor = this._uiContainer.querySelector('#vector-creator-stroke-color-sidebar').value;
        const strokeWeight = parseInt(this._uiContainer.querySelector('#vector-creator-stroke-weight-sidebar').value);
        const fillColor = this._uiContainer.querySelector('#vector-creator-fill-color-sidebar').value;
        const fillOpacity = parseFloat(this._uiContainer.querySelector('#vector-creator-fill-opacity-sidebar').value);
        const radius = parseInt(this._uiContainer.querySelector('#vector-creator-point-radius-sidebar').value);

        layers.forEach(layer => {
            if (layer instanceof L.CircleMarker) {
                layer.setStyle({
                    color: strokeColor,
                    weight: strokeWeight,
                    fillColor: fillColor,
                    fillOpacity: fillOpacity,
                    radius: radius
                });
            } else if (layer instanceof L.Polyline || layer instanceof L.Polygon || layer instanceof L.Rectangle || layer instanceof L.Circle) {
                layer.setStyle({
                    color: strokeColor,
                    weight: strokeWeight,
                    fillColor: fillColor,
                    fillOpacity: fillOpacity
                });
            }

            layer._savedStyle = {
                color: strokeColor,
                weight: strokeWeight,
                fillColor: fillColor,
                fillOpacity: fillOpacity,
                radius: radius
            };
        });
    },

    _showFileInput: function () {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.geojson,.json';
        input.style.display = 'none';
        document.body.appendChild(input);
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const geojson = JSON.parse(e.target.result);
                    this._loadGeoJSON(geojson);
                    alert("GeoJSON cargado exitosamente.");
                } catch (err) {
                    alert("Error al leer el archivo GeoJSON: " + err.message);
                }
            };
            reader.readAsText(file);
            document.body.removeChild(input);
        });
        input.click();
    },

    _loadGeoJSON: function (geojson) {
        const self = this;
        L.geoJSON(geojson, {
            pointToLayer: function (feature, latlng) {
                const style = feature.properties?.style || {};
                return L.circleMarker(latlng, {
                    radius: style.radius || self.options.defaultPointStyle.radius,
                    fillColor: style.fillColor || self.options.defaultPointStyle.fillColor,
                    color: style.color || self.options.defaultPointStyle.color,
                    weight: style.weight || self.options.defaultPointStyle.weight,
                    fillOpacity: style.fillOpacity !== undefined ? style.fillOpacity : self.options.defaultPointStyle.fillOpacity
                });
            },
            style: function (feature) {
                const style = feature.properties?.style || {};
                return {
                    color: style.color || self.options.defaultPathOptions.color,
                    weight: style.weight || self.options.defaultPathOptions.weight,
                    fillColor: style.fillColor || self.options.defaultPathOptions.color,
                    fillOpacity: style.fillOpacity !== undefined ? style.fillOpacity : 0.2
                };
            },
            onEachFeature: function (feature, layer) {
                self._drawnItems.addLayer(layer);
                layer.on('click', self._onLayerClick, self);
            }
        }).addTo(this._map);

        if (this._drawnItems.getBounds().isValid()) {
            this._map.fitBounds(this._drawnItems.getBounds());
        }
        this._updateDrawnLayersList(); // Actualizar la lista en el sidebar
    },

    // Actualiza la lista de capas dibujadas en el sidebar
    _updateDrawnLayersList: function () {
        if (!this._uiContainer) return; // No hay UI para actualizar

        const listEl = this._uiContainer.querySelector('#vector-creator-drawn-list-sidebar');
        if (!listEl) return;

        listEl.innerHTML = ''; // Limpiar la lista

        this._drawnItems.eachLayer(layer => {
            const li = L.DomUtil.create('li', '', listEl);
            // Asignar un ID temporal si no tiene uno, o usar una representación simple
            li.textContent = `${layer.feature ? layer.feature.properties?.name || 'Capa sin nombre' : 'Capa'} (${layer instanceof L.CircleMarker ? 'Punto' : 'Forma'})`;
            // Opcional: Añadir eventos para seleccionar la capa en el mapa al hacer clic en la lista
            li.style.cursor = 'pointer';
            li.addEventListener('click', () => {
                this._map.fitBounds(layer.getBounds ? layer.getBounds() : L.latLngBounds([layer.getLatLng()])); // Centrar en la capa
                // Opcional: Deseleccionar otras y seleccionar esta
                this._selectedLayers.forEach(l => this._removeHighlight(l));
                this._selectedLayers.clear();
                this._selectedLayers.add(layer);
                this._applyHighlight(layer);
                this._updateStatus();
            });
        });
    },


    _showMetadataModal: function () {
        console.log("🔍 [DEBUG] _showMetadataModal llamada.");
        console.log("🔍 [DEBUG] this._selectedLayers.size:", this._selectedLayers.size);
        console.log("🔍 [DEBUG] this._selectedLayers:", Array.from(this._selectedLayers));

        // Crear el modal
        console.log("🔍 [DEBUG] Creando elemento DOM del modal...");
        const modal = document.createElement('div');
        modal.id = 'vector-creator-metadata-modal';
        modal.innerHTML = `
            <div class="vector-creator-modal-content">
                <h3>Editar metadatos de la capa</h3>
                <label for="vector-creator-layer-title">Título de la capa:</label>
                <input type="text" id="vector-creator-layer-title" placeholder="Ej: Zonas de riesgo" value="Capa dibujada">
                <label for="vector-creator-layer-crs">Sistema de coordenadas (CRS):</label>
                <input type="text" id="vector-creator-layer-crs" placeholder="Ej: EPSG:4326" value="EPSG:4326">
                <div class="vector-creator-modal-buttons">
                    <button id="vector-creator-cancel-btn">Cancelar</button>
                    <button id="vector-creator-confirm-btn">Descargar GeoJSON</button>
                </div>
            </div>
        `;

        console.log("🔍 [DEBUG] Añadiendo modal al body...");
        document.body.appendChild(modal);

        // Asignar evento al botón de cancelar
        console.log("🔍 [DEBUG] Asignando evento a botón de cancelar...");
        document.getElementById('vector-creator-cancel-btn').addEventListener('click', function () {
            console.log("🔍 [DEBUG] Botón cancelar clicado.");
            document.body.removeChild(modal);
        });

        // Asignar evento al botón de confirmar
        console.log("🔍 [DEBUG] Asignando evento a botón de confirmar...");
        const confirmBtn = document.getElementById('vector-creator-confirm-btn');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                console.log("🔍 [DEBUG] Evento de click del botón confirmar disparado.");
                console.log("🔍 [DEBUG] this._selectedLayers.size en confirmar (antes de descargar):", this._selectedLayers.size);
                console.log("🔍 [DEBUG] Contexto de 'this' en confirmar:", this); // <-- Verificar contexto
                const title = document.getElementById('vector-creator-layer-title').value.trim() || 'Capa dibujada';
                const crs = document.getElementById('vector-creator-layer-crs').value.trim() || 'EPSG:4326';
                console.log("🔍 [DEBUG] Llamando a _downloadGeoJSONWithMetadata con title:", title, "y crs:", crs);
                this._downloadGeoJSONWithMetadata(title, crs); // <-- Esta línea depende del 'this' correcto
                console.log("🔍 [DEBUG] Removiendo modal del body...");
                document.body.removeChild(modal);
            });
        } else {
            console.error("❌ [DEBUG] Botón #vector-creator-confirm-btn no encontrado en el modal.");
        }

        // Asignar evento para cerrar al hacer clic fuera
        console.log("🔍 [DEBUG] Asignando evento para cerrar al hacer clic fuera...");
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                console.log("🔍 [DEBUG] Clic fuera del modal, removiendo...");
                document.body.removeChild(modal);
            }
        });

        console.log("🔍 [DEBUG] Modal creado y eventos asignados. Debería ser visible ahora.");
    },

    _downloadGeoJSONWithMetadata: function (title, crs) { // <-- Corregido nombre de la función
        console.log("🔍 [DEBUG] _downloadGeoJSONWithMetadata llamada.");
        console.log("🔍 [DEBUG] Título recibido:", title);
        console.log("🔍 [DEBUG] CRS recibido:", crs);
        console.log("🔍 [DEBUG] this._selectedLayers.size:", this._selectedLayers.size);

        // Verificar si hay capas para exportar
        if (this._selectedLayers.size === 0) {
            console.warn("⚠️ [DEBUG] No hay capas en _selectedLayers para exportar.");
            alert("No hay capas seleccionadas para exportar.");
            return;
        }

        const features = Array.from(this._selectedLayers).map(layer => {
            console.log("🔍 [DEBUG] Convirtiendo capa a GeoJSON:", layer);
            const feat = layer.toGeoJSON();
            if (!feat.properties) feat.properties = {};

            const opts = layer.options;
            feat.properties.style = {
                color: opts.color,
                weight: opts.weight,
                fillColor: opts.fillColor,
                fillOpacity: opts.fillOpacity,
                radius: opts.radius
            };

            feat.properties._layer_title = title;
            feat.properties._crs = crs;
            return feat;
        });

        const geojson = {
            type: "FeatureCollection",
            name: title,
            features: features,
            meta: {
                title: title,
                crs: crs,
                exported_at: new Date().toISOString()
            }
        };

        if (crs !== "EPSG:4326") {
            features.forEach(f => {
                f.properties._warning = "GeoJSON debe estar en EPSG:4326. Este CRS es solo metadato.";
            });
        }

        const dataStr = JSON.stringify(geojson, null, 2);
        console.log("🔍 [DEBUG] String de GeoJSON generado (longitud):", dataStr.length);

        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        console.log("🔍 [DEBUG] Blob creado.");

        const url = URL.createObjectURL(dataBlob);
        console.log("🔍 [DEBUG] URL del Blob creada:", url);

        const link = document.createElement('a');
        link.href = url;
        link.download = (title || 'capas') + '.geojson';
        console.log("🔍 [DEBUG] Link creado con href:", link.href, "y download:", link.download);

        document.body.appendChild(link);
        console.log("🔍 [DEBUG] Link añadido al body, ahora se hace click.");
        link.click();

        console.log("🔍 [DEBUG] Click simulado en el link. Removiendo link...");
        document.body.removeChild(link);

        console.log("🔍 [DEBUG] Revocando URL del Blob...");
        URL.revokeObjectURL(url);

        console.log("✅ [DEBUG] Descarga completada.");
    },

    _expand: function () {
        // No se usa si no hay toggle en el mapa
        return this;
    },

    _collapse: function () {
        // No se usa si no hay toggle en el mapa
        return this;
    }
});

// --- DEFINICIÓN DEL FACTORY FUNCTION ---
// Como el UMD wrapper ha sido eliminado, definimos L.vectorCreator directamente
// en el ámbito global, asumiendo que L ya está disponible.
if (typeof L !== 'undefined' && L.Class && L.VectorCreator) { // Cambiado L.Control por L.Class
    L.vectorCreator = function (map, options) { // Ahora se pasa el mapa aquí
        return new L.VectorCreator(map, options);
    };
    console.log("✅ L.vectorCreator ha sido definido correctamente (como L.Class).");
} else {
    console.error("❌ L.vectorCreator NO se pudo definir (como L.Class). Verifique que L.VectorCreator existe.");
}
