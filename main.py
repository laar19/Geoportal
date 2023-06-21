import pandas    as pd
import geopandas as gpd

import json

import base64

import requests

import hashlib

from flask     import Flask, render_template, request, jsonify
from flask_wtf import CSRFProtect

from io import BytesIO

from shapely.geometry         import Point
from shapely.geometry.polygon import Polygon

from datetime import datetime as dtime

from geo.Geoserver import Geoserver

from app.models.models import DatabaseConfig, check_satellite_images_db
from app.functions     import *
from app.config        import *

# THIRD PARTY LIBRARIES
# David Shea https://github.com/dashea/requests-file
from app.third_party.david_shea.requests_file import FileAdapter

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
csrf = CSRFProtect(app)

# Globals
db_credentials_path = "config/db_credentials.csv"
DbConn              = DatabaseConfig(db_credentials_path, 1)

mapDiv             = MapDiv()
default_map_config = mapDiv.main_config()

# Abstract all geometry colums on database
"""
geometry_colums = get_all_geometry_colums(DbConn, db_credentials_path)
tables          = dict()
for i in geometry_colums["f_table_name"]:
    tables[i] = abs_table(DbConn, i)
"""

check_satellite_images_db()

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

    # Retrieve images from database
    conn, engine = DbConn.connection()
    query        = DbConn.select_table("images", engine)
    df_images    = pd.read_sql(query, con=engine)
    #conn.close()

    images  = list()
    targets = list()
    
    # Construct polygons from database images
    for i in range(len(df_images)):
        productUpperLeftLat   = df_images.loc[i, "productupperleftlat"]
        productUpperLeftLong  = df_images.loc[i, "productupperleftlong"]
        productUpperRightLat  = df_images.loc[i, "productupperrightlat"]
        productUpperRightLong = df_images.loc[i, "productupperrightlong"]
        productLowerLeftLat   = df_images.loc[i, "productlowerleftlat"]
        productLowerLeftLong  = df_images.loc[i, "productlowerleftlong"]
        productLowerRightLat  = df_images.loc[i, "productlowerrightlat"]
        productLowerRightLong = df_images.loc[i, "productlowerrightlong"]

        dataUpperLeftLat   = df_images.loc[i, "dataupperleftlat"]
        dataUpperLeftLong  = df_images.loc[i, "dataupperleftlong"]
        dataUpperRightLat  = df_images.loc[i, "dataupperrightlat"]
        dataUpperRightLong = df_images.loc[i, "dataupperrightlong"]
        dataLowerLeftLat   = df_images.loc[i, "datalowerleftlat"]
        dataLowerLeftLong  = df_images.loc[i, "datalowerleftlong"]
        dataLowerRightLat  = df_images.loc[i, "datalowerrightlat"]
        dataLowerRightLong = df_images.loc[i, "datalowerrightlong"]
        
        polygon = Polygon(
            [
                (productUpperRightLong, productUpperRightLat),
                (productLowerRightLong, productLowerRightLat),
                (productLowerLeftLong, productLowerLeftLat),
                (productUpperLeftLong, productUpperLeftLat)
            ]
        )

        polygon_shapes = Polygon(
            [
                (dataUpperRightLong, dataUpperRightLat),
                (dataLowerRightLong, dataLowerRightLat),
                (dataLowerLeftLong, dataLowerLeftLat),
                (dataUpperLeftLong, dataUpperLeftLat)
            ]
        )
        
        targets.append(
            {
                "polygon": polygon,
                "shapes" : polygon_shapes,
                "path"   : df_images.loc[i, "path"],
                "extent" : [
                    productLowerLeftLong,
                    productLowerLeftLat,
                    productUpperRightLong,
                    productUpperRightLat
                ]
            }
        )

    #match_coordinates(DbConn, db_credentials_path, request, tables)
    #match_coordinates(DbConn, db_credentials_path, request)

    # List of user polygons
    shapes = list()

    # Compare new constructed polygons and points against recieved from user
    for i in targets:
        for j in coord_from_user:
            if i["polygon"].intersects(j):
                # Convert polygons from user to list
                tmp = list()
                for k in range(len(i["shapes"].exterior.coords)):
                    tmp.append(list(i["shapes"].exterior.coords[k]))
                shapes.append(tmp)

                # THIRD PARTY
                # David Shea https://github.com/dashea/requests-file
                s = requests.Session()
                s.mount('file://', FileAdapter())
                ### END THIRD PARTY

                #resp = s.get('file:///path/to/file')
                
                url      = i["path"]
                #response = requests.get(url)
                response = s.get(url)
                image    = Image.open(BytesIO(response.content))
                image    = black_to_transparency(image)
                #image = np.array(image)

                buffer = BytesIO()
                image.save(buffer, format="PNG")
                img   = buffer.getvalue()
                image = "data:image/png;base64,"+base64.b64encode(img).decode("utf-8")

                extent = i["extent"]
                name   = hashlib.md5(str(dtime.now()).encode()).hexdigest()
                images.append({"image": image, "extent": extent, "name": name})

    """
    from sqlalchemy.sql import text
    stmt = select().where(
        func.ST_Intersects(
            'images.cutted_image_shape' \
            ,'POLYGON ((-70.810267 10.300543, -70.872173 10.005507, -71.172781 10.064082, -71.111674 10.359124, -70.810267 10.300543))'
        )
    )
    result = conn.execute(stmt)

    rows = result.fetchall()
    for i in rows:
        print()
        print(i)
        print()

    conn.close()

    # Retrieve base layers
    """
    """
    DbConn2              = DatabaseConfig(db_credentials_path)
    layers = [
        {
            "title": "Estados de Venezuela",
            "data" : get_layer_from_db(DbConn2, db_credentials_path, "estados", proj_4326, proj_4326),
        }
    ]

    layers = {"layers": layers}
    """
    layers = 1

    # If there were no match
    if len(images) == 0:
        images = {"images": 1}
        shapes = {"shapes": 1}
        return render_template("index.html", layers=layers, result=images, shapes=shapes, map_config=default_map_config)
    else:
        return render_template("index.html", layers=layers, result={"images": images, "shapes": shapes}, map_config=map_config)

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
    
if __name__ == "__main__":
    csrf.init_app(app)
    app.run(debug=True)
