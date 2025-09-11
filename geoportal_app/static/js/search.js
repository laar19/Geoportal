document.addEventListener("DOMContentLoaded", function () {
    const sidebar_ab = document.getElementById("sidebar");
    const inf = document.getElementById("information");
    const inf2 = document.getElementById("informacion");
    const url = window.location.href;

    // Función para validar la URL
    function isSafeUrl(url) {
        const safePattern = /^[a-zA-Z0-9\-._~:/?#[\]@!$&'()*+,;=%]+$/;
        return safePattern.test(url);
    }

    // Función principal
    function mostrarinfo() {
        if (
            inf &&
            inf2 &&
            sidebar_ab &&
            isSafeUrl(url) &&
            url.includes("&search_status=")
        ) {
            inf.classList.add("active");
            inf2.classList.add("active");
            sidebar_ab.classList.remove("collapsed");
        }
    }

    // Ejecutar la función
    mostrarinfo();
});