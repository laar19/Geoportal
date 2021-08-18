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
