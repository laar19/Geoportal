function toggleLayer(layerName, map, tr_id) {
    if (map.hasLayer(layerName)) {
        map.removeLayer(layerName);
        $("#"+tr_id).css("background-color", "white");
    }
    else {
        map.addLayer(layerName);
        $("#"+tr_id).css("background-color", "antiquewhite");
    }
}

// Get the GetFeatureInfo URL
function getFeatureInfoUrl(map, layer, latlng, params) {
    var point = map.latLngToContainerPoint(latlng, map.getZoom());
    var size  = map.getSize();

    var bounds = map.getBounds();
    var sw     = bounds.getSouthWest();
    var ne     = bounds.getNorthEast();

    var defaultParams = {
        request     : "GetFeatureInfo",
        service     : "WMS",
        srs         : "EPSG:4326",
        styles      : "",
        transparent : true,
        version     : "1.1.1",
        format      : "image/png",
        bbox        : sw.lng + "," + sw.lat + "," + ne.lng + "," + ne.lat,
        height      : size.y,
        width       : size.x,
        layers      : layer.wmsParams.layers,
        query_layers: layer.wmsParams.layers,
        info_format : "text/html"
    };

    params = L.Util.extend(defaultParams, params);

    params[params.version === "1.3.0" ? "i" : "x"] = point.x;
    params[params.version === "1.3.0" ? "j" : "y"] = point.y;

    return layer._url + L.Util.getParamString(params, layer._url, true);
}

// Parse geoserver url to strip decimals
function parse_url(url) {
    const urlObj = new URL(url);
    const params = new URLSearchParams(urlObj.search);
    const x = parseInt(params.get("X"));
    const y = parseInt(params.get("Y"));
    
    params.set("X", x.toString());
    params.set("Y", y.toString());
    urlObj.search = params.toString();

    return urlObj.toString();

    /*
    // Example usage:
    const url = "http://localhost:8870/geoserver/wms?REQUEST=GetFeatureInfo&SERVICE=WMS&SRS=EPSG%3A4326&STYLES=&TRANSPARENT=true&VERSION=1.1.1&FORMAT=image%2Fpng&BBOX=-117.3715823598904%2C43.52560864329998%2C-117.33729299984398%2C43.54427564466141&HEIGHT=600&WIDTH=799&LAYERS=kesPolygon&QUERY_LAYERS=kesPolygon&INFO_FORMAT=application%2Fjson&X=450.09654676445825&Y=528.6470642089844";
    const updatedURL = parse_url(url);
    console.log(updatedURL);
    */
}
