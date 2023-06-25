import numpy as np

import pandas as pd

import geopandas as gpd

from PIL import Image

from shapely.geometry         import Point
from shapely.geometry.polygon import Polygon

from sqlalchemy             import func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm         import sessionmaker
from sqlalchemy.sql         import select

"""
# Get all geometry colums from database
def get_all_geometry_colums(DbConn, db_credentials_path):
    conn, engine = DbConn.connection()
    
    query        = DbConn.select_table("geometry_columns", engine)
    layer_tables = pd.read_sql(query, con=engine)
    conn.close()

    return layer_tables
"""

"""
# Abstract table (ORM) on database
def abs_table(DbConn, tablename):
    conn, engine = DbConn.connection()
    
    Session = sessionmaker(bind=engine)

    # these two lines perform the "database reflection" to analyze tables and relationships
    Base = automap_base()
    Base.prepare(engine, reflect=True)

    # there are many tables in the database but I want `products` and `categories`
    # only so I can leave others out
    #table = Base.classes.tablename
    #table = getattr(Base.classes, tablename)()
    table = getattr(Base.classes, tablename)

    # for debugging and passing the query results around
    # I usually add as_dict method on the classes
    def as_dict(obj):
        data = obj.__dict__
        data.pop("_sa_instance_state")
        return data

    # add the `as_dict` function to the classes
    for c in [table]:
        c.as_dict = as_dict

    conn.close()

    return table
"""

def black_to_transparency(img):
    x = np.asarray(img.convert("RGBA")).copy()

    x[:, :, 3] = (255 * (x[:, :, :3] > 25).any(axis=2)).astype(np.uint8)

    return Image.fromarray(x)

"""
# Get layer from db, retrieve layer from db
def get_layer_from_db(DbConn, db_credentials_path, table_name, layer_proj, returned_proj):
    conn, engine = DbConn.connection()
    geom_col = "geom"
    
    query = DbConn.select_table(table_name, engine)
    
    if returned_proj == 3857:
        layer = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=layer_proj) \
            .to_crs(proj_3857) \
            .to_json()

        conn.close()
            
        return layer
    else:
        layer = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=layer_proj).to_json()

        conn.close()
        
        return layer
"""

# Get coordinates from javascript, extract the list sent from javascript
def get_coord_from_js(string):
    string += ","
    
    element = str()
    list_   = list()

    for i in string:
        if i != ",":
            element += i
        else:
            list_.append(float(element))
            element = str()

    return list_

"""
# Match user coordinates selection vs stored on database
#def match_coordinates(DbConn, db_credentials_path, request, tables):
def match_coordinates(DbConn, db_credentials_path, request):
    conn, engine = DbConn.connection()
    
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
                    #coord_from_user.append(Point(tmp))
                    coord_from_user.append({"type":"POINT", "value":Point(tmp)})
                # More than two
                else:
                    coordinates = list()
                    for j in range(len(tmp)-1):
                        if j%2 == 0:
                            coordinates.append(tuple([float(tmp[j]), float(tmp[j+1])]))
                    #coord_from_user.append(Polygon(coordinates))
                    coord_from_user.append({"type":"POLYGON", "value":Polygon(coordinates)})

    print()
    print("OK")
    print()
    print(coord_from_user)

    #s = select([amo_gwgs84],
    s = select([tables["amo_gwgs84"]],
        func.ST_Intersects(tables["amo_gwgs84"].geom, 'POLYGON((-67.592493 6.984074, -66.68561 6.278721, -64.871844 7.487898, -63.043683 7.574268, -61.402657 6.969679 , -59.93437 6.235536, -59.488126 7.804587, -62.525465 9.08574, -62.942919 8.092487, -65.735543 8.524336, -66.383316 7.041654, -67.491729 7.300763, -67.592493 6.984074))'))
    result = conn.execute(s)

    rows = result.fetchall()
    for i in rows:
        print()
        print(i)
        print()

    conn.close()
"""
