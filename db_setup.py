import os

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import insert

from app.models.models                 import *
from app.models.satellite_images_table import *
from app.models.geoserver_table        import *

# Check if table exist
def check_table(engine, db_tables, i):
    insp = db.inspect(engine)
    
    if not insp.has_table(i, schema="public"):
        db_tables[i].__table__.create(engine)

# Check database
DB          = os.getenv("DB")
DB_HOST     = os.getenv("DB_HOST")
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT     = os.getenv("DB_PORT")

DbConn = DatabaseConfig(DB, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
DbConn.check_database()

# Check database tables
conn, engine = DbConn.connection()
for i in db_tables:
    check_table(engine, db_tables, i)

# Add geoserver configuration
stmt = insert(GeoserverConfig).values(
    url         = "http://localhost:8894/geoserver",
    workspace   = "satellite_images",
    service     = "wms",
    format_     = "image/png",
    transparent = True
)
result = conn.execute(stmt)
conn.commit()
conn.close()
