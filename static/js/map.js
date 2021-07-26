basemap = new ol.layer.Tile({
    source: new ol.source.OSM()
});

var view = new ol.View({
    projection: "EPSG:4326",
    //center: ol.proj.transform([0, 0], 'EPSG:4326', 'EPSG:3857'),
    center    : [0, 0],
    zoom      : 2
});

var map = new ol.Map({
    controls: ol.control.defaults({
        attribution: false,
        zoom: false,
    }),
    
    target: "map",
    layers: [basemap],
    view  : view
});
