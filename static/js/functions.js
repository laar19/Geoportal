// Show coordinate points on the map
function display_layer(data, title, mapDiv) {
    var vectorSource = new ol.source.Vector({
        features: new ol.format.GeoJSON().readFeatures(data)
    });

    vectorSource.addFeature(new ol.Feature(new ol.geom.Circle([5e6, 7e6], 1e6)));

    var vectorLayer = new ol.layer.Vector({
        title : title,
        source: vectorSource,
        style : styleFunction
    });

    //mapDiv.addLayer(vectorLayer);
    return vectorLayer;
}

// Show base 64 image on the map
function display_base64_image_onmap(base64_image, extent, mapDiv, proj) {
    image = new ol.layer.Image({
        source: new ol.source.ImageStatic({
            imageLoadFunction : function(img){
                img.getImage().src = base64_image.src;
            },
            //projection: "EPSG:4326",
            projection: proj,
            //size : [150, 150], // 150x150px
            imageExtent: extent
        })
    });

    mapDiv.addLayer(image);
}

// Show base 64 image on div
function display_base64_image_ondiv(div, base64_image) {
    var image = document.createElement("img");
    image.onload = function() {
        div.innerHTML = "";
        div.appendChild(this);
    }
    image.src = base64_image;
}

function transform_projection(coordinates, original_proj, target_proj) {
    var new_coordinates = Array();

    if(coordinates.length == 2) {
        return ol.proj.transform(coordinates, original_proj, target_proj);
    }
    else {
        for(var i=0; i<=(coordinates.length)-1; i++) {
            for(var j=0; j<=(coordinates[i].length)-1; j++) {
                new_coordinates.push(ol.proj.transform(coordinates[i][j], original_proj, target_proj));
            }
        }
    }
    
    return new_coordinates;
}
