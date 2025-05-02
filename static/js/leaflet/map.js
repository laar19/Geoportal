var map = L.map('map');
L.tileLayer(map_config["tilelayer_url"], {
    //maxZoom: 19,
    attribution: map_config["tilelayer_attribution"]
}).addTo(map);

// If there was an image search, set the las user view at the moment
// of the search
if(map_config["search_status"]) {
    map.setView(
        map_config["center"].split(","),
        map_config["zoom_level"]
    );
}
else {
    map.setView(
        map_config["center"],
        map_config["zoom_level"]
    );
}
