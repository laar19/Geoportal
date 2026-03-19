// Event delegation approach for layer toggle functionality
// This works with both initial and dynamically loaded content
$(document).ready(function() {
    //console.log("Pagination fix script loaded");
    
    // Setup AJAX headers
    $.ajaxSetup({
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    });

    // Remove any existing event handlers to prevent duplicates
    $(document).off("click", ".toggle-ly");
    
    // Use event delegation for layer toggling - works for all content
    $(document).on("click", ".toggle-ly", function(event) {
        //console.log("Layer toggle clicked");
        event.stopPropagation(); // Prevent click from affecting other elements
        var content = $(this).closest(".info-layer").find(".contenido");
        
        // Toggle visibility with flex display
        if (content.css("display") === "none" || content.css("display") === "") {
            content.css("display", "flex");
        } else {
            content.css("display", "none");
        }
    });

    // Handle pagination links
    $(document).off("click", ".pagination a");
    $(document).on("click", ".pagination a", function(e) {
        //console.log("Pagination link clicked");
        e.preventDefault();
        var url = $(this).attr("href");
        
        $.get(url, function(data) {
            //console.log("Pagination data received");
            $("#pagination-container").html(data.pagination);
            $("#results-container").html(data.results);
        });
    });

    // Auto-expand the layers list if we're on a search page
    if (window.location.href.includes("&search_status=")) {
        //console.log("Search page detected");
        // Make sure the sidebar is open
        var sidebar = $("#sidebar");
        if (sidebar.hasClass("collapsed")) {
            sidebar.removeClass("collapsed");
        }
        
        // Activate the information tab
        $("#information").addClass("active");
        $("#informacion").addClass("active");
    }
});

// For older browsers that might not properly handle document.ready with dynamically loaded content
window.addEventListener("load", function() {
    console.log("Window loaded");
});