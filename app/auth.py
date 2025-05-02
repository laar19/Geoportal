# auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from flask import request
from flask_login import login_user, logout_user, login_required
from flask import g, current_app
from .models.User import User
from .db import db
import os
import re
from dotenv import load_dotenv

import pdb

# Categories : success, info, warning, danger

auth = Blueprint('auth', __name__)


load_dotenv()

# Default map config
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # Verify reCAPTCHA
    recaptcha_response = request.form.get('g-recaptcha-response')
    if not recaptcha_response:
        flash('Please complete the reCAPTCHA.', 'danger' )
        return redirect(url_for('index_leaflet'))

    data = {
        'secret': RECAPTCHA_SECRET_KEY,  # Replace with your Secret Key
        'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()

    if not result.get('success'):
        flash('reCAPTCHA verification failed. Please try again.', 'danger' )
        return redirect(url_for('index_leaflet'))
    
    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password): 
        flash('Por favor, compruebe sus datos de acceso y vuelva a intentarlo.', 'danger' )
        return redirect(url_for('index_leaflet')) # if user doesn't exist or password is wrong, reload the page
    
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember) # store user id in session
    flash('Ingreso exitoso', 'success')
    return redirect(url_for('index_leaflet'))

@auth.route('/signup')
def signup():
    return render_template('index_leaflet')

@auth.route('/signup', methods=['POST'])
def signup_post():

    name = request.form.get('name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    password_to_confirm = request.form.get('password_to_confirm')

    
    # Verify reCAPTCHA (same process as login)
    recaptcha_response = request.form.get('g-recaptcha-response')
    if not recaptcha_response:
        flash('Please complete the reCAPTCHA.', 'danger' )
        return redirect(url_for('index_leaflet'))

    data = {
        'secret': RECAPTCHA_SECRET_KEY,  # Replace with your Secret Key
        'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()

    if not result.get('success'):
        flash('reCAPTCHA verification failed. Please try again.', 'danger' )
        return redirect(url_for('index_leaflet'))


    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    # Name and Last Name validation
    name_regex = r"^[a-zA-ZÁÉÍÓÚÜÑáéíóúüñ\s]+$"
    last_name_regex = r"^[a-zA-ZÁÉÍÓÚÜÑáéíóúüñ\s]+$"

    if not re.match(name_regex, name):
        flash('El Nombre no es válido', 'danger')
        return redirect(url_for('auth.signup'))
    if not re.match(last_name_regex, last_name):
        flash('El Apellido no es válido', 'danger')
        return redirect(url_for('index_leaflet'))
    
    if user: # if a user is found, we want to redirect back to signup page so user can try again  
        flash('El email ya existe', 'danger')
        return redirect(url_for('index_leaflet'))
    
    # Password validation
    if len(password) < 8:
        flash('La contraseña debe de tener al menos 8 caracteres', 'danger')
        return redirect(url_for('index_leaflet'))

    if password != password_to_confirm:
        flash('Los campos contraseña y confirmar contraseñas no coinciden', 'danger')
        return redirect(url_for('index_leaflet'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email, name=name, last_name=last_name, password=generate_password_hash(password))
    
    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    
    flash('Registro exitoso', 'success')
    return redirect(url_for('index_leaflet'))
        


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('index_leaflet'))