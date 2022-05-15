var decimal_places = document.getElementById("precision").value;

var draw; // global so we can remove it later
var value_draw; // global so we can remove it later

var typeSelect = document.getElementById("draw_type");
value_draw     = typeSelect.value;

function add_draw_interaction() {    
    value_draw = typeSelect.value;

    if (value_draw !== "None") {
        var source_draw = new ol.source.Vector({
            wrapX: false
        });
        
        draw = new ol.interaction.Draw({
            source: source_draw,
            type  : typeSelect.value,
        });

        draw.on("drawend", function(e) {
            var name = new Date().toLocaleString() + new Date().getTime();

            var vector_layer_draw = new ol.layer.Vector({
                source: source_draw,
                name  : name
            });
            mapDiv.addLayer(vector_layer_draw);

            //var coordinates = e.feature.getGeometry().getExtent());
            
            //var geoJsonGeom = new ol.format.GeoJSON();
            //var pp = geoJsonGeom.writeGeometry(e.feature.getGeometry());
            
            var coordinates = e.feature.getGeometry().getCoordinates();

            var new_coordinates = Array();

            // POINT or LINESTRING
            if(coordinates.length == 2) {
                addMarker(mapDiv, coordinates, main_projection, name);
                new_coordinates = round_coordinates(coordinates, decimal_places);
            }
            // SO FAR POLYGON
            else {
                for(var i=0; i<=(coordinates.length)-1; i++) {
                    for(var j=0; j<=(coordinates[i].length)-1; j++) {
                        addMarker(mapDiv, coordinates[i][j], main_projection, name);
                        new_coordinates.push(round_coordinates(coordinates[i][j], decimal_places));
                    }
                }
                new_coordinates.pop();
            }

            var coordinate_results = "";
            if(new_coordinates.length == 2) {
                coordinate_results += "<p>"+new_coordinates+"</p>";
            }
            else {
                for(var i=0; i<=(new_coordinates.length)-1; i++) {
                    coordinate_results += "<p>"+new_coordinates[i]+"</p>";
                }
            }
            var input_hidden = "<input type='hidden' name="+'matchme'+new_coordinates+" value="+new_coordinates+">";

            $(".list-group-coordinates").append(
                "<li class='list-group-item d-flex justify-content-between align-items-center border-bottom'>"
                    +"<a href='#' id='list-item-closer' class='ol-popup-closer' onClick='remove_coordinate(this, "+'"'+name+'"'+")'></a>"
                    +input_hidden
                    +"<strong> Coordinates: </strong>"
                    +"<div>"
                        +coordinate_results
                    +"</div>"
                +"</li>"
            );
        })
        mapDiv.addInteraction(draw);
    }
}

// Remove coordinate element added to sidebar
function remove_coordinate(element, layer_name) {
    mapDiv.removeInteraction(draw);
    add_draw_interaction();
    $(element).parent().remove("li");
    remove_layer(layer_name, mapDiv);
}

// Enable or disable draw interaction
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
