var mostrar = L.layerGroup();

for(var i=0; i<coordenadas.length; i++){
    L.marker([coordenadas[i].latitud,
    coordenadas[i].longitud]).bindPopup(coordenadas[i].nombre + "<br>" + coordenadas[i].region + "<br>Latitud: " + coordenadas[i].latitud + "<br>Longitud: " + coordenadas[i].longitud).addTo(mostrar)
}

mbUrl = 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw';

var streets = L.tileLayer(mbUrl, {id: "mapbox/streets-v11", tileSize: 512, zoomOffset: -1});

var map = L.map("mapa", {
    center: [7.319, -65.962],
    zoom: 5,
    layers: [streets, mostrar]
});

var baseLayers = {
};

var overlays = {
    "Mostrar torres": mostrar
};

L.control.layers(baseLayers, overlays).addTo(map);