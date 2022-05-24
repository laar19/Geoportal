import geopandas as gpd

import pandas as pd

import matplotlib.pyplot as plt

from sqlalchemy             import create_engine, MetaData, Table
from sqlalchemy.orm         import sessionmaker
from sqlalchemy.ext.automap import automap_base

from glob import glob

from xml.dom import minidom

from shapely.geometry.polygon import Polygon

# DB connection
db_type  = "postgresql"
host     = "localhost"
db_name  = "geoportal2"
user     = "postgres"
password = "root"

engine = create_engine(f"{db_type}://{user}:{password}@{host}/{db_name}")

# Open shapefiles
# Get all .shp files
path       = "data/layers/"
shapefiles = glob(path+"*.shp")

geometry = list()
for i in shapefiles:
    # Get filename without extension
    aux      = i.strip(path)
    filename = aux.strip(".shp")
    
    geometry.append({"filename": filename, "geom": gpd.read_file(i)})

# Upload shapefiles to DB
for i in geometry:
    i["geom"].to_postgis(i["filename"], engine, schema="layers", index=True, index_label="Index")

# Upload images to DB
metadata = MetaData(engine)
images   = Table("images", metadata, autoload=True, autoload_with=engine, schema="satellite_images")

def get_tag_value(xml_file, tagname):
    tag = xml_file.getElementsByTagName(tagname)

    return float(tag[0].firstChild.nodeValue)

# Open .xml and .jpg files
path      = "data/satellite_images/"
xml_files = glob(path+"*.xml")
jpg_files = glob(path+"*.jgp")

# XML tags
columns = {"productDate", "satelliteId", "sensorId", "productUpperLeftLat", "productUpperLeftLong", "productUpperRightLat", "productUpperRightLong", "productLowerLeftLat", "productLowerLeftLong", "productLowerRightLat", "productLowerRightLong", "dataUpperLeftLat", "dataUpperLeftLong", "dataUpperRightLat", "dataUpperRightLong", "dataLowerLeftLat", "dataLowerLeftLong", "dataLowerRightLat", "dataLowerRightLong"}

# Here we'll store the data from XML file
data = dict()

# For every XML file
for i in range(0, len(xml_files)):
    # parse an xml file by name
    xml_file = minidom.parse(xml_files[i])

    for j in columns:
        #use getElementsByTagName() to get tag
        tag = xml_file.getElementsByTagName(j)

        # First run
        if i > 0:
            data[j].append(tag[0].firstChild.nodeValue)
        else:
            data[j] = [tag[0].firstChild.nodeValue]

    image_coordinates = Polygon(
        [
            (get_tag_value(xml_file, "productUpperRightLong"), get_tag_value(xml_file, "productUpperRightLat")),
            (get_tag_value(xml_file, "productLowerRightLong"), get_tag_value(xml_file, "productLowerRightLat")),
            (get_tag_value(xml_file, "productLowerLeftLong"), get_tag_value(xml_file, "productLowerLeftLat")),
            (get_tag_value(xml_file, "productUpperLeftLong"), get_tag_value(xml_file, "productUpperLeftLat"))
        ]
    )

    cutted_image_shape = Polygon(
        [
            (get_tag_value(xml_file, "dataUpperRightLong"), get_tag_value(xml_file, "dataUpperRightLat")),
            (get_tag_value(xml_file, "dataLowerRightLong"), get_tag_value(xml_file, "dataLowerRightLat")),
            (get_tag_value(xml_file, "dataLowerLeftLong"), get_tag_value(xml_file, "dataLowerLeftLat")),
            (get_tag_value(xml_file, "dataUpperLeftLong"), get_tag_value(xml_file, "dataUpperLeftLat"))
        ]
    )

    if i > 0:
        data["image_coordinates"].append(str(image_coordinates))
        data["cutted_image_shape"].append(str(cutted_image_shape))
        data["path"].append(xml_files[i])
        data["metadata_xml"].append(open(xml_files[i], "r").read())
    else:
        data["image_coordinates"]  = [str(image_coordinates)]
        data["cutted_image_shape"] = [str(cutted_image_shape)]
        data["path"]               = [xml_files[i]]
        data["metadata_xml"]       = [open(xml_files[i], "r").read()]

df = pd.DataFrame(data)

drop_columns = ["productUpperLeftLat", "productUpperLeftLong", "productUpperRightLat", "productUpperRightLong", "productLowerLeftLat", "productLowerLeftLong", "productLowerRightLat", "productLowerRightLong", "dataUpperLeftLat", "dataUpperLeftLong", "dataUpperRightLat", "dataUpperRightLong", "dataLowerLeftLat", "dataLowerLeftLong", "dataLowerRightLat", "dataLowerRightLong"]

for i in drop_columns:
    df.pop(i)

df.to_sql("images", con=engine, schema="satellite_images", if_exists="append", index=False)


"""
images.insert().execute([
    {"date": "2021-08-20",
    "satellite": "VRSS-2",
    "sensor": "MSS",
    "image_coordinates": "POLYGON((-67.592493 6.984074, -66.68561 6.278721, -64.871844 7.487898, -63.043683 7.574268, -61.402657 6.969679 , -59.93437 6.235536, -59.488126 7.804587, -62.525465 9.08574, -62.942919 8.092487, -65.735543 8.524336, -66.383316 7.041654, -67.491729 7.300763, -67.592493 6.984074))",
    "path": "http://localhost/geoportal/testing/data/image1.jpg",
    "metadata_xml": "some data"}
])
"""
