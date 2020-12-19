// Load shapefile by wms

var points1 = new ol.layer.Image({
    source: new ol.source.ImageWMS({
        url: "http://localhost:8080/geoserver/geoabae/wms",
        params: {
            "LAYERS": "geoabae:primary-777_polygons",
            "VERSION": "1.1.1",
            "FORMAT": "image/png",
            "TILED": true,
            "exceptions": "application/vnd.ogc.se_inimage",
        }
    })
});

var points2 = new ol.layer.Image({
    source: new ol.source.ImageWMS({
        url: "http://localhost:8080/geoserver/geoabae/wms",
        params: {
            "LAYERS": "geoabae:centros_pob_wgs84",
            "VERSION": "1.1.1",
            "FORMAT": "image/png",
            "TILED": true,
            "exceptions": "application/vnd.ogc.se_inimage",
        }
    })
});

map.addLayer(points1);
map.addLayer(points2);
points1.setVisible(false);
