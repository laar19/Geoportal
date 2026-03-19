// herramientas-tools.js
// Adapted tools controller for geoportal main project
// Works with the existing map instance from static/js/leaflet/map.js

// Variables globales
let measureAction = null;
let coordsControl = null;
let coordsEventBound = false;
let coordsActive = false;

let drawingActive = false;
let drawMode = 'move';
let currentLine = null;
let drawnLayerGroup = null;
let tempLayer = null;
let drawnHistory = [];
let colorPicker = '#ff0000';
let weightValue = 3;

// Variables para la herramienta de vectorización
let vectorCreatorInstance = null;
window.vectorToolActive = false;

// Configure L.Measure locale for Spanish
function configureMeasureLocale() {
    L.Measure = {
        linearMeasurement: "Medición de distancia",
        areaMeasurement: "Medición de área",
        start: "Iniciar",
        meter: "m",
        meterDecimals: 0,
        kilometer: "km",
        kilometerDecimals: 2,
        squareMeter: "m²",
        squareMeterDecimals: 0,
        squareKilometers: "km²",
        squareKilometersDecimals: 2
    };
}

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function () {
    // The map is initialized in static/js/leaflet/map.js as a global variable
    // Wait a bit to ensure map is ready
    setTimeout(function () {
        if (typeof map !== 'undefined') {
            window.map = map;
            configureMeasureLocale();
            initHerramientasButtons();
            console.log("✅ Herramientas tools initialized.");
        } else {
            console.error("❌ Map not found for herramientas tools.");
        }
    }, 500);
});

// Initialize button event listeners
function initHerramientasButtons() {
    const btnMedirDistancia = document.getElementById('btn-medir-distancia');
    const btnMedirArea = document.getElementById('btn-medir-area');
    const btnCoordenadas = document.getElementById('btn-coordenadas');
    const btnDibujoLibre = document.getElementById('btn-dibujo-libre');
    const btnVectorizacion = document.getElementById('btn-vectorizacion');

    if (btnMedirDistancia) {
        btnMedirDistancia.addEventListener('click', function () {
            window.initMeasureDistance();
        });
    }

    if (btnMedirArea) {
        btnMedirArea.addEventListener('click', function () {
            window.initMeasureArea();
        });
    }

    if (btnCoordenadas) {
        btnCoordenadas.addEventListener('click', function () {
            if (btnCoordenadas.textContent.includes('Mostrar')) {
                window.initCoordinates();
                btnCoordenadas.innerHTML = '<i class="fa-solid fa-xmark"></i> Ocultar Coordenadas';
                btnCoordenadas.classList.add('active');
            } else {
                window.disableCoordinates();
                btnCoordenadas.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i> Mostrar Coordenadas';
                btnCoordenadas.classList.remove('active');
            }
        });
    }

    if (btnDibujoLibre) {
        btnDibujoLibre.addEventListener('click', function () {
            window.initDrawingTools();
        });
    }

    if (btnVectorizacion) {
        btnVectorizacion.addEventListener('click', function () {
            window.initVectorTool();
        });
    }
}

// Measure Distance Tool
window.initMeasureDistance = function () {
    if (typeof L === 'undefined' || typeof window.map === 'undefined') {
        console.error('❌ Leaflet o el mapa no están inicializados.');
        return;
    }

    configureMeasureLocale();
    disableAllTools();
    if (measureAction) {
        if (measureAction._measurementStarted) measureAction._finishMeasure();
        measureAction.disable();
        measureAction = null;
    }
    measureAction = new L.MeasureAction(window.map, { model: "distance", color: '#FF0080' });
    measureAction.enable();
};

// Measure Area Tool
window.initMeasureArea = function () {
    if (typeof L === 'undefined' || typeof window.map === 'undefined') {
        console.error('❌ Leaflet o el mapa no están inicializados.');
        return;
    }

    disableAllTools();
    if (measureAction) {
        if (measureAction._measurementStarted) measureAction._finishMeasure();
        measureAction.disable();
        measureAction = null;
    }
    measureAction = new L.MeasureAction(window.map, { model: "area", color: '#FF0080' });
    measureAction.enable();
};

// Coordinates Tool
window.initCoordinates = function () {
    if (typeof L === 'undefined' || typeof window.map === 'undefined') {
        console.error('❌ Leaflet o el mapa no están inicializados.');
        return;
    }

    disableAllTools();
    if (!coordsControl) {
        var customCoordinateOptions = {
            position: 'bottomleft',
            latitudeText: 'lat.',
            longitudeText: 'lon.',
            promptText: 'Presiona Ctrl+C para copiar las coordenadas',
            precision: 4
        };
        coordsControl = new L.Control.Coordinates(customCoordinateOptions).addTo(window.map);
    }
    L.DomUtil.removeClass(coordsControl._container, 'hidden');
    coordsControl.active = true;

    if (!coordsEventBound) {
        window.map.on('click', function (e) { coordsControl.setCoordinates(e); });
    }
    coordsEventBound = true;

    window.map.getContainer().style.cursor = 'crosshair';
    coordsActive = true;
};

window.disableCoordinates = function () {
    if (coordsControl) {
        L.DomUtil.addClass(coordsControl._container, 'hidden');
        coordsControl.active = false;
        if (coordsEventBound) {
            window.map.off('click', coordsControl.setCoordinates, coordsControl);
            coordsEventBound = false;
        }
        window.map.getContainer().style.cursor = '';
        coordsActive = false;
        if (coordsControl._marker) {
            window.map.removeLayer(coordsControl._marker);
            coordsControl._marker = null;
        }
    }
};

// Drawing Tools
window.initDrawingTools = function () {
    if (typeof L === 'undefined' || typeof window.map === 'undefined') {
        console.error('❌ Leaflet o el mapa no están inicializados.');
        return;
    }

    if (drawingActive) return;

    // Create layers if they don't exist
    if (!drawnLayerGroup) {
        drawnLayerGroup = L.layerGroup().addTo(window.map);
        tempLayer = L.layerGroup().addTo(window.map);
        drawnHistory = [];
    }

    // Render controls in the herramientas container
    const toolsPanel = document.getElementById('herramientas-controls');
    if (!toolsPanel) {
        console.error('❌ No se encontró el contenedor de herramientas.');
        return;
    }

    // Avoid duplicates
    if (document.getElementById('drawing-controls')) {
        document.getElementById('drawing-controls').remove();
    }

    const controlsHTML = `
    <div id="drawing-controls" class="herramientas-panel">
      <h5>✏️ Dibujo Libre</h5>
      <div class="control-group">
        <button id="toggleDrawModeBtn" class="btn-herramienta btn-primary">Modo: Dibujar</button>
      </div>
      <div class="control-group">
        <label for="drawColor">Color</label>
        <input type="color" id="drawColor" value="${colorPicker}">
      </div>
      <div class="control-group">
        <label for="drawWeight">Grosor: <span id="drawWeightValue">${weightValue}</span>px</label>
        <input type="range" id="drawWeight" min="1" max="10" value="${weightValue}">
      </div>
      <div class="control-group">
        <button id="toggleEraseModeBtn" class="btn-herramienta btn-erase">Modo: Borrar</button>
      </div>
      <div class="control-group buttons-row">
        <button id="undoDrawBtn" class="btn-herramienta btn-secondary">Deshacer</button>
        <button id="clearDrawBtn" class="btn-herramienta btn-danger">Limpiar todo</button>
      </div>
      <div class="control-group">
        <button id="closeDrawingBtn" class="btn-herramienta btn-close-tool">Cerrar</button>
      </div>
    </div>
  `;

    toolsPanel.innerHTML = controlsHTML;

    // Assign references
    const toggleDrawBtn = document.getElementById('toggleDrawModeBtn');
    const toggleEraseBtn = document.getElementById('toggleEraseModeBtn');
    const clearBtn = document.getElementById('clearDrawBtn');
    const undoBtn = document.getElementById('undoDrawBtn');
    const colorInput = document.getElementById('drawColor');
    const weightSlider = document.getElementById('drawWeight');
    const weightValueSpan = document.getElementById('drawWeightValue');
    const closeBtn = document.getElementById('closeDrawingBtn');

    // Events
    weightSlider.addEventListener('input', () => {
        weightValue = parseInt(weightSlider.value);
        weightValueSpan.textContent = weightValue;
    });

    colorInput.addEventListener('input', () => {
        colorPicker = colorInput.value;
    });

    toggleDrawBtn.addEventListener('click', () => {
        if (drawMode === 'draw') {
            setDrawMode('move');
        } else {
            setDrawMode('draw');
        }
    });

    toggleEraseBtn.addEventListener('click', () => {
        if (drawMode === 'erase') {
            setDrawMode('move');
        } else {
            setDrawMode('erase');
        }
    });

    clearBtn.addEventListener('click', () => {
        drawnLayerGroup.clearLayers();
        tempLayer.clearLayers();
        drawnHistory = [];
        currentLine = null;
        updateDrawButtons();
    });

    undoBtn.addEventListener('click', () => {
        if (drawnHistory.length > 0) {
            const last = drawnHistory.pop();
            drawnLayerGroup.removeLayer(last);
        }
    });

    closeBtn.addEventListener('click', () => {
        disableDrawingTools();
    });

    // Activate map events
    window.map.on('mousedown', handleDrawMouseDown);
    window.map.on('mousemove', handleDrawMouseMove);
    window.map.on('mouseup', handleDrawMouseUp);
    window.map.on('mouseout', handleDrawMouseOut);

    drawingActive = true;
    setDrawMode('draw');
};

function setDrawMode(mode) {
    if (currentLine && drawMode === 'draw') {
        finalizeCurrentLine();
    }

    drawMode = mode;

    if (mode === 'move') {
        window.map.dragging.enable();
        window.map.touchZoom.enable();
        window.map.doubleClickZoom.enable();
        window.map.scrollWheelZoom.enable();
        window.map.getContainer().style.cursor = 'grab';
    } else {
        window.map.dragging.disable();
        window.map.touchZoom.disable();
        window.map.doubleClickZoom.disable();
        window.map.scrollWheelZoom.disable();
        if (mode === 'draw') {
            window.map.getContainer().style.cursor = 'crosshair';
        } else if (mode === 'erase') {
            window.map.getContainer().style.cursor = 'pointer';
        }
    }

    updateDrawButtons();
}

function updateDrawButtons() {
    const drawBtn = document.getElementById('toggleDrawModeBtn');
    const eraseBtn = document.getElementById('toggleEraseModeBtn');

    if (drawBtn) {
        drawBtn.className = drawMode === 'draw' ? 'btn-herramienta btn-secondary' : 'btn-herramienta btn-primary';
        drawBtn.textContent = drawMode === 'draw' ? 'Modo: Dibujar (activo)' : 'Modo: Dibujar';
    }

    if (eraseBtn) {
        eraseBtn.className = drawMode === 'erase' ? 'btn-herramienta btn-erase active' : 'btn-herramienta btn-erase';
        eraseBtn.textContent = drawMode === 'erase' ? 'Modo: Borrar (activo)' : 'Modo: Borrar';
    }
}

function finalizeCurrentLine() {
    if (currentLine) {
        tempLayer.clearLayers();
        drawnLayerGroup.addLayer(currentLine);
        drawnHistory.push(currentLine);
        currentLine = null;
    }
}

function handleDrawMouseDown(e) {
    if (drawMode === 'draw') {
        currentLine = L.polyline([e.latlng], {
            color: colorPicker,
            weight: weightValue,
            smoothFactor: 1
        });
        tempLayer.addLayer(currentLine);
    } else if (drawMode === 'erase') {
        const layers = drawnLayerGroup.getLayers();
        const point = window.map.latLngToContainerPoint(e.latlng);
        const tolerance = 10;

        for (const layer of layers) {
            if (!(layer instanceof L.Polyline)) continue;
            const latlngs = layer.getLatLngs();
            if (latlngs.length < 2) continue;

            for (let i = 0; i < latlngs.length - 1; i++) {
                const p1 = window.map.latLngToContainerPoint(latlngs[i]);
                const p2 = window.map.latLngToContainerPoint(latlngs[i + 1]);
                const dist = distanceToSegment(point, p1, p2);
                if (dist <= tolerance) {
                    drawnLayerGroup.removeLayer(layer);
                    const idx = drawnHistory.indexOf(layer);
                    if (idx !== -1) drawnHistory.splice(idx, 1);
                    return;
                }
            }
        }
    }
}

function handleDrawMouseMove(e) {
    if (drawMode === 'draw' && currentLine) {
        const latlngs = currentLine.getLatLngs();
        latlngs.push(e.latlng);
        currentLine.setLatLngs(latlngs);
    }
}

function handleDrawMouseUp() {
    if (drawMode === 'draw' && currentLine) {
        finalizeCurrentLine();
    }
}

function handleDrawMouseOut() {
    if (drawMode === 'draw' && currentLine) {
        finalizeCurrentLine();
    }
}

function distanceToSegment(p, v, w) {
    const l2 = (v.x - w.x) ** 2 + (v.y - w.y) ** 2;
    if (l2 === 0) return Math.hypot(p.x - v.x, p.y - v.y);
    let t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)) / l2;
    t = Math.max(0, Math.min(1, t));
    const proj = { x: v.x + t * (w.x - v.x), y: v.y + t * (w.y - v.y) };
    return Math.hypot(p.x - proj.x, p.y - proj.y);
}

function disableDrawingTools() {
    if (!drawingActive) return;

    if (currentLine && drawMode === 'draw') {
        finalizeCurrentLine();
    }

    window.map.off('mousedown', handleDrawMouseDown);
    window.map.off('mousemove', handleDrawMouseMove);
    window.map.off('mouseup', handleDrawMouseUp);
    window.map.off('mouseout', handleDrawMouseOut);

    window.map.dragging.enable();
    window.map.touchZoom.enable();
    window.map.doubleClickZoom.enable();
    window.map.scrollWheelZoom.enable();
    window.map.getContainer().style.cursor = '';

    const controls = document.getElementById('drawing-controls');
    if (controls) controls.remove();

    drawingActive = false;
    drawMode = 'move';
}

window.disableDrawingTools = disableDrawingTools;


window.initVectorTool = function () {
    if (typeof L === 'undefined' || typeof window.map === 'undefined') {
        console.error('❌ initVectorTool: Leaflet o map no definidos.');
        return;
    }

    // A. Lógica de Toggle: Si ya está activa, la desactivamos.
    if (window.vectorToolActive) {
        disableVectorTool();
        return;
    }

    // B. Desactivar OTRAS herramientas manualmente para limpiar el mapa
    disableMeasureTool();
    disableCoordinates();
    disableDrawingTools();

    // Limpiar panel de controles (UI)
    const controlsPanel = document.getElementById('herramientas-controls');
    if (controlsPanel) {
        controlsPanel.innerHTML = '';
    }

    // C. PATRÓN SINGLETON (La clave para que NO desaparezcan los vectores)
    // Si la instancia NO existe, la creamos. Si YA existe, la reutilizamos.
    if (!vectorCreatorInstance) {
        console.log("🛠️ Creando NUEVA instancia de VectorCreator (Primer uso)");
        vectorCreatorInstance = L.vectorCreator(window.map, {
            title: 'Vectorización'
        });

        // Aseguramos que el grupo de capas esté añadido al mapa
        if (vectorCreatorInstance._drawnItems) {
            window.map.addLayer(vectorCreatorInstance._drawnItems);
        }
    } else {
        console.log("♻️ Reutilizando instancia existente (Recuperando vectores previos)");
        // Si por alguna razón el grupo se quitó del mapa, lo volvemos a poner
        if (vectorCreatorInstance._drawnItems && !window.map.hasLayer(vectorCreatorInstance._drawnItems)) {
            window.map.addLayer(vectorCreatorInstance._drawnItems);
        }
    }

    // D. Recrear o recuperar la UI
    // Nota: Aunque la instancia lógica existe, el HTML del panel se limpió en el paso B,
    // así que pedimos a la instancia que nos devuelva su interfaz.
    const uiElement = vectorCreatorInstance.createUI();

    if (controlsPanel) {
        const wrapper = document.createElement('div');
        wrapper.id = 'vector-tool-wrapper';
        wrapper.className = 'herramientas-panel';

        const closeBtn = document.createElement('button');
        closeBtn.className = 'btn-herramienta btn-close-tool';
        closeBtn.textContent = 'Cerrar Vectorización';
        closeBtn.addEventListener('click', function () {
            disableVectorTool();
        });

        wrapper.appendChild(uiElement);
        wrapper.appendChild(closeBtn);
        controlsPanel.appendChild(wrapper);
    }

    // E. Activar dibujo en el mapa
    vectorCreatorInstance.enableDrawing();
    window.vectorToolActive = true;
};


window.disableVectorTool = function () {
    if (vectorCreatorInstance) {
        // Solo pausamos el dibujo.
        // ¡IMPORTANTE! NO hacemos vectorCreatorInstance = null
        // Al mantener la variable viva, los polígonos (this._drawnItems) no se pierden.
        vectorCreatorInstance.disableDrawing();
    }

    // Quitamos la UI del sidebar
    const wrapper = document.getElementById('vector-tool-wrapper');
    if (wrapper) wrapper.remove();

    // Marcamos como inactiva para el sistema de toggle
    window.vectorToolActive = false;
};

window.disableMeasureTool = function () {
    if (measureAction) {
        if (measureAction._measurementStarted) measureAction._finishMeasure();
        measureAction.disable();
        measureAction = null;
    }
};

function disableAllTools() {
    disableMeasureTool();
    disableCoordinates();
    disableDrawingTools();
    disableVectorTool();

    // Reset button states
    const btnCoordenadas = document.getElementById('btn-coordenadas');
    if (btnCoordenadas) {
        btnCoordenadas.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i> Mostrar Coordenadas';
        btnCoordenadas.classList.remove('active');
    }

    // Clear controls panel
    const controlsPanel = document.getElementById('herramientas-controls');
    if (controlsPanel) {
        controlsPanel.innerHTML = '';
    }
}

window.disableAllTools = disableAllTools;
