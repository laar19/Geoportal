// Modified show_raster_info.js (fixes MutationObserver error)
var selectionLayer = null; // Global variable to store the highlight layer

// Utility: show a Bootstrap-style non-blocking alert that auto-dismisses
function showNonBlockingAlert(message, level) {
    try {
        const container = document.getElementById('alert-container') || document.body;
        const cls = level === 'success' ? 'alert-success' : (level === 'warning' ? 'alert-warning' : (level === 'danger' ? 'alert-danger' : 'alert-info'));
        const wrapper = document.createElement('div');
        wrapper.className = `alert ${cls} alert-dismissible fade show`;
        wrapper.setAttribute('role', 'alert');
        wrapper.style.position = container === document.body ? 'fixed' : '';
        if (container === document.body) {
            wrapper.style.top = '12px';
            wrapper.style.right = '12px';
            wrapper.style.zIndex = 2000;
            wrapper.style.maxWidth = '420px';
        }
        wrapper.innerHTML = `
            <div>${message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        container.appendChild(wrapper);
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            try {
                if (window.bootstrap && window.bootstrap.Alert) {
                    const alert = new window.bootstrap.Alert(wrapper);
                    alert.close();
                } else if (wrapper && wrapper.parentNode) {
                    wrapper.parentNode.removeChild(wrapper);
                }
            } catch (_) { }
        }, 5000);
    } catch (e) {
        // Fallback simple alert
        console.warn('Non-blocking alert:', message);
    }
}

function show_raster_info(map, geoserver_config, layers, error) {
    // If GeoServer is reported down, show a non-blocking alert and exit early
    try {
        if (typeof window !== 'undefined' && window.GEOSERVER_OK === false) {
            const msg = 'GeoServer is unavailable. Layers could not be loaded.';
            showNonBlockingAlert(msg, 'warning');
            return; // skip adding WMS layers
        }
    } catch (e) { /* no-op */ }
    var map_layers_list = [];
    var map_layers_dict = {};
    // Add a layer visibility tracker
    var layerVisibility = {};

    // Initialize Layer Customizer
    var layerCustomizer = null;
    if (typeof LayerCustomizer !== 'undefined') {
        layerCustomizer = new LayerCustomizer(map, geoserver_config);
        layerCustomizer.init();
        window.layerCustomizer = layerCustomizer; // Expose globally for debugging
    }

    // Check if layers exist and is not null/undefined
    if (!layers || Object.keys(layers).length === 0) {
        console.log("No layers provided or layers object is empty");
        return;
    }


    for (let key in layers) {
        var geoserver_url = geoserver_config["geoserver_url"] + "/" +
            layers[key]["geoserver_service"];

        var wmsLayer = L.tileLayer.wms(geoserver_url, {
            layers: layers[key]["custom_id"],
            format: layers[key]["geoserver_format"],
            transparent: layers[key]["geoserver_transparent"]
        }).addTo(map);

        // Handle tile load errors gracefully and inform the user once
        (function () {
            let alerted = false;
            wmsLayer.on('tileerror', function () {
                if (!alerted) {
                    alerted = true;
                    showNonBlockingAlert('Some map layers could not be fetched from GeoServer.', 'warning');
                }
            });
        })();

        var tmp = {
            layer_object: wmsLayer,
            layer_data: layers[key]
        };
        map_layers_list.push(tmp);
        map_layers_dict[layers[key]["custom_id"]] = wmsLayer;

        // Initialize all layers as visible
        layerVisibility[layers[key]["custom_id"]] = true;

        // Register layer with customizer
        if (layerCustomizer) {
            layerCustomizer.registerWMSLayer(layers[key]["custom_id"], wmsLayer, layers[key]);
        }
    }

    // Event delegation for customize button clicks
    $(document).on("click", ".customize-layer-btn", function (e) {
        e.preventDefault();
        e.stopPropagation();

        var layerName = $(this).data("layer");
        if (layerCustomizer && layerName) {
            // Try to detect geometry type from last clicked feature or default to Polygon
            var geometryType = window._lastGeometryType || 'Polygon';
            var layerData = layers[layerName] || {};
            layerCustomizer.selectLayer(layerName, layerData, geometryType);
        }
    });

    var info_adicional = {
        prueba1: "Hola todos",
        prueba2: "Cómo están"
    }

    map.on("click", async function (e) {
        // Remove existing highlight
        if (selectionLayer) {
            map.removeLayer(selectionLayer);
            selectionLayer = null;
        }

        // Sort layers by zIndex (highest first) to prioritize the top layer
        var activeLayers = map_layers_list
            .filter(layer => map.hasLayer(layer.layer_object))
            .sort((a, b) => {
                var ziA = a.layer_object.options.zIndex || 0;
                var ziB = b.layer_object.options.zIndex || 0;
                return ziB - ziA;
            });

        let foundFeature = false;
        let popupContent = "<div><table>";

        for (const layer of activeLayers) {
            var url = getFeatureInfoUrl(
                map,
                layer.layer_object,
                e.latlng,
                { "info_format": "application/json" }
            );

            try {
                const response = await fetch(parse_url(url));
                const data = await response.json();

                if (data.features && data.features.length > 0) {
                    var feature = data.features[0];
                    var properties = feature.properties;
                    var firstKey = Object.keys(properties)[0];
                    var firstValue = properties[firstKey];

                    // Store geometry type for layer customizer
                    if (feature.geometry && feature.geometry.type) {
                        window._lastGeometryType = feature.geometry.type;
                        window._lastClickedLayerName = layer.layer_data["name"];
                    }

                    popupContent +=
                        "<tr><td>Nombre de la Capa</td><td class='popup-table-value'>" + layer.layer_data["name"] + "</td></tr>" +
                        "<tr><td>" + firstKey + "</td><td class='popup-table-value'>" + firstValue + "</td></tr>";

                    popupContent += "</table></div>";

                    // Show highlight in red
                    selectionLayer = L.geoJSON(data, {
                        style: function () {
                            return {
                                color: "red",
                                weight: 2,
                                fillColor: "lightblue",
                                fillOpacity: 0.4
                            };
                        }
                    }).addTo(map);

                    L.popup()
                        .setLatLng(e.latlng)
                        .setContent(popupContent)
                        .openOn(map);

                    foundFeature = true;
                    break; // Stop at the first (highest) layer that has a feature
                }
            } catch (err) {
                console.warn("Error fetching feature info for layer:", layer.layer_data.name, err);
            }
        }

        // No popup is shown if no feature was found (foundFeature remains false)
    });

    // Event delegation for the image clicks
    $(document).on("click", ".image-to-layer img", function () {
        var customId = $(this).attr("id");

        // Check for customized layer first
        if (window.layerCustomizer && window.layerCustomizer.hasActiveOverlay(customId)) {
            var isVisible = window.layerCustomizer.toggleLayerVisibility(customId);
            layerVisibility[customId] = isVisible;
            updateLayerUI(); // Refresh UI to match new state
            return;
        }

        var layer = map_layers_dict[customId];
        toggleLayerAndTrackState(customId + "-layer-eye", layer, map, "div_" + customId, layerVisibility);
    });

    // Event delegation for the eye icon clicks
    $(document).on("click", ".overlay-to-layer", function () {
        var customId = $(this).siblings("img").attr("id");

        // Check for customized layer first
        if (window.layerCustomizer && window.layerCustomizer.hasActiveOverlay(customId)) {
            var isVisible = window.layerCustomizer.toggleLayerVisibility(customId);
            layerVisibility[customId] = isVisible;
            updateLayerUI(); // Refresh UI to match new state
            return;
        }

        var layer = map_layers_dict[customId];
        toggleLayerAndTrackState(customId + "-layereye", layer, map, "div_" + customId, layerVisibility);
    });

    // Add a function to update UI based on layer visibility state
    function updateLayerUI() {
        for (let layerId in layerVisibility) {
            const isVisible = layerVisibility[layerId];
            const eyeIcon = document.getElementById(layerId + "-layer-eye");
            const divElement = document.getElementById("div_" + layerId);

            if (eyeIcon) {
                if (isVisible) {
                    eyeIcon.classList.remove("fa-eye-slash");
                    eyeIcon.classList.add("fa-eye");
                    if (divElement) $(divElement).css("background-color", "antiquewhite");
                } else {
                    eyeIcon.classList.remove("fa-eye");
                    eyeIcon.classList.add("fa-eye-slash");
                    if (divElement) $(divElement).css("background-color", "white");
                }
            }
        }
    }

    // Fix for MutationObserver error - Only observe if element exists
    const paginationContainer = document.querySelector("#pagination-container");
    if (paginationContainer) {
        const observer = new MutationObserver(function (mutations) {
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
    $(document).on("paginationComplete", function () {
        updateLayerUI();
    });

    // Initialize SortableJS for drag-and-drop reordering
    var resultsContainer = document.getElementById('results-container');
    if (resultsContainer) {
        new Sortable(resultsContainer, {
            animation: 150,
            handle: '.info-layer', // Make the whole card draggable (or specify a handle)
            onEnd: function (evt) {
                // Get all layer elements in the new order
                var layerElements = Array.from(resultsContainer.querySelectorAll('.info-layer'));
                var totalLayers = layerElements.length;

                // Update z-index for each layer based on visual order
                // Visually top element = Highest z-index (draws on top)
                layerElements.forEach(function (el, index) {
                    // Extract layer name/ID from the element.
                    // We need to look at the inner structure:
                    // <div class="info-layer"> ... <span class="name-ly ...">{{ layer.name }} ... 
                    // Using the download link data attribute is safer if available
                    var downloadLink = el.querySelector('.download-layer-link');
                    if (downloadLink) {
                        var layerName = downloadLink.getAttribute('data-name');
                        var layer = map_layers_dict[layerName];
                        if (layer) {
                            // Calculate z-index: Top of list = Total Layers, Bottom = 1
                            var newZIndex = totalLayers - index;
                            layer.custom_id = layerName; // ensure ID matches
                            layer.setZIndex(newZIndex);
                            console.log("Updated z-index for " + layerName + ": " + newZIndex);
                        }
                    }
                });
            }
        });
    }

    // Event delegation for the download buttons
    $(document).on("click", ".download-layer-link", function () {
        var layerName = $(this).data("name");
        showNonBlockingAlert("Descarga (" + layerName + ") realizada con éxito", "success");
    });

    // Initial UI update
    updateLayerUI();
}

// Modified toggle function to track state
function toggleLayerAndTrackState(nameLayer, layerName, map, tr_id, layerVisibility) {
    var customId = nameLayer.replace("-layer-eye", "").replace("-layereye", "");

    if (map.hasLayer(layerName)) {
        map.removeLayer(layerName);
        $("#" + tr_id).css("background-color", "white");
        const eyeIcon = document.getElementById(nameLayer);
        if (eyeIcon) {
            eyeIcon.classList.remove("fa-eye");
            eyeIcon.classList.add("fa-eye-slash");
        }
        layerVisibility[customId] = false;
    } else {
        map.addLayer(layerName);
        $("#" + tr_id).css("background-color", "antiquewhite");
        const eyeIcon = document.getElementById(nameLayer);
        if (eyeIcon) {
            eyeIcon.classList.remove("fa-eye-slash");
            eyeIcon.classList.add("fa-eye");
        }
        layerVisibility[customId] = true;
    }
}