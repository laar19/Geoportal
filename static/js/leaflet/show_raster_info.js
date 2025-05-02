function show_raster_info(map, geoserver_config, layers, error) {
    var map_layers_list  = [];
    var map_layers_dict  = {};

    for(let key in layers) {
        var geoserver_url = geoserver_config["geoserver_url"] + "/" +
            layers[key]["geoserver_service"];
        
        var wmsLayer = L.tileLayer.wms(geoserver_url, {
            layers     : layers[key]["custom_id"],
            format     : layers[key]["geoserver_format"],
            transparent: layers[key]["geoserver_transparent"]
        }).addTo(map);

        var tmp = {
            layer_object: wmsLayer,
            layer_data  : layers[key]
        };
        map_layers_list.push(tmp);
        map_layers_dict[layers[key]["custom_id"]] = wmsLayer;
    }

    var info_adicional = {
        prueba1: "Hola todos",
        prueba2: "Cómo están"
    }

    map.on("click", function(e) {
        var fetchPromises = [];
        var popupContent = "<div><table>";

        map_layers_list.forEach((layer) => {
            if (map.hasLayer(layer.layer_object)) {  // Verificar si la capa está activa
                var url = getFeatureInfoUrl(
                    map,
                    layer.layer_object,
                    e.latlng,
                    {
                        "info_format": "application/json"
                    }
                );

                parsed_url = parse_url(url);

                fetchPromises.push(
                    (function(layer) {
                        return fetch(parsed_url)
                            .then(response => response.json())
                            .then(data => {
                                var feature = data.features[0];
                                if (feature !== undefined) {
                                    popupContent += 
                                        "<tr><td>Custom ID</td><td class='popup-table-value'>" + layer.layer_data["custom_id"] + "</td></tr>" +
                                        "<tr><td>Name</td><td class='popup-table-value'>" + layer.layer_data["name"] + "</td></tr>" +
                                        "<tr><td>Geoserver workspace</td><td class='popup-table-value'>" + layer.layer_data["geoserver_workspace"] + "</td></tr>" +
                                        "<tr><td>Geoserver service</td><td class='popup-table-value'>" + layer.layer_data["geoserver_service"] + "</td></tr>" +
                                        "<tr><td>Geoserver format</td><td class='popup-table-value'>" + layer.layer_data["geoserver_format"] + "</td></tr>" +
                                        "<tr><td>Geoserver transparent</td><td class='popup-table-value'>" + layer.layer_data["geoserver_transparent"] + "</td></tr>" +
                                        "<tr><td>Información Adicional</td><td class='popup-table-value'><ol style='margin-top: 1px; margin-bottom: 1px; list-style-type: disc;'><li style='margin-left: 1px; margin-right: 1px; margin-top: 6px; margin-bottom: 6px;'>" + info_adicional.prueba1 + "</li></ol></td></tr>";
                                }
                            });
                    })(layer)
                );
            }
        });

        Promise.all(fetchPromises).then(() => {
            popupContent += "</table></div>";

            L.popup()
                .setLatLng(e.latlng)
                .setContent(popupContent)
                .openOn(map);
        });
    });

    for(let key in map_layers_list) {
        // Add click handler to the image
        $("#"+map_layers_list[key].layer_data["custom_id"]).click(function() {
            var layer = map_layers_dict[this.id];
            toggleLayer(this.id+"-eye", layer, map, "div_"+map_layers_list[key].layer_data["custom_id"]);
        });
        
        // Add another handler specifically for the eye icon clicks
        $(".image-to-layer").find("img#" + map_layers_list[key].layer_data["custom_id"]).siblings(".overlay-to-layer").click(function() {
            var customId = $(this).siblings("img").attr("id");
            var layer = map_layers_dict[customId];
            toggleLayer(this.id+"-eye", layer, map, "div_"+customId);
        });
    }
}
