// select interaction working on "click"
var selectClick = new ol.interaction.Select({
    condition: ol.events.condition.click
});

var select = selectClick; // ref to currently selected interaction

var enable_select = document.getElementById("enable_select");
function enable_select_interaction() {
    if(enable_select.checked) {
        typeSelect.disabled = false;
        mapDiv.removeInteraction(select);
        mapDiv.addInteraction(select);
    }
    else {
        typeSelect.disabled = true;
        mapDiv.removeInteraction(select);
    }
}
