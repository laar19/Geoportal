from flask     import Flask, render_template, request, jsonify
from flask_wtf import CSRFProtect

from io import BytesIO

from shapely.geometry         import Point
from shapely.geometry.polygon import Polygon

from datetime import datetime as dtime

from folium.plugins import Draw

import pandas as pd

import json, base64, requests, hashlib

import folium

import geopandas as gpd

from app.db_config import DbConnection
from app.functions import *
from app.config    import *

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
csrf = CSRFProtect(app)

# Globals
db_credentials_path = "db_credentials.csv"
DbConn              = DbConnection()

mapDiv             = MapDiv()
default_map_config = mapDiv.main_config()

@app.route("/")
@app.route("/index")
def index():
    # Retrieve base layers
    conn, engine = DbConn.connection(db_credentials_path, 0)

    query        = DbConn.select_table("geometry_columns", conn, engine)
    layer_tables = pd.read_sql(query, con=engine)
    conn.close()

    layers = list()

    for i in layer_tables["f_table_name"]:
        layers.append(
            {
                "title": i,
                "data" : get_layer_from_db(DbConn, conn, engine, i, proj_4326, proj_4326)
            }
        )
    conn.close()

    layers = {"layers": layers}

    result = {"result": 1}
    return render_template("index.html", layers=layers, images=result, map_config=default_map_config)

@app.route("/search_image", methods=["POST"])
def search_image():
    map_config = dict()
    
    # Retrieve polygons from user
    polygons_from_user = list()
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
                    polygons_from_user.append(Point(tmp))
                # More than two
                else:
                    coordinates = list()
                    for j in range(len(tmp)-1):
                        if (j%2) == 0:
                            coordinates.append(tuple([float(tmp[j]), float(tmp[j+1])]))
                    polygons_from_user.append(Polygon(coordinates))

    # Retrieve images from database
    conn, engine = DbConn.connection(db_credentials_path, 1)
    query        = DbConn.select_table("images", conn, engine)
    df_images    = pd.read_sql(query, con=engine)
    conn.close()

    result  = list()
    targets = list()
    
    # Construct polygons from database images
    for i in range(len(df_images)):
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

    # Compare new constructed polygons and points against recieved from user
    for i in targets:
        for j in polygons_from_user:
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

    # If there were no match
    if len(result) == 0:
        result = {"result": 1}
        return render_template("index.html", layers=layers, images=result, map_config=default_map_config)
    else:
        return render_template("index.html", layers=layers, images={"result": result}, map_config=map_config)

@app.route("/sample_layers_openlayers_openlayers")
def sample_layers_openlayers():
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
    
    result = {"result": 1}
    return render_template("index.html", layers=layers, images=result, map_config=default_map_config)

@app.route("/sample_layers_folium")
def sample_layers_folium():
    # Retrieve base layers
    conn, engine = DbConn.connection(db_credentials_path, 0)

    # HAZME BONITO COMO EL DE ARRIBA
    sql = "SELECT * FROM vialidad_troncal"
    gdf = gpd.read_postgis(sql, conn)

    query        = DbConn.select_table("geometry_columns", conn, engine)
    layer_tables = pd.read_sql(query, con=engine)
    conn.close()

    layers = list()

    for i in layer_tables["f_table_name"]:
        #if i != "centros_pob_wgs84":
        layers.append(
            {
                "title": i,
                "data" : get_layer_from_db(DbConn, conn, engine, i, proj_4326, proj_4326)
            }
        )
    conn.close()

    start_coords = (46.9540700, 142.7360300)
    folium_map = folium.Map(location=start_coords, zoom_start=5.5)

    #draw = Draw()
    draw = Draw(
        export       = True,
        filename     = "my_data.geojson",
        position     = "topleft",
        draw_options = {"polyline": {"allowIntersection": False}},
        edit_options = {"poly": {"allowIntersection": False}}
    )
    draw.add_to(folium_map)

    for i in range(0, len(layers)):
        tmp     = json.loads(layers[i]["data"])
        tmp_gdf = gpd.GeoDataFrame.from_features(tmp["features"])

        for _, row in tmp_gdf.iterrows():
            if row["geometry"].geom_type != "MultiPoint":
                # Without simplifying the representation of each borough,
                # the map might not be displayed
                sim_geo = gpd.GeoSeries(row["geometry"]).simplify(tolerance=0.001)
                geo_j   = sim_geo.to_json()
                geo_j   = folium.GeoJson(data=geo_j,
                                       style_function=lambda x: {"fillColor": "orange"})
                #folium.Popup(row["nombre"]).add_to(geo_j)
                geo_j.add_to(folium_map)
    
    return folium_map._repr_html_()
    
    
if __name__ == "__main__":
    csrf.init_app(app)
    app.run(debug=True)
