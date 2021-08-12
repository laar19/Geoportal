var layer = new ol.layer.Vector({
    source: new ol.source.Vector({
        features: [
            new ol.Feature({
                geometry: new ol.geom.Point([-64.69167939001983, 5.972876377001017])
            })
        ]
    })
});
mapDiv.addLayer(layer);

var container = document.getElementById("popup");
var content   = document.getElementById("popup-content");
var closer    = document.getElementById("popup-closer");

var overlay = new ol.Overlay({
    element: container,
    autoPan: true,
    autoPanAnimation: {
        duration: 250
    }
});
mapDiv.addOverlay(overlay);

closer.onclick = function () {
    overlay.setPosition(undefined);
    closer.blur();
    return false;
};

mapDiv.on("singleclick", function (event) {
    if (mapDiv.hasFeatureAtPixel(event.pixel) === true) {
        var coordinate = event.coordinate;

        content.innerHTML = "<b>Change my style</b><br />like a leaflet marker.";
        overlay.setPosition(coordinate);
    }
    else {
        overlay.setPosition(undefined);
        closer.blur();
    }
});

content.innerHTML = "<b>Change my style</b><br />like a leaflet marker.";
overlay.setPosition([-64.69167939001983, 5.972876377001017]);
