function show_raster_info(map, geoserver_config, layers, error) {
    var map_layers = {};

    //var aux = 0;
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

        var geoserver_url = geoserver_config["geoserver_url"] + layers[key]["geoserver_workspace"]  + "/" + layers[key]["geoserver_service"] ;
        
        var wmsLayer = L.tileLayer.wms(geoserver_url, {
            layers     : layers[key]["geoserver_workspace"] + ":" + layers[key]["custom_id"],
            format     : layers[key]["geoserver_format"],
            transparent: layers[key]["geoserver_transparent"],
            //name       : _id
            //version    : '1.1.0',
            //attribution: "country layer"
        });
        //wmsLayer.addTo(map);
        map_layers[layers[key]["custom_id"]] = wmsLayer;

        if (layers[key]["layer_type"] == "vector") {
            wmsLayer.addTo(map);

            /*
            // Get the bounds of the WMS layer
            wmsLayer.on('load', function() {
                var bounds = wmsLayer.getBounds();
                console.log('Layer Bounds:', bounds);
            });
            */
        }

        //$("#previews").append('<div id='+id_+'></div>');
        //$("#informacion").append('<div id='+id_+'></div>');
        $("#"+layers[key]["custom_id"]+"").click(function() {
            var layer = map_layers[this.id];
            toggleLayer(layer, map, "div_"+layers[key]["custom_id"]);
        });

        if (layers[key]["layer_type"] == "raster") {
            var html_layer_info = "<div>"+
                "<table>"+
                    "<tr>"+
                        "<td>Satellite</td>"+
                        "<td class='popup-table-value'>" + layers[key]["satellite"] + "</td>"+
                    "</tr>"+
                    "<tr>"+
                        "<td>Sensor</td>"+
                        "<td class='popup-table-value'>" + layers[key]["sensor"] + "</td>"+
                    "</tr>"+
                    "<tr>"+
                        "<td>Orbit</td>"+
                        "<td class='popup-table-value'>" + layers[key]["orbit"] + "</td>"+
                    "</tr>"+
                    "<tr>"+
                        "<td>Scene</td>"+
                        "<td class='popup-table-value'>" + layers[key]["scene"] + "</td>"+
                    "</tr>"+
                    "<tr>"+
                        "<td>Capture date</td>"+
                        "<td class='popup-table-value'>" + layers[key]["capture_date"] + "</td>"+
                    "</tr>"+
                    "<tr>"+
                        "<td>Cloud percentage</td>"+
                        "<td class='popup-table-value'>" + layers[key]["cloud_percentage"] + "</td>"+
                    "</tr>"+
                    "<tr>"+
                        "<td>Roll angle</td>"+
                        "<td class='popup-table-value'>" + layers[key]["roll_angle"] + "</td>"+
                    "</tr>"+
                    "<tr>"+
                        "<td>Download</td>"+
                        "<td class='popup-table-value'>" + "<a href="+layers[key]["compressed_file_path"]+">Link</a>"+ "</td>"+
                    "</tr>"+
                "</table>"+
            "</div>";
            
            if (layers[key]["cutted_image_shape"] != "None") {
                var coords = JSON.parse(layers[key]["cutted_image_shape"])["coordinates"];
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

                function show_popup(e) {
                    var popup = e.target.getPopup();

                    $.ajax({
                        //url: "myurl.html",
                        url: $(location).attr("host"),
                    })
                    .done(function(data) {
                        alert(data);
                        popup.setContent(data);
                        popup.update();
                    })
                };

                polygon.on("click", show_popup);
            }
        }
    }
}
