import json

import pandas as pd

import sqlalchemy as db
from sqlalchemy_utils import create_database, database_exists

from datetime import datetime as dtime

from werkzeug.security import generate_password_hash

SECRET_KEY = generate_password_hash(str(dtime.now()))

proj_4326 = 4326
#proj_3857 = 3857
main_projection = proj_4326;

class MapDiv:
    def main_config(self):
        center = [-65.89003678746177, 8.016859315038008]
        zoom   = 5.5

        return {"center": center, "zoom": zoom}
