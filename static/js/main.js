// Update roll angle value
const roll_angle_value = document.querySelector("#roll_angle_value");
const roll_angle_      = document.querySelector("#roll_angle_");

roll_angle_value.textContent = false;
roll_angle_.addEventListener("input", (event) => {
    roll_angle_value.textContent = event.target.value;
});
