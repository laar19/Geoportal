var container = document.getElementById("popup");
var content   = document.getElementById("popup-content");
var closer    = document.getElementById("popup-closer");

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

//mapDiv.on("pointermove", function(evt) {
/*
mapDiv.on("singleclick", function(event) {
    if (mapDiv.hasFeatureAtPixel(event.pixel) === true) {
        var coordinate = event.coordinate;

        var latitude = "example";
        var longitude = "example";

        content.innerHTML = "<pre> <b>Waypoint Details </b> " + "<br>" + "Latitude : " + latitude + "<br>Longitude: " + longitude + "</pre>"
        popup.setPosition(ol.proj.fromLonLat(coordinates));
    }
    /*
    else {
        popup.setPosition(undefined);
        closer.blur();
    }
    *
});
*/

// display popup on click
mapDiv.on("click", function(evt) {
    var feature = mapDiv.forEachFeatureAtPixel(evt.pixel, function(feature) {
        return feature;
    });

    if(feature.get("display") == true) {
        content.innerHTML = "<pre> <b>Waypoint Details </b> " + "<br>" + "Population : " + feature.get("population") + "<br>Rainfall: " + feature.get("rainfall") + "</pre>"        
        popup.setPosition(evt.coordinate);
        /*
        $(container).popover({
            placement: "top",
            html: true,
            //content: feature.get("name"),
            content: "<a href='#' id='popup-closer' class='ol-popup-closer'></a><pre> <b>Waypoint Details </b> " + "<br>" + "Population : " + feature.get("population") + "<br>Rainfall: " + feature.get("rainfall") + "</pre>"
        });
        $(container).popover("show");
        */
    }
    /*
    else {
        $(container).popover("dispose");
    }
    */
});

// change mouse cursor when over marker
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
    /*
    marker.setStyle(new ol.style.Style({
        image: new ol.style.Circle({
            radius: 5,
            stroke: new ol.style.Stroke({
                color: "blue"
            }),
            fill: new ol.style.Fill({
                color: [57, 228, 193, 0.84]
            })
        })
    }));
    */

    // Change icon
    marker.setStyle(new ol.style.Style({
        image: new ol.style.Icon({
            anchor: [0.5, 46],
            anchorXUnits: "fraction",
            anchorYUnits: "pixels",
            src: "https://cdn.mapmarker.io/api/v1/pin?size=50&background=%2316A5A5&icon=fas%20fa-map-marker-alt&color=%23FFFFFF&voffset=0&hoffset=1&"
        })
    }));

    /*
    var markers_list = Array();
    markers_list.push(marker);
    */

    var layer_marker = new ol.layer.Vector({
        source: new ol.source.Vector({
            //features: markers_list
            features: [marker]
        }),
        name: name
    });

    mapDiv.addLayer(layer_marker);
}
