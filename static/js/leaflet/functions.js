function toggleLayer(layerName, map) {
    if (map.hasLayer(layerName)) {
        map.removeLayer(layerName);
    }
    else {
        map.addLayer(layerName);
    }
}
