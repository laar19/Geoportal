var source = new ol.source.Vector({
    wrapX: false
});

var draw; // global so we can remove it later
var value; // global so we can remove it later

var typeSelect = document.getElementById("draw_type");
value          = typeSelect.value;

function addInteraction() {
    //var value = typeSelect.value;
    value = typeSelect.value;

    if(value !== "None") {
        var geometryFunction, maxPoints;

        if(value === "Square") {
            value = "Circle";
            geometryFunction = ol.interaction.Draw.createRegularPolygon(4);
        }
        else if(value === "Box") {
            value = "LineString";
            maxPoints = 2;
            geometryFunction = function(coordinates, geometry) {
                if(!geometry) {
                    geometry = new ol.geom.Polygon(null);
                }
                var start = coordinates[0];
                var end = coordinates[1];
                geometry.setCoordinates([
                    [start, [start[0], end[1]], end, [end[0], start[1]], start]
                ]);
                return geometry;
            };
        }

        draw = new ol.interaction.Draw({
            source: source,
            type: /** @type {ol.geom.GeometryType} */ (value),
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
    //value = typeSelect.value;
};
