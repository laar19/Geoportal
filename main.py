import os

from dotenv import load_dotenv
load_dotenv()

from flask           import Flask, render_template, request
from flask_wtf       import CSRFProtect
from flask_paginate  import Pagination, get_page_parameter

from shapely.geometry import Polygon

from sqlalchemy.orm import sessionmaker

from app.models.models                 import DatabaseConfig
from app.models.functions              import *
from app.config                        import *

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
csrf = CSRFProtect(app)

# Default map config
MAP_ZOOM_LEVEL = os.getenv("MAP_ZOOM_LEVEL")
MAP_LAT        = os.getenv("MAP_LAT")
MAP_LONG       = os.getenv("MAP_LONG")
map_config     = get_map_config(MAP_ZOOM_LEVEL, MAP_LAT, MAP_LONG)

@app.route("/")
@app.route("/index")
def index_leaflet():
    return render_template(
        "index.html",
        geoserver_info = False,
        layers         = False,
        map_config     = map_config,
        error_         = False)

@app.route("/search", methods=["POST", "GET"])
def search():
    search = False
    q      = request.args.get("q")
    if q:
        search = True
        
    if request.method == "POST":
        DB          = os.getenv("DB")
        DB_HOST     = os.getenv("DB_HOST")
        DB_NAME     = os.getenv("DB_NAME")
        DB_USER     = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_PORT     = os.getenv("DB_PORT")
        
        DbConn       = DatabaseConfig(DB, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
        conn, engine = DbConn.connection()
        Session      = sessionmaker(bind=engine)
        db_session   = Session()
        
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

            try:
                formatted_coord_from_user3 = Polygon(formatted_coord_from_user2)
            except Exception as e:
                geoserver_info = False
                layers         = False
                
                return render_template(
                    "index.html",
                    geoserver_info = geoserver_info,
                    layers         = layers,
                    map_config     = map_config,
                    error_         = True
                )

            geoserver_info = {}
            geoserver_info["return"]        = False
            geoserver_info["geoserver_url"] = None
            geoserver_info["workspace"]     = None
            geoserver_info["service"]       = None
            geoserver_info["format"]        = None
            geoserver_info["transparent"]   = None
            
            layers = {}
            
            result = intersect(db_session, formatted_coord_from_user3)
            result_ = result+result+result+result+result
            if result:
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

                    layers[i[5]] = {
                        "custom_id"              : i[5],
                        "satellite"              : i[6],
                        "sensor"                 : i[7],
                        "capture_date"           : i[8],
                        "cutted_image_shape"     : i[9],
                        "solar_elevation"        : i[10],
                        "solar_azimuth"          : i[11],
                        "cloud_percentage"       : i[12],
                        "solar_irradiance"       : i[13],
                        "k_val"                  : i[14],
                        "b_val"                  : i[15],
                        "satellite_altitude"     : i[16],
                        "zenit_satellite_angle"  : i[17],
                        "satellite_azimuth_angle": i[18],
                        "roll_angle"             : i[19],
                        "compressed_file_path"   : i[20],
                    }

    error_ = False

    page = request.args.get(get_page_parameter(), type=int, default=1)
    #page     = request.args.get("page", type=int, default=1)
    per_page = 10
    
    pagination = Pagination(
        len(result_),
        page          = page,
        #page          = int(len(result)/2),
        #total         = int(len(result)/2),
        total         = len(result_),
        search        = search,
        per_page      = per_page,
        record_name   = "Rasters",
        css_framework = "bootstrap5"
    )
    
    if geoserver_info["return"] == False:
        geoserver_info = False
        layers         = False
        error_         = False

    return render_template(
        "index.html",
        geoserver_info = geoserver_info,
        #layers         = result[0:int(len(result)/2)],
        layers         = result_,
        map_config     = map_config,
        pagination     = pagination,
        error_         = error_
    )
    
if __name__ == "__main__":
    csrf.init_app(app)

    FLASK_HOST  = os.getenv("FLASK_HOST")
    FLASK_PORT  = os.getenv("FLASK_PORT")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG")
    #app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
    app.run(host="localhost", port=8892, debug=True)
