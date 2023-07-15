var editableLayers = new L.FeatureGroup();
map.addLayer(editableLayers);

var options = {
    position: 'topleft',
    draw: {
        marker: false,
        polyline: false,
        /*
        polyline: {
            shapeOptions: {
                color: '#f357a1',
                weight: 10
            }
        },
        */
        polygon: {
            allowIntersection: false, // Restricts shapes to simple polygons
            drawError: {
                color: '#e1e100', // Color the shape will turn when intersects
                message: '<strong>Oh snap!<strong> you can\'t draw that!' // Message that will show when intersect
            },
            shapeOptions: {
                //color: '#bada55'
                color: 'red'
            }
        },
        circle: false, // Turns off this drawing tool
        rectangle: false,
        /*
        rectangle: {
            shapeOptions: {
                clickable: false
            }
        }
        */
    },
    edit: {
        featureGroup: editableLayers, //REQUIRED!!
        remove: false
    }
};
var drawControl = new L.Control.Draw(options);
map.addControl(drawControl);

// Get coordinates, view and zoom
map.on(L.Draw.Event.CREATED, function (e) {
    var type = e.layerType,
        layer = e.layer;
        
    if(editableLayers && editableLayers.getLayers().length!==0) {
        editableLayers.clearLayers();
    }
    editableLayers.addLayer(layer);

    // Coordinates
    var coordinates = layer.toGeoJSON().geometry.coordinates;
    $("#coordinates").val(coordinates);
    console.log(coordinates);

    // Zoom
    $("#zoom_level").val(map._zoom);

    // View
    /*
    map.on('dragend', function onDragEnd(){
    var width  = map.getBounds().getEast() - map.getBounds().getWest();
    var height = map.getBounds().getNorth() - map.getBounds().getSouth();
    alert (
        'center:' + map.getCenter() +'\n'+
        'width:' + width +'\n'+
        'height:' + height +'\n'+
        'size in pixels:' + map.getSize()
    )});
    */
    $("#center").val([map.getCenter()["lat"], map.getCenter()["lng"]]);

    $("#search_status").val("True");
});

// Custom control
L.Control.Button = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var container   = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
        var button      = L.DomUtil.create('a', 'leaflet-control-button', container);
        L.DomEvent.disableClickPropagation(button);
        L.DomEvent.on(button, 'click', function(){
            document.getElementById("search_image_leaflet").submit();
        });

        container.title = "Search";

        return container;
    },
    onRemove: function(map) {},
});
var control = new L.Control.Button()
control.addTo(map);
