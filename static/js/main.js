// Update roll angle value
const roll_angle_value = document.querySelector("#roll_angle_value");
const roll_angle_      = document.querySelector("#roll_angle_");

roll_angle_value.textContent = "";
roll_angle_.addEventListener("input", (event) => {
    roll_angle_value.textContent = event.target.value;
});

// Update Cloud percentage value
const cloud_percentage_      = document.querySelector("#cloud_percentage_");
const cloud_percentage_value = document.querySelector("#cloud_percentage_value");

cloud_percentage_value.textContent = "";
cloud_percentage_.addEventListener("input", (event) => {
    cloud_percentage_value.textContent = event.target.value;
});
