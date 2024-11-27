document.addEventListener("DOMContentLoaded", function() {
    var toggles = document.querySelectorAll(".toggle-ly");

    toggles.forEach(function(toggle) {
        toggle.addEventListener("click", function(event) {
            event.stopPropagation(); // Evita que el clic afecte otros elementos
            var content = this.closest(".info-layer").querySelector(".contenido");
            if (content.style.display === "none" || content.style.display === "") {
                content.style.display = "block";
            } else {
                content.style.display = "none";
            }
        });
    });
});



