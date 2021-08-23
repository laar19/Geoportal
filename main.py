from flask import Flask, render_template, request
from flask_wtf import CSRFProtect

from io import BytesIO

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from datetime import datetime as dt

import pandas as pd
import geopandas as gpd

import json, base64, requests, hashlib

from app.db_config import DbConnection
from app.functions import *
from app.config import *

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
csrf = CSRFProtect(app)

db_credentials_path = "db_credentials.csv"

@app.route("/")
@app.route("/index")
def index():
    DbConn         = DbConnection()
    conn, engine   = DbConn.connection(db_credentials_path, 0)
    conn2, engine2 = DbConn.connection(db_credentials_path, 1)

    proj_4326 = 4326
    proj_3857 = 3857
    geom_col  = "geom"

    layers_data = list()

    query   = DbConn.select_table("estados", conn, engine)
    """
    estados = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    estados = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    layers_data.append({"title": "Estados de Venezuela", "data": estados})

    conn.close()

    layers = {"layers": layers_data}
    result = {"result": 1}
    return render_template("index.html", layers=layers, result=result)

@app.route("/search_image", methods=["POST"])
def search_image():
    DbConn = DbConnection()
    
    polygons_from_map = list()
    if request.method == "POST":
        for j in request.form:
            if j != "csrf_token":
                if len(request.form.getlist(j)) == 2:
                    polygons_from_map.append(Point(float(request.form.getlist(j)[0]), float(request.form.getlist(j)[1])))
                else:
                    list_  = list()
                    for k in range(len(request.form.getlist(j))-1):
                        if (k%2) == 0:
                            list_.append(tuple([float(request.form.getlist(j)[k]), float(request.form.getlist(j)[k+1])]))
                    polygons_from_map.append(Polygon(list_))

    # Retrieve base layers
    conn, engine   = DbConn.connection(db_credentials_path, 0)

    proj_4326 = 4326
    proj_3857 = 3857
    geom_col  = "geom"

    layers_data = list()

    query   = DbConn.select_table("estados", conn, engine)
    """
    estados = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    estados = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    layers_data.append({"title": "Estados de Venezuela", "data": estados})

    conn.close()

    layers = {"layers": layers_data}

    # Retreve images from database
    conn2, engine2 = DbConn.connection(db_credentials_path, 1)
    query          = DbConn.select_table("images", conn2, engine2)
    dataframe      = pd.read_sql(query, con=engine2)
    conn2.close()

    result   = list()
    targets  = list()
    
    # Get polygons from database images
    for i in range(len(dataframe)):
        dataUpperLeftLat      = dataframe.loc[i, "dataUpperLeftLat"]
        dataUpperLeftLong     = dataframe.loc[i, "dataUpperLeftLong"]
        dataUpperRightLat     = dataframe.loc[i, "dataUpperRightLat"]
        dataUpperRightLong    = dataframe.loc[i, "dataUpperRightLong"]
        dataLowerLeftLat      = dataframe.loc[i, "dataLowerLeftLat"]
        dataLowerLeftLong     = dataframe.loc[i, "dataLowerLeftLong"]
        dataLowerRightLat     = dataframe.loc[i, "dataLowerRightLat"]
        dataLowerRightLong    = dataframe.loc[i, "dataLowerRightLong"]
        
        productUpperLeftLat   = dataframe.loc[i, "productUpperLeftLat"]
        productUpperLeftLong  = dataframe.loc[i, "productUpperLeftLong"]
        productUpperRightLat  = dataframe.loc[i, "productUpperRightLat"]
        productUpperRightLong = dataframe.loc[i, "productUpperRightLong"]
        productLowerLeftLat   = dataframe.loc[i, "productLowerLeftLat"]
        productLowerLeftLong  = dataframe.loc[i, "productLowerLeftLong"]
        productLowerRightLat  = dataframe.loc[i, "productLowerRightLat"]
        productLowerRightLong = dataframe.loc[i, "productLowerRightLong"]
        
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
                "path"   : dataframe.loc[i, "path"],
                "extent" : [
                    productLowerLeftLong, productLowerLeftLat, productUpperRightLong, productUpperRightLat
                ]
            }
        )

    for i in targets:
        for j in polygons_from_map:
            if(i["polygon"].intersects(j)):
                url      = i["path"]
                response = requests.get(url)
                image    = Image.open(BytesIO(response.content))
                image    = black_to_transparency(image)
                #image = np.array(image)

                buffer = BytesIO()
                image.save(buffer,format="PNG")
                img   = buffer.getvalue()
                image = "data:image/png;base64,"+base64.b64encode(img).decode("utf-8")

                extent = i["extent"]
                name   = hashlib.md5(str(dt.now()).encode()).hexdigest()
                result.append({"image": image, "extent": extent, "name": name})

    if len(result) == 0:
        result = {"result": 1}
        return render_template("index.html", layers=layers, result=result)
    else:
        return render_template("index.html", layers=layers, result={"result": result})

@app.route("/sample_layers")
def sample_layers():
    DbConn         = DbConnection()
    conn, engine   = DbConn.connection(db_credentials_path, 0)
    conn2, engine2 = DbConn.connection(db_credentials_path, 1)

    proj_4326 = 4326
    proj_3857 = 3857
    geom_col  = "geom"

    layers_data = list()

    query   = DbConn.select_table("centros_pob_wgs84", conn, engine)
    """
    centros = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    centros = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    layers_data.append({"title": "Centros poblados", "data": centros})

    query   = DbConn.select_table("estados", conn, engine)
    """
    estados = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    estados = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    layers_data.append({"title": "Estados de Venezuela", "data": estados})

    query   = DbConn.select_table("vialidad_troncal", conn, engine)
    """
    vialidad = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    vialidad = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    layers_data.append({"title": "Vías troncales", "data": vialidad})
    

    query   = DbConn.select_table("amo_gwgs84", conn, engine)
    """
    amo = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    amo = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    layers_data.append({"title": "Arco minero del Orinoco", "data": amo})

    query   = DbConn.select_table("indice_pr_vrss2", conn, engine)
    """
    indice = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    indice = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    layers_data.append({"title": "ïndice ?", "data": indice})

    conn.close()

    layers = {"layers": layers_data}
    result = {"result": 1}
    return render_template("index.html", layers=layers, result=result)
    
if __name__ == "__main__":
    csrf.init_app(app)
    app.run(debug=True)
