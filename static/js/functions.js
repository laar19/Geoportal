function map_view(center, zoom) {
    var view = new ol.View({
        projection: main_projection,
        //center    : [-65.89003678746177, 8.016859315038008],
        center    : center,
        //center: ol.proj.transform([-65.89003678746177, 8.016859315038008], "EPSG:4326", "EPSG:3857"),
        zoom      : zoom
    });

    return view
}

// Show coordinate points on the map
function display_layer(data, title, map) {
    var vectorSource = new ol.source.Vector({
        features: new ol.format.GeoJSON().readFeatures(data)
    });

    vectorSource.addFeature(new ol.Feature(new ol.geom.Circle([5e6, 7e6], 1e6)));

    var vectorLayer = new ol.layer.Vector({
        title : title,
        source: vectorSource,
        name  : title,
        style : styleFunction
    });

    //map.addLayer(vectorLayer);
    return vectorLayer;
}

// Show base 64 image on the map
function display_base64_image_onmap(base64_image, extent, name, map, proj) {    
    image = new ol.layer.Image({
        source: new ol.source.ImageStatic({
            imageLoadFunction : function(img){
                img.getImage().src = base64_image.src;
            },
            //projection: "EPSG:4326",
            projection: proj,
            //size : [150, 150], // 150x150px
            imageExtent: extent
        }),
        name: name
    });

    map.addLayer(image);

    $(".list-group-result").append(
        "<li class='list-group-item d-flex justify-content-between align-items-center'>"
            +"<input type='checkbox' id="+name+" value="+name+" checked='checked' onchange='change_layer_visibility(this, mapDiv)'/>"
            +"<label for="+name+"> <strong> Some data </strong> etc </label>"
            +"<div class='image-parent'>"
                +"<img src="+base64_image.src+" class='img-fluid'>"
                +"<div class='image-parent' id='placeholder'></div>"
            +"</div>"
        +"</li>"
    );

    $("#sidebar-content > div").removeClass("active");
    $(".fa-poll-h").parent().parent().addClass("active");
    $("#results").addClass("active");
    $("#sidebar").removeClass("collapsed");
}

// Show base 64 image on div
/*
function display_base64_image_ondiv(div, base64_image) {
    var image = document.createElement("img");
    image.onload = function() {
        div.innerHTML = "";
        div.appendChild(this);
    }
    image.src = base64_image;
}
*/

function transform_projection(coordinates, original_proj, target_proj) {
    var new_coordinates = Array();

    if(coordinates.length == 2) {
        return ol.proj.transform(coordinates, original_proj, target_proj);
    }
    else {
        for(var i=0; i<=(coordinates.length)-1; i++) {
            for(var j=0; j<=(coordinates[i].length)-1; j++) {
                new_coordinates.push(ol.proj.transform(coordinates[i][j], original_proj, target_proj));
            }
        }
    }
    
    return new_coordinates;
}

// Round decimal numbers
function round_coordinates(coordinates, decimal_places) {
    var new_coordinates = Array();
    
    for(var i=0; i<=(coordinates.length)-1; i++) {
        new_coordinates.push(Number(Math.round(coordinates[i] + "e" + decimal_places) + "e-" + decimal_places));
    }

    return new_coordinates;
}

// Remove layer from map
function remove_layer(layer_name, map) {
    map.getLayers().getArray()
        .filter(layer => layer.get("name") == layer_name)
        .forEach(layer => map.removeLayer(layer));
}

// Change layer visibility
function change_layer_visibility(element, map) {
    if(element.checked == true) {
        map.getLayers().forEach(function (layer) {
            if (layer.get("name") == element.value) {
                layer.setVisible(true);
            }
        });
    }
    else {
        map.getLayers().forEach(function (layer) {
            if (layer.get("name") == element.value) {
                layer.setVisible(false);
            }
        });
    }
}

// Get map config
function get_map_config(map) {
    center = map.getView().getCenter();
}

// Draw user selection alongside with the results
function display_user_selection(map, coordinates) {
    var coordinatesPolygon = new Array();
    //Cycle traversal transfers longitude and latitude to the projection coordinate system of "EPSG:4326"
    for (var i = 0; i < coordinates.length; i++) {
        var pointTransform = ol.proj.fromLonLat([coordinates[i][0], coordinates[i][1]], "EPSG:4326");
        coordinatesPolygon.push(pointTransform);
    }
    
    var source = new ol.source.Vector();
    
    var vector = new ol.layer.Vector({
        source: source,
        style: new ol.style.Style({
            fill: new ol.style.Fill({
                color: "rgba(255, 255, 255, 0.1)"
            }),
            stroke: new ol.style.Stroke({
                color: "red",
                width: 2
            }),
            image: new ol.style.Circle({
                radius: 10,
                fill: new ol.style.Fill({
                    color: "#ffcc33"
                })
            })
        })
    });
    //The polygon here must be an array of coordinates
    var plygon = new ol.geom.Polygon([coordinatesPolygon])
    //var plygon = new ol.geom.Polygon([coordinates])
    //Polygon feature class
    var feature = new ol.Feature({
        geometry: plygon,
    });
    source.addFeature(feature);
    map.addLayer(vector);
    
}
