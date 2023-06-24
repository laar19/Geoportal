from os import listdir
from os.path import isfile, join

import pandas as pd

"""
import geopandas as gpd

from glob import glob
"""

from xml.dom import minidom

from shapely.geometry.polygon import Polygon

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from app.models.models import DatabaseConfig

"""
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
"""

def get_tag_value(xml_file, tagname):
    tag = xml_file.getElementsByTagName(tagname)

    return float(tag[0].firstChild.nodeValue)

# Open .xml and .jpg files
path      = "data/satellite_images/"
onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

xml_files = []
jpg_files = []
for i in onlyfiles:
    if ".xml" in i:
        xml_files.append(path+i)
    if ".jpg" in i:
        jpg_files.append(path+i)

# XML tags
columns = {
    "productDate",
    "satelliteId",
    "sensorId",
    "productUpperLeftLat",
    "productUpperLeftLong",
    "productUpperRightLat",
    "productUpperRightLong",
    "productLowerLeftLat",
    "productLowerLeftLong",
    "productLowerRightLat",
    "productLowerRightLong",
    "dataUpperLeftLat",
    "dataUpperLeftLong",
    "dataUpperRightLat",
    "dataUpperRightLong",
    "dataLowerLeftLat",
    "dataLowerLeftLong",
    "dataLowerRightLat",
    "dataLowerRightLong"
}

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
        data["path"].append(jpg_files[i])
        data["metadata_xml"].append(open(xml_files[i], "r").read())
    else:
        data["image_coordinates"]  = [str(image_coordinates)]
        data["cutted_image_shape"] = [str(cutted_image_shape)]
        data["path"]               = [jpg_files[i]]
        data["metadata_xml"]       = [open(xml_files[i], "r").read()]

df = pd.DataFrame(data)
df.columns = [i.lower() for i in df.columns] # Set all columns to lowercase

db = DatabaseConfig("db_credentials_geoportal.csv")
conn, engine = db.connection()
df.to_sql("satellite_images", con=engine, if_exists="append", index=False)
