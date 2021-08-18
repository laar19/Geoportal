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
value_draw     = typeSelect.value;

function add_draw_interaction() {
    value_draw = typeSelect.value;

    if (value_draw !== "None") {
        draw = new ol.interaction.Draw({
            source: source_draw,
            type  : typeSelect.value,
        });

        draw.on("drawend", function(e) {
            //alert(e.feature.getGeometry().getExtent());
            var coordinates = e.feature.getGeometry().getCoordinates();

            var new_coordinates = Array();

            if(coordinates.length == 2) {
                addMarker(mapDiv, coordinates, main_projection);
                new_coordinates = coordinates;
            }
            else {
                for(var i=0; i<=(coordinates.length)-1; i++) {
                    for(var j=0; j<=(coordinates[i].length)-1; j++) {
                        addMarker(mapDiv, coordinates[i][j], main_projection);
                        new_coordinates.push(coordinates[i][j]);
                    }
                }
                new_coordinates.pop();
            }

            $(".list-group").append(
                "<li class='list-group-item d-flex justify-content-between align-items-center'>"
                    +"<a href='#' id='list-item-closer' class='ol-popup-closer' onClick='remove_coordinate(this)'></a>"
                    +"<strong> Coordinates: </strong>"+ new_coordinates
                    +"<div class='image-parent'>"
                        //+"<img src="+base64_image.src+" class='img-fluid'>"
                        +"<div class='image-parent' id='placeholder'></div>"
                    +"</div>"
                +"</li>"
            );
            
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

// Remove coordinate item added to sidebar
function remove_coordinate(item) {
    $(item).parent().remove("li");
}

var enable_draw = document.getElementById("enable_draw");
function enable_draw_interaction() {
    if(enable_draw.checked) {
        typeSelect.disabled = false;
        mapDiv.removeInteraction(draw);
        add_draw_interaction();
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
    add_draw_interaction();
    //value_draw = typeSelect.value;
};
