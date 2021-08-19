from werkzeug.security import generate_password_hash
import datetime

SECRET_KEY = generate_password_hash(str(datetime.datetime.now()))
