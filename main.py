import json, base64, requests, hashlib

import pandas    as pd
import geopandas as gpd

from datetime import datetime as dtime

from flask     import Flask, render_template, request, jsonify
from flask_wtf import CSRFProtect

from io import BytesIO

from shapely.geometry import Point, Polygon

from sqlalchemy.orm import sessionmaker

from geo.Geoserver import Geoserver

from app.models.models                 import DatabaseConfig
from app.models.satellite_images_table import *
from app.config                        import *

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
csrf = CSRFProtect(app)

db_credentials_path = "config/db_credentials_geoportal.csv"

map_config_path = "config/map_config.csv"
map_config      = get_map_config(map_config_path)

@app.route("/")
@app.route("/index")
def index_leaflet():
    return render_template("index.html", geoserver_info=False, layers=False, map_config=map_config)

@app.route("/search", methods=["POST"])
def search():
    # Retrieve coordinates from user
    if request.method == "POST":
        previous_map_config = {
            "zoom_level"   : request.form["zoom_level"],
            "center"       : request.form["center"],
            "search_status": bool(request.form["search_status"])
        }

        # If there is an image search
        if previous_map_config["search_status"]:
            map_config = previous_map_config
            
            # Coordinates are received as string, so they are splited by comma
            # and converted into list of tuples wich contains coordinate pairs
            # The list of tuples is converted then into list of lists
            coord_from_user =  request.form["coordinates"].split(",")
            formatted_coord_from_user1 = [i for i in zip(coord_from_user[::2], coord_from_user[1::2])]
            formatted_coord_from_user2 = []
            for i in formatted_coord_from_user1:
                formatted_coord_from_user2.append(list(i))

            formatted_coord_from_user3 = Polygon(formatted_coord_from_user2)

            DbConn       = DatabaseConfig(db_credentials_path)
            conn, engine = DbConn.connection()
            Session      = sessionmaker(bind=engine)
            db_session   = Session()

            geoserver_info = {}
            geoserver_info["return"]        = False
            geoserver_info["geoserver_url"] = None
            geoserver_info["workspace"]     = None
            geoserver_info["service"]       = None
            geoserver_info["format"]        = None
            geoserver_info["transparent"]   = None
            
            layers = {}
            
            result = intersect(db_session, formatted_coord_from_user3)
            if result:
                layers_ = {}
                aux     = 0
                
                for i in result:
                    if geoserver_info["return"] == False:
                        geoserver_info["return"] = True
                        
                    if geoserver_info["geoserver_url"] == None:
                        geoserver_info["geoserver_url"] = i[0]
                        
                    if geoserver_info["workspace"] == None:
                        geoserver_info["workspace"] = i[1]
                        
                    if geoserver_info["service"] == None:
                        geoserver_info["service"] = i[2]

                    if geoserver_info["format"] == None:
                        geoserver_info["format"] = i[3]

                    if geoserver_info["transparent"] == None:
                        geoserver_info["transparent"] = i[4]

                    layers[aux] = i[5]
                    aux += 1
    
    if geoserver_info["return"] == False:
        geoserver_info = False
        layers         = False

    return render_template("index.html", geoserver_info=geoserver_info, layers=layers, map_config=map_config)
    
if __name__ == "__main__":
    csrf.init_app(app)
    app.run(host="localhost", port=5000, debug=True)
