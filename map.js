var source = new ol.source.Vector({wrapX: false});


    vector = new ol.layer.Vector({
        source: source,
        style: new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'rgba(0, 255, 0, 0.5)'
            }),
            stroke: new ol.style.Stroke({
                color: '#ffcc33',
                width: 2
            }),
            image: new ol.style.Circle({
                radius: 7,
                fill: new ol.style.Fill({
                color: '#ffcc33'
                })
            })
        })      
    });



    var map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            }),
            vector
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([37.41, 8.82]),
            zoom: 4
        })
    });



    var draw; // global so we can remove it later
    function addInteraction() 
    {
        var value = 'Box';

        if (value !== 'None') 
        {
            var geometryFunction, maxPoints;
            if (value === 'Square') 
            {
                value = 'Circle';
                geometryFunction = ol.interaction.Draw.createRegularPolygon(4);
            } 
            else if (value === 'Box') 
            {
                value = 'LineString';
                maxPoints = 2;
                geometryFunction = function(coordinates, geometry)
                {
                    if (!geometry) 
                    {
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

            map.addInteraction(draw);               
        }
    }

    draw.on('drawend',function(e){
alert(e.feature.getGeometry().getExtent());
});



    addInteraction();           
