function toggleLayer(layerName, map, tr_id) {
    if (map.hasLayer(layerName)) {
        map.removeLayer(layerName);
        $("#"+tr_id).css("background-color", "white");
    }
    else {
        map.addLayer(layerName);
        $("#"+tr_id).css("background-color", "antiquewhite");
    }
}
