function show_raster_info(map, geoserver_config, layers, error) {
    var map_layers  = [];
    var map_layers_ = {};

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
        map_layers.push(tmp);
        map_layers_[layers[key]["custom_id"]] = wmsLayer;
        
    }

    for(let key in map_layers) {
        if (map_layers[key].layer_data["layer_type"] == "vector") {
            
            // Add a click event to show popup
            map.on("click", function(e) {
                var url = getFeatureInfoUrl(
                    map,
                    map_layers[key].layer_object,
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
                            
                            var popupContent  = "<p>" +
                                    map_layers[key].layer_data["custom_id"] +
                                "</p>";
                                
                            L.popup()
                                .setLatLng(e.latlng)
                                .setContent(popupContent)
                                .openOn(map);
                        }
                    });
            });
        }

        $("#"+map_layers[key].layer_data["custom_id"]+"").click(function() {
            var layer = map_layers_[this.id];
            
            toggleLayer(
                layer,
                map,
                "div_"+map_layers[key].layer_data["custom_id"]
            );
        });

        if (map_layers[key].layer_data["layer_type"] == "raster") {
            var html_layer_info = "<div>" +
                    "<table>" +
                        "<tr>" +
                            "<td>Satellite</td>" +
                            "<td class='popup-table-value'>" +
                                map_layers[key].layer_data["satellite"] +
                            "</td>" +
                        "</tr>" +
                        "<tr>" +
                            "<td>Sensor</td>" +
                            "<td class='popup-table-value'>" +
                                map_layers[key].layer_data["sensor"] +
                            "</td>" +
                        "</tr>" +
                        "<tr>" +
                            "<td>Orbit</td>" +
                            "<td class='popup-table-value'>" +
                                map_layers[key].layer_data["orbit"] +
                            "</td>" +
                        "</tr>" +
                        "<tr>" +
                            "<td>Scene</td>" +
                            "<td class='popup-table-value'>" +
                                map_layers[key].layer_data["scene"] +
                            "</td>" +
                        "</tr>" +
                        "<tr>" +
                            "<td>Capture date</td>" +
                            "<td class='popup-table-value'>" +
                                map_layers[key].layer_data["capture_date"] +
                            "</td>" +
                        "</tr>" +
                        "<tr>" +
                            "<td>Cloud percentage</td>" +
                            "<td class='popup-table-value'>" +
                                map_layers[key].layer_data["cloud_percentage"] +
                            "</td>" +
                        "</tr>" +
                        "<tr>" +
                            "<td>Roll angle</td>" +
                            "<td class='popup-table-value'>" +
                                map_layers[key].layer_data["roll_angle"] +
                            "</td>" +
                        "</tr>" +
                        "<tr>" +
                            "<td>Download</td>" +
                            "<td class='popup-table-value'>" +
                                "<a href=" +
                                    map_layers[key]
                                        .layer_data["compressed_file_path"] +
                                ">Link</a>" +
                            "</td>" +
                        "</tr>" +
                    "</table>" +
                "</div>";
            
            if (map_layers[key].layer_data["cutted_image_shape"] != "None") {
                var coords = JSON.parse(map_layers[key]
                    .layer_data["cutted_image_shape"])["coordinates"];
                //var coords =  [[48,-3],[50,5],[44,11],[48,-3]] ;
                
                var coordinates = [[]];
                for (var i=0; i<coords[0].length; i++) {
                    coordinates[0].push([coords[0][i][1], coords[0][i][0]]);
                }

                var polygon_style = {
                    //"color"      : "red",
                    "weight"     : 0,
                    "fillOpacity": 0.0
                    //"opacity"    :0
                };
                
                var polygon  = L.polygon(coordinates, polygon_style);
                var polyline = L.polyline(coordinates, {color: "red"});
                polygon.addTo(map);
                polyline.addTo(map);

                polygon.bindPopup(html_layer_info);
            }
        }
    }
}
