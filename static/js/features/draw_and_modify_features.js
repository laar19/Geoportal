var source_draw = new ol.source.Vector({
    wrapX: false
});

var vector_layer_draw = new ol.layer.Vector({
    source: source_draw
});
mapDiv.addLayer(vector_layer_draw);

var draw; // global so we can remove it later
var value_draw; // global so we can remove it later

var typeSelect = document.getElementById("draw_type");
value_draw          = typeSelect.value;


function addInteraction() {
    value_draw = typeSelect.value;

    if (value_draw !== "None") {
        draw = new ol.interaction.Draw({
            source: source_draw,
            type  : typeSelect.value,
        });

        draw.on("drawend", function(e) {
            //alert(e.feature.getGeometry().getExtent());
            var coordinates = e.feature.getGeometry().getCoordinates();

            if(coordinates.length == 2) {
                addMarker(mapDiv, coordinates, "EPSG:3857");
            }
            else {
                for(var i=0; i<=(coordinates.length)-1; i++) {
                    for(var j=0; j<=(coordinates[i].length)-1; j++) {
                        addMarker(mapDiv, coordinates[i][j], "EPSG:3857");
                    }
                }
            }
            
            /*
            console.log("DOS");
            var geoJsonGeom = new ol.format.GeoJSON();    
            var pp = geoJsonGeom.writeGeometry(e.feature.getGeometry());
            console.log(pp);
            */
        })
        mapDiv.addInteraction(draw);
    }
}
/*
function addInteraction() {
    value_draw = typeSelect.value;

    if(value_draw !== "None") {
        var geometryFunction, maxPoints;

        if(value_draw === "Square") {
            value_draw = "Circle";
            geometryFunction = ol.interaction.Draw.createRegularPolygon(4);
        }
        else if(value_draw === "Box") {
            value_draw = "LineString";
            maxPoints = 2;
            geometryFunction = function(coordinates, geometry) {
                if(!geometry) {
                    geometry = new ol.geom.Polygon(null);
                }
                var start = coordinates[0];
                var end   = coordinates[1];
                geometry.setCoordinates([
                    [start, [start[0], end[1]], end, [end[0], start[1]], start]
                ]);
                return geometry;
            };
        }

        draw = new ol.interaction.Draw({
            source: source_draw,
            type: /** @type {ol.geom.GeometryType} * (typeSelect.value),
            geometryFunction: geometryFunction,
            maxPoints: maxPoints
        });

        draw.on("drawend", function(e) {
            alert(e.feature.getGeometry().getExtent());
        })
        mapDiv.addInteraction(draw);
    }
}
//addInteraction();
*/

var enable_draw = document.getElementById("enable_draw");
function enableInteraction() {
    if(enable_draw.checked) {
        typeSelect.disabled = false;
        mapDiv.removeInteraction(draw);
        addInteraction();
    }
    else {
        typeSelect.disabled = true;
        mapDiv.removeInteraction(draw);
    }
}

/**
 * Handle change event.
 *
 */
typeSelect.onchange = function() {
    mapDiv.removeInteraction(draw);
    addInteraction();
    //value_draw = typeSelect.value;
};
