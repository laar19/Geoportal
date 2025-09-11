var mapOpts = {};
if (typeof window.LEAFLET_MIN_ZOOM !== 'undefined' && window.LEAFLET_MIN_ZOOM !== null && window.LEAFLET_MIN_ZOOM !== '') {
    const mz = parseInt(window.LEAFLET_MIN_ZOOM, 10);
    if (!isNaN(mz)) mapOpts.minZoom = mz;
}
var map = L.map('map', mapOpts);
// --- Base layers (compact set similar to LandViewer) ---
const baseOSM = L.tileLayer(window.LEAFLET_TILE_URL, {
    attribution: window.LEAFLET_ATTRIBUTION
});

const baseEsri = L.tileLayer(window.LEAFLET_ESRI_URL, {
    attribution: window.LEAFLET_ESRI_ATTRIBUTION
});

const baseTerrain = L.tileLayer(window.LEAFLET_TERRAIN_URL, {
    attribution: window.LEAFLET_TERRAIN_ATTRIBUTION
});

const baseDark = L.tileLayer(window.LEAFLET_DARK_URL, {
    subdomains: window.LEAFLET_DARK_SUBDOMAINS,
    attribution: window.LEAFLET_DARK_ATTRIBUTION
});

// Add default base layer
baseOSM.addTo(map);

// If there was an image search, set the las user view at the moment
// of the search
if(map_config["search_status"]) {
    map.setView(
        map_config["center"].split(","),
        map_config["zoom_level"]
    );
}
else {
    map.setView(
        map_config["center"],
        map_config["zoom_level"]
    );
}

// --- Scale control ---
L.control.scale({ position: 'bottomleft', metric: true, imperial: false }).addTo(map);

// --- Basemap switcher (Layer Control) at bottom-right (above coords) ---
const baseLayers = {
    'OSM': baseOSM,
    'Satellite (Esri)': baseEsri,
    'Terrain': baseTerrain,
    'Dark': baseDark
};
L.control.layers(baseLayers, {}, { collapsed: true, position: 'bottomright' }).addTo(map);

// --- Mouse coordinates control (bottom-right, below basemap menu) ---
const MousePos = L.Control.extend({
    options: { position: 'bottomright' },
    onAdd: function() {
        const div = L.DomUtil.create('div', 'leaflet-control-mouseposition');
        div.innerHTML = 'Lat, Lon';
        this._div = div;
        return div;
    }
});
const mousePosCtl = new MousePos();
mousePosCtl.addTo(map);
map.on('mousemove', function(e){
    const lat = e.latlng.lat.toFixed(5);
    const lng = e.latlng.lng.toFixed(5);
    if (mousePosCtl && mousePosCtl._div) mousePosCtl._div.innerHTML = `${lat}, ${lng}`;
});

// (Removed opacity slider as requested)

// --- If AOI coordinates exist (from last search), draw and fit ---
try {
    if (map_config && map_config.coordinates) {
        const coordsStr = map_config.coordinates;
        if (Array.isArray(coordsStr) && coordsStr.length >= 3) {
            // Already array of [lat,lng]
            const latlngs = coordsStr.map(c => L.latLng(parseFloat(c[0]), parseFloat(c[1])));
            const poly = L.polygon(latlngs, { color: '#1e90ff', weight: 2, fillOpacity: 0.05 });
            poly.addTo(map);
            map.fitBounds(poly.getBounds(), { padding: [20,20] });
        } else if (typeof coordsStr === 'string' && coordsStr.includes(',')) {
            const parts = coordsStr.split(',');
            if (parts.length >= 6) { // at least 3 pairs
                const pairs = [];
                for (let i=0; i<parts.length-1; i+=2) {
                    const a = parseFloat(parts[i]);
                    const b = parseFloat(parts[i+1]);
                    if (!isNaN(a) && !isNaN(b)) pairs.push([a,b]);
                }
                if (pairs.length >= 3) {
                    const latlngs = pairs.map(p => L.latLng(p[0], p[1]));
                    const poly = L.polygon(latlngs, { color: '#1e90ff', weight: 2, fillOpacity: 0.05 });
                    poly.addTo(map);
                    map.fitBounds(poly.getBounds(), { padding: [20,20] });
                }
            }
        }
    }
} catch(e) {
    console.warn('AOI fit failed:', e);
}
