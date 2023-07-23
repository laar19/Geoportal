var map = L.map('map');
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
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
