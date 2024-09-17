import os

from pathlib import Path

from dotenv import load_dotenv

from sqlalchemy import insert

from app.models.models                 import *
from app.models.satellite_images_table import *
from app.models.geoserver_table        import *

# Load environment variables
# Specify the path to .env file
env_paths = [
    Path(".env"), # Is the same as load_dotenv()
    Path("deployment/geoserver/.env"),
    Path("deployment/postgis/.env")
]
# Load the environment variables from the specified files
for i in env_paths:
    load_dotenv(dotenv_path=i)

# Check if table exist
def check_table(engine, db_tables, i):
    insp = db.inspect(engine)
    
    if not insp.has_table(i, schema="public"):
        db_tables[i].__table__.create(engine)

# Check database
POSTGRES_DB_TYPE     = os.getenv("POSTGRES_DB_TYPE")
POSTGRES_DB_HOST     = os.getenv("POSTGRES_DB_HOST")
POSTGRES_DB_NAME     = os.getenv("POSTGRES_DB_NAME")
POSTGRES_DB_USER     = os.getenv("POSTGRES_DB_USER")
POSTGRES_DB_PASSWORD = os.getenv("POSTGRES_DB_PASSWORD")
POSTGRES_DB_PORT     = os.getenv("POSTGRES_DB_PORT")

DbConn = DatabaseConfig(
    POSTGRES_DB_TYPE,
    POSTGRES_DB_USER,
    POSTGRES_DB_PASSWORD,
    POSTGRES_DB_HOST,
    POSTGRES_DB_PORT,
    POSTGRES_DB_NAME
)
DbConn.check_database()
print("Check database OK")

# Check database tables
conn, engine = DbConn.connection()
for i in db_tables:
    check_table(engine, db_tables, i)
print("Check tables OK")

# Add geoserver configuration
GEOSERVER_HOST  = os.getenv("GEOSERVER_HOST")
GEOSERVER_PORT  = os.getenv("GEOSERVER_PORT")
geoserver_url   = "{}:{}/geoserver/".format(GEOSERVER_HOST, GEOSERVER_PORT)

stmt = insert(GeoserverConfig).values(
    url         = geoserver_url,
    workspace   = "satellite_images",
    service     = "wms",
    format_     = "image/png",
    transparent = True
)
result = conn.execute(stmt)
conn.commit()
conn.close()
