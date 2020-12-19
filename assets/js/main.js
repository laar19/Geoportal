function openNav() {
    document.getElementById("mySidebar").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
}

function closeNav() {
    document.getElementById("mySidebar").style.width = "0";
    document.getElementById("main").style.marginLeft= "0";
}

// Muestra el shapefile cargado
var show_shp = document.getElementById("show_shp");
show_shp.onclick = function() {
    points1.setVisible(show_shp.checked);
};

// Habilita dibujar sobre el mapa
var enable_draw = document.getElementById("enable_draw");
enable_draw.onclick = function() {
    if (enable_draw.checked == true) {
        map.addLayer(vector);
    }
    else {
        map.removeLayer(vector);
    }
};
