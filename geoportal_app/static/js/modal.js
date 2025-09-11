var modal = document.getElementById("aboutm");
var btn = document.getElementById("about");
var span = document.getElementsByClassName("closes")[0];
btn.onclick = function() {
modal.style.display = "block";
}
span.onclick = function() {
modal.style.display = "none";
}
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}    