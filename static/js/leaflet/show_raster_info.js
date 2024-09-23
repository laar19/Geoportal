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

        var geoserver_url = geoserver_config["geoserver_url"] + layers[key]["geoserver_workspace"]  + "/" + layers[key]["geoserver_service"];
        
        var wmsLayer = L.tileLayer.wms(geoserver_url, {
            //layers     : layers[key]["geoserver_workspace"] + ":" + layers[key]["custom_id"],
            layers     : layers[key]["custom_id"],
            format     : layers[key]["geoserver_format"],
            transparent: layers[key]["geoserver_transparent"],
            //name       : _id
            //version    : '1.1.0',
            //attribution: "country layer"
        });
        //wmsLayer.addTo(map);
        map_layers[layers[key]["custom_id"]] = wmsLayer;

        if (layers[key]["layer_type"] == "vector") {
            wmsLayer.addTo(map).bindPopup("My popup content", {
                trigger: 'hover',
                maxWidth: 200,
                className: 'custom-popup'
            });

            /*
            // Function to retrieve polygon data from WFS
            function getPolygonData(wmsUrl, layerName) {
                var wfsUrl = wmsUrl + '?service=WFS&version=1.1.0&request=GetFeature&typeName=' + layerName + '&outputFormat=application/json';

                axios.get(wfsUrl)
                    .then(function (response) {
                        var features = response.data.features;
                        for (var i = 0; i < features.length; i++) {
                            var feature = features[i];
                            var coordinates = feature.geometry.coordinates;
                            var polygon = L.polygon(coordinates).addTo(map).bindPopup("hi jeje");
                            console.log(coordinates);
                        }
                    })
                    .catch(function (error) {
                        console.error('Error fetching polygon data:', error);
                    });
            }

            // Call the function to retrieve polygon data
            getPolygonData(geoserver_config["geoserver_url"]+"wms", layers[key]["custom_id"]);
            */

            /*
            // Add click event listener
            map.on('click', function(e) {
                var url = wmsLayer.getFeatureInfoUrl(
                    e.latlng,
                    map.getZoom(),
                    map.getSize(),
                    {
                        'info_format': 'application/json'
                    }
                );

                // Fetch the feature info
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        // Handle the feature info data
                        console.log(data);
                        L.popup()
                            .setLatLng(e.latlng)
                            .setContent('Feature Info: ' + JSON.stringify(data))
                            .openOn(map);
                    })
                    .catch(error => console.error('Error fetching feature info:', error));
            });
            */

            /*
            map.on('click', function (e) {
                const url = geoserver_config["geoserver_url"]+"wms?service=WMS&version=1.1.1&request=GetFeatureInfo&layers="+layers[key]["geoserver_workspace"]+":"+layers[key]["custom_id"]+"&bbox=${map.getBounds().toBBoxString()}&width=${map.getSize().x}&height=${map.getSize().y}&srs=EPSG:4326&format=image/png&query_layers="+layers[key]["geoserver_workspace"]+":"+layers[key]["custom_id"]+"&info_format=application/json&x=${Math.floor(e.containerPoint.x)}&y=${Math.floor(e.containerPoint.y)}";

                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        console.log('Feature Info:', data);
                        // Display the feature info as needed
                        alert(JSON.stringify(data));
                    })
                    .catch(error => console.error('Error fetching feature info:', error));
            });
            */

            /*
            // Get the bounds of the geoserver WMS layer to draw
            const wmsUrl    = geoserver_config["geoserver_url"] + "wms?service=WMS&version=1.1.1&request=GetCapabilities";
            const workspace = layers[key]["geoserver_workspace"];
            const layerName = layers[key]["custom_id"];

            var coordinates_vector;

            axios.get(wmsUrl).then((response) => {
                const parser = new WMSCapabilities();
                const json   = parser.parse(response.data);
                const layers = json.Capability.Layer.Layer;
                const layer  = layers.find(l => l.Name === `${workspace}:${layerName}`);
                const bbox   = layer.BoundingBox[0].extent;

                var coordinates = [[]];
                for (var i=0; i<bbox.length; i++) {
                    coordinates[0].push([bbox[i][1], bbox[i][0]]);
                }
                coordinates_vector = coordinates;

                console.log("Bounding Box:", bbox);
                // Use the bounding box as needed, e.g., to fit the map view
                // map.fitBounds([[bbox[1], bbox[0]], [bbox[3], bbox[2]]]);
            }).catch((error) => {
                console.error("Error fetching WMS capabilities:", error);
            });

            console.log(coordinates_vector);

            var polygon  = L.polygon(coordinates_vector, polygon_style);
            var polyline = L.polyline(coordinates_vector, {color: "red"});
            polygon.addTo(map);
            polyline.addTo(map);

            var html_layer_info = "<div>"+
                "<table>"+
                    "<tr>"+
                        "<td>Hello</td>"
                "</table>"+
            "</div>";

            wmsLayer.bindPopup(html_layer_info);

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

            wmsLayer.on("click", show_popup);
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

                /*
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
                */
            }
        }
    }

    /*
    const polygon2 = L.polygon([
        [472545.74484795, 4823134.54431552],
        [472543.90161885, 4823132.13071817],
        [472523.76152767, 4823124.8830602]
    ]).addTo(map).bindPopup('I am a polygon.');
    */

    /*
    // Define the source projection using its Proj4 definition string
    proj4.defs("EPSG:32611", "+proj=utm +zone=11 +datum=WGS84 +units=m +no_defs");

    // Define the source and destination projections
    var sourceProjection = 'EPSG:32611'; // UTM Zone 33N
    var destProjection = 'EPSG:4326'; // WGS84

    // Example projected coordinates (easting, northing)
    var projectedCoordinates = [
        [472545.74484795, 4823134.54431552],
        [472543.90161885, 4823132.13071817],
        [472523.76152767, 4823124.8830602]
    ];
    //var projectedCoordinates = [472545.74484795, 4823134.54431552];

    // Perform the conversion
    var geographicCoordinates = proj4(sourceProjection, destProjection, projectedCoordinates);

    console.log('Latitude:', geographicCoordinates[1]);
    console.log('Longitude:', geographicCoordinates[0]);
    */

    /*
    //var proj4 = require('proj4');

    // Define the source and target projections
    var fromProj = 'EPSG:3857'; // Example: Web Mercator
    var toProj = 'EPSG:4326'; // Example: WGS84 (geographic)

    // Projected coordinates
    var projectedCoordinates = [
        [472545.74484795, 4823134.54431552],
        [472543.90161885, 4823132.13071817],
        [472523.76152767, 4823124.8830602]
    ];

    // Convert to geographic coordinates
    var geographicCoords = proj4(fromProj, toProj, projectedCoordinates);

    console.log(geographicCoords); // Output: [longitude, latitude]
    */
}
