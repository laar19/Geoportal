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

#from app.models.models import DatabaseConfig, check_satellite_images_db
from app.models.models                 import DatabaseConfig
from app.models.satellite_images_table import *
from app.functions                     import *
from app.config                        import *

# THIRD PARTY LIBRARIES
# David Shea https://github.com/dashea/requests-file
from app.third_party.david_shea.requests_file import FileAdapter

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
csrf = CSRFProtect(app)

# Check database
db_credentials_path = "config/db_credentials_geoportal.csv"
DbConn = DatabaseConfig(db_credentials_path)
DbConn.check_database()

# Check tables
conn, engine = DbConn.connection()
check_satellite_images_table(engine)
conn.close()

mapDiv             = MapDiv()
default_map_config = mapDiv.main_config()

@app.route("/")
@app.route("/index")
def index():
    # Retrieve base layers
    """
    geometry_colums = get_all_geometry_colums(DbConn, db_credentials_path)

    layers = list()

    for i in geometry_colums["f_table_name"]:
        layers.append(
            {
                "title": i,
                "data" : get_layer_from_db(DbConn, db_credentials_path, i, proj_4326, proj_4326)
            }
        )

    layers = {"layers": layers}
    """
    layers = 1
    images = {"images": 1}
    return render_template("index.html", layers=layers, result=images, map_config=default_map_config)

@app.route("/search_image", methods=["POST"])
def search_image():
    map_config = dict()
    
    # Retrieve coordinates from user
    coord_from_user = list()
    if request.method == "POST":
        map_config = {
            "center": get_coord_from_js(request.form["center"]),
            "zoom"  : float(request.form["level-zoom"])
        }
        
        for i in request.form:
            if "matchme" in i:
                tmp = get_coord_from_js(request.form.getlist(i)[0])

                # If there is only two coordinates
                if len(tmp) == 2:
                    coord_from_user.append(Point(tmp))
                # More than two
                else:
                    coordinates = list()
                    for j in range(len(tmp)-1):
                        if j%2 == 0:
                            coordinates.append(tuple([float(tmp[j]), float(tmp[j+1])]))
                    coord_from_user.append(Polygon(coordinates))
    
    Session    = sessionmaker(bind=engine)
    db_session = Session()

    images = []
    shapes = []
    for i in coord_from_user:
        result = intersect(db_session, i)
        if result:
            for j in result:
                path = j[0]
                
                productupperleftlat   = j[1]
                productupperleftlong  = j[2]
                productupperrightlat  = j[3]
                productupperrightlong = j[4]
                productlowerleftlat   = j[5]
                productlowerleftlong  = j[6]
                productlowerrightlat  = j[7]
                productlowerrightlong = j[8]

                dataupperleftlat   = j[9]
                dataupperleftlong  = j[10]
                dataupperrightlat  = j[11]
                dataupperrightlong = j[12]
                datalowerleftlat   = j[13]
                datalowerleftlong  = j[14]
                datalowerrightlat  = j[15]
                datalowerrightlong = j[16]

                polygon = Polygon(
                    [
                        (productupperrightlong, productupperrightlat),
                        (productlowerrightlong, productlowerrightlat),
                        (productlowerleftlong, productlowerleftlat),
                        (productupperleftlong, productupperleftlat)
                    ]
                )

                polygon_shapes = Polygon(
                    [
                        (dataupperrightlong, dataupperrightlat),
                        (datalowerrightlong, datalowerrightlat),
                        (datalowerleftlong, datalowerleftlat),
                        (dataupperleftlong, dataupperleftlat)
                    ]
                )
                tmp = []
                for k in range(len(polygon_shapes.exterior.coords)):
                    tmp.append(list(polygon_shapes.exterior.coords[k]))
                shapes.append(tmp)

                extent = [
                    productlowerleftlong,
                    productlowerleftlat,
                    productupperrightlong,
                    productupperrightlat
                ]

                # THIRD PARTY
                # David Shea https://github.com/dashea/requests-file
                s = requests.Session()
                s.mount("file://", FileAdapter())
                ### END THIRD PARTY

                #resp = s.get('file:///path/to/file')
                
                url      = path
                #response = requests.get(url)
                response = s.get(url)
                image    = Image.open(BytesIO(response.content))
                image    = black_to_transparency(image)
                #image = np.array(image)

                buffer = BytesIO()
                image.save(buffer, format="PNG")
                img   = buffer.getvalue()
                image = "data:image/png;base64,"+base64.b64encode(img).decode("utf-8")

                name   = hashlib.md5(str(dtime.now()).encode()).hexdigest()
                images.append({"image": image, "extent": extent, "name": name})
    
    layers = 1

    # If there were no match
    if len(images) == 0:
        images = 1
        shapes = 1

    result = {"images": images, "shapes": shapes}
    return render_template("index.html", layers=layers, result=result, map_config=map_config)

@app.route("/sample_layers_openlayers")
def sample_layers_openlayers():
    # Retrieve base layers
    """
    layers = [
        {
            "title": "Estados de Venezuela",
            "data" : get_layer_from_db(DbConn, engine, "estados", proj_4326, proj_4326)
        },
        {
            "title": "Centros poblados",
            "data" : get_layer_from_db(DbConn, engine, "centros_pob_wgs84", proj_4326, proj_4326)
        },
        {
            "title": "Vías troncales",
            "data" : get_layer_from_db(DbConn, engine, "vialidad_troncal", proj_4326, proj_4326)
        },
        {
            "title": "Arco minero del Orinoco",
            "data" : get_layer_from_db(DbConn, engine, "amo_gwgs84", proj_4326, proj_4326)
        },
        {
            "title": "índice ?",
            "data" : get_layer_from_db(DbConn, engine, "indice_pr_vrss2", proj_4326, proj_4326)
        },
    ]

    layers = {"layers": layers}
    """

    images = {"images": 1}

    geo = Geoserver("http://localhost:8080/geoserver", username="admin", password="geoserver")
    layers = geo.get_layers()
    print(layers)

    layers = 1    
    return render_template("index.html", layers=layers, result=images, map_config=default_map_config)

@app.route("/index_leaflet")
def index_leaflet():

    map_config = {
        "zoom_level"   : default_map_config["zoom"],
        "view"         : default_map_config["center"],
        "search_status": False
    }
    
    layers = 1
    images = {"images": 1}
    return render_template("index_leaflet.html", layers=layers, result=images, map_config=map_config)

@app.route("/search_image_leaflet", methods=["POST"])
def search_image_leaflet():
    # Retrieve coordinates from user
    if request.method == "POST":
        previous_map_config = {
            "zoom_level"   : request.form["zoom_level"],
            "center"         : request.form["center"],
            "search_status": bool(request.form["search_status"])
        }

        coord_from_user =  request.form["coordinates"].split(",")

        formatted_coord_from_user1 = [i for i in zip(coord_from_user[::2], coord_from_user[1::2])]
        formatted_coord_from_user2 = []
        for i in formatted_coord_from_user1:
            formatted_coord_from_user2.append(list(i))

    if previous_map_config["search_status"]:
        print("GREAT")
        map_config = previous_map_config
    else:
        map_config = default_map_config

    """
        
        for i in request.form:
            if "matchme" in i:
                tmp = get_coord_from_js(request.form.getlist(i)[0])

                # If there is only two coordinates
                if len(tmp) == 2:
                    coord_from_user.append(Point(tmp))
                # More than two
                else:
                    coordinates = list()
                    for j in range(len(tmp)-1):
                        if j%2 == 0:
                            coordinates.append(tuple([float(tmp[j]), float(tmp[j+1])]))
                    coord_from_user.append(Polygon(coordinates))
    
    Session    = sessionmaker(bind=engine)
    db_session = Session()

    images = []
    shapes = []
    for i in coord_from_user:
        result = intersect(db_session, i)
        if result:
            for j in result:
                path = j[0]
                
                productupperleftlat   = j[1]
                productupperleftlong  = j[2]
                productupperrightlat  = j[3]
                productupperrightlong = j[4]
                productlowerleftlat   = j[5]
                productlowerleftlong  = j[6]
                productlowerrightlat  = j[7]
                productlowerrightlong = j[8]

                dataupperleftlat   = j[9]
                dataupperleftlong  = j[10]
                dataupperrightlat  = j[11]
                dataupperrightlong = j[12]
                datalowerleftlat   = j[13]
                datalowerleftlong  = j[14]
                datalowerrightlat  = j[15]
                datalowerrightlong = j[16]

                polygon = Polygon(
                    [
                        (productupperrightlong, productupperrightlat),
                        (productlowerrightlong, productlowerrightlat),
                        (productlowerleftlong, productlowerleftlat),
                        (productupperleftlong, productupperleftlat)
                    ]
                )

                polygon_shapes = Polygon(
                    [
                        (dataupperrightlong, dataupperrightlat),
                        (datalowerrightlong, datalowerrightlat),
                        (datalowerleftlong, datalowerleftlat),
                        (dataupperleftlong, dataupperleftlat)
                    ]
                )
                tmp = []
                for k in range(len(polygon_shapes.exterior.coords)):
                    tmp.append(list(polygon_shapes.exterior.coords[k]))
                shapes.append(tmp)

                extent = [
                    productlowerleftlong,
                    productlowerleftlat,
                    productupperrightlong,
                    productupperrightlat
                ]

                # THIRD PARTY
                # David Shea https://github.com/dashea/requests-file
                s = requests.Session()
                s.mount("file://", FileAdapter())
                ### END THIRD PARTY

                #resp = s.get('file:///path/to/file')
                
                url      = path
                #response = requests.get(url)
                response = s.get(url)
                image    = Image.open(BytesIO(response.content))
                image    = black_to_transparency(image)
                #image = np.array(image)

                buffer = BytesIO()
                image.save(buffer, format="PNG")
                img   = buffer.getvalue()
                image = "data:image/png;base64,"+base64.b64encode(img).decode("utf-8")

                name   = hashlib.md5(str(dtime.now()).encode()).hexdigest()
                images.append({"image": image, "extent": extent, "name": name})
    """
    
    layers = 1
    images = []

    # If there were no match
    if len(images) == 0:
        images = 1
        shapes = 1

    result = {"images": images, "shapes": shapes}
    return render_template("index_leaflet.html", layers=layers, result=result, map_config=map_config)
    
if __name__ == "__main__":
    csrf.init_app(app)
    app.run(host="192.168.92.19", port=5000, debug=True)
