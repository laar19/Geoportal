from flask import Flask, render_template, jsonify

import json

import pandas as pd
import geopandas as gpd

from app.db_config import DbConnection
from app.functions import *

app = Flask(__name__)

db_credentials_path = "db_credentials.csv"

@app.route("/")
def index():

    DbConn         = DbConnection()
    conn, engine   = DbConn.connection(db_credentials_path, 0)
    conn2, engine2 = DbConn.connection(db_credentials_path, 1)

    query   = DbConn.select_table("centros_pob_wgs84", conn, engine)
    centros = gpd.read_postgis(query, con=engine)

    query   = DbConn.select_table("estados", conn, engine)
    estados = gpd.read_postgis(query, con=engine)
    
    query    = DbConn.select_table("vialidad_troncal", conn, engine)
    vialidad = gpd.read_postgis(query, con=engine)

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

    #img = folium.raster_layers.ImageOverlay(image=image, bounds=[[upperllat, upperllon], [lowerrlat, lowerrlon]])
    #img.add_to(folium_map)

    return render_template("index.html", data=[centros.to_json(), estados.to_json(), vialidad.to_json(), image])

if __name__ == "__main__":
    app.run(debug=True)
