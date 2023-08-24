import os

from dotenv import load_dotenv
load_dotenv()

from flask          import Flask, render_template, request
from flask_wtf      import CSRFProtect
from flask_paginate import Pagination, get_page_parameter

from shapely.geometry import Polygon

from sqlalchemy.orm import sessionmaker

from app.models.models    import DatabaseConfig
from app.models.functions import *
from app.config           import *

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
        geoserver_config = False,
        layers           = False,
        result           = False,
        map_config       = map_config,
        pagination       = False,
        error_           = False
    )

@app.route("/search", methods=["GET"])
def search():
    """
    search = False
    q      = request.args.get("q")
    if q:
        search = True
    """
    search   = True
    #page     = request.args.get("page", type=int, default=1)
    page     = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5
    offset   = (page - 1) * per_page
        
    if request.method == "GET":
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
            "zoom_level"   : request.args.get("zoom_level"),
            "center"       : request.args.get("center"),
            "search_status": bool(request.args.get("search_status"))
        }

        # If there is an image search
        if previous_map_config["search_status"]:
            map_config = previous_map_config
            
            # Coordinates are received as string, so they are splited by comma
            # and converted into list of tuples wich contains coordinate pairs
            # The list of tuples is converted then into list of lists
            coord_from_user =  request.args.get("coordinates").split(",")
            formatted_coord_from_user1 = [i for i in zip(coord_from_user[::2], coord_from_user[1::2])]
            formatted_coord_from_user2 = []
            for i in formatted_coord_from_user1:
                formatted_coord_from_user2.append(list(i))

            try:
                formatted_coord_from_user3 = Polygon(formatted_coord_from_user2)
            except Exception as e:
                formatted_coord_from_user3 = False

            geoserver_config = {}
            geoserver_config["return"]        = False
            geoserver_config["geoserver_url"] = None
            geoserver_config["workspace"]     = None
            geoserver_config["service"]       = None
            geoserver_config["format"]        = None
            geoserver_config["transparent"]   = None

            filters = {}

            filters["coordinates"] = formatted_coord_from_user3
                
            if request.args.get("satellite") != "ALL":
                filters["satellite"] = request.args.get("satellite")
            else:
                filters["satellite"] = False

            if request.args.get("pan") != "false":
                filters["sensor_pan"] = request.args.get("pan")
            else:
                filters["sensor_pan"] = False

            if request.args.get("mss") != "false":
                filters["sensor_mss"] = request.args.get("mss")
            else:
                filters["sensor_mss"] = False
                
            if request.args.get("orbit") != "false":
                filters["orbit"] = request.args.get("orbit")
            else:
                filters["orbit"] = False
                
            if request.args.get("scene") != "false":
                filters["scene"] = request.args.get("scene")
            else:
                filters["scene"] = False
                
            if request.args.get("start_date") != "false":
                filters["start_date"] = request.args.get("start_date")
            else:
                filters["start_date"] = False
                
            if request.args.get("end_date") != "false":
                filters["end_date"] = request.args.get("end_date")
            else:
                filters["end_date"] = False
                
            if request.args.get("roll_angle") != "false":
                filters["roll_angle"] = request.args.get("roll_angle")
            else:
                filters["roll_angle"] = False
                
            if request.args.get("cloud_percentage") != "false":
                filters["cloud_percentage"] = request.args.get("cloud_percentage")
            else:
                filters["cloud_percentage"] = False

            result        = intersect(db_session, filters)
            result_render = result.limit(per_page).offset(offset)

            layers = {}
            if result:
                geoserver_config_ = get_geoserver_config(db_session)
                
                if geoserver_config["return"] == False:
                    geoserver_config["return"] = True
                    
                if geoserver_config["geoserver_url"] == None:
                    geoserver_config["geoserver_url"] = geoserver_config_[0].url
                    
                if geoserver_config["workspace"] == None:
                    geoserver_config["workspace"] = geoserver_config_[0].workspace
                    
                if geoserver_config["service"] == None:
                    geoserver_config["service"] = geoserver_config_[0].service

                if geoserver_config["format"] == None:
                    geoserver_config["format"] = geoserver_config_[0].format_

                if geoserver_config["transparent"] == None:
                    geoserver_config["transparent"] = geoserver_config_[0].transparent

                for i in result.all():
                    layers[i.custom_id] = {
                        "custom_id"              : i.custom_id,
                        "satellite"              : i.satellite,
                        "sensor"                 : i.sensor,
                        "orbit"                  : i.orbit,
                        "scene"                  : i.scene,
                        "capture_date"           : str(i.capture_date.date()),
                        "cutted_image_shape"     : i[6],
                        "cloud_percentage"       : i.cloud_percentage,
                        "roll_angle"             : i.roll_angle,
                        "compressed_file_path"   : i.compressed_file_path,
                    }

    error_ = False

    pagination = Pagination(
        result.count(),
        page          = page,
        per_page      = per_page,
        offset        = offset,
        #total         = len(layers),
        total         = result.count(),
        search        = True,
        #search_msg    = "Found {} results".format(len(layers)),
        record_name   = "Rasters",
        css_framework = "bootstrap",
        bs_version    = 5
    )
    
    if geoserver_config["return"] == False:
        geoserver_config = False
        layers           = False
        error_           = False

    return render_template(
        "index.html",
        geoserver_config = geoserver_config,
        #layers         = result[0:int(len(result)/2)],
        layers           = layers,
        result           = result_render,
        map_config       = map_config,
        pagination       = pagination,
        error_           = error_
    )

# app name
@app.errorhandler(404)
def not_found(e):
    return render_template(
        "404.html",
        geoserver_config = False,
        layers           = False,
        result           = False,
        map_config       = map_config,
        pagination       = False,
        error_           = False
    )
    
if __name__ == "__main__":
    csrf.init_app(app)

    FLASK_HOST  = os.getenv("FLASK_HOST")
    FLASK_PORT  = os.getenv("FLASK_PORT")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
