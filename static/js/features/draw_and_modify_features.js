var decimal_places = document.getElementById("precision").value;

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
                //new_coordinates = coordinates;
                new_coordinates = round_coordinates(coordinates, decimal_places);
            }
            else {
                for(var i=0; i<=(coordinates.length)-1; i++) {
                    for(var j=0; j<=(coordinates[i].length)-1; j++) {
                        addMarker(mapDiv, coordinates[i][j], main_projection);
                        //new_coordinates.push(coordinates[i][j]);
                        new_coordinates.push(round_coordinates(coordinates[i][j], decimal_places));
                    }
                }
                new_coordinates.pop();
            }

            var coordinate_results = "";
            var input_hidden       = "";
            if(new_coordinates.length == 2) {
                //coordinate_results = "<input type='text' value="+new_coordinates+" disabled>";
                coordinate_results = "<p>"+new_coordinates+"</p>";

                for(var i=0; i<=(new_coordinates.length)-1; i++) {
                    input_hidden += "<input type='hidden' name="+'polygon'+new_coordinates+" value="+new_coordinates[i]+">";
                }
            }
            else {
                for(var i=0; i<=(new_coordinates.length)-1; i++) {
                    coordinate_results += "<p>"+new_coordinates[i]+"</p>";
                }

                for(var i=0; i<=(new_coordinates.length)-1; i++) {
                    for(var j=0; j<=(new_coordinates[i].length)-1; j++) {
                        //input_hidden += "<input type='hidden' name="+'polygon'+new_coordinates[i]+" value="+new_coordinates[i][j]+">";
                        input_hidden += "<input type='hidden' name="+'polygon'+new_coordinates+" value="+new_coordinates[i][j]+">";
                    }
                }
            }

            $(".list-group").append(
                "<li class='list-group-item d-flex justify-content-between align-items-center border-bottom'>"
                    +"<a href='#' id='list-item-closer' class='ol-popup-closer' onClick='remove_coordinate(this)'></a>"
                    //+"<input type='hidden' name="+new_coordinates+" value="+JSON.stringify(new_coordinates)+">"
                    //+"<input type='hidden' name="+'polygon'+new_coordinates+" value="+new_coordinates+">"
                    +input_hidden
                    +"<strong> Coordinates: </strong>"
                    +"<div>"
                        +coordinate_results
                    +"</div>"
                    //+"<input type='text' name='enable_draw' value="+new_coordinates+" disabled>"
                    /*
                    +"<div class='image-parent'>"
                        //+"<img src="+base64_image.src+" class='img-fluid'>"
                        +"<div class='image-parent' id='placeholder'></div>"
                    +"</div>"
                    */
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
