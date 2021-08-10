/*
var source = new ol.source.Vector();

var vector = new ol.layer.Vector({
    source: source,
    style: new ol.style.Style({
        fill: new ol.style.Fill({
            color: "rgba(255, 255, 255, 0.2)",
        }),
        stroke: new ol.style.Stroke({
            color: "#ffcc33",
            width: 2,
        }),
        image: new ol.style.Circle({
            radius: 7,
            fill: new ol.style.Fill({
                color: "#ffcc33",
            }),
        }),
    }),
});

var modify = new ol.interaction.Modify({source: source});
mapDiv.addInteraction(modify);

var draw, snap; // global so we can remove them later
var typeSelect = document.getElementById("draw_type");

function addInteractions() {
    draw = new ol.interaction.Draw({
        source: source,
        type: typeSelect.value,
    });
    mapDiv.addInteraction(draw);
    snap = new ol.interaction.Snap({source: source});
    mapDiv.addInteraction(snap);
}

/**
 * Handle change event.
 *
typeSelect.onchange = function () {
    mapDiv.removeInteraction(draw);
    mapDiv.removeInteraction(snap);
    addInteractions();
};

addInteractions();
*/

var source = new ol.source.Vector({
  wrapX: false
});

var typeSelect = document.getElementById('draw_type');

var draw; // global so we can remove it later
function addInteraction() {
  var value = typeSelect.value;
  if (value !== 'None') {
    var geometryFunction, maxPoints;
    if (value === 'Square') {
      value = 'Circle';
      geometryFunction = ol.interaction.Draw.createRegularPolygon(4);
    } else if (value === 'Box') {
      value = 'LineString';
      maxPoints = 2;
      geometryFunction = function(coordinates, geometry) {
        if (!geometry) {
          geometry = new ol.geom.Polygon(null);
        }
        var start = coordinates[0];
        var end = coordinates[1];
        geometry.setCoordinates([
          [start, [start[0], end[1]], end, [end[0], start[1]], start]
        ]);
        return geometry;
      };
    }
    draw = new ol.interaction.Draw({
      source: source,
      type: /** @type {ol.geom.GeometryType} */ (value),
      geometryFunction: geometryFunction,
      maxPoints: maxPoints
    });
    draw.on('drawend', function(e) {

      alert(e.feature.getGeometry().getExtent());
    })
    mapDiv.addInteraction(draw);
  }
}


/**
 * Handle change event.
 */
typeSelect.onchange = function() {
  mapDiv.removeInteraction(draw);
  addInteraction();
};

addInteraction();
