

/*
document.addEventListener('click', function(event) {
    // Check if the clicked element's ID ends with '-layer-eye'
    if (event.target.id && event.target.id.endsWith('-layer-eye')) {
        // Toggle between fa-eye and fa-eye-slash classes
        if (event.target.classList.contains('fa-eye')) {
            event.target.classList.remove('fa-eye');
            event.target.classList.add('fa-eye-slash');
        } else if (event.target.classList.contains('fa-eye-slash')) {
            event.target.classList.remove('fa-eye-slash');
            event.target.classList.add('fa-eye');
        }
    }
});
*/
$(document).ready(function() {
    // Universal Basemap Toggle logic (LandViewer style)
    $('#basemap-toggle').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (typeof map !== 'undefined' && typeof baseOSM !== 'undefined' && typeof baseEsri !== 'undefined') {
            if (map.hasLayer(baseOSM)) {
                map.removeLayer(baseOSM);
                baseEsri.addTo(map);
                $(this).find('i').removeClass('fa-layer-group').addClass('fa-globe');
            } else {
                map.removeLayer(baseEsri);
                baseOSM.addTo(map);
                $(this).find('i').removeClass('fa-globe').addClass('fa-layer-group');
            }
        }
    });
});
