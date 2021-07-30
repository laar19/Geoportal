// Show coordinate points on the map
function display_layer(data, map) {
    var vectorSource = new ol.source.Vector({
        features: new ol.format.GeoJSON().readFeatures(data)
    });

    vectorSource.addFeature(new ol.Feature(new ol.geom.Circle([5e6, 7e6], 1e6)));

    var vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        style : styleFunction
    });

    map.addLayer(vectorLayer);
}

function displayBase64Image(placeholder, base64Image) {
    var image = document.createElement("img");
    image.onload = function() {
        placeholder.innerHTML = '';
        placeholder.appendChild(this);
    }
    image.src = base64Image;
}
