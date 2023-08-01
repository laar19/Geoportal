function show_raster_info(map, geoserver_info, layers, error) {
    if(geoserver_info) {
        var map_layers = {};
        
        var workspace     = geoserver_info["workspace"];
        var service       = geoserver_info["service"];
        var geoserver_url = geoserver_info["geoserver_url"] + "/" + workspace + "/" + service;
        var format        = geoserver_info["format"];
        var transparent   = geoserver_info["transparent"];

        var aux = 0;
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

            var id_ = "layer_"+aux;
            
            var wmsLayer = L.tileLayer.wms(geoserver_url, {
                layers     : workspace + ":" + layers[key]["custom_id"],
                format     : format,
                transparent: transparent,
                //name       : _id
                //version    : '1.1.0',
                //attribution: "country layer"
            });
            //wmsLayer.addTo(map);
            map_layers[id_] = wmsLayer;

            $("#previews").append('<div id='+id_+'></div>');
            $("#"+id_+"").click(function() {
                var layer = map_layers[this.id];
                toggleLayer(layer, map);
            });

            var url = geoserver_info["geoserver_url"] + "/" + service + "/reflect?layers=" + workspace + ":" + layers[key]["custom_id"];
            $("#"+id_+"").append('<br><br><img src='+url+' width="100" height="100">');
            
            $("#"+id_+"").append('<div>Satellite: '+layers[key]["satellite"]+'</div>');
            $("#"+id_+"").append('<div>Sensor: '+layers[key]["sensor"]+'</div>');
            $("#"+id_+"").append('<div>Capture date: '+layers[key]["capture_date"]+'</div>');
            $("#"+id_+"").append('<div>Solar Elevation: '+layers[key]["solar_elevation"]+'</div>');
            $("#"+id_+"").append('<div>Solar Azimuth: '+layers[key]["solar_azimuth"]+'</div>');
            $("#"+id_+"").append('<div>Cloud percentage: '+layers[key]["cloud_percentage"]+'</div>');
            $("#"+id_+"").append('<div>Solar irradiance: '+layers[key]["solar_irradiance"]+'</div>');
            $("#"+id_+"").append('<div>K: '+layers[key]["k_val"]+'</div>');
            $("#"+id_+"").append('<div>B: '+layers[key]["b_val"]+'</div>');
            $("#"+id_+"").append('<div>Satellite altitude: '+layers[key]["satellite_altitude"]+'</div>');
            $("#"+id_+"").append('<div>Zenit satellite angle: '+layers[key]["zenit_satellite_angle"]+'</div>');
            $("#"+id_+"").append('<div>Satellite azimuth angle: '+layers[key]["satellite_azimuth_angle"]+'</div>');
            $("#"+id_+"").append('<div>Roll angle: '+layers[key]["roll_angle"]+'</div>');
            $("#"+id_+"").append('<a href='+layers[key]["compressed_file_path"]+'>Download</a>');

            var coords = JSON.parse(layers[key]["cutted_image_shape"])["coordinates"];
            //var coords =  [[48,-3],[50,5],[44,11],[48,-3]] ;
            
            var coordinates = [[]];
            for (var i=0; i<coords[0].length; i++) {
                coordinates[0].push([coords[0][i][1], coords[0][i][0]]);
            }
            
            var polygon = L.polygon(coordinates, {color: 'red'});
            polygon.addTo(map);
            //map.fitBounds(polygon.getBounds());

            //var marker = L.marker([33.767675, -84.537291]).addTo(map);
            //marker.bindPopup("Loading...");
            //polygon.bindPopup("Loading...");
            polygon.bindPopup(
                "<div>"+
                    "Satellite              : " + layers[key]["satellite"]               + "<br>"+
                    "Sensor                 :  " + layers[key]["sensor"]                 + "<br>"+
                    "Capture date           : " + layers[key]["capture_date"]            + "<br>"+
                    "Solar Elevation        : " + layers[key]["solar_elevation"]         + "<br>"+
                    "Solar Azimuth          : " + layers[key]["solar_azimuth"]           + "<br>"+
                    "Cloud percentage       : " + layers[key]["cloud_percentage"]        + "<br>"+
                    "Solar irradiance       : " + layers[key]["solar_irradiance"]        + "<br>"+
                    "K                      : " + layers[key]["k_val"]                   + "<br>"+
                    "B                      : " + layers[key]["b_val"]                   + "<br>"+
                    "Satellite altitude     : " + layers[key]["satellite_altitude"]      + "<br>"+
                    "Satellite zenit angle  : " + layers[key]["zenit_satellite_angle"]   + "<br>"+
                    "Satellite azimuth angle: " + layers[key]["satellite_azimuth_angle"] + "<br>"+
                    "Roll angle             : " + layers[key]["roll_angle"]              + "<br>"+
                    "<a href="+layers[key]["compressed_file_path"]+">Download</a>"+
                "</div>"
            );

            function show_popup(e) {
                var popup = e.target.getPopup();


                $.ajax({
                    url: "myurl.html",
                    })
                    .done(function(data) {
                        alert(data);
                        popup.setContent(data);
                        popup.update();
                    })
                    .fail(function(data) {
                        alert("FAIL: "+data);
                    });
                };

            //marker.on('click', onMapClick );
            polygon.on("click", show_popup);

            aux = aux + 1;
        }
    }
    else {
        if(error_) {
            alert("Wrong area");
        }
    }
}
