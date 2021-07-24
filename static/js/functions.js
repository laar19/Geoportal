// Show coordinate points on the map
function display_points(data) {
    var source = new ol.source.Vector({});
    var layer  = new ol.layer.Vector({source: source});
    
    for(var i=0; i<data.length; i++) {
        var marker = new ol.Feature({
            geometry: new ol.geom.Point([data[i][0], data[i][1]])
        });
        source.addFeature(marker);
    }
    
    map.addLayer(layer);
}
