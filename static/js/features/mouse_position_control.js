var mousePositionControl = new ol.control.MousePosition({
    coordinateFormat: ol.coordinate.createStringXY(6),
    projection: main_projection,
    // comment the following two lines to have the mouse position
    // be placed within the map.
    className    : "custom-mouse-position",
    target       : document.getElementById("mouse-position"),
    undefinedHTML: "&nbsp;",
});

var projectionSelect = document.getElementById("projection");
projectionSelect.addEventListener("change", function (event) {
    mousePositionControl.setProjection(event.target.value);
    main_projection = event.target.value;
});
  
var precisionInput = document.getElementById("precision");
precisionInput.addEventListener("change", function (event) {
    var format = ol.coordinate.createStringXY(event.target.valueAsNumber);
    mousePositionControl.setCoordinateFormat(format);
});

mapDiv.addControl(mousePositionControl);
