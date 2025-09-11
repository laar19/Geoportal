const openModalBtn = document.getElementById('open-modal-btn');
const closeModalBtn = document.getElementById('close-modal-btn');
const myModal = document.getElementById('myModal');

const viewsRegisterLink = document.getElementById('views-register');
const viewsLoginLink = document.getElementById('views-login');
const formLogin = document.getElementById('form-login');
const formRegister = document.getElementById('form-register');

openModalBtn.addEventListener('click', () => {
    myModal.style.display = 'flex';
});

closeModalBtn.addEventListener('click', () => {
    myModal.style.display = 'none';
});

viewsRegisterLink.addEventListener('click', (sesion) => {
    sesion.preventDefault();
    formLogin.style.display = 'none';
    formRegister.style.display = 'block';
});

viewsLoginLink.addEventListener('click', (signup) => {
    signup.preventDefault();
    formLogin.style.display = 'block';
    formRegister.style.display = 'none';
});
