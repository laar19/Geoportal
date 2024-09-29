import os

import geopandas as gpd

from pathlib import Path

from glob import glob

from sqlalchemy       import create_engine, Column, MetaData, Table, text, insert
from sqlalchemy.types import VARCHAR

from dotenv import load_dotenv

from app.models.vectors_table import *

# Load environment variables
# Specify the path to .env file
env_paths = [
    Path("deployment/postgis/.env")
]
# Load the environment variables from the specified files
for i in env_paths:
    load_dotenv(dotenv_path=i)

# DB conn
POSTGRES_DB_TYPE     = os.getenv("POSTGRES_DB_TYPE")
POSTGRES_DB_HOST     = os.getenv("POSTGRES_DB_HOST")
POSTGRES_DB_NAME     = os.getenv("POSTGRES_DB_NAME")
POSTGRES_DB_USER     = os.getenv("POSTGRES_DB_USER")
POSTGRES_DB_PASSWORD = os.getenv("POSTGRES_DB_PASSWORD")
POSTGRES_DB_PORT     = os.getenv("POSTGRES_DB_PORT")

engine = create_engine(
    "{}://{}:{}@{}:{}/{}".format(
        POSTGRES_DB_TYPE,
        POSTGRES_DB_USER,
        POSTGRES_DB_PASSWORD,
        POSTGRES_DB_HOST,
        POSTGRES_DB_PORT,
        POSTGRES_DB_NAME
    )
)

# Get all .shp files
source_dir_ = "/sample_data/"
data_source = os.path.expanduser("~") + source_dir_
shapefiles  = glob(data_source+"*.shp")

geometry = list()
for i in shapefiles:
    # Get filename without extension
    aux      = i.strip(data_source)
    filename = aux.strip(".shp")
    filename = filename.lower()

    gdf = gpd.read_file(i)      # Read the shapefile
    gdf = gdf.to_crs(epsg=4326) # Transform CRS

    # Add colums
    gdf["custom_id"]             = filename
    gdf["name"]                  = filename
    gdf["geoserver_workspace"]   = filename
    gdf["geoserver_service"]     = "wms"
    gdf["geoserver_format"]      = "image/png"
    gdf["geoserver_transparent"] = "true"
    gdf["test_json_field"]       = {"test": True}

    # Rename the column
    #gdf = gdf.rename(columns={"geom": "geometry"})

    #geometry.append({"filename": filename, "geom": gpd.read_file(i)})
    geometry.append({"filename": filename, "geom": gdf})

# Upload shapefiles to DB

# Points
#pointDf.to_postgis("wellpoints", engine, index=True, index_label="Index")

# Lines
#lineDf.to_postgis("contourlines", engine, index=True, index_label="Index")

# Polygons
#polyDf.to_postgis("lakepolygons", engine, index=True, index_label="Index")

# Create the new schema and insert the new column
schema_name = "vectors"

def create_schema(engine, schema_name):
    with engine.connect() as conn:
        # Check if schema exists
        result = conn.execute(
            text(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema_name"
            ),
            {"schema_name": schema_name}
        )
        exists = result.fetchone()
        
        if not exists:
            # Create schema if it does not exist
            conn.execute(text(f"CREATE SCHEMA {schema_name}"))
            conn.commit()
            print(f"Schema '{schema_name}' created.")
        else:
            print(f"Schema '{schema_name}' already exists.")

try:
    create_schema(engine, schema_name)
except Exception as e:
    print(f"An error occurred: {e}")

for i in geometry:
    i["geom"].to_postgis(
        i["filename"],
        engine,
        schema      = schema_name,
        index       = True,
        index_label = "Index"
    )

    """
    stmt = insert(Vectors).values(
        custom_id             = i["filename"],
        name                  = i["filename"],
        geoserver_workspace   = i["filename"],
        geoserver_service     = "wms",
        geoserver_format      = "image/png",
        geoserver_transparent = "true"
    )

    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    """
