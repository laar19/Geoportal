from flask import Flask, render_template

import json

import pandas as pd
import geopandas as gpd

import base64

from app.db_config import DbConnection
from app.functions import *

app = Flask(__name__)

db_credentials_path = "db_credentials.csv"

@app.route("/")
def index():

    DbConn         = DbConnection()
    conn, engine   = DbConn.connection(db_credentials_path, 0)
    conn2, engine2 = DbConn.connection(db_credentials_path, 1)

    data = list()

    query   = DbConn.select_table("centros_pob_wgs84", conn, engine)
    centros = gpd.read_postgis(query, con=engine)
    centros.rename(columns = {"geom":"geometry"}, inplace = True)
    centros = gpd.GeoDataFrame(centros, crs=4326)
    centros = centros.to_crs(3857)
    data.append(centros.to_json())

    query   = DbConn.select_table("estados", conn, engine)
    estados = gpd.read_postgis(query, con=engine)
    estados.rename(columns = {"geom":"geometry"}, inplace = True)
    estados = gpd.GeoDataFrame(estados, crs=4326)
    estados = estados.to_crs(3857)
    data.append(estados.to_json())
    
    query    = DbConn.select_table("vialidad_troncal", conn, engine)
    vialidad = gpd.read_postgis(query, con=engine)
    vialidad.rename(columns = {"geom":"geometry"}, inplace = True)
    vialidad = gpd.GeoDataFrame(vialidad, crs=4326)
    vialidad = vialidad.to_crs(3857)
    data.append(vialidad.to_json())
    
    query    = DbConn.select_table("amo_gwgs84", conn, engine)
    amo = gpd.read_postgis(query, con=engine)
    amo.rename(columns = {"geom":"geometry"}, inplace = True)
    amo = gpd.GeoDataFrame(amo, crs=4326)
    amo = amo.to_crs(3857)
    data.append(amo.to_json())
    
    query    = DbConn.select_table("indice_pr_vrss2", conn, engine)
    indice = gpd.read_postgis(query, con=engine)
    indice.rename(columns = {"geom":"geometry"}, inplace = True)
    indice = gpd.GeoDataFrame(indice, crs=4326)
    indice = indice.to_crs(3857)
    data.append(indice.to_json())

    conn.close()

    # Add image to map
    
    query     = DbConn.select_table("images", conn2, engine2)
    dataframe = pd.read_sql(query, con=engine2)
    conn2.close()

    # importing modules
    import requests
    from io import BytesIO
    url = dataframe.loc[0, "path"]
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    
    image = black_to_transparency(image)
    #image = np.array(image)

    upperllat=dataframe.loc[0, "ullat"]
    upperllon=dataframe.loc[0, "ullon"]
    lowerrlat=dataframe.loc[0, "lrlat"]
    lowerrlon=dataframe.loc[0, "lrlon"]
    extent = [lowerrlon, lowerrlat, upperllon, upperllat]

    buffer = BytesIO()
    image.save(buffer,format="PNG")
    img = buffer.getvalue()
    image = "data:image/png;base64,"+base64.b64encode(img).decode("utf-8")
    
    raw_data = {"image": image}

    #return render_template("index.html", data=[centros.to_json(), estados.to_json(), vialidad.to_json()], image=raw_data, extent=extent)
    #return render_template("index.html", data, img_str)
    return render_template("index.html", data=data, image=raw_data, extent=extent)

if __name__ == "__main__":
    app.run(debug=True)
