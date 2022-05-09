from PIL import Image

from shapely.geometry         import Point
from shapely.geometry.polygon import Polygon

import geopandas as gpd
import numpy     as np

def black_to_transparency(img):
    x = np.asarray(img.convert("RGBA")).copy()

    x[:, :, 3] = (255 * (x[:, :, :3] > 25).any(axis=2)).astype(np.uint8)

    return Image.fromarray(x)

# Get layer from db, retrieve layer from db
def get_layer_from_db(DbConn, conn, engine, table_name, layer_proj, returned_proj):
    geom_col = "geom"
    
    query = DbConn.select_table(table_name, conn, engine)
    
    if returned_proj == 3857:
        layer = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=layer_proj) \
            .to_crs(proj_3857) \
            .to_json()
            
        return layer
    else:
        layer = gpd.read_postgis(query, con=engine, geom_col=geom_col, crs=layer_proj).to_json()
        
        return layer

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
