var container = document.getElementById("popup");
var content   = document.getElementById("popup-content");
var closer    = document.getElementById("popup-closer");

// Close popup 
closer.onclick = function() {
    popup.setPosition(undefined);
    closer.blur();
    return false;
};

// Popup showing the position the user clicked
var popup = new ol.Overlay({
    element: container,
    autoPan: true,
    positioning: "bottom-center",
    autoPanAnimation: {
        duration: 250
    }
});
mapDiv.addOverlay(popup);

// display popup on click
// NEVER DELETE THIS ONE
/*
mapDiv.on("click", function(evt) {
    var feature = mapDiv.forEachFeatureAtPixel(evt.pixel, function(feature) {
        return feature;
    });

    if(feature.get("display") == true) {
        content.innerHTML = "<pre> <b>Waypoint Details </b> " + "<br>" + "Population : " + feature.get("population") + "<br>Rainfall: " + feature.get("rainfall") + "</pre>"
        popup.setPosition(evt.coordinate);
    }
});
*/

// change mouse cursor when hover marker
mapDiv.on("pointermove", function(e) {
    var pixel = mapDiv.getEventPixel(e.originalEvent);
    var hit   = mapDiv.hasFeatureAtPixel(pixel);
    mapDiv.getTarget().style.cursor = hit ? "pointer" : "";
});

// Close the popup when the map is moved
/*
mapDiv.on("movestart", function() {
    $(container).popover("dispose");
});
*/

// Add marker on polygon draw or point
// NEVER DELETE THIS ONE
/*
function addMarker(mapDiv, coordinates, proj, name) {
    var marker;
    
    if(proj == main_projection) {
        marker = new ol.Feature({
            geometry  : new ol.geom.Point(coordinates),
            display   : true,
            population: 4000,
            rainfall  : 500
        });
    }
    else {
        marker = new ol.Feature({
            geometry  : new ol.geom.Point(ol.proj.fromLonLat(coordinates)),
            display   : true,
            population: 4000,
            rainfall  : 500
        });
    }

    // Change icon
    marker.setStyle(new ol.style.Style({
        image: new ol.style.Icon({
            anchor: [0.5, 46],
            anchorXUnits: "fraction",
            anchorYUnits: "pixels",
            src: "http://localhost/geoportal/static/img/pin_marker.png"
        })
    }));

    var layer_marker = new ol.layer.Vector({
        source: new ol.source.Vector({
            //features: markers_list
            features: [marker]
        }),
        name: name
    });

    mapDiv.addLayer(layer_marker);
}
*/
