from flask import Flask, render_template

import json

import pandas as pd
import geopandas as gpd

from app.db_config import DbConnection

app = Flask(__name__)

db_credentials_path = "db_credentials.csv"

@app.route("/")
def index():
    #fields_df = pd.read_csv("testing/data/fields.csv")
    #fields    = fields_df.to_json()
    #fields    = fields_df.to_json(orient="values")
    #fields    = fields_df.to_json(orient="columns")
    #fields    = fields_df.to_json(orient="index")
    #fields    = fields_df.to_json(orient="table")

    DbConn   = DbConnection()
    conn, engine = DbConn.connection(db_credentials_path)
    """
    centros  = DbConn.select_table("centros_pob_wgs84", conn)
    estados  = DbConn.select_table("estados", conn)
    vialidad = DbConn.select_table("vialidad_troncal", conn)
    """

    """
    data["centros"]  = gpd.read_postgis("centros_pob_wgs84", con=engine).to_json()
    data["estados"]  = gpd.read_postgis("estados", con=engine).to_json()
    data["vialidad"] = gpd.read_postgis("vialidad_troncal", con=engine).to_json()
    display_on_map = json.dumps(data)
    """

    #data["centros"] = DbConn.select_table("centros_pob_wgs84", conn, engine)
    #data["estados"] = DbConn.select_table("estados", conn, engine)
    #data["vialidad"] = DbConn.select_table("vialidad_troncal", conn, engine)

    #data = dict()
    """
    data = DbConn.select_table("centros_pob_wgs84",
        conn,
        engine)[["latitud", "longitud"]].copy().to_json(orient="values")
    """

    query = DbConn.select_table("centros_pob_wgs84", conn, engine)
    centros = pd.read_sql(query, conn)[["latitud", "longitud"]].copy().to_json(orient="values")

    query = DbConn.select_table("estados", conn, engine)
    estados = gpd.read_postgis(query, con=engine)#.to_crs(epsg=4326)

    conn.close()

    return render_template("index.html", data=[centros, estados.to_json()])

if __name__ == "__main__":
    app.run(debug=True)
