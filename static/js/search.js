var sidebar_ab = document.getElementById("sidebar");
var inf = document.getElementById("information");
var inf2 = document.getElementById("informacion");
var url = window.location.href;

function mostrarinfo() {
    if (url.includes("&search_status=True")) {
        inf.classList.add("active");
        inf2.classList.add("active");
        sidebar_ab.classList.remove("collapsed");
    }
}

window.onload = function() {
    mostrarinfo();
};