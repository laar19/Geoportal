import pandas as pd

from datetime import datetime as dtime

from werkzeug.security import generate_password_hash

SECRET_KEY = generate_password_hash(str(dtime.now()))

def get_map_config(path, position=0):
    data       = pd.read_csv(path)

    map_config = {
        "zoom_level": int(data["zoom_level"][position]),
        "center"    : [float(data["lat"][position]), float(data["long"][position])]
    }

    return map_config
