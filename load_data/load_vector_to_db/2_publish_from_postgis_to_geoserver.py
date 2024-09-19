import os

from pathlib import Path

from glob import glob

from dotenv import load_dotenv

from geo.Geoserver import Geoserver

from sqlalchemy     import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.models.models    import DatabaseConfig
from app.models.functions import *

"""
# DB connection
db_type  = "postgresql"
host     = "localhost"
port     = "8870"
db_name  = "geoportal_db"
user     = "root"
password = "root"

engine = create_engine(f"{db_type}://{user}:{password}@{host}:{port}/{db_name}")
engine = create_engine(
    f"{POSTGRES_DB_TYPE}://{POSTGRES_DB_USER}:{POSTGRES_DB_PASSWORD}@{POSTGRES_DB_HOST}:{POSTGRES_DB_PORT}/{POSTGRES_DB_NAME}"
)
"""
# Load environment variables
# Specify the path to .env file
env_paths = [
    Path("deployment/geoserver/.env"),
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

inspector  = inspect(engine)
Session    = sessionmaker(bind=engine)
db_session = Session()

schema_name = "vectors"
"""
# Get all tables from the schema
table_names = inspector.get_table_names(schema=schema_name)
"""

# Initialize the library
geoserver_config_        = get_geoserver_config(db_session)
geoserver_url            = geoserver_config_[0].url[:-1]
GEOSERVER_ADMIN_USER     = os.getenv("GEOSERVER_ADMIN_USER")
GEOSERVER_ADMIN_PASSWORD = os.getenv("GEOSERVER_ADMIN_PASSWORD")

geo = Geoserver(
    geoserver_url,
    username = GEOSERVER_ADMIN_USER,
    password = GEOSERVER_ADMIN_PASSWORD
)

# Get all .shp files
source_dir_ = "/sample_data/"
data_source = os.path.expanduser("~") + source_dir_
shapefiles  = glob(data_source+"*.shp")

filenames = list()
for i in shapefiles:
    # Get filename without extension
    aux      = i.strip(data_source)
    filename = aux.strip(".shp")

    filenames.append(filename)

# For creating workspace
#for i in table_names:
for i in filenames:
    try:
        geo.create_workspace(workspace=i)
    except Exception as e:
        if "409" in str(e):
            print("Workspace already exist")
            print("Continue...")
    finally:
        # For creating postGIS connection and publish postGIS table
        geo.create_featurestore(
            store_name  = i,
            workspace   = i,
            db          = POSTGRES_DB_NAME,
            host        = "172.22.0.1", # docker gateway
            port        = POSTGRES_DB_PORT,
            schema      = schema_name,
            pg_user     = POSTGRES_DB_USER,
            pg_password = POSTGRES_DB_PASSWORD
        )

        geo.publish_featurestore(
            workspace  = i,
            store_name = i,
            pg_table   = i
        )
