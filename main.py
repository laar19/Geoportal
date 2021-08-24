from flask import Flask, render_template, request, jsonify
from flask_wtf import CSRFProtect

from io import BytesIO

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from datetime import datetime as dtime

import pandas as pd

import json, base64, requests, hashlib

from app.db_config import DbConnection
from app.functions import *
from app.config import *

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
csrf = CSRFProtect(app)

# Globals
db_credentials_path = "db_credentials.csv"
DbConn              = DbConnection()

mapDiv = MapDiv()
default_map_config = mapDiv.main_config()

@app.route("/")
@app.route("/index")
def index():
    # Retrieve base layers
    conn, engine = DbConn.connection(db_credentials_path, 0)

    layers = [
        {
            "title": "Estados de Venezuela",
            "data" : get_layer_from_db(DbConn, conn, engine, "estados", proj_4326, proj_4326)
        }
    ]

    conn.close()

    layers = {"layers": layers}
    # End retrieve base layers

    result = {"result": 1}
    return render_template("index.html", layers=layers, images=result, map_config=default_map_config)

@app.route("/search_image", methods=["POST"])
def search_image():
    map_config = dict()
    
    # Retrieve polygons from user
    polygons_from_map = list()
    if request.method == "POST":
        map_config = {
            "center": get_coord_from_js(request.form["center"]),
            "zoom"  : float(request.form["level-zoom"])
        }
        
        for i in request.form:
            if i != "csrf_token":
                tmp = get_coord_from_js(request.form.getlist(i)[0])
                
                #if len(request.form.getlist(i)) == 2:
                if len(tmp) == 2:
                    #polygons_from_map.append(Point(float(request.form.getlist(j)[0]), float(request.form.getlist(j)[1])))
                    polygons_from_map.append(Point(tmp))
                else:
                    coordinates = list()
                    #for k in range(len(request.form.getlist(i))-1):
                    for j in range(len(tmp)-1):
                        if (j%2) == 0:
                            #coordinates.append(tuple([float(request.form.getlist(i)[j]), float(request.form.getlist(i)[j+1])]))
                            coordinates.append(tuple([float(tmp(i)[j]), float(tmp(i)[j+1])]))
                    polygons_from_map.append(Polygon(coordinates))

    # Retrieve images from database
    conn, engine = DbConn.connection(db_credentials_path, 1)
    query        = DbConn.select_table("images", conn, engine)
    df_images    = pd.read_sql(query, con=engine)
    conn.close()

    result  = list()
    targets = list()
    
    # Construct polygons from database images
    for i in range(len(df_images)):
        """
        dataUpperLeftLat      = df_images.loc[i, "dataUpperLeftLat"]
        dataUpperLeftLong     = df_images.loc[i, "dataUpperLeftLong"]
        dataUpperRightLat     = df_images.loc[i, "dataUpperRightLat"]
        dataUpperRightLong    = df_images.loc[i, "dataUpperRightLong"]
        dataLowerLeftLat      = df_images.loc[i, "dataLowerLeftLat"]
        dataLowerLeftLong     = df_images.loc[i, "dataLowerLeftLong"]
        dataLowerRightLat     = df_images.loc[i, "dataLowerRightLat"]
        dataLowerRightLong    = df_images.loc[i, "dataLowerRightLong"]
        """
        
        productUpperLeftLat   = df_images.loc[i, "productUpperLeftLat"]
        productUpperLeftLong  = df_images.loc[i, "productUpperLeftLong"]
        productUpperRightLat  = df_images.loc[i, "productUpperRightLat"]
        productUpperRightLong = df_images.loc[i, "productUpperRightLong"]
        productLowerLeftLat   = df_images.loc[i, "productLowerLeftLat"]
        productLowerLeftLong  = df_images.loc[i, "productLowerLeftLong"]
        productLowerRightLat  = df_images.loc[i, "productLowerRightLat"]
        productLowerRightLong = df_images.loc[i, "productLowerRightLong"]
        
        polygon = Polygon(
            [
                (productUpperRightLong, productUpperRightLat),
                (productLowerRightLong, productLowerRightLat),
                (productLowerLeftLong, productLowerLeftLat),
                (productUpperLeftLong, productUpperLeftLat)
            ]
        )
        targets.append(
            {
                "polygon": polygon,
                "path"   : df_images.loc[i, "path"],
                "extent" : [
                    productLowerLeftLong,
                    productLowerLeftLat,
                    productUpperRightLong,
                    productUpperRightLat
                ]
            }
        )

    # Compare new constructed polygons against recieved from user
    for i in targets:
        for j in polygons_from_map:
            if(i["polygon"].intersects(j)):
                url      = i["path"]
                response = requests.get(url)
                image    = Image.open(BytesIO(response.content))
                image    = black_to_transparency(image)
                #image = np.array(image)

                buffer = BytesIO()
                image.save(buffer, format="PNG")
                img   = buffer.getvalue()
                image = "data:image/png;base64,"+base64.b64encode(img).decode("utf-8")

                extent = i["extent"]
                name   = hashlib.md5(str(dtime.now()).encode()).hexdigest()
                result.append({"image": image, "extent": extent, "name": name})

    # Retrieve base layers
    conn, engine = DbConn.connection(db_credentials_path, 0)

    layers = [
        {
            "title": "Estados de Venezuela",
            "data" : get_layer_from_db(DbConn, conn, engine, "estados", proj_4326, proj_4326)
        }
    ]

    conn.close()

    layers = {"layers": layers}
    # End retrieve base layers

    # If there were no match
    if len(result) == 0:
        result = {"result": 1}
        return render_template("index.html", layers=layers, images=result, map_config=default_map_config)
    else:
        return render_template("index.html", layers=layers, images={"result": result}, map_config=map_config)

@app.route("/sample_layers")
def sample_layers():
    # Retrieve base layers
    conn, engine = DbConn.connection(db_credentials_path, 0)

    layers = [
        {
            "title": "Estados de Venezuela",
            "data" : get_layer_from_db(DbConn, conn, engine, "estados", proj_4326, proj_4326)
        },
        {
            "title": "Centros poblados",
            "data" : get_layer_from_db(DbConn, conn, engine, "centros_pob_wgs84", proj_4326, proj_4326)
        },
        {
            "title": "Vías troncales",
            "data" : get_layer_from_db(DbConn, conn, engine, "vialidad_troncal", proj_4326, proj_4326)
        },
        {
            "title": "Arco minero del Orinoco",
            "data" : get_layer_from_db(DbConn, conn, engine, "amo_gwgs84", proj_4326, proj_4326)
        },
        {
            "title": "índice ?",
            "data" : get_layer_from_db(DbConn, conn, engine, "indice_pr_vrss2", proj_4326, proj_4326)
        },
    ]

    conn.close()

    layers = {"layers": layers}
    # End retrieve base layers
    
    result = {"result": 1}
    return render_template("index.html", layers=layers, images=result, map_config=default_map_config)
    
if __name__ == "__main__":
    csrf.init_app(app)
    app.run(debug=True)
