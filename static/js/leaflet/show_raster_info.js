function show_raster_info(map, geoserver_config, layers, error) {
    var map_layers_list  = [];
    var map_layers_dict  = {};

    for(let key in layers) {
        /*
        var test = L.tileLayer.wms("http://172.20.0.3:8080/geoserver/satellite_images/wms", {
            layers     : "satellite_images:VRSS-2_MSS_0288_0330_20221022_L2A_404132008447_THUMB_modified",
            format     : "image/png",
            transparent: true,
            //version    : '1.1.0',
            //attribution: "country layer"
        });
        test.addTo(map);
        */

        var geoserver_url = geoserver_config["geoserver_url"] + "/" +
            layers[key]["geoserver_service"];
        
        var wmsLayer = L.tileLayer.wms(geoserver_url, {
            layers     : layers[key]["custom_id"],
            format     : layers[key]["geoserver_format"],
            transparent: layers[key]["geoserver_transparent"],
            //name       : _id
            //version    : '1.1.0',
            //attribution: "country layer"
        }).addTo(map);

        var tmp = {
            layer_object: wmsLayer,
            layer_data  : layers[key]
            
        };
        map_layers_list.push(tmp);
        map_layers_dict[layers[key]["custom_id"]] = wmsLayer;
    }

    for(let key in map_layers_list) {
        if (map_layers_list[key].layer_data["layer_type"] == "vector") {
            
            // Add a click event to show popup
            map.on("click", function(e) {
                var url = getFeatureInfoUrl(
                    map,
                    map_layers_list[key].layer_object,
                    e.latlng,
                    {
                        "info_format": "application/json"
                    }
                );

                parsed_url = parse_url(url);
                fetch(parsed_url)
                    .then(response => response.json())
                    .then(data => {
                        var feature = data.features[0];
                        if (feature !== undefined) {
                            
                            var popupContent  = "<div>" +
                                    "<table>" +
                                        "<tr>" +
                                            "<td>Custom ID</td>" +
                                            "<td class='popup-table-value'>" +
                                                map_layers_list[key].layer_data["custom_id"] +
                                            "</td>" +
                                        "</tr>" +
                                        "<tr>" +
                                            "<td>Name</td>" +
                                            "<td class='popup-table-value'>" +
                                                map_layers_list[key].layer_data["name"] +
                                            "</td>" +
                                        "</tr>" +
                                        "<tr>" +
                                            "<td>Geoserver workspace</td>" +
                                            "<td class='popup-table-value'>" +
                                                map_layers_list[key].layer_data["geoserver_workspace"] +
                                            "</td>" +
                                        "</tr>" +
                                        "<tr>" +
                                            "<td>Geoserver service</td>" +
                                            "<td class='popup-table-value'>" +
                                                map_layers_list[key].layer_data["geoserver_service"] +
                                            "</td>" +
                                        "</tr>" +
                                        "<tr>" +
                                            "<td>Geoserver format</td>" +
                                            "<td class='popup-table-value'>" +
                                                map_layers_list[key].layer_data["geoserver_format"] +
                                            "</td>" +
                                        "</tr>" +
                                        "<tr>" +
                                            "<td>Geoserver transparent</td>" +
                                            "<td class='popup-table-value'>" +
                                                map_layers_list[key].layer_data["geoserver_transparent"] +
                                            "</td>" +
                                        "</tr>" +
                                    "</table>" +
                                "</div>";
                                
                            L.popup()
                                .setLatLng(e.latlng)
                                .setContent(popupContent)
                                .openOn(map);
                        }
                    });
            });
        }
        
        $("#"+map_layers_list[key].layer_data["custom_id"]).click(function() {
            var layer = map_layers_dict[this.id];
            toggleLayer(layer, map, "div_"+map_layers_list[key].layer_data["custom_id"]);
        });
    }
}
