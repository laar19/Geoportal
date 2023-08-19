var editableLayers = new L.FeatureGroup();
map.addLayer(editableLayers);

var options = {
    position: 'topleft',
    draw: {
        marker: false,
        polyline: false,
        /*
        polyline: {
            shapeOptions: {
                color: '#f357a1',
                weight: 10
            }
        },
        */
        polygon: false,
        /*
        polygon: {
            allowIntersection: false, // Restricts shapes to simple polygons
            drawError: {
                color: '#e1e100', // Color the shape will turn when intersects
                message: '<strong>Oh snap!<strong> you can\'t draw that!' // Message that will show when intersect
            },
            shapeOptions: {
                //color: '#bada55'
                color: 'red'
            }
        },
        */
        circle: false, // Turns off this drawing tool
        //rectangle: false,
        rectangle: {
            shapeOptions: {
                clickable: false,
                color: 'red'
            }
        }
    },
    /*
    edit: {
        featureGroup: editableLayers, //REQUIRED!!
        remove: false
    }
    */
};
var drawControl = new L.Control.Draw(options);
map.addControl(drawControl);

// Get coordinates, view and zoom
map.on(L.Draw.Event.CREATED, function (e) {
    var type  = e.layerType,
        layer = e.layer;
        
    if(editableLayers && editableLayers.getLayers().length!==0) {
        editableLayers.clearLayers();
    }
    editableLayers.addLayer(layer);

    // Coordinates
    var coordinates = layer.toGeoJSON().geometry.coordinates;
    $("#coordinates").val(coordinates);

    // Zoom
    $("#zoom_level").val(map._zoom);

    // View
    /*
    map.on('dragend', function onDragEnd(){
    var width  = map.getBounds().getEast() - map.getBounds().getWest();
    var height = map.getBounds().getNorth() - map.getBounds().getSouth();
    alert (
        'center:' + map.getCenter() +'\n'+
        'width:' + width +'\n'+
        'height:' + height +'\n'+
        'size in pixels:' + map.getSize()
    )});
    */
    $("#center").val([map.getCenter()["lat"], map.getCenter()["lng"]]);

    $("#search_status").val("True");
});

// Custom control
/*
L.Control.Button = L.Control.extend({
    options: {
        position: 'topleft'
    },
    onAdd: function (map) {
        var container   = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
        var button      = L.DomUtil.create('a', 'search-button leaflet-control-button', container);
        L.DomEvent.disableClickPropagation(button);
        L.DomEvent.on(button, 'click', function(){
            $("#satellite").val($("#select_satellite").val());
            document.getElementById("search").submit();
        });

        container.title = "Search";

        return container;
    },
    onRemove: function(map) {},
});
var control = new L.Control.Button()
control.addTo(map);
*/

/*
new L.cascadeButtons([
    {icon: 'bi bi-geo-alt-fill', ignoreActiveState:true , command: () =>{console.log('test') }},
    {icon: 'bi bi-fullscreen', ignoreActiveState:true , command: () =>{console.log('test') }},
], {position:'topleft', direction:'vertical'}).addTo(map);
*/

new L.cascadeButtons([
    // {icon: 'fas fa-home', ignoreActiveState:true , command: () =>{console.log('test') }},
    /*
    {icon: 'bi bi-crop', items:[
        {icon: 'bi bi-square', command: () =>{console.log('hola')}},
        {icon: 'bi bi-circle', command: () =>{console.log('hola')}},
        {icon: 'bi bi-pentagon', command: () =>{console.log('hola')}},
       
    ]},

    {icon: 'bi bi-layers', items: [
        {icon: 'bi bi-1-circle', command: () =>{console.log('hola')}},
        {icon: 'bi bi-2-circle', command: () =>{console.log('hola')}},
        {icon: 'bi bi-3-circle', command: () =>{console.log('hola')}},
    ]},
    */

    {
        icon: 'bi-search', command: () => {
            $("#satellite").val($("#select_satellite").val());

            if ($("#sensor_pan").is(":checked")) {
                $("#pan").val($("#sensor_pan").val());
            }
            else {
                $("#pan").val(false);
            }
            if ($("#sensor_mss").is(":checked")) {
                $("#mss").val($("#sensor_mss").val());
            }
            else {
                $("#mss").val(false);
            }

            $("#orbit").val($("#orbit_").val());
            $("#scene").val($("#scene_").val());
            $("#start_date").val($("#start_date_").val());
            $("#end_date").val($("#end_date_").val());
            $("#roll_angle").val($("#roll_angle_value").val());
            $("#cloud_percentage").val($("#cloud_percentage_value").val());
            
            document.getElementById("search").submit();
        }
    },
    
    {icon: 'bi bi-share', items: [
        {icon: 'bi bi-twitter', command: () =>{console.log('hola')}},
        {icon: 'bi bi-facebook', command: () =>{console.log('hola')}},
        {icon: 'bi bi-instagram', command: () =>{console.log('hola')}},
        {icon: 'fbi bi-whatsapp', command: () =>{console.log('hola')}},
    ]},
], {position:'topleft', direction:'vertical'}).addTo(map);

//L.Control.geocoder().addTo(map);

var sidebar1 = L.control.sidebar('sidebar').addTo(map);

var sidebar2 = L.control.sidebar('sidebar1', {position: 'right'}).addTo(map);
//var sidebar2 = L.control.sidebar('sidebar1').addTo(map);
