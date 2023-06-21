import json

import sqlalchemy as db
from sqlalchemy_utils import create_database, database_exists

import pandas as pd

import datetime

from werkzeug.security import generate_password_hash

SECRET_KEY = generate_password_hash(str(datetime.datetime.now()))

#######################################################################
# Begin map config

proj_4326 = 4326
#proj_3857 = 3857
main_projection = proj_4326;

class MapDiv:
    def main_config(self):
        center = [-65.89003678746177, 8.016859315038008]
        zoom   = 5.5

        return {"center": center, "zoom": zoom}
        
# End map config
#######################################################################

def set_config():
    
    with open("config.json") as json_data:
        d = json.load(json_data)
    
    print("1- Localhost")
    print("2- Pythonanywhere")
    print("3- Heroku")
    
    opc = int(input("Choose of the options above: "))

    if opc == 1:
        return d["localhost"]
    elif opc == 2:
        return d["pythonanywhere"]
    elif opc == 3:
        return d["heroku"]
    else:
        return None
