from flask import Flask, render_template, request
from flask_wtf import CSRFProtect

import json

import pandas as pd
import geopandas as gpd

import base64

import requests

from io import BytesIO

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipoint import MultiPoint

from app.db_config import DbConnection
from app.functions import *
from app.config import *

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
csrf = CSRFProtect(app)

db_credentials_path = "db_credentials.csv"

@app.route("/")
def index():
    DbConn         = DbConnection()
    conn, engine   = DbConn.connection(db_credentials_path, 0)
    conn2, engine2 = DbConn.connection(db_credentials_path, 1)

    proj_4326 = 4326
    proj_3857 = 3857
    geom_col  = "geom"

    data = list()

    query   = DbConn.select_table("centros_pob_wgs84", conn, engine)
    """
    centros = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    centros = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    data.append(centros)

    query   = DbConn.select_table("estados", conn, engine)
    """
    estados = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    estados = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    data.append(estados)

    query   = DbConn.select_table("vialidad_troncal", conn, engine)
    """
    vialidad = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    vialidad = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    data.append(vialidad)

    query   = DbConn.select_table("amo_gwgs84", conn, engine)
    """
    amo = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    amo = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    data.append(amo)

    query   = DbConn.select_table("indice_pr_vrss2", conn, engine)
    """
    indice = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    indice = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    data.append(indice)

    conn.close()

    # Add image to map
    """
    
    query     = DbConn.select_table("images", conn2, engine2)
    dataframe = pd.read_sql(query, con=engine2)
    conn2.close()

    # importing modules
    url = dataframe.loc[0, "path"]
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    
    image = black_to_transparency(image)
    #image = np.array(image)

    upperllat= dataframe.loc[0, "ullat"]
    upperllon= dataframe.loc[0, "ullon"]
    lowerrlat= dataframe.loc[0, "lrlat"]
    lowerrlon= dataframe.loc[0, "lrlon"]
    extent = [lowerrlon, lowerrlat, upperllon, upperllat]
    extent = {"extent": [productLowerLeftLong, productLowerLeftLat, productUpperRightLong, productUpperRightLat]}

    buffer = BytesIO()
    image.save(buffer,format="PNG")
    img = buffer.getvalue()
    image = "data:image/png;base64,"+base64.b64encode(img).decode("utf-8")
    
    raw_data = {"image": image}

    #return render_template("index.html", data=[centros.to_json(), estados.to_json(), vialidad.to_json()], image=raw_data, extent=extent)
    #return render_template("index.html", data, img_str)
    """
    #return render_template("index.html", data=data, image=raw_data, extent=extent)
    return render_template("index.html", data=data, image={"null": 1}, extent={"null": 1})
    #return render_template("index.html", data=data, image=1, extent=1)
    #return render_template("index.html", data=data)

@app.route("/search_image", methods=["POST"])
def search_image():
    DbConn         = DbConnection()
    conn, engine   = DbConn.connection(db_credentials_path, 0)
    conn2, engine2 = DbConn.connection(db_credentials_path, 1)

    proj_4326 = 4326
    proj_3857 = 3857
    geom_col  = "geom"

    data = list()

    query   = DbConn.select_table("centros_pob_wgs84", conn, engine)
    """
    centros = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    centros = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    data.append(centros)

    query   = DbConn.select_table("estados", conn, engine)
    """
    estados = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    estados = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    data.append(estados)

    query   = DbConn.select_table("vialidad_troncal", conn, engine)
    """
    vialidad = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    vialidad = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    data.append(vialidad)

    query   = DbConn.select_table("amo_gwgs84", conn, engine)
    """
    amo = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    amo = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    data.append(amo)

    query   = DbConn.select_table("indice_pr_vrss2", conn, engine)
    """
    indice = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326) \
        .to_crs(proj_3857) \
        .to_json()
    """
    indice = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=proj_4326).to_json()
    data.append(indice)

    conn.close()

    #################################################################
    
    conn2, engine2 = DbConn.connection(db_credentials_path, 1)
    query     = DbConn.select_table("images", conn2, engine2)
    dataframe = pd.read_sql(query, con=engine2)
    conn2.close()

    url      = dataframe.loc[0, "path"]
    response = requests.get(url)
    image    = Image.open(BytesIO(response.content))
    image    = black_to_transparency(image)
    #image = np.array(image)

    buffer = BytesIO()
    image.save(buffer,format="PNG")
    img   = buffer.getvalue()
    image = "data:image/png;base64,"+base64.b64encode(img).decode("utf-8")
    
    raw_data = {"image": image}

    images = list()
    
    dataUpperLeftLat      = dataframe.loc[0, "dataUpperLeftLat"]
    dataUpperLeftLong     = dataframe.loc[0, "dataUpperLeftLong"]
    dataUpperRightLat     = dataframe.loc[0, "dataUpperRightLat"]
    dataUpperRightLong    = dataframe.loc[0, "dataUpperRightLong"]
    dataLowerLeftLat      = dataframe.loc[0, "dataLowerLeftLat"]
    dataLowerLeftLong     = dataframe.loc[0, "dataLowerLeftLong"]
    dataLowerRightLat     = dataframe.loc[0, "dataLowerRightLat"]
    dataLowerRightLong    = dataframe.loc[0, "dataLowerRightLong"]
    
    productUpperLeftLat   = dataframe.loc[0, "productUpperLeftLat"]
    productUpperLeftLong  = dataframe.loc[0, "productUpperLeftLong"]
    productUpperRightLat  = dataframe.loc[0, "productUpperRightLat"]
    productUpperRightLong = dataframe.loc[0, "productUpperRightLong"]
    productLowerLeftLat   = dataframe.loc[0, "productLowerLeftLat"]
    productLowerLeftLong  = dataframe.loc[0, "productLowerLeftLong"]
    productLowerRightLat  = dataframe.loc[0, "productLowerRightLat"]
    productLowerRightLong = dataframe.loc[0, "productLowerRightLong"]

    #extent = [productLowerLeftLong, productLowerLeftLat, productUpperRightLong, productUpperRightLat]
    extent = {"extent": [productLowerLeftLong, productLowerLeftLat, productUpperRightLong, productUpperRightLat]}
    
    target = Polygon(
        [
            (productUpperRightLong, productUpperRightLat),
            (productLowerRightLong, productLowerRightLat),
            (productLowerLeftLong, productLowerLeftLat),
            (productUpperLeftLong, productUpperLeftLat)
        ]
    )
    
    intersection_elements = list()
    
    if request.method == "POST":
        print("\nAQUI\n")
        print(request.form)
        print()

        for i in request.form:
            if i != "csrf_token":
                if len(request.form.getlist(i)) == 2:
                    intersection_elements.append(Point(float(request.form.getlist(i)[0]), float(request.form.getlist(i)[1])))
                else:
                    list_  = list()
                    for j in range(len(request.form.getlist(i))-1):
                        if (j%2) == 0:
                            list_.append(tuple([float(request.form.getlist(i)[j]), float(request.form.getlist(i)[j+1])]))
                    intersection_elements.append(Polygon(list_))

        
        for i in intersection_elements:
            if(target.intersects(i)):
                print()
                print(True)
                print()
                return render_template("index.html", data=data, image=raw_data, extent=extent)
            else:
                print()
                print(False)
                print()
                return render_template("index.html", data=data, image={"null": 1}, extent={"null": 1})
                #return render_template("index.html", data=data, image=1, extent=1)

    return None

if __name__ == "__main__":
    csrf.init_app(app)
    app.run(debug=True)
