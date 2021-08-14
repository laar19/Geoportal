//var coordinates = [-64.691679, 5.972876];

/*
var content = document.getElementById("popup-content");

straitSource = new ol.source.Vector({
    wrapX: true
});
var straitsLayer = new ol.layer.Vector({
    source: straitSource
});
mapDiv.addLayer(straitsLayer);

// Popup showing the position the user clicked
var container = document.getElementById("popup");
var popup = new ol.Overlay({
    element: container,
    autoPan: true,
    autoPanAnimation: {
        duration: 250
    }
});
mapDiv.addOverlay(popup);


// Add a pointermove handler to the map to render the popup.

mapDiv.on("pointermove", function (evt) {
    var feature = mapDiv.forEachFeatureAtPixel(evt.pixel, function (feat, layer) {
        return feat;
    });

    if (feature && feature.get("type") == "Point") {
        var coordinate = evt.coordinate;    //default projection is EPSG:3857 you may want to use ol.proj.transform
        content.innerHTML = feature.get("desc");
        popup.setPosition(coordinate);
    }
    else {
        popup.setPosition(undefined);
    }
});



/*
mapDiv.on("pointermove", function (event) {
    if (mapDiv.hasFeatureAtPixel(event.pixel) === true) {
        var coordinate = event.coordinate;

        content.innerHTML = straitSource.uidIndex_["34"].values_.desc;
        popup.setPosition(coordinate);
    }
    else {
        popup.setPosition(undefined);
    }
});
*


//var data=[{"Lon":19.455128,"Lat":41.310575},{"Lon":19.455128,"Lat":41.310574},{"Lon":19.457388,"Lat":41.300442},{"Lon":19.413507,"Lat":41.295189},{"Lon":16.871931,"Lat":41.175926},{"Lon":16.844809,"Lat":41.151096},{"Lon":16.855165,"Lat":45}];

var data = [
    {"Lon":coordinates[0],"Lat":coordinates[1]}
];


function addPointGeom(data) {
    data.forEach(function(item) { //iterate through array...
        var longitude = item.Lon;
        var latitude  = item.Lat;

        var iconFeature = new ol.Feature({
            //geometry: new ol.geom.Point([longitude, latitude]),
            geometry: new ol.geom.Point(ol.proj.transform([longitude, latitude], "EPSG:4326", "EPSG:3857")),
            type: "Point",
            desc: "<pre> <b>Waypoint Details </b> " + "<br>" + "Latitude : " + latitude + "<br>Longitude: " + longitude + "</pre>"
        });

        var iconStyle = new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 5,
                    stroke: new ol.style.Stroke({
                        color: "blue"
                    }),
                    fill: new ol.style.Fill({
                        color: [57, 228, 193, 0.84]
                    })
                })
            });

        iconFeature.setStyle(iconStyle);
        straitSource.addFeature(iconFeature);
    });
}// End of function showStraits()

addPointGeom(data);
*/




var container = document.getElementById("popup");
var content   = document.getElementById("popup-content");
var closer    = document.getElementById("popup-closer");
// Popup showing the position the user clicked
var container = document.getElementById("popup");
var popup = new ol.Overlay({
    element: container,
    autoPan: true,
    autoPanAnimation: {
        duration: 250
    }
});
mapDiv.addOverlay(popup);



var coordinates = [-64.691679, 5.972876];
let marcador = new ol.Feature({
    geometry: new ol.geom.Point(
        ol.proj.fromLonLat(coordinates)// En dónde se va a ubicar
    ),
});

 marcador.setStyle(new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 5,
                    stroke: new ol.style.Stroke({
                        color: "blue"
                    }),
                    fill: new ol.style.Fill({
                        color: [57, 228, 193, 0.84]
                    })
                })
            }));

// Agregamos icono
/*
marcador.setStyle(new ol.style.Style({
    image: new ol.style.Icon({
        src: "https://cdns.iconmonstr.com/wp-content/assets/preview/2021/240/iconmonstr-bed-9.png",
    })
}));
*/

// marcadores debe ser un arreglo
const marcadores = []; // Arreglo para que se puedan agregar otros más tarde

marcadores.push(marcador);// Agregamos el marcador al arreglo

let capa = new ol.layer.Vector({
    source: new ol.source.Vector({
        features: marcadores, // A la capa le ponemos los marcadores
    }),
});
// Y agregamos la capa al mapa
mapDiv.addLayer(capa);

//mapDiv.on('pointermove', function(evt) {
/*
mapDiv.on('singleclick', function(evt) {
    var feature = mapDiv.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
        // Aquí se puede filtrar la feature
        return feature;
    });
    if (feature) {
        var latitude = "example";
        var longitude = "example";
        //alert("Click en: ", feature);
        //content.innerHTML = feature.get("desc");
        content.innerHTML = "<pre> <b>Waypoint Details </b> " + "<br>" + "Latitude : " + latitude + "<br>Longitude: " + longitude + "</pre>"
        popup.setPosition(ol.proj.fromLonLat(coordinates));
    }
    else {
        popup.setPosition(undefined);
    }
});
*/

closer.onclick = function () {
    popup.setPosition(undefined);
    closer.blur();
    return false;
};

mapDiv.on("singleclick", function (event) {
    if (mapDiv.hasFeatureAtPixel(event.pixel) === true) {
        var coordinate = event.coordinate;

        var latitude = "example";
        var longitude = "example";

        content.innerHTML = content.innerHTML = "<pre> <b>Waypoint Details </b> " + "<br>" + "Latitude : " + latitude + "<br>Longitude: " + longitude + "</pre>"
        popup.setPosition(ol.proj.fromLonLat(coordinates));
    }
    /*
    else {
        popup.setPosition(undefined);
        closer.blur();
    }
    */
});
