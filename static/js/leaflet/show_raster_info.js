// Modified show_raster_info.js (fixes MutationObserver error)
function show_raster_info(map, geoserver_config, layers, error) {
    var map_layers_list  = [];
    var map_layers_dict  = {};
    // Add a layer visibility tracker
    var layerVisibility = {};

    // Check if layers exist and is not null/undefined
    if (!layers || Object.keys(layers).length === 0) {
        console.log("No layers provided or layers object is empty");
        return;
    }

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

        // Initialize all layers as visible
        layerVisibility[layers[key]["custom_id"]] = true;
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

    // Event delegation for the image clicks
    $(document).on("click", ".image-to-layer img", function() {
        var customId = $(this).attr("id");
        var layer = map_layers_dict[customId];
        toggleLayerAndTrackState(customId+"-layer-eye", layer, map, "div_"+customId, layerVisibility);
    });
    
    // Event delegation for the eye icon clicks
    $(document).on("click", ".overlay-to-layer", function() {
        var customId = $(this).siblings("img").attr("id");
        var layer = map_layers_dict[customId];
        toggleLayerAndTrackState(customId+"-layereye", layer, map, "div_"+customId, layerVisibility);
    });
    
    // Add a function to update UI based on layer visibility state
    function updateLayerUI() {
        for(let layerId in layerVisibility) {
            const isVisible = layerVisibility[layerId];
            const eyeIcon = document.getElementById(layerId + "-layer-eye");
            const divElement = document.getElementById("div_" + layerId);
            
            if(eyeIcon) {
                if(isVisible) {
                    eyeIcon.classList.remove("fa-eye-slash");
                    eyeIcon.classList.add("fa-eye");
                    if(divElement) $(divElement).css("background-color", "antiquewhite");
                } else {
                    eyeIcon.classList.remove("fa-eye");
                    eyeIcon.classList.add("fa-eye-slash");
                    if(divElement) $(divElement).css("background-color", "white");
                }
            }
        }
    }

    // Fix for MutationObserver error - Only observe if element exists
    const paginationContainer = document.querySelector("#pagination-container");
    if (paginationContainer) {
        const observer = new MutationObserver(function(mutations) {
            updateLayerUI();
        });

        // Start observing the container where your paginated content appears
        observer.observe(paginationContainer, {
            childList: true,
            subtree: true
        });
    }
    
    // Call this after pagination or whenever the DOM is updated
    // You'll need to add this call to your pagination logic
    $(document).on("paginationComplete", function() {
        updateLayerUI();
    });
    
    // Initial UI update
    updateLayerUI();
}

// Modified toggle function to track state
function toggleLayerAndTrackState(nameLayer, layerName, map, tr_id, layerVisibility) {
    var customId = nameLayer.replace("-layer-eye", "").replace("-layereye", "");
    
    if (map.hasLayer(layerName)) {
        map.removeLayer(layerName);
        $("#"+tr_id).css("background-color", "white");
        const eyeIcon = document.getElementById(nameLayer);
        if (eyeIcon) {
            eyeIcon.classList.remove("fa-eye");
            eyeIcon.classList.add("fa-eye-slash");
        }
        layerVisibility[customId] = false;
    } else {
        map.addLayer(layerName);
        $("#"+tr_id).css("background-color", "antiquewhite");
        const eyeIcon = document.getElementById(nameLayer);
        if (eyeIcon) {
            eyeIcon.classList.remove("fa-eye-slash");
            eyeIcon.classList.add("fa-eye");
        }
        layerVisibility[customId] = true;
    }
}