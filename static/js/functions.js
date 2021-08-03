// Show coordinate points on the map
function display_layer(data, mapDiv) {
    var vectorSource = new ol.source.Vector({
        features: new ol.format.GeoJSON().readFeatures(data)
    });

    vectorSource.addFeature(new ol.Feature(new ol.geom.Circle([5e6, 7e6], 1e6)));

    var vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        style : styleFunction
    });

    mapDiv.addLayer(vectorLayer);
}

// Show base 64 image on the map
function display_base64_image(base64_image, extent, mapDiv) {
    image = new ol.layer.Image({
        source: new ol.source.ImageStatic({
            imageLoadFunction : function(img){
                img.getImage().src = base64_image.src;
            },
            projection: "EPSG:4326",
            //size : [150, 150], // 150x150px
            imageExtent: extent
        })
    });

    mapDiv.addLayer(image);
}

// Show base 64 image on div
function display_base64_image_div(div, base64_image) {
    var image = document.createElement("img");
    image.onload = function() {
        div.innerHTML = "";
        div.appendChild(this);
    }
    image.src = base64_image;
}
