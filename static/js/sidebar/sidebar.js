/* Start basemaps */
var osm = new ol.layer.Tile({
    title  : "OSM", // A layer must have a title to appear in the layerswitcher
    type   : "base", // Again set this layer as a base layer
    visible: true,
    source : new ol.source.OSM()
});

var satelite = new ol.layer.Tile({
    title  : "Satelite", // A layer must have a title to appear in the layerswitcher
    type   : "base", // Again set this layer as a base layer
    visible: false,
    source : new ol.source.XYZ({
        attributions: ["Powered by Esri",
                       "Source: Esri, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community"],
        attributionsCollapsible: false,
        url: "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        maxZoom: 23
    })
});
/* End basemaps */

var mapDiv = new ol.Map({
    //target: "mapDiv",
    target: document.getElementById("mapDiv"),
    layers: [
        new ol.layer.Group({
            title : "Base maps", // A layer must have a title to appear in the layerswitcher
            layers: [osm, satelite]
        })
    ],
    //view: view
    view: view
});

/* Start sample data */
/*
var uk_layers = new ol.layer.Group({
    // A layer must have a title to appear in the layerswitcher
    title: "Sample_data",
    // Adding a "fold" property set to either "open" or "close" makes the group layer
    // collapsible
    fold: "open",
    layers: [
        new ol.layer.Image({
            // A layer must have a title to appear in the layerswitcher
            title: "Countries",
            source: new ol.source.ImageArcGISRest({
                ratio: 1,
                params: { LAYERS: "show:0" },
                url: "https://ons-inspire.esriuk.com/arcgis/rest/services/Administrative_Boundaries/Countries_December_2016_Boundaries/MapServer"
            })
        }),
        new ol.layer.Group({
            // A layer must have a title to appear in the layerswitcher
            title: "Census",
            fold: "open",
            layers: [
                new ol.layer.Image({
                    // A layer must have a title to appear in the layerswitcher
                    title: "Districts",
                    source: new ol.source.ImageArcGISRest({
                        ratio: 1,
                        params: { LAYERS: "show:0" },
                        url: "https://ons-inspire.esriuk.com/arcgis/rest/services/Census_Boundaries/Census_Merged_Local_Authority_Districts_December_2011_Boundaries/MapServer"
                    })
                }),
                new ol.layer.Image({
                    // A layer must have a title to appear in the layerswitcher
                    title: "Wards",
                    visible: false,
                    source: new ol.source.ImageArcGISRest({
                        ratio: 1,
                        params: { LAYERS: "show:0" },
                        url: "https://ons-inspire.esriuk.com/arcgis/rest/services/Census_Boundaries/Census_Merged_Wards_December_2011_Boundaries/MapServer"
                    })
                })
            ]
        })
    ]
});
*/
//mapDiv.addLayer(uk_layers);
/* End sample data */

// Get out-of-the-map div element with the ID "layers" and renders layers to it.
// NOTE: If the layers are changed outside of the layer switcher then you
// will need to call ol.control.LayerSwitcher.renderPanel again to refesh
// the layer tree. Style the tree via CSS.
var sidebar = new ol.control.Sidebar({
    element: "sidebar",
    position: "left"
});
var toc  = document.getElementById("layers");
var toc2 = document.getElementById("layers2");

mapDiv.on("rendercomplete",function(e) {
    var zoomLevel   = mapDiv.getView().getZoom();
    var zoomRounded = Math.round(zoomLevel*10)/10;
    document.getElementById("zoom-level").innerHTML = zoomRounded;
    document.getElementById("level-zoom").value     = zoomRounded;
    document.getElementById("center").value         = mapDiv.getView().getCenter();
});
