import pandas as pd

from datetime import datetime as dtime

from werkzeug.security import generate_password_hash

SECRET_KEY = generate_password_hash(str(dtime.now()))

def get_map_config(zoom_level, lat, long_):
    map_config = {
        "coordinates"  : [float(lat), float(long_)],
        "zoom_level"   : int(zoom_level),
        "center"       : [float(lat), float(long_)],
        "search_status": False
    }

    return map_config
